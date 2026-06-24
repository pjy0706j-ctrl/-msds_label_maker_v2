"""산업안전보건표지 출력 탭.

assets(safety_signs) 폴더를 스캔하여 카테고리별 표지를 자동으로 불러오고,
선택한 표지를 원하는 규격의 PDF로 출력하는 독립 Flet 모듈.

새 PNG 파일을 safety_signs/<category>/ 폴더에 추가하면 코드 수정 없이
자동으로 목록에 반영됨.
"""

import os
import sys
import webbrowser
from dataclasses import dataclass, field

import flet as ft
import fitz  # PyMuPDF

if getattr(sys, "frozen", False):
    # PyInstaller 번들: safety_signs는 assets/ 하위에 위치 (ghs_images와 동일 규칙)
    BASE_DIR = os.path.join(sys._MEIPASS, "assets")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAFETY_SIGNS_DIR = os.path.join(BASE_DIR, "safety_signs")

# PDF 출력 파일은 항상 실행 파일이 위치한 폴더 기준으로 저장
APP_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, "frozen", False) \
    else os.path.dirname(os.path.abspath(__file__))

BORDER = ft.Border(
    top=ft.BorderSide(1, "#DEE2E6"),
    bottom=ft.BorderSide(1, "#DEE2E6"),
    left=ft.BorderSide(1, "#DEE2E6"),
    right=ft.BorderSide(1, "#DEE2E6"),
)
BG_PANEL  = "#F8F9FA"
BG_HEADER = "#E9ECEF"

CATEGORY_LABELS = {
    "prohibition": "금지표지",
    "warning": "경고표지",
    "mandatory": "지시표지",
    "emergency": "안내표지",
}

# 파일명(확장자 제외) → 한글 표지명. 매핑이 없으면 파일명을 자동 변환하여 표시(확장 시 코드 수정 불필요).
SIGN_NAME_KR = {
    "no_entry": "출입금지",
    "no_open_flame": "화기금지",
    "do_not_use": "사용금지",
    "no_entry_unless_authorized": "관계자 외 출입금지",
    "no_pedestrians": "보행금지",

    "caution_forklift": "지게차 주의",
    "caution_gears": "기어 주의",
    "caution_hand_crush": "손 끼임 주의",
    "caution_noisy_area": "소음 주의",
    "caution_risk_of_danger": "위험 주의",
    "caution_trip_harzard": "걸림 주의",
    "caution_under_repair": "수리중 주의",
    "caution_watch_your_hand": "손 주의",
    "cold_hazard": "저온 경고",
    "corrosion_warning": "부식성물질 경고",
    "electrical_harzard": "감전 위험",
    "exploding_bomb_warning": "폭발성물질 경고",
    "falling_objects": "낙하물 주의",
    "flame_over_circle_warning": "산화성물질 경고",
    "flame_warning": "발화성물질 경고",
    "health_hazard_warning": "건강유해성 경고",
    "hot_surface": "고온 경고",
    "no_unauthorized_access": "관계자 외 출입금지",
    "radiation_harzard": "방사선 위험",
    "skull_warning": "독성물질 경고",

    "wear_dust_mask": "방진마스크 착용",
    "wear_ear_protection": "보호귀 착용",
    "wear_eye_ear_head_protection": "보안경·보호귀·안전모 착용",
    "wear_eye_protection": "보안경 착용",
    "wear_face_shield": "보호안면 착용",
    "wear_foot_pretection": "안전화 착용",
    "wear_foot_protection_gloves": "안전화·안전장갑 착용",
    "wear_gas_mask": "방독마스크 착용",
    "wear_head_protection": "안전모 착용",
    "wear_protective_clothes": "보호복 착용",
    "wear_protective_clothes_hot": "방열복 착용",
    "wear_protective_gloves": "보호장갑 착용",
    "wear_safety_harness": "안전대 착용",

    "emergency_stop_switch": "비상정지 스위치",
    "eye_wash_station": "세안장치",
    "first_exit": "비상구",
    "safety_passage": "안전통로",
    "safety_shower": "비상샤워장치",
}


def humanize_filename(stem: str) -> str:
    """매핑이 없는 파일명을 보기 좋게 변환하는 fallback."""
    return stem.replace("_", " ").strip().title()


@dataclass
class SafetySign:
    """표지 1개를 표현하는 데이터 모델 (추후 복합표지·사용자 정의 표지 확장의 기반 단위)."""

    category: str
    key: str          # 파일명(확장자 제외)
    path: str         # 절대경로
    name_kr: str = field(default="")

    def __post_init__(self):
        if not self.name_kr:
            self.name_kr = SIGN_NAME_KR.get(self.key, humanize_filename(self.key))


class SafetySignLibrary:
    """safety_signs 폴더를 스캔하여 카테고리별 표지 목록을 관리.

    PNG 파일을 추가/삭제하면 reload() 또는 재실행 시 자동으로 목록에 반영된다.
    """

    def __init__(self, root_dir: str = SAFETY_SIGNS_DIR):
        self.root_dir = root_dir
        self.signs_by_category: dict[str, list[SafetySign]] = {}
        self.reload()

    def reload(self):
        self.signs_by_category = {}
        for category in CATEGORY_LABELS:
            folder = os.path.join(self.root_dir, category)
            signs = []
            if os.path.isdir(folder):
                for fname in sorted(os.listdir(folder)):
                    if fname.lower().endswith(".png"):
                        key = os.path.splitext(fname)[0]
                        signs.append(SafetySign(category=category, key=key,
                                                 path=os.path.join(folder, fname)))
            self.signs_by_category[category] = signs

    def all_signs(self) -> list[SafetySign]:
        result = []
        for signs in self.signs_by_category.values():
            result.extend(signs)
        return result

    def search(self, keyword: str) -> list[SafetySign]:
        """추후 확장 포인트: 표지 이름/카테고리 키워드 검색."""
        keyword = (keyword or "").strip()
        if not keyword:
            return self.all_signs()
        return [s for s in self.all_signs()
                if keyword in s.name_kr or keyword in s.key]


# ── 출력 규격 ────────────────────────────────────────────────
PRINT_SPECS = {
    "98.8 x 92.7 mm": {"w_mm": 98.8, "h_mm": 92.7, "mode": "grid"},
    "A5": {"w_mm": 148.0, "h_mm": 210.0, "mode": "single"},
    "A4": {"w_mm": 210.0, "h_mm": 297.0, "mode": "single"},
}
MM_TO_PT = 72 / 25.4


class SafetySignPdfBuilder:
    """선택된 표지를 지정 규격의 PDF로 출력.

    소형 규격(98.8x92.7mm)은 A4 용지에 여러 칸으로 배치하고,
    A5/A4는 표지 1개당 1페이지로 출력한다.
    추후 복합표지(여러 표지를 한 칸에 합성) 확장 시 _draw_sign_cell만 교체하면 된다.
    """

    def __init__(self, spec_key: str):
        self.spec = PRINT_SPECS.get(spec_key, PRINT_SPECS["98.8 x 92.7 mm"])

    def build(self, signs: list[SafetySign], output_path: str) -> str:
        doc = fitz.open()
        if self.spec["mode"] == "grid":
            self._build_grid(doc, signs)
        else:
            self._build_single_per_page(doc, signs)
        doc.save(output_path)
        doc.close()
        return output_path

    def _build_grid(self, doc, signs: list[SafetySign]):
        page_w, page_h = 210 * MM_TO_PT, 297 * MM_TO_PT
        label_w = self.spec["w_mm"] * MM_TO_PT
        label_h = self.spec["h_mm"] * MM_TO_PT
        margin = 10 * MM_TO_PT
        gap = 4 * MM_TO_PT

        cols = max(1, int((page_w - 2 * margin + gap) // (label_w + gap)))
        rows = max(1, int((page_h - 2 * margin + gap) // (label_h + gap)))
        per_page = cols * rows

        for start in range(0, len(signs), per_page):
            page = doc.new_page(width=page_w, height=page_h)
            chunk = signs[start:start + per_page]
            for idx, sign in enumerate(chunk):
                col = idx % cols
                row = idx // cols
                x0 = margin + col * (label_w + gap)
                y0 = margin + row * (label_h + gap)
                self._draw_sign_cell(page, sign, x0, y0, label_w, label_h, caption_size=9)

    def _build_single_per_page(self, doc, signs: list[SafetySign]):
        page_w = self.spec["w_mm"] * MM_TO_PT
        page_h = self.spec["h_mm"] * MM_TO_PT
        for sign in signs:
            page = doc.new_page(width=page_w, height=page_h)
            margin = 15 * MM_TO_PT
            self._draw_sign_cell(page, sign, margin, margin,
                                  page_w - 2 * margin, page_h - 2 * margin,
                                  caption_size=18)

    def _draw_sign_cell(self, page, sign: SafetySign, x0, y0, w, h, caption_size):
        caption_h = caption_size * 1.8
        img_rect = fitz.Rect(x0, y0, x0 + w, y0 + h - caption_h)

        pix = fitz.Pixmap(sign.path)
        img_w, img_h = pix.width, pix.height
        scale = min(img_rect.width / img_w, img_rect.height / img_h)
        draw_w, draw_h = img_w * scale, img_h * scale
        cx = img_rect.x0 + (img_rect.width - draw_w) / 2
        cy = img_rect.y0 + (img_rect.height - draw_h) / 2
        page.insert_image(fitz.Rect(cx, cy, cx + draw_w, cy + draw_h), filename=sign.path)

        caption_rect = fitz.Rect(x0, y0 + h - caption_h, x0 + w, y0 + h)
        page.insert_textbox(caption_rect, sign.name_kr, fontsize=caption_size,
                             fontname="helv", align=1)
        page.draw_rect(fitz.Rect(x0, y0, x0 + w, y0 + h), color=(0.6, 0.6, 0.6), width=0.5)


# ── Flet UI ──────────────────────────────────────────────────
def build_safety_sign_tab(page: ft.Page) -> ft.Row:
    """'산업안전보건표지 출력' 탭 콘텐츠를 생성. main_flet.py 의 Tabs 에 연결해서 사용."""

    library = SafetySignLibrary()
    selected: dict[str, bool] = {}

    preview_grid = ft.GridView(
        expand=True, runs_count=3, max_extent=160,
        child_aspect_ratio=0.85, spacing=8, run_spacing=8,
    )
    spec_radio = ft.RadioGroup(
        value="98.8 x 92.7 mm",
        content=ft.Column([
            ft.Radio(value="98.8 x 92.7 mm", label="98.8 x 92.7 mm"),
            ft.Radio(value="A5", label="A5"),
            ft.Radio(value="A4", label="A4"),
        ]),
    )
    status_text = ft.Text("", size=12, color="#6C757D")

    def refresh_preview():
        preview_grid.controls.clear()
        for sign in library.all_signs():
            if selected.get(sign.path):
                preview_grid.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Image(src=sign.path, width=90, height=90,
                                     fit=ft.ImageFit.CONTAIN),
                            ft.Text(sign.name_kr, size=11, text_align=ft.TextAlign.CENTER),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        padding=8, border=BORDER, border_radius=6, bgcolor="white",
                    )
                )
        page.update()

    def on_toggle(sign: SafetySign, value: bool):
        selected[sign.path] = value
        refresh_preview()

    def build_category_block(category: str) -> ft.Column:
        signs = library.signs_by_category.get(category, [])
        checkboxes = [
            ft.Checkbox(
                label=sign.name_kr, value=False,
                on_change=lambda e, s=sign: on_toggle(s, e.control.value),
            )
            for sign in signs
        ]
        return ft.Column([
            ft.Text(f"[{CATEGORY_LABELS[category]}]", size=13,
                    weight=ft.FontWeight.BOLD, color="#495057"),
            *checkboxes,
            ft.Divider(color="#DEE2E6"),
        ], spacing=2)

    selection_column = ft.Column(
        [build_category_block(cat) for cat in CATEGORY_LABELS],
        scroll=ft.ScrollMode.AUTO, spacing=6, expand=True,
    )

    def on_generate_pdf(e):
        chosen = [s for s in library.all_signs() if selected.get(s.path)]
        if not chosen:
            status_text.value = "⚠ 출력할 표지를 1개 이상 선택하세요."
            page.update()
            return
        out_path = os.path.join(APP_DIR, "safety_signs_output.pdf")
        SafetySignPdfBuilder(spec_radio.value).build(chosen, out_path)
        status_text.value = f"✅ PDF 생성 완료: {out_path}"
        page.update()
        webbrowser.open(out_path)

    def panel(title, content, width=None, expand=False):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color="#495057"),
                    bgcolor=BG_HEADER,
                    padding=ft.padding.Padding(left=12, right=8, top=6, bottom=6),
                    border_radius=ft.border_radius.BorderRadius(
                        top_left=6, top_right=6, bottom_left=0, bottom_right=0),
                ),
                ft.Container(content=content, padding=10, expand=True),
            ], spacing=0, expand=True),
            border=BORDER, border_radius=6, bgcolor=BG_PANEL,
            width=width, expand=expand,
        )

    selection_panel = panel("🚧 표지 선택", selection_column, width=260)
    preview_panel = panel("🖼 미리보기", preview_grid, expand=True)
    spec_panel = panel(
        "📐 출력 규격",
        ft.Column([
            spec_radio,
            ft.Container(height=12),
            ft.ElevatedButton("📄 PDF 생성", on_click=on_generate_pdf,
                              style=ft.ButtonStyle(bgcolor="#343A40", color="white")),
            ft.Container(height=8),
            status_text,
        ]),
        width=260,
    )

    return ft.Row(
        controls=[selection_panel, preview_panel, spec_panel],
        spacing=10, expand=True, vertical_alignment=ft.CrossAxisAlignment.START,
    )
