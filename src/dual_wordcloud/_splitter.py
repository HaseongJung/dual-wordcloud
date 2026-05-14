from collections import Counter


def split_for_comparison(
    a: Counter,
    b: Counter,
    count_a: int,
    count_b: int,
    ratio_threshold: float = 2.0,
) -> tuple[Counter, Counter, Counter]:
    """두 Counter를 정규화 빈도 기반으로 left/center/right로 분리한다.

    각 키워드를 기사 수로 정규화한 뒤 비율 임계값으로 배치를 결정한다:
      - 한쪽에만 있는 단어: 해당 side (정규화 빈도)
      - norm_a / norm_b > ratio_threshold: left (norm_a)
      - norm_b / norm_a > ratio_threshold: right (norm_b)
      - 그 외 (비슷한 빈도): center ((norm_a + norm_b) / 2)
    """
    all_keys = set(a.keys()) | set(b.keys())
    left: Counter = Counter()
    center: Counter = Counter()
    right: Counter = Counter()

    for k in all_keys:
        norm_a = a.get(k, 0) / count_a
        norm_b = b.get(k, 0) / count_b

        if norm_b == 0:
            left[k] = norm_a
        elif norm_a == 0:
            right[k] = norm_b
        elif norm_a / norm_b > ratio_threshold:
            left[k] = norm_a
        elif norm_b / norm_a > ratio_threshold:
            right[k] = norm_b
        else:
            center[k] = (norm_a + norm_b) / 2

    return left, center, right
