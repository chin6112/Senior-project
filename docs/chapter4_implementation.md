# บทที่ 4
# การพัฒนาระบบ (Implementation)

ผลการประเมินและตัวเลขการทดสอบอยู่ใน [10_ch4_results.md](./10_ch4_results.md) และบทที่ 5

## 4.1 โครงสร้างโปรเจกต์

| ส่วน | ไฟล์ | หน้าที่ |
|------|------|---------|
| UI | `app.py`, `streamlit_app.py` | หน้าจอ 3 แท็บ (Validate / History / Evaluation) และ entry point สำหรับ Cloud |
| Service | `dq/service.py` | อ่าน CSV → คำนวณ hash → ตรวจสอบ → ตัดสินผล → บันทึก |
| Engine | `dq/engine.py` | ฟังก์ชันตรวจสอบ (`CHECKS`), `run_checks`, `infer_config` |
| Policy | `dq/policy.py` | ตัดสิน PASS / WARN / FAIL |
| Store | `dq/store.py` | SQLite: `runs`, `rule_results` |
| Config | `config/rules.yaml` | กฎและเกณฑ์ |
| Evaluation | `evaluate.py`, `evaluate_dual.py` | คำนวณ Precision / Recall / F1 |

## 4.2 กลไกการตรวจสอบ
- กฎแต่ละข้อระบุ `column`, `check`, `severity` ใน YAML และถูกส่งไปยังฟังก์ชันใน `CHECKS`
- ชนิดการตรวจ: `not_null`, `unique`, `parseable_date`, `numeric_min`, `optional_date`, `optional_numeric` และ `duplicate_row`
- ผลลัพธ์คือ DataFrame ของความล้มเหลว (`csv_row`, `rule`, `column`, `severity`) โดยเลขแถวนับ header เป็นแถวที่ 1

## 4.3 การสร้างกฎอัตโนมัติสำหรับ CSV ทั่วไป
เมื่อไฟล์ไม่มีคอลัมน์ `order_id`, `order_date`, `amount` ครบ ระบบเรียก `infer_config` เพื่อ
- ประเมินชนิดคอลัมน์ (numeric / date / text / empty) จากตัวอย่าง 1,000 ค่าแรก
- เพิ่มกฎ missing เมื่อค่าว่างน้อยกว่าหรือเท่ากับ 5% ของแถว
- เพิ่มกฎ duplicate สำหรับคอลัมน์ชื่อ `id` หรือลงท้าย `_id` ที่ค่าไม่ซ้ำอย่างน้อย 95%
- เพิ่มกฎ not numeric / invalid date สำหรับคอลัมน์ที่ชนิดสอดคล้อง
- เพิ่มกฎ duplicate_row เสมอ และสร้างตารางโปรไฟล์คอลัมน์แสดงบนหน้าจอ

## 4.4 การตัดสินผล (Policy)
`PolicyEvaluator` เทียบจำนวนความล้มเหลวกับ `thresholds` ใน YAML (`max_critical_failures`, `max_warning_failures`) ได้ผล PASS / WARN / FAIL

## 4.5 การจัดเก็บประวัติ
`save_run` บันทึกสรุปการรันลง `runs` และจำนวนความล้มเหลวต่อกฎลง `rule_results` พร้อม SHA-256 ของไฟล์ และมี migration เพิ่มคอลัมน์ให้ฐานข้อมูลเก่าอัตโนมัติ

## 4.6 หน้าจอ
- **Validate:** สถานะ ตัวชี้วัด กราฟตามกฎ ตารางแถวที่มีปัญหา (แสดงสูงสุด 2,000 แถว) และปุ่มดาวน์โหลดรายงาน
- **History:** ตารางประวัติ และกราฟแนวโน้ม Pass Rate
- **Evaluation:** Macro Precision / Recall / F1 และตารางรายกฎ
