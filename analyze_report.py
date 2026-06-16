import json, collections, sys
data = json.load(open("test_report.json", encoding="utf-8"))
total  = len(data)
oks    = [d for d in data if d["status"] == "OK"]
warns  = [d for d in data if d["status"] == "WARN"]
errors = [d for d in data if d["status"] == "ERROR"]

warn_types = collections.Counter()
for d in warns:
    for w in d["warnings"]:
        warn_types[w] += 1

# WARN 중 어떤 조합이 많은지
combo = collections.Counter()
for d in warns:
    combo[tuple(sorted(d["warnings"]))] += 1

err_types = collections.Counter()
for d in errors:
    msg = d["errors"][0][:100] if d["errors"] else "unknown"
    err_types[msg] += 1

print(f"=== 전체 {total}개 ===")
print(f"OK   : {len(oks)}")
print(f"WARN : {len(warns)}")
print(f"ERROR: {len(errors)}")
print()

print("--- WARN 유형별 건수 (중복 집계) ---")
for k, v in warn_types.most_common():
    print(f"  {v:3d}건  {k}")
print()

print("--- 복합 WARN 패턴 (상위 10) ---")
for pat, cnt in combo.most_common(10):
    print(f"  {cnt:3d}건  {' + '.join(pat)}")
print()

print("--- WARN 파일 목록 ---")
for d in warns:
    print(f"  [{', '.join(d['warnings'])}]  {d['file']}")
print()

if errors:
    print("--- ERROR 파일 및 원인 ---")
    for d in errors:
        msg = d["errors"][0][:120] if d["errors"] else "unknown"
        print(f"  {d['file']}")
        print(f"    원인: {msg}")
