import streamlit as st
import pandas as pd
import os

# --- CẤU HÌNH TÊN FILE ---
# 1. Tên file Excel đầu vào (Bạn nhớ để file này cùng thư mục với code)
INPUT_EXCEL_FILE = 'file_gan_nhan.xlsx' 

# 2. Tên file Excel kết quả đầu ra
OUTPUT_EXCEL_FILE = 'ket_qua_gan_nhan.xlsx'

# --- HÀM XỬ LÝ DỮ LIỆU ---
def load_data():
    """Đọc file Excel (.xlsx) an toàn"""
    if os.path.exists(INPUT_EXCEL_FILE):
        try:
            # SỬA LỖI Ở ĐÂY: Dùng read_excel, KHÔNG dùng read_csv
            df = pd.read_excel(INPUT_EXCEL_FILE, engine='openpyxl') 
            return df
        except Exception as e:
            st.error(f"Lỗi khi đọc file Excel: {e}")
            st.info("Gợi ý: Hãy chạy lệnh 'pip install openpyxl' nếu bạn chưa cài.")
            return None
    else:
        st.error(f"⚠️ Không tìm thấy file: '{INPUT_EXCEL_FILE}'")
        return None

def save_to_excel(text_id, text_content, label, note):
    """Lưu kết quả vào file Excel output"""
    
    # Tạo một dòng dữ liệu mới
    new_data = pd.DataFrame([{
        'id': text_id,
        'text': text_content,
        'label': label,
        'note': note
    }])

    try:
        if os.path.exists(OUTPUT_EXCEL_FILE):
            # Nếu file kết quả đã có, đọc lên và nối thêm dòng mới
            existing_df = pd.read_excel(OUTPUT_EXCEL_FILE, engine='openpyxl')
            updated_df = pd.concat([existing_df, new_data], ignore_index=True)
        else:
            # Nếu chưa có, dòng mới chính là khởi đầu
            updated_df = new_data
        
        # Lưu đè lại vào file Excel
        updated_df.to_excel(OUTPUT_EXCEL_FILE, index=False, engine='openpyxl')
        
    except Exception as e:
        st.error(f"Lỗi khi lưu file: {e}")
        # Gợi ý tắt file excel nếu đang mở
        st.warning("⚠️ Hãy đóng file Excel kết quả nếu bạn đang mở nó!")

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Tool Gán Nhãn Excel", layout="centered")
st.title("📊 Tool Gán Nhãn (Excel Version)")

# 1. Quản lý trạng thái (Index câu hiện tại)
if 'index' not in st.session_state:
    st.session_state.index = 0

# 2. Load dữ liệu
df = load_data()

# 3. Logic hiển thị
if df is not None and not df.empty:
    total = len(df)
    current = st.session_state.index

    # Kiểm tra xem còn dữ liệu để gán không
    if current < total:
        row = df.iloc[current]

        # Thanh tiến trình
        st.progress(current / total)
        st.caption(f"Câu số: {current + 1} / {total}")

        # Hiển thị nội dung
        st.info(f"📝 **Nội dung:**\n\n{row['text']}")

        # Form gán nhãn
        with st.form("labeling_form"):
            label = st.radio(
                "Chọn nhãn:",
                ["Tích cực", "Tiêu cực", "Trung lập"],
                index=None
            )
            note = st.text_input("Ghi chú:")
            
            submitted = st.form_submit_button("Lưu & Tiếp theo ➡️")

            if submitted:
                if label:
                    # Lưu dữ liệu
                    save_to_excel(row['id'], row['text'], label, note)
                    # Tăng index
                    st.session_state.index += 1
                    st.rerun()
                else:
                    st.warning("Vui lòng chọn một nhãn!")
    else:
        # Khi hoàn thành
        st.success("🎉 Đã gán nhãn xong toàn bộ dữ liệu!")
        st.balloons()

        # Nút tải file
        if os.path.exists(OUTPUT_EXCEL_FILE):
            with open(OUTPUT_EXCEL_FILE, "rb") as f:
                st.download_button(
                    "📥 Tải file kết quả (.xlsx)",
                    f,
                    file_name="ket_qua_final.xlsx"
                )