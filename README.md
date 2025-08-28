# Explore the Rapid Prototype in AI Project

โปรเจกต์นี้พัฒนาด้วย **Streamlit** เพื่อตอบโจทย์การสร้าง Rapid Prototype ด้าน AI/Computer Vision โดยมีฟีเจอร์ครบตามที่อาจารย์กำหนด

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
- Layout สองฝั่ง:  
  - **ซ้าย:** เลือกแหล่งภาพและควบคุมกล้อง  
  - **ขวา:** ปรับแต่งการประมวลผล + ดูผลลัพธ์ + Histogram

---

## Installation

1. Clone repo นี้
   ```bash
   git clone <your_repo_url>
   cd <your_repo_name>
2. สร้าง virtual environment
    python3 -m venv venv
    source venv/bin/activate   # macOS / Linux
    venv\Scripts\activate      # Windows
3. ติดตั้ง dependency
    pip install -r requirements.txt
4. รันแอป
    streamlit run app.py

![Input Panel](docs/1.jpeg)
![Webcam Running](docs/2.jpeg)
![Gray CLAHE](docs/3.jpeg)
![Canny Edge](docs/4.jpeg)
![Histogram](docs/5.jpeg)
