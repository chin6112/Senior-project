# บทที่ 5
# การทดสอบและสรุปผล (Testing)

## 5.1 การทดสอบหน่วย (Unit Tests)
รันด้วย `pytest tests/ -v` ผ่านทั้งหมด **19 tests**

| ไฟล์ | จำนวน | ขอบเขต |
|------|------:|--------|
| `tests/test_rules.py` | 7 | กฎ missing_id, duplicate_id, invalid_date, invalid_amount |
| `tests/test_policy.py` | 6 | เกณฑ์ PASS / WARN / FAIL |
| `tests/test_generic.py` | 6 | กฎอัตโนมัติสำหรับ CSV ทั่วไปและ fallback ใน service |

## 5.2 การประเมินความแม่นยำ
| ชุดข้อมูล | จำนวนแถว | Precision | Recall | F1 |
|-----------|---------:|----------:|-------:|---:|
| Standard (`orders_labeled.csv`) | 200 | 1.000 | 1.000 | 1.000 |
| Hard (`orders_hard.csv`) | 45 | 0.500 | 1.000 | 0.500 |

รายละเอียดและข้อควรระวังในการตีความอยู่ใน [10_ch4_results.md](./10_ch4_results.md)

## 5.3 การทดสอบอัตโนมัติ (CI)
GitHub Actions รัน pytest และ `evaluate.py` ทุกครั้งที่ push / pull request

## 5.4 การทดสอบกับผู้ใช้
ยังไม่ได้ดำเนินการ ให้บันทึกผลในตารางหัวข้อ 4.4 ของ [10_ch4_results.md](./10_ch4_results.md)
