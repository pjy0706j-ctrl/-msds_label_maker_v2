import os, sys, json, traceback, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msds_parser import (extract_text_from_pdf_path, extract_product_name,
    extract_product_name_retry, extract_supplier_info, extract_signal_word,
    extract_hazard_statements, extract_precautionary_statements,
    select_precautionary_statements, get_h_codes, match_pictograms,
    detect_company, detect_company_from_filename, infer_signal_word_from_h_codes,
    is_non_hazardous)
from config import label_specs

def test_one(pdf_path):
    file_name = os.path.basename(pdf_path)
    r = {"file": file_name, "status": "OK", "errors": [], "warnings": [],
         "company": "", "product": "", "signal": "", "h_codes": [],
         "prec_sections": [], "supplier": "", "pictograms": []}
    try:
        text = extract_text_from_pdf_path(pdf_path)
        r["company"] = detect_company_from_filename(file_name) or detect_company(text)
        r["product"] = extract_product_name(text) or extract_product_name_retry(text)
        if not r["product"]: r["warnings"].append("제품명 추출 실패")
        r["signal"] = extract_signal_word(text)
        hazard = extract_hazard_statements(text)
        r["h_codes"] = get_h_codes(hazard)
        # 신호어가 없고 H코드가 있으면 H코드로 추론 (추론 성공은 경고 없음)
        if not r["signal"] and r["h_codes"]:
            r["signal"] = infer_signal_word_from_h_codes(r["h_codes"])
        non_hazardous = is_non_hazardous(text)
        if not r["signal"] and not non_hazardous: r["warnings"].append("신호어 추출 실패")
        if not r["h_codes"] and not non_hazardous: r["warnings"].append("H코드 추출 실패")
        prec = extract_precautionary_statements(text)
        r["prec_sections"] = [s for s in ["예방","대응","저장","폐기"] if f"<{s}>" in prec]
        if not r["prec_sections"] and not non_hazardous: r["warnings"].append("P코드 추출 실패")
        supplier = extract_supplier_info(text)
        r["supplier"] = (supplier[:80].replace("\n"," ")) if supplier else ""
        if not supplier: r["warnings"].append("공급자정보 추출 실패")
        r["pictograms"] = match_pictograms(r["h_codes"])
        if r["warnings"]: r["status"] = "WARN"
    except Exception as ex:
        r["status"] = "ERROR"
        r["errors"] += [str(ex), traceback.format_exc()]
    return r

def run_batch(folder):
    folder = Path(folder)
    seen = set()
    pdfs = []
    for p in sorted(folder.glob("*.pdf")) + sorted(folder.glob("*.PDF")):
        if p.name.lower() not in seen:
            seen.add(p.name.lower()); pdfs.append(p)
    if not pdfs:
        print(f"[!] PDF 없음: {folder}"); return
    print(f"\n{'='*60}\n  총 {len(pdfs)}개 파일\n{'='*60}\n")
    summary = {"ok": 0, "warn": 0, "error": 0}
    results = []
    for pdf in pdfs:
        r = test_one(str(pdf)); results.append(r)
        icon = {"OK":"[OK]","WARN":"[WARN]","ERROR":"[ERROR]"}[r["status"]]
        print(f"{icon} {r['file']}")
        print(f"   회사:{r['company']}  제품:{r['product'][:35]}")
        print(f"   신호어:{r['signal'] or '없음'}  H코드:{r['h_codes']}")
        print(f"   공급자:{r['supplier'][:50] or '없음'}")
        for w in r["warnings"]: print(f"   [W] {w}")
        for e in r["errors"]: print(f"   [E] {e[:150]}")
        print(); summary[r["status"].lower()] += 1
    print(f"{'='*60}")
    print(f"OK:{summary['ok']} WARN:{summary['warn']} ERROR:{summary['error']}")
    json.dump(results, open("test_report.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("리포트: test_report.json")

if __name__ == "__main__":
    run_batch(sys.argv[1] if len(sys.argv)>1 else ".")
