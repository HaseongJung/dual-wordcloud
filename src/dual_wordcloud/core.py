"""듀얼 워드클라우드의 메인 공개 인터페이스."""
from __future__ import annotations

import io
from collections import Counter
from pathlib import Path

from PIL import Image

from dual_wordcloud._renderer import render
from dual_wordcloud._splitter import split_for_comparison


class DualWordCloud:
    """벤 다이어그램 스타일의 듀얼 워드클라우드."""

    def __init__(
        self,
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
    ) -> None:
        self._left = left
        self._center = center
        self._right = right
        self._left_label = left_label
        self._right_label = right_label
        self._word_colors = word_colors
        self._colormap = colormap
        self._left_border_color = left_border_color
        self._right_border_color = right_border_color
        self._left_word_color = left_word_color
        self._right_word_color = right_word_color
        self._center_word_color = center_word_color
        self._font_path = font_path
        self._quality_scale = quality_scale
        self._image: Image.Image | None = None

    @classmethod
    def from_regions(
        cls,
        left: Counter,
        center: Counter,
        right: Counter,
        left_label: str = "Left",
        right_label: str = "Right",
        word_colors: dict[str, str] | None = None,
        colormap: str | None = None,
        font_path: str | Path | None = None,
        left_border_color: str = "#2980b9",
        right_border_color: str = "#e74c3c",
        left_word_color: str = "#2980b9",
        right_word_color: str = "#e74c3c",
        center_word_color: str = "#95a5a6",
        quality_scale: int = 2,
    ) -> DualWordCloud:
        """세 영역(left/center/right)을 직접 지정하는 모드."""
        return cls(
            left=left, center=center, right=right,
            left_label=left_label, right_label=right_label,
            word_colors=word_colors, colormap=colormap,
            left_border_color=left_border_color,
            right_border_color=right_border_color,
            left_word_color=left_word_color,
            right_word_color=right_word_color,
            center_word_color=center_word_color,
            font_path=Path(font_path) if font_path else None,
            quality_scale=quality_scale,
        )

    @classmethod
    def from_comparison(
        cls,
        left: Counter,
        right: Counter,
        count_left: int,
        count_right: int,
        left_label: str = "Left",
        right_label: str = "Right",
        word_colors: dict[str, str] | None = None,
        colormap: str | None = None,
        ratio_threshold: float = 2.0,
        font_path: str | Path | None = None,
        left_border_color: str = "#2980b9",
        right_border_color: str = "#e74c3c",
        left_word_color: str = "#2980b9",
        right_word_color: str = "#e74c3c",
        center_word_color: str = "#95a5a6",
        quality_scale: int = 2,
    ) -> DualWordCloud:
        """두 Counter를 비교하는 모드. 내부에서 split_for_comparison을 자동 처리한다."""
        left_split, center_split, right_split = split_for_comparison(
            left, right, count_left, count_right, ratio_threshold
        )
        return cls(
            left=left_split, center=center_split, right=right_split,
            left_label=left_label, right_label=right_label,
            word_colors=word_colors, colormap=colormap,
            left_border_color=left_border_color,
            right_border_color=right_border_color,
            left_word_color=left_word_color,
            right_word_color=right_word_color,
            center_word_color=center_word_color,
            font_path=Path(font_path) if font_path else None,
            quality_scale=quality_scale,
        )

    def _get_image(self) -> Image.Image:
        """캐시된 이미지를 반환하고, 없으면 렌더링 후 캐시한다."""
        if self._image is None:
            self._image = render(
                left=self._left, center=self._center, right=self._right,
                left_label=self._left_label, right_label=self._right_label,
                word_colors=self._word_colors, colormap=self._colormap,
                left_border_color=self._left_border_color,
                right_border_color=self._right_border_color,
                left_word_color=self._left_word_color,
                right_word_color=self._right_word_color,
                center_word_color=self._center_word_color,
                font_path=self._font_path,
                quality_scale=self._quality_scale,
            )
        return self._image

    def to_file(self, path: str | Path) -> Path:
        """PNG 파일로 저장하고 저장 경로를 반환한다."""
        path = Path(path)
        self._get_image().save(path, format="PNG")
        return path

    def to_image(self) -> Image.Image:
        """PIL Image를 반환한다."""
        return self._get_image()

    def show(self) -> None:
        """시스템 뷰어로 이미지를 표시한다."""
        self._get_image().show()

    def _repr_png_(self) -> bytes:
        """Jupyter 셀에서 인라인 표시를 위한 PNG bytes를 반환한다."""
        buf = io.BytesIO()
        self._get_image().save(buf, format="PNG")
        return buf.getvalue()
