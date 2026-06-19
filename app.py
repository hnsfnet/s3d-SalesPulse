from pathlib import Path

import pandas as pd
import streamlit as st

import charts
import data_utils

st.set_page_config(page_title="电商销售数据分析仪表盘", page_icon="📊", layout="wide")

DATA_FILE = Path(__file__).parent / "orders_data.csv"


@st.cache_data
def load_data(path):
    df = pd.read_csv(path, encoding="utf-8-sig", parse_dates=["订单日期"])
    df["销售额"] = df["单价"] * df["数量"]
    return df


@st.cache_data
def apply_filters(df, date_range, categories, region):
    return data_utils.filter_orders(df, date_range, categories, region)


@st.cache_data
def compute_kpis(df):
    return data_utils.compute_kpis(df)


df_raw = load_data(DATA_FILE)


def init_session_state():
    min_date = df_raw["订单日期"].min().date()
    max_date = df_raw["订单日期"].max().date()
    all_cats = sorted(df_raw["类目"].unique().tolist())

    defaults = {
        "page": "📊 数据概览",
        "date_range": (min_date, max_date),
        "categories": all_cats,
        "region": "全部",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session_state()

all_categories = sorted(df_raw["类目"].unique().tolist())
all_regions = ["全部"] + sorted(df_raw["地区"].unique().tolist())

with st.sidebar:
    st.markdown("## 📊 电商销售分析")
    st.caption("E-Commerce Sales Dashboard")
    st.divider()

    st.radio(
        "页面导航",
        ["📊 数据概览", "📈 类目对比分析"],
        key="page",
    )

    st.divider()
    st.subheader("🔍 筛选条件")

    st.date_input(
        "订单日期范围",
        key="date_range",
        min_value=df_raw["订单日期"].min().date(),
        max_value=df_raw["订单日期"].max().date(),
    )

    st.multiselect(
        "类目（可多选）",
        options=all_categories,
        key="categories",
        placeholder="请选择类目",
    )

    st.selectbox(
        "地区",
        all_regions,
        key="region",
    )


def render_overview(data):
    st.title("📊 电商销售数据分析仪表盘")
    if len(data) == 0:
        st.warning("当前筛选条件下无数据，请调整筛选条件。")
        return
    st.markdown(
        f"共载入 **{len(data):,}** 条订单记录，"
        f"时间跨度 {data['订单日期'].min().date()} 至 {data['订单日期'].max().date()}"
    )
    st.divider()

    kpis = compute_kpis(data)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("总销售额", f"¥{kpis['total_sales']:,.0f}", key="kpi_sales")
    with k2:
        st.metric("总订单数", f"{kpis['total_orders']:,}", key="kpi_orders")
    with k3:
        st.metric("客单价（按用户）", f"¥{kpis['avg_customer_value']:,.0f}", key="kpi_aov")
    with k4:
        st.metric("有销量商品数", f"{kpis['sku_count']:,}", key="kpi_sku")

    st.divider()

    st.subheader("📈 每日销售额趋势")
    st.plotly_chart(
        charts.make_daily_sales_line(data),
        use_container_width=True,
        key="overview_line_chart",
    )

    st.divider()

    st.subheader("🧩 各类目销售额占比")
    st.plotly_chart(
        charts.make_category_sales_pie(data),
        use_container_width=True,
        key="overview_pie_chart",
    )


def render_category_comparison(data):
    st.title("📈 类目对比分析")
    if len(data) == 0:
        st.warning("当前筛选条件下无数据，请调整筛选条件。")
        return
    st.markdown(
        f"当前筛选条件：**{len(data):,}** 条订单，"
        f"日期 {data['订单日期'].min().date()} ~ {data['订单日期'].max().date()}"
    )
    st.divider()

    st.subheader("🏷️ 各类目销售额对比")
    st.plotly_chart(
        charts.make_category_sales_bar(data),
        use_container_width=True,
        key="cat_bar_chart",
    )

    st.divider()

    st.subheader("🌍 各地区类目销售分布（堆叠）")
    st.plotly_chart(
        charts.make_category_region_stacked_bar(data),
        use_container_width=True,
        key="cat_stacked_chart",
    )


filtered_df = apply_filters(
    df_raw,
    st.session_state["date_range"],
    st.session_state["categories"],
    st.session_state["region"],
)

if st.session_state["page"] == "📊 数据概览":
    render_overview(filtered_df)
else:
    render_category_comparison(filtered_df)
