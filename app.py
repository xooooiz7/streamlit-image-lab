# app.py
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from urllib.request import urlopen
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, VideoTransformerBase

st.set_page_config(page_title="AI Rapid Prototype", layout="centered")
st.title("Explore the Rapid Prototype in AI Project (WebRTC, Captured-First)")

st.markdown("""
**Features**
- เปิด/ปิดกล้อง (default ปิด) + Capture / Re-capture (ถ่ายใหม่ทันที) + Clear + Reset stream
- เลือกแหล่งประมวลผล: Captured / Live / Sample (ควบคุมชัด ไม่เผลอไปใช้ live)
- Upload / URL
- Image Processing: Gray (+CLAHE), Blur, Canny Edge, Brightness/Contrast
- Spinner ตอนประมวลผล + Before/After + Histogram
""")

# ---------------- Helpers ----------------
def load_sample_rgb():
    img = cv2.imread("sample.jpg")
    if img is None:
        # gradient sample 640x360
        h, w = 360, 640
        g1 = np.tile(np.linspace(0, 255, w, dtype=np.uint8), (h, 1))
        g2 = np.tile(np.linspace(255, 0, w, dtype=np.uint8), (h, 1))
        img = np.dstack([g1, g2, ((g1//2 + g2//2))]).astype(np.uint8)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def to_rgb(bgr):
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

# ---------------- UI: Source ----------------
option = st.radio("เลือก Source ของรูปภาพ:", ["Webcam", "Upload", "URL"])
frame_rgb_preview = None    # สำหรับโชว์
frame_rgb_for_processing = None  # สำหรับ pipeline
processed = None

# ---------------- Webcam via WebRTC ----------------
if option == "Webcam":
    # init states
    if "camera_on" not in st.session_state:
        st.session_state.camera_on = False
    if "captured" not in st.session_state:
        st.session_state.captured = None
    if "webrtc_key" not in st.session_state:
        st.session_state.webrtc_key = "webrtc-0"

    class FrameGrabber(VideoTransformerBase):
        """ดึงเฟรมล่าสุดจากเบราว์เซอร์ผ่าน WebRTC (ลดโหลดก่อนเก็บ)"""
        def __init__(self):
            self.latest_bgr = None

        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            # ลดขนาดกัน CPU spike
            h, w = img.shape[:2]
            if w > 960:
                scale = 960 / w
                img = cv2.resize(img, (int(w*scale), int(h*scale)))
            self.latest_bgr = img
            return img  # pass-through preview

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("เปิดกล้อง"):
        st.session_state.camera_on = True
        st.session_state.captured = None
        st.rerun()
    if c2.button("ปิดกล้อง"):
        st.session_state.camera_on = False
        st.session_state.captured = None
        st.rerun()
    if c3.button("Reset stream"):
        st.session_state.webrtc_key = f"webrtc-{time.time()}"
        st.rerun()
    if c4.button("Clear capture"):
        st.session_state.captured = None
        st.rerun()

    live_rgb = None
    if st.session_state.camera_on:
        rtc_config = RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )
        constraints = {
            "video": {"width": {"ideal": 640}, "height": {"ideal": 480}, "frameRate": {"ideal": 24}},
            "audio": False
        }
        ctx = webrtc_streamer(
            key=st.session_state.webrtc_key,
            mode=WebRtcMode.SENDRECV,
            video_transformer_factory=FrameGrabber,
            media_stream_constraints=constraints,
            rtc_configuration=rtc_config,
            async_processing=True,
            video_html_attrs={"autoPlay": True, "muted": True, "playsinline": True},
        )

        cap1, cap2 = st.columns(2)
        if cap1.button("Capture") and ctx and ctx.video_transformer and ctx.video_transformer.latest_bgr is not None:
            st.session_state.captured = ctx.video_transformer.latest_bgr.copy()
            st.rerun()
        if cap2.button("Re-capture") and ctx and ctx.video_transformer and ctx.video_transformer.latest_bgr is not None:
            # ถ่ายใหม่ทันที (แทนการตั้ง None)
            st.session_state.captured = ctx.video_transformer.latest_bgr.copy()
            st.rerun()

        if ctx and ctx.state.playing and ctx.video_transformer and ctx.video_transformer.latest_bgr is not None:
            live_rgb = to_rgb(ctx.video_transformer.latest_bgr)

        # Preview: โชว์ Captured ถ้ามี ไม่งั้นโชว์ Live ถ้ามี
        if st.session_state.captured is not None:
            frame_rgb_preview = to_rgb(st.session_state.captured)
            st.image(frame_rgb_preview, caption="Webcam (Captured Preview)", channels="RGB")
        elif live_rgb is not None:
            frame_rgb_preview = live_rgb
            st.image(frame_rgb_preview, caption="Live Preview (Webcam)", channels="RGB")
        else:
            st.info("กำลังรอสัญญาณกล้อง...")

    else:
        st.info("🔒 กล้องปิดอยู่ (กด 'เปิดกล้อง' เพื่อเริ่มใช้งาน)")
        frame_rgb_preview = load_sample_rgb()
        st.image(frame_rgb_preview, caption="Sample Image (กล้องปิด)", channels="RGB")

    # --- เลือกแหล่ง “สำหรับประมวลผล” แบบชัดเจน ---
    choices = ["Captured", "Live", "Sample"]
    default_idx = 0 if st.session_state.captured is not None else (1 if live_rgb is not None else 2)
    src_choice = st.radio("ใช้ภาพจาก:", choices, index=default_idx, horizontal=True)

    if src_choice == "Captured":
        if st.session_state.captured is None:
            st.warning("ยังไม่มีภาพ Captured — กด  Capture หรือ Re-capture ก่อน")
        else:
            frame_rgb_for_processing = to_rgb(st.session_state.captured)
    elif src_choice == "Live":
        if live_rgb is None:
            st.warning("ยังไม่มีสัญญาณ Live — เปิดกล้อง/รอสัญญาณก่อน หรือเลือก Sample")
        else:
            frame_rgb_for_processing = live_rgb
    else:  # Sample
        frame_rgb_for_processing = load_sample_rgb()

# ---------------- Upload ----------------
elif option == "Upload":
    uploaded = st.file_uploader("อัปโหลดไฟล์รูป", type=["jpg", "jpeg", "png"])
    if uploaded:
        data = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        bgr = cv2.imdecode(data, 1)
        frame_rgb_preview = to_rgb(bgr)
        st.image(frame_rgb_preview, caption="อัปโหลดสำเร็จ", channels="RGB")
        frame_rgb_for_processing = frame_rgb_preview

# ---------------- URL ----------------
elif option == "URL":
    url = st.text_input("ใส่ URL ของรูปภาพ:")
    if url:
        try:
            resp = urlopen(url)
            data = np.asarray(bytearray(resp.read()), dtype=np.uint8)
            bgr = cv2.imdecode(data, 1)
            frame_rgb_preview = to_rgb(bgr)
            st.image(frame_rgb_preview, caption="โหลดจาก URL สำเร็จ", channels="RGB")
            frame_rgb_for_processing = frame_rgb_preview
        except Exception as e:
            st.error(f"โหลดรูปจาก URL ไม่ได้: {e}")

# ---------------- Image Processing ----------------
if frame_rgb_for_processing is not None:
    st.subheader("Image Processing")

    proc = st.selectbox("เลือกวิธีการประมวลผล", ["Gray", "Blur", "Canny Edge", "Brightness/Contrast"])
    strength = st.slider("Parameter", 1, 10, 3)

    with st.spinner(" กำลังประมวลผล..."):
        time.sleep(0.4)

        if proc == "Gray":
            mode = st.radio("โหมด Gray:", ["Plain", "Enhance (CLAHE)"], horizontal=True, index=1)
            gray = cv2.cvtColor(frame_rgb_for_processing, cv2.COLOR_RGB2GRAY)
            if mode == "Enhance (CLAHE)":
                clip = st.slider("CLAHE Clip Limit", 1.0, 6.0, 3.0, 0.1)
                tiles = st.slider("CLAHE TileGridSize", 4, 16, 8, 2)  # ต้องเป็นเลขคู่ๆ จะได้หารลงตัว
                clahe = cv2.createCLAHE(clipLimit=float(clip), tileGridSize=(int(tiles), int(tiles)))
                processed = clahe.apply(gray)
            else:
                processed = gray

            # Before/After
            cL, cR = st.columns(2)
            cL.image(gray, caption="Before (Gray base)", channels="GRAY")
            cR.image(processed, caption="After", channels="GRAY")

        elif proc == "Blur":
            k = strength * 2 + 1
            processed = cv2.GaussianBlur(frame_rgb_for_processing, (k, k), 0)
            cL, cR = st.columns(2)
            cL.image(frame_rgb_for_processing, caption="Before", channels="RGB")
            cR.image(processed, caption=f"After (Gaussian k={k})", channels="RGB")

        elif proc == "Canny Edge":
            gray = cv2.cvtColor(frame_rgb_for_processing, cv2.COLOR_RGB2GRAY)
            t1, t2 = 30 * strength, 90 * strength
            processed = cv2.Canny(gray, t1, t2)
            cL, cR = st.columns(2)
            cL.image(frame_rgb_for_processing, caption="Before", channels="RGB")
            cR.image(processed, caption=f"After (Canny {t1},{t2})", channels="GRAY")

        elif proc == "Brightness/Contrast":
            b = st.slider("Brightness (β)", -100, 100, 0)
            a = st.slider("Contrast (α)", 0.5, 3.0, 1.0)
            processed = cv2.convertScaleAbs(frame_rgb_for_processing, alpha=a, beta=b)
            cL, cR = st.columns(2)
            cL.image(frame_rgb_for_processing, caption="Before", channels="RGB")
            cR.image(processed, caption=f"After (α={a}, β={b})", channels="RGB")

    # ---------------- Histogram ----------------
    st.subheader("Histogram ของภาพที่ประมวลผลแล้ว")
    fig, ax = plt.subplots()
    if processed is not None and processed.ndim == 2:
        ax.hist(processed.ravel(), bins=256, range=[0, 256])
    elif processed is not None:
        for i, name in enumerate(["R", "G", "B"]):
            ax.hist(processed[:, :, i].ravel(), bins=256, range=[0, 256], alpha=0.5, label=name)
        ax.legend(loc="upper right")
    st.pyplot(fig)
else:
    st.caption("เลือกแหล่งรูป/กล้อง แล้วกำหนด “ใช้ภาพจาก” ให้ชัดเจนก่อนเริ่มประมวลผล")
