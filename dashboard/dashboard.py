import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    layout="wide"
)

# ======================================================
# DATA PREPARATION HELPERS
# ======================================================

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    df["year"] = df["dteday"].dt.year
    df["month"] = df["dteday"].dt.month
    return df


def filter_by_date(df, start_date, end_date):
    return df[
        (df["dteday"] >= pd.to_datetime(start_date)) &
        (df["dteday"] <= pd.to_datetime(end_date))
    ]


def create_monthly_trends(df, years=[2011, 2012]):
    df_filtered = df[df["year"].isin(years)]

    monthly = (
        df_filtered
        .groupby(["year", "month"])
        .agg(total_rentals=("cnt", "sum"))
        .reset_index()
    )

    pivot = monthly.pivot(
        index="month",
        columns="year",
        values="total_rentals"
    )

    month_names = [
        pd.to_datetime(str(m), format="%m").strftime("%b")
        for m in pivot.index
    ]

    return pivot, month_names


def create_total_per_year(df):
    return (
        df.groupby("year")
        .agg(total_rentals=("cnt", "sum"))
        .reset_index()
    )


# ======================================================
# PLOT HELPERS
# ======================================================

def plot_monthly_and_yearly(monthly_pivot, month_names, total_per_year):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for year in monthly_pivot.columns:
        axes[0].plot(
            monthly_pivot.index,
            monthly_pivot[year],
            marker="o",
            label=str(year)
        )

    axes[0].set_xticks(monthly_pivot.index)
    axes[0].set_xticklabels(month_names)
    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("Total Rentals")
    axes[0].set_title("Monthly Bike Rentals: 2011 vs 2012")
    axes[0].legend()
    axes[0].grid(True)

    sns.barplot(
        x="year",
        y="total_rentals",
        data=total_per_year,
        ax=axes[1],
        legend=False
    )

    axes[1].set_title("Total Bike Rentals per Year")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Total Rentals")
    axes[1].ticklabel_format(style="plain", axis="y")

    for p in axes[1].patches:
        axes[1].annotate(
            f"{int(p.get_height()):,}",
            (p.get_x() + p.get_width()/2, p.get_height()),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    return fig


def plot_weather_correlation(df):
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))

    corr = df[["temp", "hum", "windspeed", "cnt"]].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=axes[0, 0])
    axes[0, 0].set_title("Korelasi Cuaca vs Jumlah Sewa")

    sns.regplot(x="temp", y="cnt", data=df, ax=axes[0, 1])
    axes[0, 1].set_title("Temperature vs Rentals")

    sns.regplot(x="hum", y="cnt", data=df, ax=axes[1, 0])
    axes[1, 0].set_title("Humidity vs Rentals")

    sns.regplot(x="windspeed", y="cnt", data=df, ax=axes[1, 1])
    axes[1, 1].set_title("Windspeed vs Rentals")

    plt.tight_layout()
    return fig


# ======================================================
# MAIN APP
# ======================================================

day_df = load_data("day.csv")

# Sidebar (FIXED DATE PICKER)
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    st.image(
        "https://github.com/dicodingacademy/assets/raw/main/logo.png",
        width=180
    )

    st.subheader("Filter Tanggal")

    start_date = st.date_input(
        "Tanggal Mulai",
        min_value=min_date,
        max_value=max_date,
        value=min_date
    )

    end_date = st.date_input(
        "Tanggal Akhir",
        min_value=start_date,
        max_value=max_date,
        value=max_date
    )

main_df = filter_by_date(day_df, start_date, end_date)

# Aggregation
monthly_pivot, month_names = create_monthly_trends(main_df)
total_per_year = create_total_per_year(main_df)

# Dashboard
st.title("🚲 Bike Sharing Dashboard")

st.subheader("📈 Tren Bulanan & Tahunan")
st.pyplot(
    plot_monthly_and_yearly(
        monthly_pivot,
        month_names,
        total_per_year
    )
)

st.subheader("🌦️ Pengaruh Cuaca terhadap Penyewaan")
st.pyplot(plot_weather_correlation(main_df))