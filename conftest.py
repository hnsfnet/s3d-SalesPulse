import pandas as pd
import pytest

COLUMNS = [
    "订单编号",
    "订单日期",
    "商品名称",
    "类目",
    "地区",
    "单价",
    "数量",
    "用户ID",
]


def _build(rows):
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["订单日期"] = pd.to_datetime(df["订单日期"])
    df["单价"] = df["单价"].astype(int)
    df["数量"] = df["数量"].astype(int)
    df["销售额"] = df["单价"] * df["数量"]
    return df


@pytest.fixture
def sample_df():
    return _build(
        [
            ("OD001", "2026-03-01", "蓝牙耳机", "电子产品", "华北", 100, 2, "U001"),
            ("OD002", "2026-03-01", "男士T恤", "服饰", "华东", 50, 3, "U002"),
            ("OD003", "2026-03-02", "蓝牙耳机", "电子产品", "华南", 100, 1, "U001"),
            ("OD004", "2026-04-01", "坚果礼盒", "食品", "华北", 80, 2, "U003"),
            ("OD005", "2026-05-01", "男士T恤", "服饰", "华西", 50, 4, "U002"),
        ]
    )


@pytest.fixture
def single_record_df():
    return _build(
        [("OD001", "2026-03-01", "蓝牙耳机", "电子产品", "华北", 100, 2, "U001")]
    )


@pytest.fixture
def all_same_user_df():
    return _build(
        [
            ("OD001", "2026-03-01", "蓝牙耳机", "电子产品", "华北", 100, 2, "U001"),
            ("OD002", "2026-03-02", "男士T恤", "服饰", "华东", 50, 3, "U001"),
            ("OD003", "2026-03-03", "坚果礼盒", "食品", "华南", 80, 2, "U001"),
        ]
    )


@pytest.fixture
def empty_df():
    df = pd.DataFrame(columns=COLUMNS + ["销售额"])
    df["订单日期"] = pd.to_datetime(df["订单日期"])
    df["单价"] = df["单价"].astype(int)
    df["数量"] = df["数量"].astype(int)
    return df
