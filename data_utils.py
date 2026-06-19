import pandas as pd


def filter_orders(df, date_range, categories, region):
    start, end = date_range
    mask = (df["订单日期"].dt.date >= start) & (df["订单日期"].dt.date <= end)
    if categories:
        mask &= df["类目"].isin(categories)
    if region != "全部":
        mask &= df["地区"] == region
    return df.loc[mask].reset_index(drop=True)


def compute_kpis(df):
    total_sales = df["销售额"].sum()
    total_orders = df["订单编号"].nunique()
    total_customers = df["用户ID"].nunique()
    avg_customer_value = total_sales / total_customers if total_customers > 0 else 0
    sku_count = df["商品名称"].nunique()
    return {
        "total_sales": float(total_sales),
        "total_orders": int(total_orders),
        "total_customers": int(total_customers),
        "avg_customer_value": float(avg_customer_value),
        "sku_count": int(sku_count),
    }


def aggregate_category_sales(df):
    return (
        df.groupby("类目")["销售额"]
        .sum()
        .reset_index()
        .sort_values("销售额", ascending=False)
    )


def aggregate_category_region_sales(df):
    return df.groupby(["类目", "地区"])["销售额"].sum().reset_index()


def aggregate_daily_sales(df):
    if df.empty:
        return pd.DataFrame(columns=["日期", "销售额"])
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
    return daily
