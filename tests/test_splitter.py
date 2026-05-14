from collections import Counter

import pytest

from dual_wordcloud._splitter import split_for_comparison


def test_left_only_word():
    """B에 없는 단어는 left에 배치된다."""
    a = Counter({"대출": 10})
    b = Counter()
    left, center, right = split_for_comparison(a, b, count_a=100, count_b=100)
    assert "대출" in left
    assert "대출" not in center
    assert "대출" not in right


def test_right_only_word():
    """A에 없는 단어는 right에 배치된다."""
    a = Counter()
    b = Counter({"금리": 10})
    left, center, right = split_for_comparison(a, b, count_a=100, count_b=100)
    assert "금리" in right
    assert "금리" not in left
    assert "금리" not in center


def test_similar_frequency_goes_center():
    """두 Counter에서 비슷한 빈도의 단어는 center에 배치된다."""
    a = Counter({"대출": 10})
    b = Counter({"대출": 10})
    left, center, right = split_for_comparison(a, b, count_a=100, count_b=100)
    assert "대출" in center


def test_dominant_a_goes_left():
    """A의 정규화 빈도가 ratio_threshold 초과 시 left에 배치된다."""
    a = Counter({"대출": 21})
    b = Counter({"대출": 10})
    left, center, right = split_for_comparison(
        a, b, count_a=100, count_b=100, ratio_threshold=2.0
    )
    assert "대출" in left


def test_dominant_b_goes_right():
    """B의 정규화 빈도가 ratio_threshold 초과 시 right에 배치된다."""
    a = Counter({"대출": 10})
    b = Counter({"대출": 21})
    left, center, right = split_for_comparison(
        a, b, count_a=100, count_b=100, ratio_threshold=2.0
    )
    assert "대출" in right


def test_normalization_by_article_count():
    """기사 수로 정규화: A 절대 수치가 크더라도 정규화 후 비슷하면 center에 배치된다."""
    a = Counter({"대출": 20})  # count_a=200 → norm=0.1
    b = Counter({"대출": 10})  # count_b=100 → norm=0.1
    left, center, right = split_for_comparison(
        a, b, count_a=200, count_b=100, ratio_threshold=2.0
    )
    assert "대출" in center
