from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Konfigurasi dan lokasi file
st.set_page_config(
    page_title="Bike Sharing Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

DASHBOARD_DIR = Path(__file__).resolve().parent
PROJECT_DIR = DASHBOARD_DIR.parent
DAILY_FILE = DASHBOARD_DIR / "main_data.csv"
HOURLY_FILE = PROJECT_DIR / "data" / "data_2.csv"

SEASON_LABELS = {
    1: "Spring",
    2: "Summer",
    3: "Fall",
    4: "Winter",
}
WEATHER_LABELS = {
    1: "Cerah / sedikit awan",
    2: "Berkabut / berawan",
    3: "Hujan atau salju ringan",
    4: "Hujan lebat / salju / kabut",
}
WORKINGDAY_LABELS = {0: "Bukan hari kerja", 1: "Hari kerja"}


@st.cache_data(show_spinner="Memuat dataset Bike Sharing...")
def load_data(
    daily_path: str,
    hourly_path: str,
    daily_file_signature: tuple[int, int],
    hourly_file_signature: tuple[int, int],
):
    """Memuat data dan mengikat cache ke versi fisik kedua file CSV.

    Signature berisi waktu modifikasi (nanodetik) dan ukuran file. Nilainya
    menjadi bagian dari cache key sehingga perubahan isi CSV memicu pembacaan ulang.
    """
    daily = pd.read_csv(daily_path, parse_dates=["dteday"])
    hourly = pd.read_csv(hourly_path, parse_dates=["dteday"])

    for frame in (daily, hourly):
        frame["year"] = frame["yr"].map({0: 2011, 1: 2012}).astype("Int64")
        frame["season_label"] = frame["season"].map(SEASON_LABELS)
        frame["weather_label"] = frame["weathersit"].map(WEATHER_LABELS)
        frame["workingday_label"] = frame["workingday"].map(WORKINGDAY_LABELS)
        frame["month_name"] = frame["dteday"].dt.strftime("%B")

    return daily, hourly


st.title("Bike Sharing Analytics Dashboard")
st.caption(
    "Eksplorasi pola penyewaan sepeda Capital Bikeshare, Washington, D.C. "
    "Periode data: 1 Januari 2011–31 Desember 2012."
)

# Pastikan file proyek tersedia dan tampilkan pesan yang dapat ditindaklanjuti.
missing_files = [str(path) for path in (DAILY_FILE, HOURLY_FILE) if not path.exists()]
if missing_files:
    st.error(
        "Dataset belum ditemukan. Pastikan struktur folder submission tidak diubah. "
        "File yang dibutuhkan: " + ", ".join(missing_files)
    )
    st.stop()

try:
    daily_stat = DAILY_FILE.stat()
    hourly_stat = HOURLY_FILE.stat()
    day_df, hour_df = load_data(
        str(DAILY_FILE),
        str(HOURLY_FILE),
        (daily_stat.st_mtime_ns, daily_stat.st_size),
        (hourly_stat.st_mtime_ns, hourly_stat.st_size),
    )
except Exception as error:  # noqa: BLE001 - tampilkan penyebab yang membantu pengguna
    st.exception(error)
    st.stop()


# Filter interaktif
st.sidebar.header("Filter Analisis")
year_options = sorted(day_df["year"].dropna().unique().tolist())
month_options = list(range(1, 13))
season_options = [SEASON_LABELS[key] for key in sorted(SEASON_LABELS)]
weather_options = [WEATHER_LABELS[key] for key in sorted(WEATHER_LABELS) if key in day_df["weathersit"].unique()]
day_type_options = list(WORKINGDAY_LABELS.values())

selected_years = st.sidebar.multiselect("Tahun", year_options, default=year_options)
selected_months = st.sidebar.multiselect("Bulan", month_options, default=month_options)
selected_seasons = st.sidebar.multiselect("Musim", season_options, default=season_options)
selected_weather = st.sidebar.multiselect("Kondisi cuaca (analisis harian)", weather_options, default=weather_options)
selected_day_types = st.sidebar.multiselect("Jenis hari", day_type_options, default=day_type_options)


def apply_common_filters(frame: pd.DataFrame, filter_weather: bool = True) -> pd.DataFrame:
    result = frame.copy()
    if selected_years:
        result = result[result["year"].isin(selected_years)]
    else:
        result = result.iloc[0:0]
    if selected_months:
        result = result[result["mnth"].isin(selected_months)]
    else:
        result = result.iloc[0:0]
    if selected_seasons:
        result = result[result["season_label"].isin(selected_seasons)]
    else:
        result = result.iloc[0:0]
    if filter_weather:
        if selected_weather:
            result = result[result["weather_label"].isin(selected_weather)]
        else:
            result = result.iloc[0:0]
    if selected_day_types:
        result = result[result["workingday_label"].isin(selected_day_types)]
    else:
        result = result.iloc[0:0]
    return result


day_filtered = apply_common_filters(day_df, filter_weather=True)
# Cuaca difilter pada analisis harian. Analisis pola jam mempertahankan seluruh
# kondisi cuaca agar weathersit=4 yang hanya muncul pada data per jam tidak hilang.
hour_filtered = apply_common_filters(hour_df, filter_weather=False)

if day_filtered.empty or hour_filtered.empty:
    st.warning("Tidak ada data untuk kombinasi filter tersebut. Silakan pilih kembali filter di sisi kiri.")
    st.stop()

# KPI utama
total_rentals = int(day_filtered["cnt"].sum())
average_daily = float(day_filtered["cnt"].mean())
registered_share = float(day_filtered["registered"].sum() / day_filtered["cnt"].sum() * 100)
casual_share = float(day_filtered["casual"].sum() / day_filtered["cnt"].sum() * 100)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total penyewaan", f"{total_rentals:,.0f}")
kpi2.metric("Rata-rata penyewaan / hari", f"{average_daily:,.0f}")
kpi3.metric("Pengguna terdaftar", f"{registered_share:.1f}%")
kpi4.metric("Pengguna casual", f"{casual_share:.1f}%")
st.caption(
    f"Filter aktif: {len(day_filtered):,} hari dan {len(hour_filtered):,} catatan per jam. "
    "Filter cuaca diterapkan pada ringkasan harian; pola per jam mencakup semua kondisi cuaca. "
    "Data per jam yang tidak tercatat tidak dianggap sebagai penyewaan nol."
)

# Tab dashboard
tab_overview, tab_hourly, tab_context, tab_advanced = st.tabs(
    ["Ringkasan", "Pola per Jam", "Musim & Cuaca", "Analisis Lanjutan"]
)

with tab_overview:
    st.subheader("Tren Penyewaan Sepeda")
    monthly = (
        day_filtered.assign(year_month=day_filtered["dteday"].dt.to_period("M").astype(str))
        .groupby("year_month", as_index=False)
        .agg(total_rentals=("cnt", "sum"), average_daily_rentals=("cnt", "mean"), days=("cnt", "size"))
    )
    fig_month = px.line(
        monthly,
        x="year_month",
        y="total_rentals",
        markers=True,
        title="Total Penyewaan per Bulan",
        labels={"year_month": "Bulan", "total_rentals": "Total penyewaan"},
    )
    fig_month.update_layout(hovermode="x unified", margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig_month, use_container_width=True)

    user_mix = pd.DataFrame(
        {
            "Tipe pengguna": ["Casual", "Registered"],
            "Total penyewaan": [day_filtered["casual"].sum(), day_filtered["registered"].sum()],
        }
    )
    fig_mix = px.pie(
        user_mix,
        names="Tipe pengguna",
        values="Total penyewaan",
        hole=0.45,
        title="Komposisi Penyewaan Menurut Tipe Pengguna",
    )
    st.plotly_chart(fig_mix, use_container_width=True)

with tab_hourly:
    st.subheader("Perbedaan Pola Penyewaan per Jam")
    hourly_pattern = (
        hour_filtered.groupby(["workingday_label", "hr"], as_index=False)
        .agg(avg_rentals=("cnt", "mean"), observations=("cnt", "size"))
    )
    fig_hour = px.line(
        hourly_pattern,
        x="hr",
        y="avg_rentals",
        color="workingday_label",
        markers=True,
        title="Rata-rata Penyewaan per Jam: Hari Kerja vs Bukan Hari Kerja",
        labels={
            "hr": "Jam",
            "avg_rentals": "Rata-rata penyewaan per jam",
            "workingday_label": "Jenis hari",
        },
    )
    fig_hour.update_xaxes(dtick=1)
    fig_hour.update_layout(hovermode="x unified", margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig_hour, use_container_width=True)

    if not hourly_pattern.empty:
        peak_indices = hourly_pattern.groupby("workingday_label")["avg_rentals"].idxmax()
        peak_table = hourly_pattern.loc[peak_indices].sort_values("workingday_label").copy()
        peak_table["jam_puncak"] = peak_table["hr"].map(lambda hour: f"{int(hour):02d}:00")
        peak_table = peak_table.rename(
            columns={
                "workingday_label": "Jenis hari",
                "avg_rentals": "Rata-rata penyewaan",
                "observations": "Jumlah catatan per jam",
            }
        )
        st.markdown("**Jam dengan rata-rata permintaan tertinggi pada filter aktif**")
        st.dataframe(
            peak_table[["Jenis hari", "jam_puncak", "Rata-rata penyewaan", "Jumlah catatan per jam"]],
            use_container_width=True,
            hide_index=True,
        )

with tab_context:
    st.subheader("Permintaan Berdasarkan Musim dan Cuaca")
    season_summary = (
        day_filtered.groupby("season_label", as_index=False)
        .agg(avg_rentals=("cnt", "mean"), days=("cnt", "size"))
        .sort_values("avg_rentals", ascending=False)
    )
    weather_summary = (
        day_filtered.groupby("weather_label", as_index=False)
        .agg(avg_rentals=("cnt", "mean"), days=("cnt", "size"))
        .sort_values("avg_rentals", ascending=False)
    )
    left, right = st.columns(2)
    with left:
        fig_season = px.bar(
            season_summary,
            x="season_label",
            y="avg_rentals",
            text_auto=".0f",
            title="Rata-rata Penyewaan Harian per Musim",
            labels={"season_label": "Musim", "avg_rentals": "Rata-rata penyewaan / hari"},
        )
        fig_season.update_layout(xaxis_tickangle=-20, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig_season, use_container_width=True)
    with right:
        fig_weather = px.bar(
            weather_summary,
            x="weather_label",
            y="avg_rentals",
            text_auto=".0f",
            title="Rata-rata Penyewaan Harian per Kondisi Cuaca",
            labels={"weather_label": "Kondisi cuaca", "avg_rentals": "Rata-rata penyewaan / hari"},
        )
        fig_weather.update_layout(xaxis_tickangle=-25, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig_weather, use_container_width=True)

    st.caption(
        "Nama musim dan kondisi cuaca ditampilkan secara konsisten tanpa kode angka. "
        "Kategori yang tidak memiliki observasi pada data harian tidak ditampilkan."
    )
    with st.expander("Lihat tabel ringkasan kategori"):
        st.markdown("**Musim**")
        st.dataframe(season_summary, use_container_width=True, hide_index=True)
        st.markdown("**Cuaca**")
        st.dataframe(weather_summary, use_container_width=True, hide_index=True)

with tab_advanced:
    st.subheader("Analisis Lanjutan: Manual Grouping dan Binning")
    st.markdown(
        "Analisis ini menggunakan pengelompokan berbasis aturan dan kuantil, "
        "bukan algoritma machine learning. Batas kategori dihitung ulang mengikuti filter aktif."
    )

    # Manual grouping berdasarkan rentang waktu.
    period_bins = [-1, 5, 10, 15, 19, 23]
    period_labels = ["Dini hari (00–05)", "Pagi (06–10)", "Siang (11–15)", "Sore (16–19)", "Malam (20–23)"]
    grouped_hour = hour_filtered.copy()
    grouped_hour["time_period"] = pd.cut(
        grouped_hour["hr"], bins=period_bins, labels=period_labels, include_lowest=True
    )
    period_summary = (
        grouped_hour.groupby(["workingday_label", "time_period"], observed=False, as_index=False)
        .agg(avg_rentals=("cnt", "mean"), observations=("cnt", "size"))
    )
    fig_period = px.bar(
        period_summary,
        x="time_period",
        y="avg_rentals",
        color="workingday_label",
        barmode="group",
        title="Rata-rata Penyewaan Menurut Kelompok Waktu",
        labels={
            "time_period": "Kelompok waktu",
            "avg_rentals": "Rata-rata penyewaan per jam",
            "workingday_label": "Jenis hari",
        },
    )
    fig_period.update_layout(xaxis_tickangle=-15, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig_period, use_container_width=True)

    # Binning jumlah penyewaan harian menjadi tiga kelompok kuantil.
    binned_daily = day_filtered.copy()
    if binned_daily["cnt"].nunique() >= 3:
        binned_daily["demand_level"] = pd.qcut(
            binned_daily["cnt"].rank(method="first"),
            q=3,
            labels=["Rendah", "Sedang", "Tinggi"],
        )
        demand_summary = (
            binned_daily.groupby("demand_level", observed=False, as_index=False)
            .agg(days=("cnt", "size"), avg_rentals=("cnt", "mean"), median_rentals=("cnt", "median"))
        )
        fig_demand = px.bar(
            demand_summary,
            x="demand_level",
            y="days",
            color="demand_level",
            text="days",
            title="Jumlah Hari pada Setiap Tingkat Permintaan (Binning Tercile)",
            labels={"demand_level": "Tingkat permintaan", "days": "Jumlah hari"},
        )
        st.plotly_chart(fig_demand, use_container_width=True)
        st.dataframe(demand_summary, use_container_width=True, hide_index=True)
    else:
        st.info("Binning tidak dapat ditampilkan karena variasi jumlah penyewaan pada filter terlalu sedikit.")

st.divider()
st.caption(
    "Sumber: Bike Sharing Dataset, Capital Bikeshare (2011–2012). "
    "Analisis bersifat deskriptif; perbedaan rata-rata tidak membuktikan sebab-akibat."
)
