# Projek Probabilitas dan Statistika - Kelompok 3 (3 TI F)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NarumBella-TIG/ProbStat-Kelompok3/blob/main/analisis_probstat_kelompok3.ipynb)

**Analisis Deskriptif Produktivitas Tandan Buah Segar (TBS) Kelapa Sawit Berdasarkan Sistem Pemupukan, Umur Tanaman, dan Defisit Air di Kalimantan Tengah Tahun 2019-2025**

Politeknik Caltex Riau, Program Studi Teknik Informatika.

| NIM | Nama |
| --- | --- |
| 2455301223 | Intan Lestari W |
| 2455301225 | M. Narum Bella |
| 2455301226 | Mirna |
| 2455301234 | Raihan Ahmada Siahaan |

## Rumusan masalah

1. Bagaimana gambaran produktivitas TBS, umur tanaman, dan defisit air klimatik pada 240 blok kebun sawit tahun 2019-2025?
2. Bagaimana perbandingan produktivitas TBS antara blok pemupukan presisi berbasis sensor dan blok pemupukan seragam, sebelum dan sesudah sensor digunakan?
3. Bagaimana gambaran produktivitas TBS berdasarkan kelompok umur tanaman dan tingkat defisit air?

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

## Metode (statistika deskriptif)

| Rumusan masalah | Analisis |
| --- | --- |
| RM 1 | Ukuran pemusatan (rata-rata, median, modus), penyebaran (jangkauan, varians, simpangan baku, koefisien variasi), letak (kuartil, IQR), dan bentuk (skewness, kurtosis); histogram dan boxplot |
| RM 2 | Statistik deskriptif produktivitas per kelompok blok (presisi dan kontrol) dan per periode (2019-2023 dan 2024-2025), rata-rata per tahun, grafik tren, boxplot |
| RM 3 | Statistik deskriptif produktivitas per kelompok umur tanaman dan per tingkat defisit air (rendah, sedang, tinggi berdasarkan kuartil), diagram batang, boxplot |

## Variabel

| Variabel | Kolom | Jenis data |
| --- | --- | --- |
| Produktivitas TBS (ton/ha/tahun) | `ffb_yield_t_ha` | Numerik (rasio) |
| Umur tanaman (tahun) | `palm_age_yr` | Numerik (rasio) |
| Defisit air klimatik (mm/tahun) | `climatic_water_deficit_mm` | Numerik (rasio) |
| Kelompok blok | `assigned_group` | Kategorik (nominal) |
| Periode | dari `observation_year` | Kategorik (ordinal) |
| Kelompok umur | dari `palm_age_yr` | Kategorik (ordinal) |
| Tingkat defisit air | dari kuartil `climatic_water_deficit_mm` | Kategorik (ordinal) |

## Sumber data

Wiratmoko, A., Nugroho, A. P., & Sutiarso, L. (2026). *Oil palm block-year dataset for sensor-guided variable-rate nutrient management under rainfed conditions in Central Kalimantan, Indonesia (2019-2025)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22703312

Lisensi data: CC BY 4.0. Nilai data tidak diubah; keterangan lengkap ada di lembar `Info_Dataset`.

## Penggunaan AI

Penyusunan kode analisis dibantu Claude (Anthropic). Prompt dan jawaban AI yang digunakan dilampirkan pada berkas lampiran laporan sesuai ketentuan mata kuliah. Kelompok bertanggung jawab atas kode, hasil analisis, dan kesimpulan.
