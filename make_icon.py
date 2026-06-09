"""
MSDS Label Maker 로고 아이콘 생성
"""
from PIL import Image, ImageDraw, ImageFont
import os

def make_icon():
    sizes = [256, 128, 64, 48, 32, 16]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 배경: 둥근 사각형 (진한 파란색)
        margin = max(1, size // 16)
        r = size // 6  # 모서리 반경
        bg_color = (25, 118, 210, 255)   # #1976D2 (파란색)
        accent_color = (255, 193, 7, 255) # #FFC107 (노란색/경고색)
        white = (255, 255, 255, 255)

        # 둥근 사각형 배경
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=r, fill=bg_color
        )

        # GHS 경고 다이아몬드 심볼 (중앙 상단)
        cx = size // 2
        # 다이아몬드 크기
        d = int(size * 0.38)
        dy = int(size * 0.28)  # 다이아몬드 중심 y

        # 다이아몬드 외곽 (빨간 테두리)
        pts_outer = [
            (cx, dy - d),
            (cx + d, dy),
            (cx, dy + d),
            (cx - d, dy),
        ]
        draw.polygon(pts_outer, fill=accent_color)

        # 다이아몬드 내부 (흰색)
        inner = int(d * 0.78)
        pts_inner = [
            (cx, dy - inner),
            (cx + inner, dy),
            (cx, dy + inner),
            (cx - inner, dy),
        ]
        draw.polygon(pts_inner, fill=white)

        # 느낌표 (!)
        ex_w = max(2, size // 18)
        ex_h = max(3, size // 10)
        ex_x1 = cx - ex_w // 2
        ex_x2 = cx + ex_w // 2
        ex_top = dy - int(d * 0.45)
        # 세로 막대
        draw.rectangle([ex_x1, ex_top, ex_x2, ex_top + ex_h], fill=bg_color)
        # 점
        dot_r = max(1, ex_w)
        dot_y = ex_top + ex_h + max(2, size // 28)
        draw.ellipse([cx - dot_r, dot_y, cx + dot_r, dot_y + dot_r * 2], fill=bg_color)

        # 하단 텍스트: "MSDS"
        text = "MSDS"
        font_size = max(6, size // 7)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        tx = (size - tw) // 2
        ty = size - margin - font_size - max(2, size // 20)
        draw.text((tx, ty), text, fill=white, font=font)

        images.append(img)

    # ICO 저장
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
    images[0].save(
        out_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print(f"아이콘 저장: {out_path}")

    # PNG도 저장 (256x256, Flet window icon용)
    png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.png")
    images[0].save(png_path, format="PNG")
    print(f"PNG 저장: {png_path}")

if __name__ == "__main__":
    make_icon()
