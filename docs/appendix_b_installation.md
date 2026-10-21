# ภาคผนวก ข: การติดตั้งและใช้งานระบบ

## ความต้องการเบื้องต้น
- Python 3.10 ขึ้นไป
- Git

## ขั้นตอนติดตั้ง (Windows)
```powershell
git clone https://github.com/chin6112/Senior-project.git
cd Senior-project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## คำสั่งที่ใช้บ่อย
```powershell
streamlit run app.py          # เปิดเว็บที่ http://localhost:8501
pytest tests/ -v              # รันการทดสอบ
python evaluate.py            # ประเมินชุดมาตรฐาน
python evaluate_dual.py       # ประเมินทั้งชุดมาตรฐานและ Hard
```

## ไฟล์สำคัญ
- `config/rules.yaml` — กฎและเกณฑ์
- `dq_history.db` — ฐานข้อมูลประวัติ (สร้างอัตโนมัติ)
- `data/samples/` — ไฟล์ตัวอย่าง

## Deploy
Streamlit Community Cloud: ตั้งค่า main file เป็น `streamlit_app.py`
