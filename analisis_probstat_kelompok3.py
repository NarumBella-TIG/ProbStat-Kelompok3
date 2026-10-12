# %% [markdown]
# # Analisis Deskriptif Produktivitas TBS Kelapa Sawit Berdasarkan Sistem Pemupukan, Umur Tanaman, dan Defisit Air
#
# **Projek Probabilitas dan Statistika - Kelompok 3 (3 TI F), Politeknik Caltex Riau**
#
# Anggota: Intan Lestari W (2455301223), M. Narum Bella (2455301225), Mirna (2455301226),
# Raihan Ahmada Siahaan (2455301234)
#
# Sumber data: Wiratmoko, Nugroho, & Sutiarso (2026), Zenodo,
# https://doi.org/10.5281/zenodo.22703312 (CC BY 4.0)
#
# Rumusan masalah:
# 1. Bagaimana gambaran produktivitas TBS, umur tanaman, dan defisit air klimatik pada 240 blok
#    kebun sawit tahun 2019-2025?
# 2. Bagaimana perbandingan produktivitas TBS antara blok pemupukan presisi berbasis sensor dan blok
#    pemupukan seragam, sebelum dan sesudah sensor digunakan?
# 3. Bagaimana gambaran produktivitas TBS berdasarkan kelompok umur tanaman dan tingkat defisit air?

# %% [markdown]
# ## 0. Persiapan library

# %%
import os
import urllib.request

import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)
plt.rcParams["figure.dpi"] = 110

OUT = "output"          # folder hasil grafik dan tabel
os.makedirs(OUT, exist_ok=True)


def simpan(fig, nama):
    """Simpan grafik ke folder output lalu tampilkan."""
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, nama), dpi=150)
    plt.show()


# %% [markdown]
# ## 1. Membaca dan memeriksa data
#
# Data dibaca dari folder `data/`. Kalau file tidak ada (misalnya saat dijalankan di Google Colab),
# file diunduh otomatis dari repository GitHub kelompok.

# %%
FILE = "data/3TIF_03_ProduktivitasTBSSawit.xlsx"
URL = ("https://raw.githubusercontent.com/NarumBella-TIG/ProbStat-Kelompok3/main/"
       "data/3TIF_03_ProduktivitasTBSSawit.xlsx")

if not os.path.exists(FILE):
    os.makedirs("data", exist_ok=True)
    urllib.request.urlretrieve(URL, FILE)

df = pd.read_excel(FILE, sheet_name="Dataset")
print("Ukuran data:", df.shape[0], "baris x", df.shape[1], "kolom")
df.head()

# %%
# Unit observasi = satu blok kebun pada satu tahun,
# jadi kombinasi block_id + observation_year harus unik
duplikat = df.duplicated(["block_id", "observation_year"]).sum()
print("Baris duplikat (blok + tahun):", duplikat)
print("Jumlah blok:", df["block_id"].nunique(),
      "| jumlah pasangan:", df["matched_pair_id"].nunique())
print("Tahun pengamatan:", sorted(df["observation_year"].unique().tolist()))

# %%
# Hitung data kosong (missing value) di setiap kolom
missing = df.isna().sum()
missing = missing[missing > 0]          # tampilkan hanya kolom yang ada data kosongnya

tabel_missing = pd.DataFrame({
    "jumlah kosong": missing,
    "persen (%)": (missing / len(df) * 100).round(2),
})
print("Total sel kosong:", int(df.isna().sum().sum()), "dari", df.size, "sel")
print("Kolom yang punya data kosong:", len(missing), "dari", df.shape[1])
print(tabel_missing)

# Pastikan tiga variabel utama tidak ada yang kosong
print("\nMissing pada variabel utama:")
print(df[["ffb_yield_t_ha", "palm_age_yr", "climatic_water_deficit_mm"]].isna().sum())

# %%
# Tiga variabel utama dan variabel pengelompok
Y = "ffb_yield_t_ha"                   # produktivitas TBS (ton/ha/tahun)
UMUR = "palm_age_yr"                   # umur tanaman (tahun)
DEFISIT = "climatic_water_deficit_mm"  # defisit air klimatik (mm/tahun)

UTAMA = [Y, UMUR, DEFISIT]
LABEL = {Y: "Produktivitas TBS (ton/ha/tahun)",
         UMUR: "Umur tanaman (tahun)",
         DEFISIT: "Defisit air klimatik (mm/tahun)"}
NAMA_KELOMPOK = {"control_arm": "Blok kontrol (seragam)",
                 "precision_arm": "Blok presisi (sensor)"}

# Periode: 2019-2023 semua blok dipupuk seragam; mulai 2024 blok presisi memakai sensor
df["periode"] = df["observation_year"].apply(lambda t: "2019-2023 (sebelum)" if t <= 2023
                                             else "2024-2025 (sesudah)")
print(df[UTAMA].dtypes)
print("Missing pada variabel utama:", int(df[UTAMA].isna().sum().sum()))

# %% [markdown]
# ## 2. Rumusan Masalah 1: Gambaran produktivitas TBS, umur tanaman, dan defisit air

# %%
def ringkasan(data):
    """Statistik deskriptif lengkap untuk satu kolom angka."""
    q1, q3 = data.quantile([0.25, 0.75])
    return pd.Series({
        "n": data.count(),
        "rata-rata": data.mean(),
        "median": data.median(),
        "modus": data.mode().iloc[0],
        "simpangan baku": data.std(),
        "varians": data.var(),
        "minimum": data.min(),
        "Q1": q1,
        "Q3": q3,
        "maksimum": data.max(),
        "jangkauan": data.max() - data.min(),
        "IQR": q3 - q1,
        "koef. variasi (%)": data.std() / data.mean() * 100,
        "skewness": stats.skew(data),
        "kurtosis": stats.kurtosis(data),
    })


tabel_deskriptif = pd.DataFrame({LABEL[k]: ringkasan(df[k]) for k in UTAMA}).round(2)
tabel_deskriptif.to_csv(os.path.join(OUT, "tabel1_deskriptif.csv"))
tabel_deskriptif

# %%
# Histogram ketiga variabel utama
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
for i, k in enumerate(UTAMA):
    ax[i].hist(df[k], bins=25, color="#4C72B0", edgecolor="white")
    ax[i].axvline(df[k].mean(), color="red", linestyle="--", label=f"rata-rata {df[k].mean():.2f}")
    ax[i].axvline(df[k].median(), color="green", linestyle=":",
                  label=f"median {df[k].median():.2f}")
    ax[i].set_xlabel(LABEL[k])
    ax[i].set_ylabel("Frekuensi")
    ax[i].legend(fontsize=8)
fig.suptitle("Distribusi variabel utama (n = 1.676)")
simpan(fig, "gambar1_histogram_variabel_utama.png")

# %%
# Boxplot ketiga variabel utama: melihat kuartil, median, dan pencilan (outlier)
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
for i, k in enumerate(UTAMA):
    ax[i].boxplot(df[k], showmeans=True)
    ax[i].set_xticks([])
    ax[i].set_ylabel(LABEL[k])
fig.suptitle("Boxplot variabel utama (segitiga = rata-rata, garis oranye = median)")
simpan(fig, "gambar2_boxplot_variabel_utama.png")

# %% [markdown]
# ## 3. Rumusan Masalah 2: Perbandingan blok presisi berbasis sensor dan blok seragam
#
# Setiap blok presisi dipasangkan dengan satu blok kontrol (120 pasangan). Pada 2019-2023 semua blok
# dipupuk seragam; mulai 2024 blok presisi memakai pemupukan berbasis sensor. Perbandingan dilakukan
# dengan statistik deskriptif per kelompok, sebelum dan sesudah sensor digunakan.

# %%
# Statistik deskriptif produktivitas per kelompok blok dan per periode
tabel_kelompok = (df.groupby(["periode", "assigned_group"])[Y]
                  .agg(["count", "mean", "median", "std", "min", "max"]).round(2))
tabel_kelompok.columns = ["n", "rata-rata", "median", "simpangan baku", "minimum", "maksimum"]
tabel_kelompok = tabel_kelompok.rename(index=NAMA_KELOMPOK)
tabel_kelompok.to_csv(os.path.join(OUT, "tabel2_deskriptif_per_kelompok_periode.csv"))
tabel_kelompok

# %%
# Rata-rata produktivitas per tahun untuk kedua kelompok blok (selisih dihitung sebelum dibulatkan)
per_tahun = df.pivot_table(index="observation_year", columns="assigned_group",
                           values=Y, aggfunc="mean")
per_tahun.columns = ["Blok kontrol", "Blok presisi"]
per_tahun["Selisih"] = per_tahun["Blok presisi"] - per_tahun["Blok kontrol"]
per_tahun = per_tahun.round(2)
per_tahun.to_csv(os.path.join(OUT, "tabel3_rata_rata_per_tahun.csv"))
print(per_tahun)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(per_tahun.index, per_tahun["Blok kontrol"], marker="o", label="Blok kontrol (seragam)")
ax.plot(per_tahun.index, per_tahun["Blok presisi"], marker="s",
        label="Blok presisi (sensor mulai 2024)")
ax.axvspan(2023.5, 2025.5, color="orange", alpha=0.15, label="Periode sensor digunakan")
ax.set_xlabel("Tahun")
ax.set_ylabel(LABEL[Y])
ax.set_title("Rata-rata produktivitas TBS per tahun")
ax.legend()
simpan(fig, "gambar3_tren_per_tahun.png")

# %%
# Boxplot produktivitas kedua kelompok, sebelum dan sesudah sensor digunakan
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
for i, p in enumerate(["2019-2023 (sebelum)", "2024-2025 (sesudah)"]):
    data_p = df[df["periode"] == p]
    kelompok = [data_p.loc[data_p["assigned_group"] == g, Y] for g in NAMA_KELOMPOK]
    ax[i].boxplot(kelompok, tick_labels=list(NAMA_KELOMPOK.values()), showmeans=True)
    ax[i].set_title(p)
ax[0].set_ylabel(LABEL[Y])
fig.suptitle("Produktivitas TBS per kelompok blok, sebelum dan sesudah sensor digunakan")
simpan(fig, "gambar4_boxplot_kelompok_periode.png")

# %% [markdown]
# ## 4. Rumusan Masalah 3: Produktivitas berdasarkan kelompok umur tanaman dan tingkat defisit air

# %%
# Statistik deskriptif produktivitas per kelompok umur tanaman
df["kelompok_umur"] = pd.cut(df[UMUR], bins=[4, 8, 12, 16, 20, 24],
                             labels=["5-8", "9-12", "13-16", "17-20", "21-24"])
tabel_umur = (df.groupby("kelompok_umur", observed=True)[Y]
              .agg(["count", "mean", "median", "std", "min", "max"]).round(2))
tabel_umur.columns = ["n", "rata-rata", "median", "simpangan baku", "minimum", "maksimum"]
tabel_umur.to_csv(os.path.join(OUT, "tabel4_tbs_per_kelompok_umur.csv"))
tabel_umur

# %%
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].bar(tabel_umur.index.astype(str), tabel_umur["rata-rata"], color="#4C72B0")
for x, v in zip(tabel_umur.index.astype(str), tabel_umur["rata-rata"]):
    ax[0].text(x, v + 0.3, f"{v:.2f}", ha="center")
ax[0].set_xlabel("Kelompok umur tanaman (tahun)")
ax[0].set_ylabel("Rata-rata produktivitas TBS (ton/ha)")
ax[0].set_title("Rata-rata produktivitas per kelompok umur")

kelompok = [df.loc[df["kelompok_umur"] == g, Y] for g in tabel_umur.index]
ax[1].boxplot(kelompok, tick_labels=list(tabel_umur.index.astype(str)), showmeans=True)
ax[1].set_xlabel("Kelompok umur tanaman (tahun)")
ax[1].set_ylabel(LABEL[Y])
ax[1].set_title("Sebaran produktivitas per kelompok umur")
simpan(fig, "gambar5_tbs_per_kelompok_umur.png")

# %%
# Tingkat defisit air dibagi berdasarkan kuartil: rendah (<= Q1), sedang (Q1-Q3), tinggi (> Q3)
q1_def, q3_def = df[DEFISIT].quantile([0.25, 0.75])
print(f"Q1 defisit air = {q1_def:.2f} mm | Q3 defisit air = {q3_def:.2f} mm")
df["tingkat_defisit"] = pd.cut(df[DEFISIT], bins=[-1, q1_def, q3_def, df[DEFISIT].max()],
                               labels=["Rendah", "Sedang", "Tinggi"])
tabel_defisit = (df.groupby("tingkat_defisit", observed=True)[Y]
                 .agg(["count", "mean", "median", "std", "min", "max"]).round(2))
tabel_defisit.columns = ["n", "rata-rata", "median", "simpangan baku", "minimum", "maksimum"]
tabel_defisit.to_csv(os.path.join(OUT, "tabel5_tbs_per_tingkat_defisit.csv"))
tabel_defisit

# %%
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
kelompok = [df.loc[df["tingkat_defisit"] == g, Y] for g in tabel_defisit.index]
ax[0].boxplot(kelompok, tick_labels=list(tabel_defisit.index.astype(str)), showmeans=True)
ax[0].set_xlabel("Tingkat defisit air (berdasarkan kuartil)")
ax[0].set_ylabel(LABEL[Y])
ax[0].set_title("Produktivitas TBS per tingkat defisit air")

per_tahun_def = df.groupby("observation_year")[[DEFISIT, Y]].mean().round(2)
ax[1].bar(per_tahun_def.index, per_tahun_def[DEFISIT], color="#DD8452")
ax[1].set_xlabel("Tahun")
ax[1].set_ylabel("Rata-rata defisit air (mm/tahun)")
ax[1].set_title("Rata-rata defisit air per tahun")
simpan(fig, "gambar6_tbs_per_tingkat_defisit.png")
per_tahun_def.to_csv(os.path.join(OUT, "tabel6_defisit_dan_tbs_per_tahun.csv"))
per_tahun_def

# %% [markdown]
# ## 5. Ringkasan hasil

# %%
sesudah = per_tahun.loc[[2024, 2025]]
sebelum = per_tahun.loc[2019:2023]
print("RINGKASAN HASIL ANALISIS DESKRIPTIF")
print("=" * 60)
print(f"RM1  Rata-rata produktivitas TBS {df[Y].mean():.2f} ton/ha (sd {df[Y].std():.2f}), "
      f"median {df[Y].median():.2f}, rentang {df[Y].min():.2f}-{df[Y].max():.2f}")
print(f"     Rata-rata umur tanaman {df[UMUR].mean():.1f} tahun; "
      f"defisit air rata-rata {df[DEFISIT].mean():.1f} mm, median {df[DEFISIT].median():.1f} mm")
print(f"RM2  2019-2023: selisih rata-rata per tahun presisi - kontrol antara "
      f"{sebelum['Selisih'].min():.2f} dan {sebelum['Selisih'].max():.2f} ton/ha")
print(f"     2024-2025: blok presisi lebih tinggi {sesudah['Selisih'].min():.2f}-"
      f"{sesudah['Selisih'].max():.2f} ton/ha per tahun")
terbaik = tabel_umur["rata-rata"].idxmax()
print(f"RM3  Rata-rata tertinggi pada kelompok umur {terbaik} tahun "
      f"({tabel_umur.loc[terbaik, 'rata-rata']:.2f} ton/ha)")
print(f"     Rata-rata produktivitas: "
      f"defisit rendah {tabel_defisit.loc['Rendah', 'rata-rata']:.2f}, "
      f"sedang {tabel_defisit.loc['Sedang', 'rata-rata']:.2f}, "
      f"tinggi {tabel_defisit.loc['Tinggi', 'rata-rata']:.2f} ton/ha")
print(f"\nSemua grafik dan tabel tersimpan di folder '{OUT}/'")
