# Classification Pneumonia with Visual Heatmap

Sistem klasifikasi deteksi dini pneumonia berbasis deep learning yang menggunakan Convolutional Neural Network (CNN) untuk menganalisis citra X-ray dada. Aplikasi ini memberikan hasil klasifikasi Normal vs Pneumonia dengan tingkat kepercayaan serta visualisasi heatmap untuk membantu interpretasi keputusan model. Dirancang untuk digunakan di rumah sakit sebagai alat skrining awal untuk meningkatkan efisiensi diagnosis dan mendeteksi pneumonia secara lebih dini.

## Fitur-fitur

- Upload dan analisis citra X-ray dada
- Klasifikasi otomatis Normal vs Pneumonia
- Visualisasi dengan CLAHE (Contrast Limited Adaptive Histogram Equalization)
- Saliency maps untuk menunjukkan area penting dalam prediksi
- Overlay visualisasi untuk interpretasi hasil
- Sistem autentikasi pengguna
- Sistem manajemen admin
- Riwayat prediksi dan feedback
- Statistik penggunaan dan akurasi

## Struktur File
```
├── app.py                 # Aplikasi utama Flask
├── db.py                  # Fungsi-fungsi database
├── env.py                 # Konfigurasi environment
├── requirements.txt       # Dependensi project
├── .env                   # Konfigurasi environment (tidak di-commit)
├── .gitignore            # File yang diabaikan oleh Git
├── modelPneumonia.h5     # Model pembelajaran mesin
├── static/               # File statis (CSS, JS, gambar)
│   ├── uploads/          # Tempat upload gambar (akan dibuat otomatis)
│   └── styles.css        # File CSS
├── templates/            # Template HTML
│   ├── admin/            # Template untuk admin
│   ├── index.html        # Halaman beranda
│   ├── predict.html      # Halaman upload dan prediksi
│   ├── result.html       # Halaman hasil prediksi
│   ├── history.html      # Halaman riwayat     
│   ├── login.html        # Halaman login       
│   ├── register.html     # Halaman registrasi  
│   └── navbar.html       # Komponen navbar     
└── README.md             # File dokumentasi ini
```

## Teknologi yang Digunakan

- **Backend**: Python, Flask
- **Machine Learning**: TensorFlow, Keras
- **Pemrosesan Gambar**: OpenCV, Pillow
- **Visualisasi**: Matplotlib
- **Database**: MySQL
- **Frontend**: HTML, CSS, Bootstrap
- **Environment**: python-dotenv

## Screenshot

Berikut adalah tampilan dari aplikasi sistem klasifikasi deteksi pneumonia:

![Tampilan Beranda](static/screenshot/user_beranda.jpeg)
![Tampilan Upload](static/screenshot/user_prediksi.jpeg)
<div style="display: flex; gap: 10px;">
  <img src="static/screenshot/normal.jpeg" alt="Hasil Prediksi Normal" width="45%">
  <img src="static/screenshot/pneumonia.jpeg" alt="Hasil Prediksi Pneumonia" width="45%">
</div>
![Tampilan Admin](static/screenshot/admin_dashboard.jpeg)

## Kontribusi

Jika Anda ingin berkontribusi:

1. Fork project ini
2. Buat branch fitur baru (`git checkout -b fitur/fitur-baru`)
3. Commit perubahan Anda (`git commit -m 'Tambah fitur baru'`)
4. Push ke branch (`git push origin fitur/fitur-baru`)
5. Buat pull request

## Akurasi Model

Berikut adalah hasil pelatihan model pada setiap epoch:

| Epochs | Model Accuracy | Val Accuracy | Loss   | Val Loss | Learning Rate |
|--------|----------------|--------------|--------|----------|---------------|
| 1      | 82.77%         | 50.00%       | 0.5785 | 5.7308   | 0.0010        |
| 2      | 91.37%         | 63.00%       | 0.2326 | 1.1354   | 0.0010        |
| 3      | 93.25%         | 86.42%       | 0.1911 | 0.3628   | 0.0010        |
| 4      | 93.76%         | 77.05%       | 0.1731 | 0.7230   | 0.0010        |
| 5      | 94.16%         | 95.90%       | 0.1552 | 0.1406   | 0.0010        |
| 6      | 95.14%         | 94.50%       | 0.1308 | 0.1256   | 0.0010        |

Model menunjukkan peningkatan akurasi yang signifikan selama proses pelatihan, dengan akurasi model sebesar 95.14% dan akurasi validasi sebesar 94.50% pada epoch terakhir.

## Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## Penulis

- Nama: [Nama Anda - akan diisi]
- Email: [Email Anda - akan diisi]