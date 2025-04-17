from filters import Filter3Days, Filter5Days

def test_filter_3_days_true():
    prices = [100, 101, 102]
    assert Filter3Days.apply(prices)

def test_filter_3_days_false():
    prices = [100, 99, 101]
    assert not Filter3Days.apply(prices)

def test_filter_5_days_true():
    prices = [100, 99, 98, 99, 100]
    assert Filter5Days.apply(prices)

def test_filter_5_days_false():
    prices = [100, 99, 98, 97, 96]
    assert not Filter5Days.apply(prices)