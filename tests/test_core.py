import io
from collections import Counter
from pathlib import Path

import pytest
from PIL import Image

from dual_wordcloud.core import DualWordCloud


@pytest.fixture
def regions():
    return {
        "left": Counter({"긍정어": 5, "희망": 3}),
        "center": Counter({"중립어": 2}),
        "right": Counter({"부정어": 4, "위기": 2}),
    }


@pytest.fixture
def comparison():
    return {
        "left": Counter({"대출": 20, "금리": 15, "부채": 5}),
        "right": Counter({"예금": 18, "금리": 14, "적금": 8}),
        "count_left": 100,
        "count_right": 100,
    }


# --- from_regions ---

def test_from_regions_returns_instance(regions):
    dwc = DualWordCloud.from_regions(**regions)
    assert isinstance(dwc, DualWordCloud)


def test_from_regions_to_image(regions):
    dwc = DualWordCloud.from_regions(**regions, quality_scale=1)
    img = dwc.to_image()
    assert isinstance(img, Image.Image)
    assert img.width > 0


def test_from_regions_to_file(regions, tmp_path):
    dwc = DualWordCloud.from_regions(**regions, quality_scale=1)
    out = tmp_path / "out.png"
    result = dwc.to_file(out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_from_regions_repr_png(regions):
    dwc = DualWordCloud.from_regions(**regions, quality_scale=1)
    png_bytes = dwc._repr_png_()
    assert isinstance(png_bytes, bytes)
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"


def test_from_regions_render_cached(regions):
    """렌더링 결과가 캐싱되어 두 번째 호출 시 동일 객체를 반환한다."""
    dwc = DualWordCloud.from_regions(**regions, quality_scale=1)
    img1 = dwc.to_image()
    img2 = dwc.to_image()
    assert img1 is img2


# --- from_comparison ---

def test_from_comparison_returns_instance(comparison):
    dwc = DualWordCloud.from_comparison(**comparison)
    assert isinstance(dwc, DualWordCloud)


def test_from_comparison_to_image(comparison):
    """from_comparison은 내부에서 split을 처리하고 렌더링한다."""
    dwc = DualWordCloud.from_comparison(**comparison, quality_scale=1)
    img = dwc.to_image()
    assert isinstance(img, Image.Image)


def test_from_comparison_with_word_colors(comparison):
    dwc = DualWordCloud.from_comparison(
        **comparison,
        word_colors={"대출": "#3498db", "예금": "#e74c3c"},
        quality_scale=1,
    )
    assert isinstance(dwc.to_image(), Image.Image)
