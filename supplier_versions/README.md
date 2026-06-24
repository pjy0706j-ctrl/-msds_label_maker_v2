# 공급사용 경고표지 출력 프로그램

원본 **MSDS Label Maker** 와 **완전히 분리된** 공급사 전용 경고표지 출력 프로그램입니다.
각 공급사는 **자신이 공급하는 원료의 경고표지만** 선택·출력할 수 있습니다.

> ⚠️ 원본 프로그램(`C:\-msds_label_maker` 루트)은 이 폴더와 독립적이며, 본 폴더 작업은 원본을 수정하지 않습니다.

---

## 생성되는 프로그램

| 공급사 | 폴더 | EXE | 허용 제품 |
|--------|------|-----|-----------|
| 한성 | `Hansung/` | `Hansung_Label.exe` | 석회석, 백운석 |
| BMS | `BMS/` | `BMS_Label.exe` | 장석 |
| 대한슬래그 | `DaehanSlag/` | `DaehanSlag_Label.exe` | Slag |

각 프로그램은 지정된 원료만 드롭다운에 표시되며, 다른 제품은 보이지 않습니다.

### 출력 규격
- 100 x 57 mm
- 70 x 37 mm

기능: 제품 선택 → 규격 선택 → 미리보기 → 🖨 인쇄 / 📄 PDF로 저장

---

## 폴더 구성

```
supplier_versions/
├── supplier_config.json   # 공급사 → 허용 제품 / 회사정보
├── products_data.json     # 제품 → GHS 라벨 데이터(신호어·유해문구·예방조치문구·그림문자)
├── label_specs.py         # 출력 규격(100×57, 70×37)
├── label_generator.py     # 원본 라벨 생성 로직 복사본(독립 실행)
├── supplier_app.py        # 공통 Flet 앱
├── entry_Hansung.py       # 한성 진입점
├── entry_BMS.py           # BMS 진입점
├── entry_DaehanSlag.py    # 대한슬래그 진입점
├── build_suppliers.py     # 3종 EXE 빌드 스크립트
├── ghs_images/            # GHS 그림문자
├── Hansung/  BMS/  DaehanSlag/   # 빌드 결과(EXE)
└── README.md
```

---

## 공급사 / 제품 추가 방법 (코드 수정 불필요)

### 새 공급사 추가
`supplier_config.json` 에 항목 추가 후 `entry_<공급사>.py` 1개 작성:
```json
"NewCo": {
  "display_name": "새회사",
  "products": ["제품A"],
  "company_info": "공급자: 새회사\n주소: ...\n긴급연락처: ..."
}
```
```python
# entry_NewCo.py
from supplier_app import run_app
if __name__ == "__main__":
    run_app("NewCo")
```
`build_suppliers.py` 의 `TARGETS` 에 한 줄 추가 후 빌드.

### 새 제품 추가
`products_data.json` 에 제품 항목 추가:
```json
"제품A": {
  "signal_word": "경고",
  "pictograms": ["exclamation.png"],
  "hazard_statements": "H315 ...",
  "precautionary_statements": "<예방>\nP261 ...\n<대응>\n...\n<저장>\n...\n<폐기>\n..."
}
```
사용 가능 그림문자: `corrosion / environment / exclamation / exploding_bomb / flame / flame_over_circle / gas_cylinder / health_hazard / skull` (.png)

---

## ⚠️ 중요 — GHS 데이터 검증 필수

`products_data.json` 의 신호어·유해문구·예방조치문구·그림문자는 **일반적인 예시값**입니다.
**배포 전 반드시 각 제품의 실제 MSDS와 대조하여 수정**하고,
`supplier_config.json` 의 회사 주소·긴급연락처(`[ ]` 부분)를 실제 값으로 채우세요.

---

## 빌드 방법

```bash
cd supplier_versions
python build_suppliers.py
```
→ `Hansung/`, `BMS/`, `DaehanSlag/` 폴더에 각 EXE 생성.
