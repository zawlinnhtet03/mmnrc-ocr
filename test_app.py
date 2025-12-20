import streamlit as st
import requests
from PIL import Image, ImageDraw
import io

# ⚠️ REPLACE THIS WITH YOUR ACTUAL MODAL URL
API_URL = "https://zawlinnhtet958--burmese-nrc-ocr-backend-api-predict.modal.run"

st.set_page_config(page_title="KYC API Tester", layout="wide")
st.title("Dinger KYC • API Integration Test")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Client Side")
    uploaded = st.file_uploader("Upload NRC", type=["jpg", "png", "jpeg"])
    
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption="Input Image", use_column_width=True)
        
        if st.button("Simulate KYC Request"):
            # Prepare the payload
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            payload = img_byte_arr.getvalue()
            
            with st.spinner("Sending request to API..."):
                try:
                    # THIS IS THE KEY LINE FOR YOUR KYE APP
                    response = requests.post(API_URL, data=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state['results'] = data
                        st.success(f"Success! Time: {response.elapsed.total_seconds():.2f}s")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

with col2:
    st.subheader("Server Response (API Output)")
    
    if 'results' in st.session_state:
        res = st.session_state['results']
        
        # 1. Parse Fields
        fields = res.get("field_texts", {})
        st.json(fields)  # Show raw JSON for developer inspection
        
        # 2. Visualize Bounding Boxes (Optional check)
        if uploaded and "detections" in res:
            draw = ImageDraw.Draw(img)
            for det in res["detections"]:
                x1, y1, x2, y2 = det["bbox"]
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                draw.text((x1, y1), det["label"], fill="red")
            st.image(img, caption="Server Vision Debug", use_column_width=True)