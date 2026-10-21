# ภาคผนวก ค: คู่มือการใช้งาน

## 1. ตรวจสอบไฟล์ (แท็บ Validate)
1. กด Upload CSV แล้วเลือกไฟล์ (ลองใช้ `data/samples/orders_valid.csv` หรือ `orders_with_issues.csv`)
2. ดูสถานะ 🟢 PASS / 🟡 WARN / 🔴 FAIL และตัวชี้วัด Rows checked, Rows with issues, Critical failures
3. ดูกราฟ Failures by rule และตาราง Rows to review (เลขแถวนับ header เป็นแถวที่ 1)
4. กด Download failure report เพื่อส่งให้เจ้าของข้อมูลแก้ไข
5. ไฟล์ที่ไม่ใช่ Order จะแสดง Column profile and inferred rules

## 2. ดูประวัติ (แท็บ History)
ดู Pass Rate ล่าสุด ค่าเฉลี่ย ตารางประวัติ และกราฟแนวโน้ม

## 3. ดูความแม่นยำ (แท็บ Evaluation)
ดู Macro Precision / Recall / F1 และตารางรายกฎ

## 4. ปรับกฎ
แก้ไข `config/rules.yaml` (ชนิด check: `not_null`, `unique`, `parseable_date`, `numeric_min`) แล้วรีเฟรชหน้าเว็บ
