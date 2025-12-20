import streamlit as st
import requests
from PIL import Image, ImageDraw
import io
import time

# ⚠️ YOUR MODAL API
API_URL = "https://zawlinnhtet958--burmese-nrc-ocr-backend-api-predict.modal.run"

# Image size limit (important for Streamlit Cloud)
MAX_IMAGE_SIZE = 1024  # px
REQUEST_TIMEOUT = 60   # seconds
RETRIES = 2

st.set_page_config(page_title="KYC API Tester", layout="wide")
st.title("Dinger KYC • API Integration Test")

col1, col2 = st.columns(2)

def call_modal_api(payload):
    headers = {
        "Content-Type": "application/octet-stream"
    }

    for attempt in range(RETRIES + 1):
        try:
            response = requests.post(
                API_URL,
                data=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            return response
        except requests.exceptions.RequestException as e:
            if attempt < RETRIES:
                time.sleep(3)  # wait before retry
            else:
                raise e

with col1:
    st.subheader("Client Side (Mobile App)")
    uploaded = st.file_uploader("Upload NRC", type=["jpg", "png", "jpeg"])

    if uploaded:
        img = Image.open(uploaded).convert("RGB")

        # 🔥 Resize image (CRITICAL for Streamlit Cloud)
        if max(img.size) > MAX_IMAGE_SIZE:
            img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE))

        st.image(img, caption="Input Image", use_column_width=True)

        if st.button("Simulate Request"):
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="JPEG", quality=85)
            payload = img_byte_arr.getvalue()

            st.write(f"Payload size: {len(payload) / 1024:.1f} KB")

            with st.spinner("Sending request to Modal API..."):
                try:
                    response = call_modal_api(payload)

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["results"] = data
                        st.success(
                            f"Success! Time: {response.elapsed.total_seconds():.2f}s"
                        )
                    else:
                        st.error(
                            f"API Error {response.status_code}: {response.text}"
                        )

                except Exception as e:
                    st.error("Connection to API failed")
                    st.exception(e)

with col2:
    st.subheader("Server Response (API Output)")

    if "results" in st.session_state:
        res = st.session_state["results"]

        # 1️⃣ Parsed fields
        fields = res.get("field_texts", {})
        st.json(fields)

        # 2️⃣ Bounding box visualization
        if uploaded and "detections" in res:
            debug_img = img.copy()
            draw = ImageDraw.Draw(debug_img)

            for det in res["detections"]:
                x1, y1, x2, y2 = det["bbox"]
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                draw.text((x1, y1), det["label"], fill="red")

            st.image(
                debug_img,
                caption="Server Vision Debug",
                use_column_width=True
            )
