from datetime import date

import pytest

import data_utils


def test_filter_by_date_range(sample_df):
    result = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 3, 2)), [], "全部"
    )
    assert len(result) == 3
    assert result["销售额"].sum() == 450


def test_filter_by_single_date(sample_df):
    result = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 3, 1)), [], "全部"
    )
    assert len(result) == 2
    assert result["销售额"].sum() == 350


def test_filter_by_category(sample_df):
    result = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 5, 1)), ["电子产品"], "全部"
    )
    assert set(result["类目"]) == {"电子产品"}
    assert result["销售额"].sum() == 300


def test_filter_by_multiple_categories(sample_df):
    result = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 5, 1)), ["服饰", "食品"], "全部"
    )
    assert len(result) == 3
    assert result["销售额"].sum() == 510


def test_filter_by_region(sample_df):
    result = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 5, 1)), [], "华北"
    )
    assert set(result["地区"]) == {"华北"}
    assert result["销售额"].sum() == 360


def test_filter_region_all_returns_everything(sample_df):
    result = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 5, 1)), [], "全部"
    )
    assert len(result) == len(sample_df)


def test_filter_combined(sample_df):
    result = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 5, 1)), ["服饰"], "华东"
    )
    assert len(result) == 1
    assert result["销售额"].sum() == 150


def test_filter_no_match_returns_empty(sample_df):
    result = data_utils.filter_orders(
        sample_df, (date(2026, 6, 1), date(2026, 6, 30)), [], "全部"
    )
    assert len(result) == 0


def test_filter_does_not_mutate_input(sample_df):
    original_len = len(sample_df)
    data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 3, 1)), [], "全部"
    )
    assert len(sample_df) == original_len


def test_compute_kpis_basic(sample_df):
    kpis = data_utils.compute_kpis(sample_df)
    assert kpis["total_sales"] == 810
    assert kpis["total_orders"] == 5
    assert kpis["total_customers"] == 3
    assert kpis["sku_count"] == 3
    assert kpis["avg_customer_value"] == pytest.approx(270.0)


def test_compute_kpis_single_record(single_record_df):
    kpis = data_utils.compute_kpis(single_record_df)
    assert kpis["total_sales"] == 200
    assert kpis["total_orders"] == 1
    assert kpis["total_customers"] == 1
    assert kpis["sku_count"] == 1
    assert kpis["avg_customer_value"] == pytest.approx(200.0)


def test_compute_kpis_all_same_user_counts_once(all_same_user_df):
    kpis = data_utils.compute_kpis(all_same_user_df)
    assert kpis["total_orders"] == 3
    assert kpis["total_customers"] == 1
    assert kpis["avg_customer_value"] == pytest.approx(510.0)


def test_compute_kpis_empty(empty_df):
    kpis = data_utils.compute_kpis(empty_df)
    assert kpis["total_sales"] == 0.0
    assert kpis["total_orders"] == 0
    assert kpis["total_customers"] == 0
    assert kpis["sku_count"] == 0
    assert kpis["avg_customer_value"] == 0.0


def test_aggregate_category_sales(sample_df):
    result = data_utils.aggregate_category_sales(sample_df)
    assert list(result["类目"]) == ["服饰", "电子产品", "食品"]
    assert result.loc[result["类目"] == "服饰", "销售额"].iloc[0] == 350
    assert result.loc[result["类目"] == "电子产品", "销售额"].iloc[0] == 300
    assert result.loc[result["类目"] == "食品", "销售额"].iloc[0] == 160


def test_aggregate_category_sales_single_record(single_record_df):
    result = data_utils.aggregate_category_sales(single_record_df)
    assert len(result) == 1
    assert result["销售额"].iloc[0] == 200


def test_aggregate_category_sales_empty(empty_df):
    result = data_utils.aggregate_category_sales(empty_df)
    assert len(result) == 0
    assert list(result.columns) == ["类目", "销售额"]


def test_aggregate_category_region_sales(sample_df):
    result = data_utils.aggregate_category_region_sales(sample_df)
    assert len(result) == 5
    electronics_north = result[
        (result["类目"] == "电子产品") & (result["地区"] == "华北")
    ]
    assert electronics_north["销售额"].iloc[0] == 200


def test_aggregate_daily_sales(sample_df):
    result = data_utils.aggregate_daily_sales(sample_df)
    assert len(result) == 62
    assert result["销售额"].sum() == 810
    assert result["日期"].iloc[0] == "2026-03-01"
    assert result["日期"].iloc[-1] == "2026-05-01"


def test_aggregate_daily_sales_single_record(single_record_df):
    result = data_utils.aggregate_daily_sales(single_record_df)
    assert len(result) == 1
    assert result["销售额"].iloc[0] == 200


def test_aggregate_daily_sales_empty(empty_df):
    result = data_utils.aggregate_daily_sales(empty_df)
    assert len(result) == 0
    assert list(result.columns) == ["日期", "销售额"]
