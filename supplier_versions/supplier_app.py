"""공급사용 경고표지 출력 앱 (공통 코드).

원본 MSDS Label Maker의 경고표지 출력 로직(label_generator)을 그대로 재사용하되,
공급사별로 지정된 원료만 선택·출력할 수 있도록 제한한 독립 실행 버전.

- supplier_config.json : 공급사 → 허용 제품 목록 / 회사정보
- products_data.json   : 제품 → GHS 라벨 데이터 (신호어·유해문구·예방조치문구·그림문자)

새 공급사·제품은 위 두 JSON만 수정하면 코드 변경 없이 확장된다.
각 공급사 EXE는 entry_<공급사>.py 에서 run_app("<공급사ID>") 를 호출해 만든다.
"""

import os
import sys
import json
import webbrowser

import flet as ft

from label_generator import make_pictogram_html, make_label_html
from label_specs import label_specs


def _resource_path(filename: str) -> str:
    """번들(EXE) 실행 시와 소스 실행 시 모두에서 데이터 파일 경로를 찾는다."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def _output_dir() -> str:
    """인쇄/PDF 결과를 저장할 폴더 (EXE가 있는 폴더 / 소스 폴더)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.dirname(os.path.abspath(__file__))


def _load_json(filename: str) -> dict:
    with open(_resource_path(filename), encoding="utf-8") as f:
        return json.load(f)


# ── 색상/테두리 ──────────────────────────────────────────────
BG_PANEL  = "#F8F9FA"
BG_HEADER = "#E9ECEF"
ACCENT    = "#2196F3"
BORDER = ft.Border(
    top=ft.BorderSide(1, "#DEE2E6"), bottom=ft.BorderSide(1, "#DEE2E6"),
    left=ft.BorderSide(1, "#DEE2E6"), right=ft.BorderSide(1, "#DEE2E6"),
)


def run_app(supplier_id: str):
    """공급사 전용 앱 실행. supplier_id 는 supplier_config.json 의 키."""

    suppliers = _load_json("supplier_config.json")
    products_data = _load_json("products_data.json")

    if supplier_id not in suppliers:
        raise ValueError(f"supplier_config.json 에 '{supplier_id}' 공급사가 없습니다.")

    sup = suppliers[supplier_id]
    display_name = sup.get("display_name", supplier_id)
    company_info = sup.get("company_info", "")
    allowed_products = [p for p in sup.get("products", []) if p in products_data]

    def font_settings_for(spec: dict) -> dict:
        return {
            "product_font":    spec["product_font"],
            "signal_font":     spec["signal_font"],
            "title_font":      spec["title_font"],
            "hazard_font":     spec["text_font"],
            "precaution_font": spec["small_font"],
            "supplier_font":   spec["supplier_font"],
            "msds_font":       4.0,
            "pictogram_scale": 1.0,
        }

    def main(page: ft.Page):
        page.title = f"{display_name} 경고표지 출력"
        page.window.width = 1100
        page.window.height = 820
        page.bgcolor = "#F1F3F5"
        page.padding = 12

        product_dd = ft.Dropdown(
            label="제품 선택",
            value=allowed_products[0] if allowed_products else None,
            options=[ft.dropdown.Option(p) for p in allowed_products],
            width=260,
        )
        spec_radio = ft.RadioGroup(
            value=list(label_specs.keys())[0],
            content=ft.Row([ft.Radio(value=k, label=k) for k in label_specs]),
        )
        preview_area = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        status_bar = ft.Text("제품과 규격을 선택한 뒤 미리보기를 확인하세요.",
                             size=12, color="#495057")

        def current_product():
            return products_data.get(product_dd.value or "", {})

        def build_html() -> str:
            p = current_product()
            spec = label_specs[spec_radio.value]
            return make_label_html(
                product_name=product_dd.value or "",
                supplier_info=company_info,
                signal_word=p.get("signal_word", ""),
                hazard_statements=p.get("hazard_statements", ""),
                short_precautionary_statements=p.get("precautionary_statements", ""),
                pictogram_html=make_pictogram_html(p.get("pictograms", [])),
                spec=spec, offset_x=0, offset_y=0,
                font_settings=font_settings_for(spec),
            )

        def build_preview():
            """Edge 없이 동작하는 Flet 네이티브 미리보기."""
            p = current_product()
            if not product_dd.value:
                preview_area.controls = [ft.Text("제품을 선택하세요.", size=13, color="#868E96")]
                page.update()
                return
            ghs_dir = _resource_path(os.path.join("assets", "ghs_images")) \
                if getattr(sys, "frozen", False) \
                else os.path.join(os.path.dirname(os.path.abspath(__file__)), "ghs_images")
            pics = [ft.Image(src=os.path.join(ghs_dir, f), width=54, height=54)
                    for f in p.get("pictograms", [])
                    if os.path.exists(os.path.join(ghs_dir, f))]
            signal = p.get("signal_word", "")
            signal_color = "#C0392B" if signal in ("위험", "경고") else "#212529"

            def sec(title, body):
                return ft.Column([
                    ft.Container(
                        content=ft.Text(title, size=11, weight=ft.FontWeight.BOLD, color="#495057"),
                        border=ft.Border(bottom=ft.BorderSide(1, "#DEE2E6")),
                        padding=ft.padding.Padding(0, 0, 0, 2),
                    ),
                    ft.Text(body or "", size=11, selectable=True),
                ], spacing=3)

            card = ft.Container(
                content=ft.Column([
                    ft.Text(product_dd.value, size=17, weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
                    ft.Row([ft.Row(pics, wrap=True, spacing=6),
                            ft.Text(signal, size=24, weight=ft.FontWeight.W_900, color=signal_color)],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=1, color="#DEE2E6"),
                    sec("[유해·위험문구]", p.get("hazard_statements", "")),
                    sec("[예방조치문구]", p.get("precautionary_statements", "")),
                    sec("[공급자정보]", company_info),
                    ft.Text("* 자세한 내용은 물질안전보건자료(MSDS) 참조 하시오",
                            size=9, italic=True, color="#6C757D", text_align=ft.TextAlign.CENTER),
                ], spacing=8),
                padding=16, border=BORDER, border_radius=8, bgcolor="white", width=440,
            )
            preview_area.controls = [card]
            page.update()

        def on_change(e=None):
            build_preview()
            status_bar.value = f"미리보기: {product_dd.value}  /  규격 {spec_radio.value}"
            page.update()

        product_dd.on_change = on_change
        spec_radio.on_change = on_change

        def _write_and_open(auto_print: bool):
            if not product_dd.value:
                status_bar.value = "⚠ 제품을 먼저 선택하세요."
                page.update()
                return
            html = build_html()
            if auto_print:
                # 브라우저 인쇄 대화상자 자동 호출 → "PDF로 저장" 선택 가능
                html = html.replace("</body>",
                    "<script>window.onload=function(){setTimeout(function(){window.print();},400);}</script></body>")
            fname = f"{supplier_id}_label_{product_dd.value}.html"
            out_path = os.path.join(_output_dir(), fname)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            webbrowser.open(out_path)
            status_bar.value = f"🖨 출력 창 열기: {out_path}"
            page.update()

        def on_print(e):
            _write_and_open(auto_print=False)

        def on_pdf(e):
            _write_and_open(auto_print=True)

        # ── 레이아웃 ───────────────────────────────────────
        header = ft.Container(
            content=ft.Column([
                ft.Text(f"🏷  {display_name} 경고표지 출력", size=20,
                        weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("⚠ 출력 전 반드시 원본 MSDS와 대조·검토 후 사용하십시오. | Windows 64비트 전용",
                        size=11, color="#FFD166"),
            ], spacing=2),
            bgcolor="#343A40",
            padding=ft.padding.Padding(left=16, right=16, top=10, bottom=10),
            border_radius=6,
        )

        left = ft.Container(
            content=ft.Column([
                ft.Text("제품 / 규격 선택", size=14, weight=ft.FontWeight.BOLD, color="#495057"),
                ft.Divider(color="#DEE2E6"),
                product_dd,
                ft.Container(height=8),
                ft.Text("규격 선택", size=13, weight=ft.FontWeight.BOLD, color="#495057"),
                spec_radio,
                ft.Container(height=16),
                ft.ElevatedButton("🖨 인쇄", on_click=on_print, width=240,
                                  style=ft.ButtonStyle(bgcolor="#343A40", color="white")),
                ft.ElevatedButton("📄 PDF로 저장", on_click=on_pdf, width=240,
                                  style=ft.ButtonStyle(bgcolor="#1971C2", color="white")),
                ft.Container(height=8),
                status_bar,
            ], spacing=6),
            width=320, padding=14, border=BORDER, border_radius=6, bgcolor=BG_PANEL,
        )
        right = ft.Container(
            content=ft.Column([
                ft.Text("미리보기", size=14, weight=ft.FontWeight.BOLD, color="#495057"),
                ft.Divider(color="#DEE2E6"),
                preview_area,
            ], spacing=6, expand=True),
            padding=14, border=BORDER, border_radius=6, bgcolor=BG_PANEL, expand=True,
        )

        page.add(header, ft.Row([left, right], spacing=12, expand=True,
                                vertical_alignment=ft.CrossAxisAlignment.START))
        on_change()

    # 오프라인/보안망 환경: localhost DNS 차단 대응 (원본과 동일)
    import socket
    _orig = socket.getaddrinfo
    def _patched(host, *a, **k):
        return _orig("127.0.0.1" if host == "localhost" else host, *a, **k)
    socket.getaddrinfo = _patched

    if getattr(sys, "frozen", False):
        os.environ.setdefault("FLET_VIEW_PATH", os.path.join(sys._MEIPASS, "flet_client"))

    assets = sys._MEIPASS if getattr(sys, "frozen", False) \
        else os.path.dirname(os.path.abspath(__file__))
    try:
        ft.run(main, assets_dir=assets)
    except Exception:
        import traceback
        with open(os.path.join(_output_dir(), "error_log.txt"), "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
