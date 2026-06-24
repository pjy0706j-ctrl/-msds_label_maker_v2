"""공급사용 경고표지 프로그램 3종 EXE 빌드 스크립트.

각 공급사별로 독립 실행되는 EXE를 supplier_versions/<공급사폴더>/ 에 생성한다.
원본 MSDS 프로그램과 완전히 분리되어 있으며, 이 폴더만으로 빌드/배포 가능.

실행:  python build_suppliers.py
"""

import os
import sys
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FLET_DIR = os.path.join(os.path.expanduser("~"), ".flet", "client",
                        "flet-desktop-full-0.85.2", "flet")
ICON = os.path.join(os.path.dirname(HERE), "app_icon.ico")  # 원본 아이콘 재사용(읽기 전용)

# (출력 폴더, EXE 이름, 진입 스크립트)
TARGETS = [
    ("Hansung",    "Hansung_Label",    "entry_Hansung.py"),
    ("BMS",        "BMS_Label",        "entry_BMS.py"),
    ("DaehanSlag", "DaehanSlag_Label", "entry_DaehanSlag.py"),
]

SEP = ";" if os.name == "nt" else ":"


def add_data(src, dest):
    return f"{os.path.join(HERE, src)}{SEP}{dest}"


def build_one(folder, name, entry):
    dist = os.path.join(HERE, folder)
    work = os.path.join(HERE, "_build", name)
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--windowed",
        "--name", name,
        "--distpath", dist,
        "--workpath", work,
        "--specpath", os.path.join(HERE, "_build"),
        "--add-data", add_data("ghs_images", os.path.join("assets", "ghs_images")),
        "--add-data", add_data("supplier_config.json", "."),
        "--add-data", add_data("products_data.json", "."),
        "--add-data", f"{FLET_DIR}{SEP}flet_client",
        "--hidden-import", "flet",
        "--hidden-import", "flet_desktop",
    ]
    if os.path.exists(ICON):
        args += ["--icon", ICON]
    args.append(os.path.join(HERE, entry))

    print(f"\n{'='*60}\n  빌드: {name}  →  {dist}\n{'='*60}")
    subprocess.run(args, cwd=HERE, check=True)


def main():
    for folder, name, entry in TARGETS:
        build_one(folder, name, entry)
    # 중간 산출물 정리
    shutil.rmtree(os.path.join(HERE, "_build"), ignore_errors=True)
    print("\n[완료] 모든 공급사 EXE 빌드 완료")
    for folder, name, _ in TARGETS:
        print(f"   - {folder}/{name}/{name}.exe")


if __name__ == "__main__":
    main()
