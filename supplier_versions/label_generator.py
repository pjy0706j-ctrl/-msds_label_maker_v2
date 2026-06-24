import os
import re
import base64
import html


def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def make_pictogram_html(pictogram_files):
    import sys
    pictogram_html = ""
    if getattr(sys, "frozen", False):
        # PyInstaller 번들: ghs_images는 assets/ 하위에 위치
        base_dir = os.path.join(sys._MEIPASS, "assets")
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(base_dir, "ghs_images")

    for img_file in pictogram_files:
        candidates = [
            img_file,
            img_file + ".gif",
            img_file + ".jpg",
            img_file + ".jpeg",
            img_file.replace(".png", ".gif"),
            img_file.replace(".png", ".jpg"),
            img_file.replace(".png", ".jpeg"),
            img_file + ".png",
        ]
        img_path = None
        for candidate in candidates:
            candidate_path = os.path.join(image_dir, candidate)
            if os.path.exists(candidate_path):
                img_path = candidate_path
                break

        if img_path:
            img_base64 = image_to_base64(img_path)
            ext = os.path.splitext(img_path)[1].lower()
            if ext == ".gif":
                mime = "image/gif"
            elif ext in [".jpg", ".jpeg"]:
                mime = "image/jpeg"
            else:
                mime = "image/png"
            pictogram_html += f'\n            <img src="data:{mime};base64,{img_base64}">'
        else:
            pictogram_html += (
                f"\n            <div style='color:red; font-size:10px;'>"
                f"이미지 없음: {os.path.join(image_dir, img_file)}</div>"
            )

    return pictogram_html


def safe_html_text(text):
    return html.escape(text or "")


def _make_label_cells(label_html: str, spec: dict, offset_x: float, offset_y: float) -> str:
    """
    CSS grid 대신 절대좌표로 각 라벨을 배치.
    브라우저 렌더링 오차가 누적되지 않아 아이라벨 용지 규격에 정확히 맞음.
    """
    cols      = spec["cols"]
    rows      = spec["rows"]
    label_w   = spec["label_w"]
    label_h   = spec["label_h"]
    margin_l  = spec["margin_left"]  + offset_x
    margin_t  = spec["margin_top"]   + offset_y
    gap_x     = spec["gap_x"]
    gap_y     = spec["gap_y"]

    result = []
    for r in range(rows):
        for c in range(cols):
            left = margin_l + c * (label_w + gap_x)
            top  = margin_t + r * (label_h + gap_y)
            # label_html의 첫 <div class="label..."> 에 style 주입
            cell = label_html.replace(
                '<div class="label ',
                f'<div style="left:{left:.3f}mm;top:{top:.3f}mm;" class="label ',
                1,
            )
            result.append(cell)
    return "\n".join(result)


def make_label_html(
    product_name,
    supplier_info,
    signal_word,
    hazard_statements,
    short_precautionary_statements,
    pictogram_html,
    spec,
    offset_x,
    offset_y,
    font_settings,
):
    product_name = safe_html_text(product_name)
    _signal_raw  = signal_word
    signal_word  = safe_html_text(signal_word)
    signal_color = "#C0392B" if _signal_raw in ("위험", "경고") else "#212529"

    # ── 공급자정보: \n → <br> (줄바꿈 유지) ──────────────
    supplier_info = html.escape(supplier_info or "").replace("\n", "<br>")

    # ── 유해위험문구: H코드 문장을 공백으로 연결 (세로 여백 최소화) ──
    hazard_statements = safe_html_text(
        "  ".join(l.strip() for l in hazard_statements.splitlines() if l.strip())
    )

    # ── 예방조치문구: 섹션 헤더 <br>, 섹션 내 P코드는 공백 연결 ──
    def _compact_prec(text: str) -> str:
        lines = text.splitlines()
        output_parts = []
        current_section = ""
        current_codes: list[str] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            m = re.match(r"<(예방|대응|저장|폐기)>", line)
            if m:
                if current_section and current_codes:
                    output_parts.append(
                        f"[{current_section}] " + "  ".join(current_codes)
                    )
                current_section = m.group(1)
                current_codes = []
            else:
                current_codes.append(line)
        if current_section and current_codes:
            output_parts.append(
                f"[{current_section}] " + "  ".join(current_codes)
            )
        # 섹션 사이 <br> 로 줄바꿈
        return "<br>".join(html.escape(p) for p in output_parts)

    short_precautionary_statements = _compact_prec(short_precautionary_statements)

    # 그림문자 크기 자동조절
    pic_count = pictogram_html.count("<img")
    base_pic = spec["base_pic"]

    if spec["label_h"] <= 40:
        if pic_count >= 6:
            pic_size = base_pic * 0.72
        elif pic_count == 5:
            pic_size = base_pic * 0.82
        elif pic_count == 4:
            pic_size = base_pic * 0.9
        else:
            pic_size = base_pic
    else:
        if pic_count >= 6:
            pic_size = base_pic * 0.58
        elif pic_count == 5:
            pic_size = base_pic * 0.68
        elif pic_count == 4:
            pic_size = base_pic * 0.78
        elif pic_count == 3:
            pic_size = base_pic * 0.9
        elif pic_count == 2:
            pic_size = base_pic * 1.0
        else:
            pic_size = base_pic

    pic_size *= font_settings["pictogram_scale"]

    # 2칸 높이 제한 제거
    if spec["label_h"] >= 120:
        text_max_height = "none"
        small_text_max_height = "none"
        text_overflow = "visible"
        small_text_overflow = "visible"
        supplier_max_height = "none"
        supplier_overflow = "visible"
    else:
        text_max_height = "22mm"
        small_text_max_height = "18mm"
        text_overflow = "hidden"
        small_text_overflow = "hidden"
        supplier_max_height = "7mm"
        supplier_overflow = "hidden"

    # 라벨 타입별 HTML 구성
    if spec["label_h"] <= 40:
        # 24칸
        label_one = f"""
        <div class="label label-24">
            <div class="product">{product_name}</div>
            <div class="top-area">
                <div class="pictograms">{pictogram_html}</div>
                <div class="signal-side">{signal_word}</div>
            </div>
            <div class="supplier-mini">{supplier_info}</div>
            <div class="msds-mini">기타 자세한 사항은 물질안전보건자료 참조</div>
        </div>
        """

    elif spec["label_h"] >= 120:
        # 2칸
        label_one = f"""
        <div class="label label-2">
            <div class="product">{product_name}</div>
            <div class="top-area">
                <div class="pictograms">{pictogram_html}</div>
                <div class="signal-side">{signal_word}</div>
            </div>
            <div class="section-title">[유해위험문구]</div>
            <div class="text">{hazard_statements}</div>
            <div class="section-title">[예방조치문구]</div>
            <div class="small-text">{short_precautionary_statements}</div>
            <div class="section-title">[공급자정보]</div>
            <div class="supplier-large">{supplier_info}</div>
            <div class="msds-bottom">* 자세한 내용은 물질안전보건자료(MSDS) 참조 하시오</div>
        </div>
        """

    else:
        # 9칸
        label_one = f"""
        <div class="label label-9">
            <div class="product">{product_name}</div>
            <div class="top-area">
                <div class="pictograms">{pictogram_html}</div>
                <div class="signal-side">{signal_word}</div>
            </div>
            <div class="section-title">[유해위험문구]</div>
            <div class="text">{hazard_statements}</div>
            <div class="section-title">[예방조치문구]</div>
            <div class="small-text">{short_precautionary_statements}</div>
            <div class="section-title">[공급자정보]</div>
            <div class="supplier">{supplier_info}</div>
            <div class="msds-bottom">* 자세한 내용은 물질안전보건자료(MSDS) 참조 하시오</div>
        </div>
        """

    label_sheet_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>

@page {{
    size: 210mm 297mm;
    margin: 0;
}}

body {{
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}

.sheet {{
    position: relative;
    width: 210mm;
    height: 297mm;
    overflow: hidden;
}}

.label {{
    position: absolute;
    box-sizing: border-box;
    width: {spec['label_w']}mm;
    height: {spec['label_h']}mm;
    border: 1px solid #999;
    padding: {spec['padding']}mm;
    padding-top: {"1.5mm" if spec["label_h"] <= 40 else "2mm"};
    padding-bottom: {"1.5mm" if spec["label_h"] <= 40 else "2mm"};
    font-size: 7px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: stretch;
}}

.product {{
    font-size: {font_settings['product_font']}px;
    font-weight: bold;
    text-align: center;
    letter-spacing: -0.2px;
    /* 시약명↔그림문자 간격 최소화 */
    margin-bottom: {"0.5mm" if spec["label_h"] <= 40 else "1mm"};
    line-height: 1.05;
    word-break: break-word;
    overflow-wrap: break-word;
    white-space: normal;
    height: auto;
    min-height: {"3mm" if spec["label_h"] <= 40 else "5mm"};
}}

.pictograms {{
    text-align: center;
    /* 그림문자 아래 간격 최소화 */
    margin-bottom: {"0mm" if spec["label_h"] <= 40 else "0.2mm"};
    min-height: {"10mm" if spec["label_h"] <= 40 else "auto"};
    display: {"grid" if spec["label_h"] <= 40 else "flex"};
    grid-template-columns: {"repeat(3, 1fr)" if spec["label_h"] <= 40 else "none"};
    flex-wrap: wrap;
    justify-content: center;
    justify-items: center;
    align-items: center;
    row-gap: 0;
}}

.two-column {{
    display: flex;
    gap: 3mm;
    margin-top: 2mm;
    margin-bottom: 2mm;
    align-items: flex-start;
}}

.left-column {{
    flex: 1;
    min-width: 0;
}}

.right-column {{
    flex: 1;
    min-width: 0;
}}

.pictograms img {{
    width: {pic_size}mm;
    height: {pic_size}mm;
    margin: {"0.1mm" if spec["label_h"] <= 40 else "0.5mm"};
}}

.top-area {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    /* 그림문자↔문구 사이 여백 최소화 */
    margin-top: 0;
    margin-bottom: {"0mm" if spec["label_h"] <= 40 else "0.5mm"};
}}

.signal-side {{
    font-size: {font_settings['signal_font']}px;
    font-weight: 900;
    text-align: center;
    width: 28%;
    line-height: 1.0;
    letter-spacing: -0.5px;
    color: {signal_color};
}}


.msds-mini {{
    font-size: {font_settings['msds_font']}px;
    text-align: center;
    margin-top: 0.3mm;
}}

.msds-bottom {{
    font-size: {font_settings['msds_font']}px;
    text-align: center;
    margin-top: 1mm;
    font-weight: bold;
}}

.section-title {{
    font-weight: bold;
    font-size: {font_settings['title_font']}px;
    margin-top: {"0mm" if spec["label_h"] <= 40 else "0.5mm"};
    margin-bottom: 0;
    padding-top: 0.1mm;
    border-top: 1px solid #ccc;
}}

.text {{
    white-space: normal;
    word-break: break-word;
    font-size: {font_settings['hazard_font']}px;
    line-height: 1.02;
    overflow: visible;
    margin-bottom: 0.5mm;
}}

.small-text {{
    white-space: normal;
    word-break: break-word;
    font-size: {font_settings['precaution_font']}px;
    line-height: 1.0;
    overflow: visible;
    margin-bottom: {"0.1mm" if spec["label_h"] <= 40 else "1mm"};
}}

.supplier {{
    white-space: normal;   /* <br> 태그로 줄바꿈 처리 */
    word-break: break-word;
    overflow-wrap: break-word;
    font-size: {font_settings['supplier_font']}px;
    line-height: {"1.1" if spec["label_h"] <= 40 else "1.3"};
    overflow: visible;
    padding-bottom: {"0mm" if spec["label_h"] <= 40 else "0.5mm"};
}}
.supplier-large {{
    white-space: normal;
    word-break: break-word;
    font-size: {font_settings['supplier_font']}px;
    line-height: 1.3;
}}
.supplier-mini {{
    white-space: normal;
    font-size: {font_settings['supplier_font']}px;
    line-height: 1.0;
    margin-top: 0.5mm;
}}

/* ── 인쇄 전용 규칙 ── */
@media print {{
    @page {{
        size: 210mm 297mm;
        margin: 0;
    }}
    body {{
        margin: 0;
        padding: 0;
    }}
    .sheet {{
        /* 인쇄 시 transform 없이 정확한 위치 */
        page-break-inside: avoid;
    }}
    .label {{
        overflow: hidden;
        page-break-inside: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}
}}
</style>
</head>
<body>
<div class="sheet">
    {_make_label_cells(label_one, spec, offset_x, offset_y)}
</div>

<script>
// ── 라벨별 자동 축소: 내용이 라벨 높이를 초과하지 않도록 ──
(function() {{
  var DPR        = window.devicePixelRatio || 1;
  var PX_PER_MM  = 96 / 25.4;          // CSS px/mm (96dpi 기준)
  var MIN_FONT   = 2.8;                 // px 최솟값
  var MIN_LH     = 0.85;               // line-height 최솟값
  var FONT_STEP  = 0.15;
  var LH_STEP    = 0.02;
  var PAD_STEP   = 0.2;
  var MG_STEP    = 0.2;

  var maxH_mm  = {spec['label_h']};
  var maxH_px  = maxH_mm * PX_PER_MM;
  var padOrig  = {spec['padding']} * PX_PER_MM;

  document.querySelectorAll('.label').forEach(function(lbl) {{
    // overflow:hidden이면 scrollHeight가 maxH_px와 같아도 내용이 클 수 있음
    // → 일시적으로 overflow:visible 로 바꿔 실제 높이 측정
    lbl.style.overflow = 'visible';

    var textEls   = Array.from(lbl.querySelectorAll(
                      '.text,.small-text,.supplier,.supplier-large,.supplier-mini,.product'));
    var spacerEls = Array.from(lbl.querySelectorAll(
                      '.section-title,.top-area,.msds-bottom,.msds-mini'));
    var iter = 0;

    while (lbl.scrollHeight > maxH_px * 1.01 && iter < 400) {{
      var ov = lbl.scrollHeight - maxH_px;

      // 단계1: 여백/패딩 줄이기
      if (ov > PX_PER_MM * 1) {{
        spacerEls.forEach(function(el) {{
          var mt = parseFloat(el.style.marginTop)  || 0;
          var mb = parseFloat(el.style.marginBottom)|| 0;
          if (mt > 0) el.style.marginTop    = Math.max(0, mt - MG_STEP) + 'px';
          if (mb > 0) el.style.marginBottom = Math.max(0, mb - MG_STEP) + 'px';
        }});
        var curPad = parseFloat(lbl.style.paddingTop) || padOrig;
        if (curPad > PX_PER_MM * 0.5) {{
          var np = Math.max(PX_PER_MM * 0.5, curPad - PAD_STEP);
          lbl.style.paddingTop    = np + 'px';
          lbl.style.paddingBottom = np + 'px';
        }}
      }}

      // 단계2: 폰트 크기 줄이기
      var reduced = false;
      textEls.forEach(function(el) {{
        var fs = parseFloat(window.getComputedStyle(el).fontSize);
        if (fs > MIN_FONT) {{
          el.style.fontSize = Math.max(MIN_FONT, fs - FONT_STEP) + 'px';
          reduced = true;
        }}
      }});

      // 단계3: line-height 줄이기 (폰트 최솟값 도달 후)
      if (!reduced) {{
        textEls.forEach(function(el) {{
          var lh = parseFloat(el.style.lineHeight) || 1.05;
          if (lh > MIN_LH) {{
            el.style.lineHeight = Math.max(MIN_LH, lh - LH_STEP).toFixed(3);
            reduced = true;
          }}
        }});
      }}

      if (!reduced) break;
      iter++;
    }}

    // 자동축소 완료 → 다시 overflow:hidden (인쇄 시 경계 벗어남 방지)
    lbl.style.overflow = 'hidden';
  }});
}})();
</script>

</body>
</html>
"""
    return label_sheet_html
