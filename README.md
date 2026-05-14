# dual-wordcloud

Venn diagram–style wordcloud that splits keywords across three regions: left-only, shared (center), and right-only.

## Installation

```bash
pip install dual-wordcloud
```

## Usage

### Mode 1: Direct regions (`from_regions`)

Use when you already have keywords pre-divided into three groups — e.g. positive / neutral / negative sentiment.

```python
from collections import Counter
from dual_wordcloud import DualWordCloud

positive = Counter({"성장": 42, "혁신": 35, "안정": 28})
neutral  = Counter({"금리": 20, "실적": 18})
negative = Counter({"손실": 30, "위기": 25, "부채": 15})

dwc = DualWordCloud.from_regions(
    left=positive,
    center=neutral,
    right=negative,
    left_label="긍정",
    right_label="부정",
    left_border_color="#3498db",
    right_border_color="#e74c3c",
)
dwc.to_file("sentiment.png")
```

### Mode 2: Comparison (`from_comparison`)

Use when you have two raw keyword counters and want to compare them. Keyword placement (left / center / right) is determined automatically by normalized frequency ratio.

```python
from collections import Counter
from dual_wordcloud import DualWordCloud

bnk   = Counter({"대출": 120, "금리": 95, "부채": 40, "성장": 60})
hana  = Counter({"예금": 110, "금리": 88, "투자": 75, "성장": 58})

dwc = DualWordCloud.from_comparison(
    left=bnk,
    right=hana,
    count_left=1000,   # total articles for BNK (for normalization)
    count_right=850,   # total articles for Hana
    left_label="BNK",
    right_label="하나",
)
dwc.to_file("comparison.png")
```

Keywords that appear predominantly in one source land in that source's circle. Keywords with similar frequency in both land in the center intersection.

### Output

```python
dwc.to_file("output.png")   # save PNG, returns Path
dwc.to_image()              # PIL Image (for further processing)
dwc.show()                  # open in system viewer
dwc                         # inline display in Jupyter Notebook
```

## Parameters

### `from_regions(left, center, right, **kwargs)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `left` | `Counter[str]` | required | Left circle keywords |
| `center` | `Counter[str]` | required | Intersection keywords |
| `right` | `Counter[str]` | required | Right circle keywords |
| `left_label` | `str` | `"Left"` | Left circle label |
| `right_label` | `str` | `"Right"` | Right circle label |
| `word_colors` | `dict[str, str] \| None` | `None` | Per-word hex colors (highest priority) |
| `colormap` | `str \| None` | `None` | matplotlib colormap name (e.g. `"Reds"`) |
| `font_path` | `str \| Path \| None` | `None` | Font file path. Auto-detected if `None` |
| `left_border_color` | `str` | `"#2980b9"` | Left circle border color |
| `right_border_color` | `str` | `"#e74c3c"` | Right circle border color |
| `left_word_color` | `str` | `"#2980b9"` | Left region word fallback color |
| `right_word_color` | `str` | `"#e74c3c"` | Right region word fallback color |
| `center_word_color` | `str` | `"#95a5a6"` | Center region word fallback color |
| `quality_scale` | `int` | `2` | Render quality 1–3 |

### `from_comparison(left, right, count_left, count_right, **kwargs)`

Same as `from_regions` plus:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count_left` | `int` | required | Total document count for left (normalization denominator) |
| `count_right` | `int` | required | Total document count for right |
| `ratio_threshold` | `float` | `2.0` | Frequency ratio above which a keyword is placed exclusively in one circle |

### Word color priority

```
word_colors[keyword]   →  per-word color (highest)
colormap               →  matplotlib colormap
*_word_color           →  region fallback color (lowest)
```

## Korean font

The renderer auto-detects common Korean system fonts (AppleSDGothicNeo, NanumGothic, Malgun Gothic). To use a specific font:

```python
dwc = DualWordCloud.from_regions(
    ...,
    font_path="/path/to/NanumGothic.ttf",
)
```

## Requirements

- Python 3.12+
- matplotlib, matplotlib-venn, wordcloud, shapely, Pillow, numpy
