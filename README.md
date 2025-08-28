# Explore the Rapid Prototype in AI Project

โปรเจกต์นี้พัฒนาด้วย **Streamlit** เพื่อตอบโจทย์การสร้าง Rapid Prototype ด้าน AI/Computer Vision 

---

## Features
- เปิด/ปิดกล้องผ่านเบราว์เซอร์ (WebRTC) พร้อมปุ่ม **Capture / Re-capture / Reset**
- รองรับการใช้งานภาพจาก **Webcam / Upload / URL / Sample image**
- Image Processing อย่างง่าย:
  - Grayscale (Plain + CLAHE Enhancement)
  - Gaussian Blur
  - Canny Edge Detection
  - Brightness/Contrast Adjustment
- ปรับ **Parameter** ได้ผ่าน GUI เช่น kernel size, threshold, brightness/contrast
- แสดงผล **Before → After** เทียบกันแบบ side-by-side
- แสดง **Histogram** ของภาพที่ประมวลผลแล้วแบบอัตโนมัติ

---

## Installation

1. Clone repo นี้
   ```bash
   git clone https://github.com/xooooiz7/streamlit-image-lab.git
   cd streamlit-image-lab
2. สร้าง virtual environment
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # macOS / Linux
    venv\Scripts\activate      # Windows
3. ติดตั้ง dependency
    ```bash
    pip install -r requirements.txt
4. รันแอป
    ```bash
    streamlit run app.py


### 1. Input Panel
![Input Panel](docs/1.jpeg)  
**Input** สำหรับเลือก Source ของรูปภาพ (Webcam / Upload / URL / Sample)  
พร้อมปุ่มควบคุมกล้อง เช่น เปิด–ปิด, Reset stream, Clear capture

---

### 2. Webcam Running
![Webcam Running](docs/2.jpeg)  
ตัวอย่างการเปิด **Webcam** และแสดงผลภาพสดจากกล้องในแอป พร้อมปุ่ม Capture / Re-capture เพื่อเก็บภาพใช้งานต่อ

---

### 3. Gray CLAHE
![Gray CLAHE](docs/3.jpeg)  
ตัวอย่าง **Image Processing** แบบ Grayscale พร้อมใช้เทคนิค **CLAHE** เพื่อเพิ่ม contrast ให้เห็นรายละเอียดชัดเจน  
ภาพแสดง Before (Gray base) เทียบกับ After (CLAHE Enhanced)

---

### 4. Canny Edge Detection
![Canny Edge](docs/4.jpeg)  
ตัวอย่างการใช้ **Canny Edge Detection** ตรวจจับเส้นขอบของวัตถุ  
ด้านซ้ายเป็นภาพต้นฉบับ, ด้านขวาเป็นผลลัพธ์เส้นขอบหลังประมวลผล

---

### 5. Histogram
![Histogram](docs/5.jpeg)  
ตัวอย่าง **Histogram** ของภาพที่ประมวลผลแล้ว  
แสดงการกระจายของค่า pixel intensity เพื่อใช้วิเคราะห์คุณสมบัติของรูป
