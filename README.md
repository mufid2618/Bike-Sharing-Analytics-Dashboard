# Proyek Analisis Data — Bike Sharing Dataset

Proyek ini menganalisis pola penyewaan sepeda Capital Bikeshare di Washington, D.C., Amerika Serikat, selama 2011–2012. Proyek terdiri dari notebook analisis dan dashboard interaktif berbasis Streamlit.

## Struktur direktori

```text
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   ├── data_1.csv
│   └── data_2.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Dataset

| File | Isi | Jumlah baris |
|---|---|---:|
| `data/data_1.csv` | Data penyewaan harian (asal: `day.csv`) | 731 |
| `data/data_2.csv` | Data penyewaan per jam (asal: `hour.csv`) | 17.379 |
| `dashboard/main_data.csv` | Salinan data harian dengan kolom label pendukung untuk dashboard | 731 |

`data_1.csv` dan `data_2.csv` adalah salinan file sumber yang disediakan untuk proyek. `main_data.csv` berisi data harian beserta kolom label bantu (`season_label`, `weather_label`, `workingday_label`, `year`, dan `year_month`) untuk KPI, tren harian, dan ringkasan musim/cuaca dalam dashboard; data per jam dibaca dari `data/data_2.csv`.

### Pertanyaan bisnis

1. Bagaimana perbedaan rata-rata jumlah penyewaan sepeda pada setiap jam antara hari kerja dan hari bukan hari kerja selama 1 Januari 2011–31 Desember 2012, dan pada jam berapa permintaan rata-rata mencapai puncaknya untuk masing-masing jenis hari?
2. Bagaimana perbedaan rata-rata jumlah penyewaan sepeda harian berdasarkan kategori musim (`season`) dan kondisi cuaca (`weathersit`) selama 1 Januari 2011–31 Desember 2012, serta kategori mana yang memiliki rata-rata penyewaan tertinggi dan terendah?

Notebook mencakup SMART Questions, Gathering Data, Assessing Data, Cleaning Data, EDA, visualisasi, explanatory analysis, analisis lanjutan dengan manual grouping dan binning, serta kesimpulan dan rekomendasi.

## Persyaratan

- Python 3.10 atau lebih baru direkomendasikan.
- `pip` untuk memasang dependency.

## Menjalankan notebook

1. Buka `notebook.ipynb` melalui Jupyter Notebook, JupyterLab, atau Google Colab.
2. Pastikan folder `data/` berada sejajar dengan notebook dan berisi `data_1.csv` serta `data_2.csv`.
3. Jalankan seluruh cell dari atas ke bawah.

Notebook memiliki fallback upload untuk Google Colab jika file belum ditemukan. Untuk eksekusi lokal dari root proyek, notebook membaca file dari folder `data/`.

## Menjalankan dashboard secara lokal

Buka terminal pada folder `submission/`, lalu jalankan:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run dashboard/dashboard.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run dashboard/dashboard.py
```

Setelah Streamlit berjalan, buka alamat lokal yang ditampilkan di terminal (umumnya `http://localhost:8501`). Jangan memindahkan `dashboard.py` secara terpisah dari folder `dashboard/`, karena aplikasi menggunakan path relatif terhadap struktur proyek.

## Fitur dashboard

- Filter tahun, bulan, musim, kondisi cuaca, dan jenis hari.
- KPI total penyewaan, rata-rata penyewaan harian, serta komposisi pengguna casual dan registered.
- Tren total penyewaan per bulan.
- Perbandingan rata-rata penyewaan per jam pada hari kerja dan bukan hari kerja, termasuk tabel jam puncak.
- Perbandingan rata-rata penyewaan menurut musim dan kondisi cuaca.
- Analisis lanjutan dengan manual grouping periode waktu dan binning permintaan harian.

## Catatan kualitas dan batasan data

- Data harian berisi 731 observasi dan data per jam berisi 17.379 observasi.
- Dataset sumber tidak menunjukkan missing value atau baris duplikat pada pemeriksaan awal.
- `dteday` dikonversi menjadi tipe tanggal saat analisis.
- Ada tanggal pada `hour.csv` yang memiliki kurang dari 24 catatan jam. Slot yang tidak ada tidak diperlakukan sebagai penyewaan nol.
- Outlier yang ditandai dengan aturan IQR tidak otomatis dihapus karena dapat mencerminkan variasi permintaan yang nyata.
- Label kategori musim dan cuaca mengikuti pemetaan pada `Readme.txt` dataset. Gunakan kode kategori dan definisi sumber secara konsisten; label tidak ditafsirkan ulang sebagai definisi meteorologis independen.
- Analisis bersifat deskriptif dan tidak membuktikan hubungan sebab-akibat.

## Sumber dataset dan sitasi

Dataset disusun oleh Hadi Fanaee-T dari Laboratory of Artificial Intelligence and Decision Support (LIAAD), University of Porto. Deskripsi sumber menyatakan bahwa data berasal dari sistem Capital Bikeshare, Washington, D.C., untuk tahun 2011 dan 2012.

Publikasi terkait dataset:

Fanaee-T, H., & Gama, J. (2013). *Event labeling combining ensemble detectors and background knowledge*. Progress in Artificial Intelligence. DOI: [10.1007/s13748-013-0040-3](https://doi.org/10.1007/s13748-013-0040-3).


