from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="电商销售数据分析仪表盘", page_icon="📊", layout="wide")

with st.sidebar:
    st.markdown("## 📊 电商销售分析")
    st.caption("E-Commerce Sales Dashboard")

DATA_FILE = Path(__file__).parent / "orders_data.csv"


@st.cache_data
def load_data(path):
    df = pd.read_csv(path, encoding="utf-8-sig", parse_dates=["订单日期"])
    df["销售额"] = df["单价"] * df["数量"]
    return df


df = load_data(DATA_FILE)

st.title("📊 电商销售数据分析仪表盘")
st.markdown(
    f"共载入 **{len(df):,}** 条订单记录，"
    f"时间跨度 {df['订单日期'].min().date()} 至 {df['订单日期'].max().date()}"
)
st.divider()

total_sales = df["销售额"].sum()
total_orders = df["订单编号"].nunique()
avg_order_value = total_sales / total_orders
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
