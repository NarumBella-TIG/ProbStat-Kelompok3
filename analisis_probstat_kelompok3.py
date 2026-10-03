# %% [markdown]
# # Analisis Pengaruh Manajemen Nutrisi Presisi Berbasis Sensor terhadap Produktivitas TBS Kelapa Sawit
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
# 2. Apakah terdapat perbedaan rata-rata produktivitas TBS yang signifikan antara blok pemupukan
#    presisi berbasis sensor dan blok pemupukan seragam pada tahun 2024-2025?
# 3. Seberapa besar pengaruh umur tanaman dan defisit air klimatik terhadap produktivitas TBS?

# %% [markdown]
# ## 0. Persiapan library

# %%
import os
import urllib.request

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.formula.api as smf

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)
plt.rcParams["figure.dpi"] = 110

ALPHA = 0.05            # taraf signifikansi untuk semua uji
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

# Missing value per kolom (hanya kolom yang ada data kosongnya)
missing = df.isna().sum()
print("\nMissing value:")
print(missing[missing > 0])

# %%
# Tiga variabel utama dan satu variabel pengelompok
Y = "ffb_yield_t_ha"                 # produktivitas TBS (ton/ha/tahun)
UMUR = "palm_age_yr"                 # umur tanaman (tahun)
DEFISIT = "climatic_water_deficit_mm"  # defisit air klimatik (mm/tahun)
SISTEM = "management_system"         # sistem pemupukan

UTAMA = [Y, UMUR, DEFISIT]
LABEL = {Y: "Produktivitas TBS (ton/ha/tahun)",
         UMUR: "Umur tanaman (tahun)",
         DEFISIT: "Defisit air klimatik (mm/tahun)"}
NAMA_SISTEM = {"sensor_guided_variable_rate": "Presisi berbasis sensor",
               "uniform_standard": "Seragam (standar)"}

print(df[UTAMA].dtypes)
print("Missing pada variabel utama:", int(df[UTAMA].isna().sum().sum()))

# %% [markdown]
# ## 2. Rumusan Masalah 1: Statistika deskriptif

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
# Rata-rata produktivitas per tahun untuk kedua kelompok blok.
# 2019-2023 semua blok masih dipupuk seragam; 2024-2025 blok precision_arm memakai sensor.
per_tahun = df.pivot_table(index="observation_year", columns="assigned_group",
                           values=Y, aggfunc="mean").round(2)
per_tahun.columns = ["Blok kontrol", "Blok presisi"]
per_tahun["Selisih"] = (per_tahun["Blok presisi"] - per_tahun["Blok kontrol"]).round(2)
per_tahun.to_csv(os.path.join(OUT, "tabel2_rata_rata_per_tahun.csv"))
print(per_tahun)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(per_tahun.index, per_tahun["Blok kontrol"], marker="o", label="Blok kontrol (seragam)")
ax.plot(per_tahun.index, per_tahun["Blok presisi"], marker="s",
        label="Blok presisi (sensor mulai 2024)")
ax.axvspan(2023.5, 2025.5, color="orange", alpha=0.15, label="Periode perlakuan sensor")
ax.set_xlabel("Tahun")
ax.set_ylabel(LABEL[Y])
ax.set_title("Rata-rata produktivitas TBS per tahun")
ax.legend()
simpan(fig, "gambar2_tren_per_tahun.png")

# %%
# Boxplot produktivitas per sistem pemupukan pada periode perlakuan (2024-2025)
perlakuan = df[df["observation_year"] >= 2024]
kelompok = [perlakuan.loc[perlakuan[SISTEM] == s, Y] for s in NAMA_SISTEM]

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.boxplot(kelompok, tick_labels=list(NAMA_SISTEM.values()), showmeans=True)
ax.set_ylabel(LABEL[Y])
ax.set_title("Produktivitas TBS per sistem pemupukan, 2024-2025")
simpan(fig, "gambar3_boxplot_sistem_pemupukan.png")

tabel_sistem = perlakuan.groupby(SISTEM)[Y].apply(ringkasan).unstack().round(2)
tabel_sistem.index = [NAMA_SISTEM[i] for i in tabel_sistem.index]
tabel_sistem.to_csv(os.path.join(OUT, "tabel3_deskriptif_per_sistem.csv"))
tabel_sistem

# %% [markdown]
# ## 3. Distribusi probabilitas produktivitas TBS
#
# Produktivitas TBS adalah variabel kontinu, sehingga didekati dengan distribusi normal.
# Kecocokannya diperiksa dengan Q-Q plot, lalu dipakai untuk menghitung peluang.

# %%
mu, sigma = df[Y].mean(), df[Y].std()
x = np.linspace(df[Y].min(), df[Y].max(), 200)

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].hist(df[Y], bins=30, density=True, color="#4C72B0", edgecolor="white", label="Data")
ax[0].plot(x, stats.norm.pdf(x, mu, sigma), "r-", lw=2, label=f"Normal(μ={mu:.2f}, σ={sigma:.2f})")
ax[0].set_xlabel(LABEL[Y])
ax[0].set_ylabel("Kepadatan")
ax[0].legend()
stats.probplot(df[Y], dist="norm", plot=ax[1])
ax[1].set_title("Q-Q plot terhadap distribusi normal")
simpan(fig, "gambar4_distribusi_normal_tbs.png")

# %%
# Peluang dihitung dua cara: dari model normal dan dari proporsi data sebenarnya (empiris)
batas_atas, batas_bawah = 28, 20
peluang = pd.DataFrame({
    "Model normal": [1 - stats.norm.cdf(batas_atas, mu, sigma),
                     stats.norm.cdf(batas_bawah, mu, sigma),
                     stats.norm.cdf(batas_atas, mu, sigma)
                     - stats.norm.cdf(batas_bawah, mu, sigma)],
    "Empiris (data)": [(df[Y] > batas_atas).mean(),
                       (df[Y] < batas_bawah).mean(),
                       df[Y].between(batas_bawah, batas_atas).mean()],
}, index=[f"P(TBS > {batas_atas})", f"P(TBS < {batas_bawah})",
          f"P({batas_bawah} ≤ TBS ≤ {batas_atas})"]).round(4)
peluang.to_csv(os.path.join(OUT, "tabel4_peluang_normal.csv"))
print("Skewness:", round(stats.skew(df[Y]), 3), "| Kurtosis:", round(stats.kurtosis(df[Y]), 3))
peluang

# %% [markdown]
# ## 4. Rumusan Masalah 2: Uji beda produktivitas blok presisi vs blok seragam
#
# Setiap blok presisi sudah dipasangkan dengan satu blok kontrol (120 pasangan),
# sehingga uji yang dipakai
# adalah **uji t sampel berpasangan** pada periode perlakuan 2024-2025.
#
# - H0: rata-rata selisih produktivitas (presisi - seragam) = 0
# - H1: rata-rata selisih produktivitas ≠ 0
# - α = 0,05

# %%
def data_berpasangan(data):
    """Satu baris per pasangan per tahun, kolom = produktivitas blok presisi dan blok kontrol."""
    p = data.pivot_table(index=["matched_pair_id", "observation_year"],
                         columns="assigned_group", values=Y).dropna()
    return p["precision_arm"], p["control_arm"]


presisi, kontrol = data_berpasangan(perlakuan)
selisih = presisi - kontrol
n = len(selisih)
print("Jumlah pasangan-tahun:", n)
print(f"Rata-rata selisih: {selisih.mean():.3f} ton/ha | "
      f"simpangan baku selisih: {selisih.std():.3f}")
print("Pasangan yang blok presisinya lebih tinggi:", int((selisih > 0).sum()), "dari", n)

# %%
# Syarat uji t berpasangan: selisih berdistribusi normal (uji Shapiro-Wilk)
sw = stats.shapiro(selisih)
print(f"Shapiro-Wilk selisih: W = {sw.statistic:.4f}, p = {sw.pvalue:.4f}")
print("Kesimpulan:",
      "selisih berdistribusi normal" if sw.pvalue > ALPHA else "selisih tidak normal")

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.hist(selisih, bins=25, color="#55A868", edgecolor="white")
ax.axvline(0, color="black", lw=1)
ax.axvline(selisih.mean(), color="red", linestyle="--",
           label=f"rata-rata selisih {selisih.mean():.2f}")
ax.set_xlabel("Selisih produktivitas presisi - seragam (ton/ha)")
ax.set_ylabel("Frekuensi")
ax.set_title("Distribusi selisih per pasangan blok, 2024-2025")
ax.legend()
simpan(fig, "gambar5_histogram_selisih_pasangan.png")

# %%
uji_t = stats.ttest_rel(presisi, kontrol)
ci = stats.t.interval(1 - ALPHA, df=n - 1, loc=selisih.mean(), scale=stats.sem(selisih))
cohen_dz = selisih.mean() / selisih.std()
wilcoxon = stats.wilcoxon(selisih)  # uji nonparametrik sebagai pembanding

print(f"Uji t berpasangan: t({n - 1}) = {uji_t.statistic:.3f}, p = {uji_t.pvalue:.3e}")
print(f"Interval kepercayaan 95% rata-rata selisih: {ci[0]:.3f} sampai {ci[1]:.3f} ton/ha")
print(f"Ukuran efek Cohen's dz: {cohen_dz:.3f}")
print(f"Wilcoxon signed-rank: W = {wilcoxon.statistic:.1f}, p = {wilcoxon.pvalue:.3e}")
print("Keputusan:",
      "H0 ditolak, ada perbedaan signifikan" if uji_t.pvalue < ALPHA else "H0 diterima")

# %%
# Pemeriksaan pembanding: sebelum perlakuan (2019-2023) kedua kelompok seharusnya tidak berbeda.
# Uji yang sama juga diulang per tahun.
hasil_uji = []
periode = {"2019-2023 (sebelum)": df[df["observation_year"] <= 2023],
           "2024-2025 (perlakuan)": perlakuan,
           "2024": df[df["observation_year"] == 2024],
           "2025": df[df["observation_year"] == 2025]}
for nama, data in periode.items():
    a, b = data_berpasangan(data)
    t = stats.ttest_rel(a, b)
    hasil_uji.append({"Periode": nama, "n pasangan": len(a), "rata-rata presisi": a.mean(),
                      "rata-rata kontrol": b.mean(), "rata-rata selisih": (a - b).mean(),
                      "t": t.statistic, "p-value": t.pvalue,
                      "keputusan": "signifikan" if t.pvalue < ALPHA else "tidak signifikan"})
tabel_uji = pd.DataFrame(hasil_uji).round(4)
tabel_uji.to_csv(os.path.join(OUT, "tabel5_uji_t_berpasangan.csv"), index=False)
tabel_uji

# %% [markdown]
# ## 5. Rumusan Masalah 3: Pengaruh umur tanaman dan defisit air terhadap produktivitas
#
# Langkah: korelasi Pearson, lalu regresi linear berganda. Karena hubungan umur dengan produktivitas
# diduga melengkung, dibuat dua model:
#
# - Model 1: TBS = b0 + b1·umur + b2·defisit
# - Model 2: TBS = b0 + b1·umur + b2·umur² + b3·defisit

# %%
hasil_korelasi = []
for k in [UMUR, DEFISIT]:
    r, p = stats.pearsonr(df[k], df[Y])
    hasil_korelasi.append({"Variabel": LABEL[k], "r Pearson": r, "p-value": p,
                           "keputusan": "signifikan" if p < ALPHA else "tidak signifikan"})
tabel_korelasi = pd.DataFrame(hasil_korelasi).round(4)
tabel_korelasi.to_csv(os.path.join(OUT, "tabel6_korelasi.csv"), index=False)
tabel_korelasi

# %%
# Rata-rata produktivitas per kelompok umur, untuk melihat bentuk hubungannya
df["kelompok_umur"] = pd.cut(df[UMUR], bins=[4, 8, 12, 16, 20, 24],
                             labels=["5-8", "9-12", "13-16", "17-20", "21-24"])
tabel_umur = df.groupby("kelompok_umur", observed=True)[Y].agg(["count", "mean", "std"]).round(2)
tabel_umur.columns = ["n", "rata-rata TBS", "simpangan baku"]
tabel_umur.to_csv(os.path.join(OUT, "tabel7_tbs_per_kelompok_umur.csv"))
tabel_umur

# %%
model1 = smf.ols(f"{Y} ~ {UMUR} + {DEFISIT}", data=df).fit()
model2 = smf.ols(f"{Y} ~ {UMUR} + I({UMUR}**2) + {DEFISIT}", data=df).fit()
print(model1.summary())

# %%
print(model2.summary())

# %%
perbandingan = pd.DataFrame({
    "Model 1 (linear)": [model1.rsquared, model1.rsquared_adj, model1.fvalue,
                         model1.f_pvalue, model1.aic],
    "Model 2 (+ umur²)": [model2.rsquared, model2.rsquared_adj, model2.fvalue,
                          model2.f_pvalue, model2.aic],
}, index=["R²", "R² disesuaikan", "F", "p-value F", "AIC"]).round(4)
perbandingan.to_csv(os.path.join(OUT, "tabel8_perbandingan_model.csv"))

koef = pd.DataFrame({"koefisien": model2.params, "p-value": model2.pvalues}).round(5)
koef.to_csv(os.path.join(OUT, "tabel9_koefisien_model2.csv"))
umur_puncak = -model2.params[UMUR] / (2 * model2.params[f"I({UMUR} ** 2)"])
print(f"Umur dengan produktivitas tertinggi menurut Model 2: {umur_puncak:.1f} tahun")
print(koef)
perbandingan

# %%
# Scatter plot dan garis/kurva hasil regresi
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))

ax[0].scatter(df[UMUR], df[Y], alpha=0.25, s=12)
u = np.linspace(df[UMUR].min(), df[UMUR].max(), 100)
d_rata = df[DEFISIT].mean()
ax[0].plot(u, model1.predict(pd.DataFrame({UMUR: u, DEFISIT: d_rata})), "r--",
           label="Model 1 (linear)")
ax[0].plot(u, model2.predict(pd.DataFrame({UMUR: u, DEFISIT: d_rata})), "g-", lw=2,
           label="Model 2 (kuadratik)")
ax[0].set_xlabel(LABEL[UMUR])
ax[0].set_ylabel(LABEL[Y])
ax[0].set_title("Umur tanaman vs produktivitas")
ax[0].legend()

ax[1].scatter(df[DEFISIT], df[Y], alpha=0.25, s=12, color="#DD8452")
m, b = np.polyfit(df[DEFISIT], df[Y], 1)
dd = np.linspace(df[DEFISIT].min(), df[DEFISIT].max(), 100)
ax[1].plot(dd, m * dd + b, "r--", label=f"garis tren (kemiringan {m:.4f})")
ax[1].set_xlabel(LABEL[DEFISIT])
ax[1].set_ylabel(LABEL[Y])
ax[1].set_title("Defisit air vs produktivitas")
ax[1].legend()
simpan(fig, "gambar6_scatter_regresi.png")

# %%
# Pemeriksaan asumsi regresi Model 2: sisaan (residual) menyebar acak dan mendekati normal
residual = model2.resid
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].scatter(model2.fittedvalues, residual, alpha=0.25, s=12)
ax[0].axhline(0, color="red", lw=1)
ax[0].set_xlabel("Nilai prediksi (ton/ha)")
ax[0].set_ylabel("Residual")
ax[0].set_title("Residual vs nilai prediksi")
stats.probplot(residual, dist="norm", plot=ax[1])
ax[1].set_title("Q-Q plot residual Model 2")
simpan(fig, "gambar7_asumsi_residual.png")

# %% [markdown]
# ## 6. Ringkasan hasil

# %%
print("RINGKASAN HASIL ANALISIS")
print("=" * 60)
print(f"RM1  Rata-rata produktivitas TBS {df[Y].mean():.2f} ton/ha (sd {df[Y].std():.2f}), "
      f"rentang {df[Y].min():.2f}-{df[Y].max():.2f}")
print(f"     Rata-rata umur tanaman {df[UMUR].mean():.1f} tahun, "
      f"defisit air {df[DEFISIT].mean():.1f} mm/tahun")
print(f"RM2  Selisih rata-rata presisi - seragam (2024-2025): {selisih.mean():.2f} ton/ha, "
      f"t = {uji_t.statistic:.2f}, p = {uji_t.pvalue:.2e} -> "
      f"{'signifikan' if uji_t.pvalue < ALPHA else 'tidak signifikan'}")
sebelum = tabel_uji.iloc[0]
print(f"     Sebelum perlakuan (2019-2023): selisih {sebelum['rata-rata selisih']:.2f}, "
      f"p = {sebelum['p-value']:.3f} "
      f"-> {sebelum['keputusan']}")
print(f"RM3  Model 1 R² = {model1.rsquared:.3f}; Model 2 (dengan umur²) R² = {model2.rsquared:.3f}")
print(f"     Produktivitas tertinggi pada umur sekitar {umur_puncak:.1f} tahun; "
      f"koefisien defisit air = {model2.params[DEFISIT]:.4f} ton/ha per mm")
print(f"\nSemua grafik dan tabel tersimpan di folder '{OUT}/'")
