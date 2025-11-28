import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- CẤU HÌNH ---
INPUT_EXCEL_FILE = 'file_gan_nhan.xlsx' # File gốc chứa dữ liệu
SHEET_URL = "https://docs.google.com/spreadsheets/d/1VDro6njhY0p5QfAYlrf5_yu5ngMdHU3X8_rbgSVqepM/edit?hl=vi&gid=0#gid=0DÁN_LINK_GOOGLE_SHEET_CỦA_BẠN_VÀO_ĐÂY" # Ví dụ: https://docs.google.com/spreadsheets/d/xxxx...

# --- KẾT NỐI GOOGLE SHEETS ---
def get_gsheet_client():
    # Lấy thông tin từ secrets
    creds_dict = dict(st.secrets["gsheets"])
    
    # Định nghĩa scope (quyền)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Tạo credentials
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def load_done_data_from_sheet():
    """Đọc dữ liệu đã làm từ Google Sheet về để lọc"""
    try:
        client = get_gsheet_client()
        sheet = client.open_by_url(SHEET_URL).sheet1
        # Lấy toàn bộ records
        data = sheet.get_all_records() 
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame() # Trả về rỗng nếu chưa có gì hoặc lỗi

def save_to_gsheet(text_id, text_content, label, note):
    """Ghi trực tiếp 1 dòng lên Google Sheet"""
    try:
        client = get_gsheet_client()
        sheet = client.open_by_url(SHEET_URL).sheet1
        # Thêm dòng mới vào cuối bảng
        sheet.append_row([text_id, text_content, label, note])
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu lên Google Sheet: {e}")
        return False

# --- HÀM XỬ LÝ LOGIC (QUAN TRỌNG) ---
def get_remaining_data(df_input, df_done):
    """
    Lấy Input trừ đi Output (dựa vào ID)
    để ra danh sách các câu chưa làm.
    """
    if df_done.empty or 'id' not in df_done.columns:
        return df_input
    
    # Lấy danh sách ID đã làm
    done_ids = df_done['id'].unique()
    
    # Lọc: Chỉ giữ lại những dòng trong Input mà ID KHÔNG nằm trong done_ids
    # Dấu ~ nghĩa là phủ định (NOT)
    df_remaining = df_input[~df_input['id'].isin(done_ids)]
    
    return df_remaining

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Tool Gán Nhãn Dữ Liệu 'Niềm tin bản thân' Online", layout="centered")
st.title("☁️ Tool Gán Nhãn Dữ Liệu 'Niềm tin bản thân' Online")

# 1. Load Input (File Excel gốc)
if os.path.exists(INPUT_EXCEL_FILE):
    try:
        df_input = pd.read_excel(INPUT_EXCEL_FILE, engine='openpyxl')
        # Đảm bảo cột ID là string hoặc int thống nhất để so sánh
        df_input['id'] = df_input['id'].astype(str) 
    except Exception as e:
        st.error(f"Lỗi đọc file Input: {e}")
        st.stop()
else:
    st.error("Không tìm thấy file Excel đầu vào!")
    st.stop()

# 2. Load Output (Dữ liệu đã làm trên Sheet)
df_done = load_done_data_from_sheet()
if not df_done.empty:
    df_done['id'] = df_done['id'].astype(str)

# 3. Tính toán dữ liệu còn lại
df_remaining = get_remaining_data(df_input, df_done)

# Thống kê tiến độ
total = len(df_input)
done_count = len(df_done) if not df_done.empty else 0
st.progress(done_count / total)
st.caption(f"Tiến độ: Đã làm {done_count} / {total} câu. (Còn lại {len(df_remaining)} câu)")

# 4. Hiển thị Form gán nhãn
if not df_remaining.empty:
    # Lấy dòng đầu tiên của danh sách CÒN LẠI (Luôn là dòng đầu vì danh sách tự co ngắn lại)
    row = df_remaining.iloc[0]

    st.info(f"📝 **Nội dung (ID: {row['id']}):**\n\n{row['text']}")

    with st.form("labeling_form"):
        label = st.radio(
            "Chọn nhãn:",
            ["Niềm tin bản thân rõ ràng", "Niềm tin bản thân ngầm định", "Không phải niềm tin bản thân"],
            index=None
        )
        note = st.text_input("Ghi chú:")
        
        submitted = st.form_submit_button("Lưu & Tiếp theo ➡️")

        if submitted:
            if label:
                # Ghi lên Sheet
                success = save_to_gsheet(row['id'], row['text'], label, note)
                if success:
                    st.success("Đã lưu thành công!")
                    st.rerun() # Load lại trang -> Tự động tính lại df_remaining -> Hiện câu mới
            else:
                st.warning("Vui lòng chọn nhãn!")

else:
    st.success("🎉 TUYỆT VỜI! Đã gán nhãn xong toàn bộ dữ liệu!")
    st.balloons()