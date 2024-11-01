# Program Chat UDP dengan Transfer File

Proyek ini menyediakan server dan client chat berbasis UDP dengan dukungan transfer file. Pengguna dapat berkomunikasi secara real-time, dan file yang dikirim oleh pengguna akan disimpan di folder khusus di server.

## Anggota Kelompok

- Filbert Fuvian | 18222024
- Ananda Farhan R | 182220

## Spesifikasi Utama
- Server mampu menerima pesan yang dikirim client dan mencetaknya ke layar. ✅
- Server mampu meneruskan pesan satu client ke client lain. ✅
- Client mampu mengirimkan pesan ke server dengan IP dan port yang ditentukan pengguna. ✅
- Client mampu menerima pesan dari client lain (yang diteruskan oleh server), dan mencetaknya ke layar. ✅
- Client harus memasukkan password untuk dapat bergabung ke chatroom. ✅
- Client memiliki username yang unik. ✅


## Spesifikasi Opsional
- Aplikasi mengimplementasikan TCP over UDP. ✅
- Seluruh pesan dienkripsi menggunakan algoritma kriptografi klasik simetris cipher Caesar. ✅
- Aplikasi mampu digunakan untuk mengirimkan dan menerima pesan bertipe file biner. ✅
- Aplikasi mampu menunjukkan apabila integritas pesan telah rusak, baik dengan memanfaatkan checksum ✅
- Aplikasi mampu menyimpan pesan-pesan lampau meskipun telah ditutup; mekanisme dan tempat penyimpanan bebas, baik di client maupun di server. ✅
- Aplikasi mampu mengotentikasi pengguna. ✅
- Aplikasi diprogram menggunakan paradigma object oriented programming atau pemrograman berorientasi objek ✅
- Aplikasi memiliki GUI. ✅

<br>
<br>

# Cara Menjalankan Program

## Kebutuhan

- Python 3.x
- Library yang diperlukan: `socket`, `threading`, `binascii`, `tkinter` (untuk GUI client)

## Persiapan

1. Clone atau unduh repository ini ke komputer Anda.
2. Pastikan Python 3.x sudah terinstall.

## Struktur Program

- **server.py**: Menjalankan server chat UDP, mengelola koneksi client, pesan, dan transfer file.
- **client.py**: Menjalankan client chat UDP dengan antarmuka grafis untuk mengirim pesan dan file.

## Petunjuk Penggunaan

### Menjalankan Server

1. Buka terminal.
2. Arahkan ke direktori main.
3. Jalankan perintah berikut untuk memulai server:

   ```bash
   python server.py

### Menjalankan Client

1. Buka terminal.
2. Arahkan ke direktori main.
3. Jalankan perintah berikut untuk memulai server:

   ```bash
   python client.py

4. Menghubungkan ke Server:

- Client akan meminta IP server, port, password, dan username.
- Masukkan alamat IP server dan nomor port (default: 127.0.0.1 dan 12345).
- Masukkan password yang telah dikonfigurasi di server.
- Pilih username yang unik.

5. Mengirim Pesan:

- Ketik pesan di kotak input pada bagian bawah GUI client dan tekan tombol Send.
- Pesan akan muncul di area chat, dan client lain yang terhubung akan menerima pesan tersebut.

6. Mengirim File:

- Klik tombol Send File untuk membuka dialog file.
- Pilih file yang ingin dikirim. Server akan menyimpan file tersebut di folder received_files, dan semua client lain yang terhubung akan menerima notifikasi bahwa ada file yang diterima.