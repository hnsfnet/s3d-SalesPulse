from datetime import date

import pytest

import charts
import data_utils


def test_date_range_filter_updates_kpis_and_chart_source(sample_df):
    full_kpis = data_utils.compute_kpis(sample_df)

    filtered = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 3, 2)), [], "全部"
    )
    filtered_kpis = data_utils.compute_kpis(filtered)

    assert full_kpis["total_sales"] == 810
    assert filtered_kpis["total_sales"] == 450
    assert filtered_kpis["total_orders"] == 3

    line_fig = charts.make_daily_sales_line(filtered)
    assert list(line_fig.data[0].x) == ["2026-03-01", "2026-03-02"]
    assert list(line_fig.data[0].y) == [350, 100]


def test_category_filter_updates_pie_and_bar(sample_df):
    filtered = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 5, 1)), ["电子产品"], "全部"
    )
    assert data_utils.compute_kpis(filtered)["total_sales"] == 300

    pie_fig = charts.make_category_sales_pie(filtered)
    assert list(pie_fig.data[0].labels) == ["电子产品"]
    assert list(pie_fig.data[0].values) == [300]

    bar_fig = charts.make_category_sales_bar(filtered)
    assert list(bar_fig.data[0].x) == ["电子产品"]
    assert list(bar_fig.data[0].y) == [300]


def test_region_filter_updates_kpis_and_stacked_chart(sample_df):
    filtered = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 5, 1)), [], "华北"
    )
    kpis = data_utils.compute_kpis(filtered)
    assert kpis["total_sales"] == 360
    assert kpis["total_customers"] == 2

    stacked_fig = charts.make_category_region_stacked_bar(filtered)
    regions = {trace.name for trace in stacked_fig.data}
    assert regions == {"华北"}


def test_aov_after_filter_uses_filtered_users(sample_df):
    full_kpis = data_utils.compute_kpis(sample_df)
    assert full_kpis["avg_customer_value"] == pytest.approx(270.0)

    filtered = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 5, 1)), [], "华北"
    )
    filtered_kpis = data_utils.compute_kpis(filtered)

    assert filtered["用户ID"].nunique() == 2
    assert filtered_kpis["total_customers"] == 2
    assert filtered_kpis["total_sales"] == 360
    assert filtered_kpis["avg_customer_value"] == pytest.approx(180.0)


def test_filter_chain_then_render_all_charts(sample_df):
    filtered = data_utils.filter_orders(
        sample_df, (date(2026, 3, 1), date(2026, 5, 1)), ["服饰", "电子产品"], "华东"
    )

    pie_fig = charts.make_category_sales_pie(filtered)
    assert set(pie_fig.data[0].labels) == {"服饰"}

    bar_fig = charts.make_category_sales_bar(filtered)
    assert set(bar_fig.data[0].x) == {"服饰"}

    line_fig = charts.make_daily_sales_line(filtered)
    assert line_fig.data[0].y[-1] == 150
