import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

import data_utils

_BASE_LAYOUT = dict(
    height=440,
    margin=dict(l=10, r=10, t=20, b=10),
    template="plotly_white",
)


def make_daily_sales_line(df: pd.DataFrame, line_color: str = "#2563eb") -> Figure:
    daily = data_utils.aggregate_daily_sales(df)
    fig = px.line(daily, x="日期", y="销售额", markers=True, template="plotly_white")
    fig.update_traces(
        line_color=line_color,
        hovertemplate="日期： %{x}<br>销售额： ¥%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        **_BASE_LAYOUT,
        xaxis_title="日期",
        yaxis_title="销售额（元）",
        hovermode="x unified",
    )
    return fig


def make_category_sales_pie(df: pd.DataFrame) -> Figure:
    cat_sales = data_utils.aggregate_category_sales(df)
    fig = px.pie(
        cat_sales,
        names="类目",
        values="销售额",
        hole=0.4,
        template="plotly_white",
    )
    fig.update_traces(
        textposition="inside",
        textinfo="label+percent",
        hovertemplate="类目： %{label}<br>销售额： ¥%{value:,.0f}<br>占比： %{percent}<extra></extra>",
    )
    fig.update_layout(**_BASE_LAYOUT, legend_title="类目")
    return fig


def make_category_sales_bar(df: pd.DataFrame) -> Figure:
    cat_sales = data_utils.aggregate_category_sales(df)
    fig = px.bar(
        cat_sales,
        x="类目",
        y="销售额",
        text_auto=".2s",
        template="plotly_white",
        color="销售额",
        color_continuous_scale="Blues",
    )
    fig.update_traces(
        hovertemplate="类目： %{x}<br>销售额： ¥%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        **_BASE_LAYOUT,
        xaxis_title="类目",
        yaxis_title="销售额（元）",
        coloraxis_showscale=False,
    )
    return fig


def make_category_region_stacked_bar(df: pd.DataFrame) -> Figure:
    cat_sales = data_utils.aggregate_category_sales(df)
    cat_order = cat_sales["类目"].tolist()
    cat_region_sales = data_utils.aggregate_category_region_sales(df)
    fig = px.bar(
        cat_region_sales,
        x="类目",
        y="销售额",
        color="地区",
        template="plotly_white",
        category_orders={"类目": cat_order},
    )
    fig.update_traces(
        hovertemplate="类目： %{x}<br>地区： %{color}<br>销售额： ¥%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        **_BASE_LAYOUT,
        xaxis_title="类目",
        yaxis_title="销售额（元）",
        barmode="stack",
        legend_title="地区",
    )
    return fig
