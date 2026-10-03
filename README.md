# Projek Probabilitas dan Statistika - Kelompok 3 (3 TI F)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NarumBella-TIG/ProbStat-Kelompok3/blob/main/analisis_probstat_kelompok3.ipynb)

**Analisis Pengaruh Manajemen Nutrisi Presisi Berbasis Sensor terhadap Produktivitas Tandan Buah Segar (TBS) Kelapa Sawit di Kalimantan Tengah Tahun 2019-2025**

Politeknik Caltex Riau, Program Studi Teknologi Informasi.

| NIM | Nama |
| --- | --- |
| 2455301223 | Intan Lestari W |
| 2455301225 | M. Narum Bella |
| 2455301226 | Mirna |
| 2455301234 | Raihan Ahmada Siahaan |

## Rumusan masalah

1. Bagaimana gambaran produktivitas TBS, umur tanaman, dan defisit air klimatik pada 240 blok kebun sawit tahun 2019-2025?
2. Apakah terdapat perbedaan rata-rata produktivitas TBS yang signifikan antara blok pemupukan presisi berbasis sensor dan blok pemupukan seragam pada tahun 2024-2025?
3. Seberapa besar pengaruh umur tanaman dan defisit air klimatik terhadap produktivitas TBS?

## Isi repository

| File / folder | Isi |
| --- | --- |
| `analisis_probstat_kelompok3.ipynb` | Notebook analisis lengkap beserta hasilnya (bisa dibuka di Google Colab) |
| `analisis_probstat_kelompok3.py` | Kode yang sama dalam bentuk skrip Python |
| `data/3TIF_03_ProduktivitasTBSSawit.xlsx` | Dataset (lembar Dataset, Kamus_Variabel, Info_Dataset, Cek_Kelayakan) |
| `output/` | Grafik (`gambar*.png`) dan tabel hasil (`tabel*.csv`) yang dipakai di laporan |
| `requirements.txt` | Daftar library Python |

## Cara menjalankan

**Google Colab:** klik tombol *Open in Colab* di atas, lalu pilih *Runtime > Run all*. Dataset diunduh otomatis dari repository ini.

**Komputer sendiri:**

```bash
pip install -r requirements.txt
python analisis_probstat_kelompok3.py
```

Grafik dan tabel hasil akan tersimpan di folder `output/`.

## Metode

| Rumusan masalah | Analisis |
| --- | --- |
| RM 1 | Statistika deskriptif (rata-rata, median, modus, simpangan baku, kuartil, skewness, kurtosis), histogram, boxplot, tren per tahun, distribusi normal dan peluang |
| RM 2 | Uji normalitas Shapiro-Wilk pada selisih, uji t sampel berpasangan (α = 0,05), interval kepercayaan 95%, Cohen's dz, uji Wilcoxon sebagai pembanding |
| RM 3 | Korelasi Pearson, regresi linear berganda (Model 1 linear dan Model 2 dengan suku umur²), pemeriksaan residual |

## Sumber data

Wiratmoko, A., Nugroho, A. P., & Sutiarso, L. (2026). *Oil palm block-year dataset for sensor-guided variable-rate nutrient management under rainfed conditions in Central Kalimantan, Indonesia (2019-2025)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22703312

Lisensi data: CC BY 4.0. Nilai data tidak diubah; keterangan lengkap ada di lembar `Info_Dataset`.

## Penggunaan AI

Penyusunan kode analisis dibantu Claude (Anthropic). Prompt dan jawaban AI yang digunakan dilampirkan pada berkas lampiran laporan sesuai ketentuan mata kuliah. Kelompok bertanggung jawab atas kode, hasil analisis, dan kesimpulan.
