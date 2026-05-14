# dual-wordcloud

벤 다이어그램 스타일의 워드클라우드. 키워드를 세 영역(왼쪽 전용 / 공통(교집합) / 오른쪽 전용)으로 나눠 시각화합니다.

## 설치

```bash
pip install dual-wordcloud
```

## 사용법

### 모드 1: 영역 직접 지정 (`from_regions`)

키워드를 세 그룹으로 미리 나눠놓은 경우 사용합니다. 긍정/중립/부정 감성 분류가 대표적인 예입니다.

```python
from collections import Counter
from dual_wordcloud import DualWordCloud

긍정 = Counter({"성장": 42, "혁신": 35, "안정": 28})
중립 = Counter({"금리": 20, "실적": 18})
부정 = Counter({"손실": 30, "위기": 25, "부채": 15})

dwc = DualWordCloud.from_regions(
    left=긍정,
    center=중립,
    right=부정,
    left_label="긍정",
    right_label="부정",
    left_border_color="#3498db",
    right_border_color="#e74c3c",
)
dwc.to_file("sentiment.png")
```

### 모드 2: 두 대상 비교 (`from_comparison`)

두 Counter를 넣으면 키워드 배치(왼쪽/교집합/오른쪽)를 자동으로 계산합니다. 정규화 빈도 비율 기준으로 분류되므로 기사 수가 다른 두 대상도 공정하게 비교됩니다.

```python
from collections import Counter
from dual_wordcloud import DualWordCloud

bnk  = Counter({"대출": 120, "금리": 95, "부채": 40, "성장": 60})
hana = Counter({"예금": 110, "금리": 88, "투자": 75, "성장": 58})

dwc = DualWordCloud.from_comparison(
    left=bnk,
    right=hana,
    count_left=1000,   # BNK 전체 기사 수 (정규화 분모)
    count_right=850,   # 하나 전체 기사 수
    left_label="BNK",
    right_label="하나",
)
dwc.to_file("comparison.png")
```

한쪽에서 압도적으로 많이 나오는 키워드는 해당 원 안에, 두 대상에서 비슷한 빈도로 나오는 키워드는 교집합에 배치됩니다.

### 출력

```python
dwc.to_file("output.png")   # PNG 파일 저장, Path 반환
dwc.to_image()              # PIL Image 반환 (추가 가공 등)
dwc.show()                  # 시스템 뷰어로 바로 확인
dwc                         # Jupyter Notebook 셀에서 인라인 표시
```

## 파라미터

### `from_regions(left, center, right, **kwargs)`

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `left` | `Counter[str]` | 필수 | 왼쪽 원 키워드 |
| `center` | `Counter[str]` | 필수 | 교집합 키워드 |
| `right` | `Counter[str]` | 필수 | 오른쪽 원 키워드 |
| `left_label` | `str` | `"Left"` | 왼쪽 원 라벨 |
| `right_label` | `str` | `"Right"` | 오른쪽 원 라벨 |
| `word_colors` | `dict[str, str] \| None` | `None` | 키워드별 hex 색상 (최우선) |
| `colormap` | `str \| None` | `None` | matplotlib colormap명 (예: `"Reds"`) |
| `font_path` | `str \| Path \| None` | `None` | 폰트 경로. `None`이면 자동탐색 |
| `left_border_color` | `str` | `"#2980b9"` | 왼쪽 원 테두리색 |
| `right_border_color` | `str` | `"#e74c3c"` | 오른쪽 원 테두리색 |
| `left_word_color` | `str` | `"#2980b9"` | 왼쪽 단어 폴백색 |
| `right_word_color` | `str` | `"#e74c3c"` | 오른쪽 단어 폴백색 |
| `center_word_color` | `str` | `"#95a5a6"` | 교집합 단어 폴백색 |
| `quality_scale` | `int` | `2` | 렌더링 품질 1~3 |

### `from_comparison(left, right, count_left, count_right, **kwargs)`

`from_regions`의 모든 파라미터에 추가로:

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `count_left` | `int` | 필수 | 왼쪽 전체 문서 수 (정규화 분모) |
| `count_right` | `int` | 필수 | 오른쪽 전체 문서 수 |
| `ratio_threshold` | `float` | `2.0` | 이 비율 초과 시 한쪽 원에 단독 배치 |

### 단어 색상 우선순위

```
word_colors[키워드]   →  키워드별 개별 색상 (최우선)
colormap             →  matplotlib colormap 적용
*_word_color         →  영역별 폴백 색상 (최후순위)
```

## 한글 폰트

AppleSDGothicNeo, NanumGothic, Malgun Gothic 등 주요 한글 폰트를 자동으로 탐색합니다. 특정 폰트를 지정하려면:

```python
dwc = DualWordCloud.from_regions(
    ...,
    font_path="/path/to/NanumGothic.ttf",
)
```

## 요구사항

- Python 3.12+
- matplotlib, matplotlib-venn, wordcloud, shapely, Pillow, numpy
