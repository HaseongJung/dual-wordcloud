"""듀얼 워드클라우드 렌더링 모듈."""
import io
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import shapely.geometry as geom
from matplotlib_venn import venn2
from PIL import Image, ImageDraw
from wordcloud import WordCloud


def _resolve_font_path() -> Path | None:
    """시스템에서 사용 가능한 폰트를 자동으로 찾는다."""
    candidates = [
        Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
        Path("/Library/Fonts/NanumGothic.ttf"),
        Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
        Path("C:/Windows/Fonts/malgun.ttf"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _make_color_func(color_lookup: dict[str, str], fallback: str) -> callable:
    """키워드별 색상 매핑 함수. 매핑에 없는 단어는 fallback 색상을 사용한다."""
    def color_func(word: str, **kwargs) -> str:
        return color_lookup.get(word, fallback)
    return color_func


def _make_region_color_func(color: str) -> callable:
    """영역 전체를 단일 색상으로 칠하는 함수를 반환한다."""
    return lambda word, **kwargs: color


def render(
    left: Counter,
    center: Counter,
    right: Counter,
    left_label: str,
    right_label: str,
    word_colors: dict[str, str] | None,
    colormap: str | None,
    left_border_color: str,
    right_border_color: str,
    left_word_color: str,
    right_word_color: str,
    center_word_color: str,
    font_path: Path | None,
    quality_scale: int,
) -> Image.Image:
    """세 Counter를 받아 듀얼 워드클라우드 PIL Image를 반환한다."""
    if font_path is None:
        font_path = _resolve_font_path()

    scale = max(1, min(int(quality_scale), 3))
    border_colors = [left_border_color, right_border_color]
    word_colors_by_region = [left_word_color, right_word_color, center_word_color]

    if not any([left, center, right]):
        raise ValueError("left, center, right 중 하나 이상은 비어있지 않아야 합니다")

    global_max = max(
        max(left.values(), default=0),
        max(center.values(), default=0),
        max(right.values(), default=0),
    ) or 1
    left = Counter({k: v / global_max for k, v in left.items()})
    center = Counter({k: v / global_max for k, v in center.items()})
    right = Counter({k: v / global_max for k, v in right.items()})

    fig_width, fig_height, dpi = 25, 15, 300

    rc_params = {"axes.unicode_minus": False}
    if font_path:
        font_prop = fm.FontProperties(fname=str(font_path))
        rc_params["font.family"] = font_prop.get_name()

    with matplotlib.rc_context(rc_params):
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
        venn = venn2(subsets=(10, 10, 5), set_labels=(left_label, right_label), ax=ax)

        subset_data = {
            frozenset({0}): left,
            frozenset({1}): right,
            frozenset({0, 1}): center,
        }
        subset_keys = [frozenset({0}), frozenset({1}), frozenset({0, 1})]

        for idx, patch in enumerate(venn.patches):
            if patch is None:
                continue
            patch.set_facecolor("none")
            if idx < len(border_colors):
                patch.set_edgecolor(border_colors[idx])
                patch.set_linewidth(2)
            else:
                patch.set_linewidth(0)

        for label in venn.subset_labels:
            if label:
                label.set_visible(False)

        for idx, patch in enumerate(venn.patches):
            if idx >= len(subset_keys):
                continue
            counter = subset_data.get(subset_keys[idx], Counter())
            if not counter:
                continue

            path = patch.get_path()
            if path is None:
                continue
            vertices = path.vertices
            if len(vertices) < 3:
                continue

            polygon = geom.Polygon(vertices)
            min_x, min_y, max_x, max_y = polygon.bounds
            width = max(100, min(800, int((max_x - min_x) * dpi * scale)))
            height = max(100, min(600, int((max_y - min_y) * dpi * scale)))

            img_mask = Image.new("L", (width, height), 255)
            draw = ImageDraw.Draw(img_mask)
            x_range = max_x - min_x if max_x > min_x else 1
            y_range = max_y - min_y if max_y > min_y else 1
            px_vertices = [
                (int((x - min_x) / x_range * (width - 1)),
                 int((max_y - y) / y_range * (height - 1)))
                for x, y in vertices
            ]
            draw.polygon(px_vertices, fill=0)
            mask = np.array(img_mask)

            region_word_color = word_colors_by_region[idx] if idx < len(word_colors_by_region) else "#95a5a6"
            wc_kwargs: dict = {}
            if word_colors:
                region_lookup = {k: v for k, v in word_colors.items() if k in counter}
                wc_kwargs["color_func"] = _make_color_func(region_lookup, fallback=region_word_color)
            elif colormap:
                wc_kwargs["colormap"] = colormap
            else:
                wc_kwargs["color_func"] = _make_region_color_func(region_word_color)

            wc = WordCloud(
                font_path=str(font_path) if font_path else None,
                width=width, height=height, mask=mask,
                mode="RGBA", background_color=None,
                prefer_horizontal=0.7, min_font_size=8,
                max_font_size=int(48 * scale),
                **wc_kwargs,
            )
            wc.generate_from_frequencies(counter)
            ax.imshow(np.array(wc), extent=[min_x, max_x, min_y, max_y],
                      aspect="auto", alpha=0.9, zorder=10)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                    pad_inches=0.1, transparent=False, facecolor="white")
        plt.close(fig)

    buf.seek(0)
    return Image.open(buf).copy()
