import streamlit as st
import requests
from PIL import Image
import io
import os
import time
from dotenv import load_dotenv

# 1. Cấu hình trang (Phải để đầu tiên)
st.set_page_config(
    page_title="AI Detection System",
    page_icon="🕵️",
    layout="wide"
)

# Load biến môi trường
load_dotenv()
API_URL = os.getenv("API_URL")

# --- CSS Tùy chỉnh cho đẹp ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
    }
    .reportview-container {
        background: #f0f2f6
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Thanh bên trái) ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("---")
    
    # Check trạng thái Server
    st.subheader("System Status")
    try:
        # Gọi thử vào root hoặc docs để check server sống hay chết
        response = requests.get(f"{API_URL}/docs", timeout=2)
        if response.status_code == 200:
            st.success(f"🟢 Server Online: {API_URL}")
        else:
            st.error("🔴 Server Error")
    except:
        st.error("🔴 Connection Failed")

    st.markdown("---")
    
    # Cấu hình Model
    st.subheader("Model Config")
    confidence_threshold = st.slider(
        "Confidence Threshold", 
        min_value=0.0, max_value=1.0, value=0.5, step=0.05,
        help="Chỉ hiện các vật thể có độ tự tin cao hơn mức này."
    )
    
    model_version = st.selectbox(
        "Select Model Version",
        ["DeepLabV3_Production", "DeepLabV3_Staging (Beta)"],
        index=0
    )

# --- MAIN PAGE (Giao diện chính) ---
st.title("🕵️ Object Detection System")
st.markdown("Upload an image to detect objects via Azure Cloud API.")

# Chia cột: Bên trái upload, Bên phải kết quả
col1, col2 = st.columns([1, 1])

uploaded_file = None

with col1:
    st.subheader("1. Input Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Hiển thị ảnh gốc
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Image", use_column_width=True)

with col2:
    st.subheader("2. Detection Result")
    
    if uploaded_file is not None:
        # Nút bấm bắt đầu Detect
        if st.button("🚀 Analyze Image"):
            with st.spinner('Sending data to Azure Server...'):
                try:
                    # Chuẩn bị file để gửi
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format=image.format)
                    img_bytes = img_bytes.getvalue()
                    
                    files = {"data": ("image.jpg", img_bytes, "image/jpeg")}
                    
                    # Ghi nhận thời gian bắt đầu
                    start_time = time.time()
                    
                    # --- GỌI API (Thay đường dẫn endpoint của bạn vào đây) ---
                    # Ví dụ endpoint là /predict/image
                    api_endpoint = f"{API_URL}/api/predict" # Sửa lại cho đúng route của bạn
                    
                    # Giả lập gửi thêm threshold (nếu API bạn có hỗ trợ)
                    params = {"threshold": confidence_threshold}
                    
                    response = requests.post(api_endpoint, files=files, params=params)
                    
                    # Tính toán độ trễ (Latency)
                    latency = time.time() - start_time
                    
                    if response.status_code == 200:
                        # 1. Nếu API trả về ảnh đã vẽ box
                        # result_image = Image.open(io.BytesIO(response.content))
                        # st.image(result_image, caption="Processed Image", use_column_width=True)
                        
                        # 2. (Trường hợp phổ biến) Nếu API trả về JSON tọa độ
                        # Ở đây mình giả lập hiển thị JSON để bạn debug
                        st.success(f"✅ Detection Complete in {latency:.2f}s")
                        
                        # Hiển thị kết quả dạng JSON cho "ngầu" (Dân kỹ thuật thích cái này)
                        with st.expander("View Raw JSON Response"):
                            st.json(response.json())
                            
                        # Nếu API trả về ảnh (Binary) thì uncomment dòng dưới:
                        # st.image(response.content, use_column_width=True)
                        
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error connecting to API: {e}")

    else:
        st.info("👈 Please upload an image from the left panel to start.")

# --- FOOTER ---
st.markdown("---")
st.caption("Built by Rom1009 | Powered by FastAPI, Docker & Azure Cloud")