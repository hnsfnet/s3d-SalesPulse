from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="电商销售数据分析仪表盘", page_icon="📊", layout="wide")

DATA_FILE = Path(__file__).parent / "orders_data.csv"


@st.cache_data
def load_data(path):
    df = pd.read_csv(path, encoding="utf-8-sig", parse_dates=["订单日期"])
    df["销售额"] = df["单价"] * df["数量"]
    return df


df_raw = load_data(DATA_FILE)


def init_session_state():
    min_date = df_raw["订单日期"].min().date()
    max_date = df_raw["订单日期"].max().date()
    all_cats = sorted(df_raw["类目"].unique().tolist())
    all_regions = ["全部"] + sorted(df_raw["地区"].unique().tolist())

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
        options=sorted(df_raw["类目"].unique().tolist()),
        key="categories",
        placeholder="请选择类目",
    )

    st.selectbox(
        "地区",
        ["全部"] + sorted(df_raw["地区"].unique().tolist()),
        key="region",
    )


def apply_filters(df):
    start, end = st.session_state["date_range"]
    mask = (df["订单日期"].dt.date >= start) & (df["订单日期"].dt.date <= end)
    if st.session_state["categories"]:
        mask &= df["类目"].isin(st.session_state["categories"])
    if st.session_state["region"] != "全部":
        mask &= df["地区"] == st.session_state["region"]
    return df.loc[mask].reset_index(drop=True)


df = apply_filters(df_raw)


def render_overview():
    st.title("📊 电商销售数据分析仪表盘")
    st.markdown(
        f"共载入 **{len(df):,}** 条订单记录，"
        f"时间跨度 {df['订单日期'].min().date()} 至 {df['订单日期'].max().date()}"
        if len(df) > 0
        else "⚠️ 当前筛选条件下无数据，请调整筛选条件。"
    )
    if len(df) == 0:
        return
    st.divider()

    total_sales = df["销售额"].sum()
    total_orders = df["订单编号"].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    sku_count = df["商品名称"].nunique()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("总销售额", f"¥{total_sales:,.0f}")
    with k2:
        st.metric("总订单数", f"{total_orders:,}")
    with k3:
        st.metric("客单价", f"¥{avg_order_value:,.0f}")
    with k4:
        st.metric("有销量商品数", f"{sku_count:,}")

    st.divider()

    st.subheader("📈 每日销售额趋势")
    full_range = pd.date_range(
        df["订单日期"].min().normalize(),
        df["订单日期"].max().normalize(),
        freq="D",
    )
    daily = (
        df.groupby(df["订单日期"].dt.normalize())["销售额"]
        .sum()
        .reindex(full_range, fill_value=0)
        .reset_index()
    )
    daily.columns = ["日期", "销售额"]
    daily["日期"] = daily["日期"].dt.strftime("%Y-%m-%d")

    fig_line = px.line(
        daily,
        x="日期",
        y="销售额",
        markers=True,
        template="plotly_white",
    )
    fig_line.update_traces(
        line_color="#2563eb",
        hovertemplate="日期： %{x}<br>销售额： ¥%{y:,.0f}<extra></extra>",
    )
    fig_line.update_layout(
        xaxis_title="日期",
        yaxis_title="销售额（元）",
        hovermode="x unified",
        height=440,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    st.subheader("🧩 各类目销售额占比")
    cat_sales = (
        df.groupby("类目")["销售额"].sum().reset_index().sort_values("销售额", ascending=False)
    )
    fig_pie = px.pie(
        cat_sales,
        names="类目",
        values="销售额",
        hole=0.4,
        template="plotly_white",
    )
    fig_pie.update_traces(
        textposition="inside",
        textinfo="label+percent",
        hovertemplate="类目： %{label}<br>销售额： ¥%{value:,.0f}<br>占比： %{percent}<extra></extra>",
    )
    fig_pie.update_layout(
        height=440,
        legend_title="类目",
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_pie, use_container_width=True)


def render_category_comparison():
    st.title("📈 类目对比分析")
    if len(df) == 0:
        st.warning("当前筛选条件下无数据，请调整筛选条件。")
        return
    st.markdown(
        f"当前筛选条件：**{len(df):,}** 条订单，"
        f"日期 {df['订单日期'].min().date()} ~ {df['订单日期'].max().date()}"
    )
    st.divider()

    st.subheader("🏷️ 各类目销售额对比")
    cat_sales = (
        df.groupby("类目")["销售额"].sum().reset_index().sort_values("销售额", ascending=False)
    )
    fig_bar = px.bar(
        cat_sales,
        x="类目",
        y="销售额",
        text_auto=".2s",
        template="plotly_white",
        color="销售额",
        color_continuous_scale="Blues",
    )
    fig_bar.update_traces(
        hovertemplate="类目： %{x}<br>销售额： ¥%{y:,.0f}<extra></extra>",
    )
    fig_bar.update_layout(
        xaxis_title="类目",
        yaxis_title="销售额（元）",
        height=440,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    st.subheader("🌍 各地区类目销售分布（堆叠）")
    cat_region_sales = (
        df.groupby(["类目", "地区"])["销售额"].sum().reset_index()
    )
    cat_order = cat_sales["类目"].tolist()
    fig_stacked = px.bar(
        cat_region_sales,
        x="类目",
        y="销售额",
        color="地区",
        template="plotly_white",
        category_orders={"类目": cat_order},
    )
    fig_stacked.update_traces(
        hovertemplate="类目： %{x}<br>地区： %{color}<br>销售额： ¥%{y:,.0f}<extra></extra>",
    )
    fig_stacked.update_layout(
        xaxis_title="类目",
        yaxis_title="销售额（元）",
        barmode="stack",
        height=440,
        legend_title="地区",
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_stacked, use_container_width=True)


if st.session_state["page"] == "📊 数据概览":
    render_overview()
else:
    render_category_comparison()
