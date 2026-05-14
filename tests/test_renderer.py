from collections import Counter

from PIL import Image

from dual_wordcloud._renderer import render


def test_render_returns_pil_image():
    """기본 파라미터로 렌더링 시 PIL Image를 반환한다."""
    img = render(
        left=Counter({"hello": 5, "world": 3}),
        center=Counter({"both": 2}),
        right=Counter({"foo": 4, "bar": 2}),
        left_label="L", right_label="R",
        word_colors=None, colormap=None,
        left_border_color="#2980b9", right_border_color="#e74c3c",
        left_word_color="#2980b9", right_word_color="#e74c3c",
        center_word_color="#95a5a6",
        font_path=None, quality_scale=1,
    )
    assert isinstance(img, Image.Image)
    assert img.width > 0
    assert img.height > 0


def test_render_with_word_colors():
    """word_colors 제공 시 크래시 없이 PIL Image를 반환한다."""
    img = render(
        left=Counter({"대출": 5}),
        center=Counter(),
        right=Counter({"금리": 3}),
        left_label="A", right_label="B",
        word_colors={"대출": "#3498db", "금리": "#e74c3c"},
        colormap=None,
        left_border_color="#2c3e50", right_border_color="#2c3e50",
        left_word_color="#2c3e50", right_word_color="#2c3e50",
        center_word_color="#95a5a6",
        font_path=None, quality_scale=1,
    )
    assert isinstance(img, Image.Image)


def test_render_empty_center():
    """center Counter가 비어도 크래시 없이 PIL Image를 반환한다."""
    img = render(
        left=Counter({"a": 5}),
        center=Counter(),
        right=Counter({"b": 3}),
        left_label="L", right_label="R",
        word_colors=None, colormap=None,
        left_border_color="#2980b9", right_border_color="#e74c3c",
        left_word_color="#2980b9", right_word_color="#e74c3c",
        center_word_color="#95a5a6",
        font_path=None, quality_scale=1,
    )
    assert isinstance(img, Image.Image)


def test_render_raises_on_all_empty():
    """세 Counter가 모두 비어있으면 ValueError를 발생시킨다."""
    import pytest
    with pytest.raises(ValueError, match="하나 이상"):
        render(
            left=Counter(), center=Counter(), right=Counter(),
            left_label="L", right_label="R",
            word_colors=None, colormap=None,
            left_border_color="#2980b9", right_border_color="#e74c3c",
            left_word_color="#2980b9", right_word_color="#e74c3c",
            center_word_color="#95a5a6",
            font_path=None, quality_scale=1,
        )
