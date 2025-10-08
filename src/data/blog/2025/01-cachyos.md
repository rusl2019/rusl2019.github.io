---
title: "Things to Do After Installing CachyOS"
description: "A step-by-step guide on what to configure, optimize, and install after setting up CachyOS for the first time."
pubDatetime: 2025-10-08T09:00:00Z
modDatetime:
author: "Muhammad Ruslan Novianto"
slug: "things-to-do-after-installing-cachyos"
featured: false
draft: false
tags:
  - "Linux"
  - "CachyOS"
  - "Post-installation"
  - "System Optimization"
ogImage: ""
canonicalURL: ""
---

# CachyOS (Arch Linux)

Panduan ini memberikan langkah-langkah untuk memperbarui sistem CachyOS dan menginstal berbagai perangkat lunak, termasuk AUR helper, aplikasi Flatpak, Visual Studio Code, Docker, dan lainnya. Pastikan Anda memiliki koneksi internet yang stabil sebelum memulai.

---

## 1. Prasyarat
Sebelum memulai, pastikan Anda memiliki hak akses root atau sudo dan sistem CachyOS sudah terinstal. Jalankan perintah berikut untuk memastikan sistem dalam keadaan baik:

```bash
sudo pacman -Syy
```

---

## 2. Memperbarui Sistem
Perbarui semua paket yang terinstal ke versi terbaru untuk memastikan kompatibilitas dan keamanan.

```bash
sudo pacman -Syu --noconfirm
```

**Catatan**: Opsi `--noconfirm` digunakan untuk menghindari konfirmasi manual. Gunakan dengan hati-hati, karena ini akan menyetujui semua pembaruan tanpa tinjauan.

---

## 3. Menginstal `yay` (AUR Helper)
`yay` adalah alat bantu untuk mengelola paket dari Arch User Repository (AUR). Langkah-langkah berikut akan menginstal `yay`:

```bash
# Instal dependensi yang diperlukan
sudo pacman -S --needed --noconfirm git base-devel

# Kloning repositori yay
git clone https://aur.archlinux.org/yay.git || { echo "Gagal mengkloning repositori yay"; exit 1; }

# Masuk ke direktori yay
cd yay

# Bangun dan instal paket
makepkg -si --noconfirm || { echo "Gagal menginstal yay"; exit 1; }

# Bersihkan direktori sementara
cd ..
rm -rf yay
```

**Catatan**: Pastikan Anda memiliki cukup ruang disk dan izin yang tepat. Jika terjadi kegagalan, periksa pesan kesalahan untuk detail lebih lanjut.

---

## 4. Menginstal `ghostty`
`ghostty` adalah emulator terminal modern. Instal dengan perintah berikut:

```bash
yay -S --noconfirm ghostty
```

**Catatan**: Pastikan `ghostty` tersedia di AUR atau repositori resmi. Jika tidak tersedia, periksa nama paket atau gunakan alternatif seperti `alacritty`.

---

## 5. Menginstal Flatpak dan Aplikasi
Flatpak memungkinkan instalasi aplikasi lintas distribusi. Langkah-langkah berikut menginstal Flatpak dan beberapa aplikasi populer:

```bash
# Instal Flatpak
sudo pacman -S --noconfirm flatpak

# Tambahkan repositori Flathub
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Instal aplikasi dari Flathub
flatpak install --noninteractive flathub io.github.zen_browser.zen
flatpak install --noninteractive flathub com.spotify.Client
flatpak install --noninteractive flathub com.wps.Office
```

**Catatan**: Pastikan nama aplikasi Flatpak benar (misalnya, `io.github.zen_browser.zen` untuk Zen Browser). Opsi `--noninteractive` digunakan untuk instalasi tanpa konfirmasi.

---

## 6. Menginstal Visual Studio Code
Instal Visual Studio Code dari AUR menggunakan `yay`:

```bash
yay -S --noconfirm visual-studio-code-bin
```

**Catatan**: Paket `visual-studio-code-bin` adalah versi biner yang sudah dikompilasi. Jika Anda lebih suka membangun dari sumber, gunakan `visual-studio-code`.

---

## 7. Menginstal GitHub CLI
GitHub CLI (`gh`) memungkinkan Anda mengelola repositori GitHub dari terminal. Instal dengan perintah berikut:

```bash
sudo pacman -S --noconfirm github-cli
```

**Catatan**: Setelah instalasi, jalankan `gh auth login` untuk mengonfigurasi autentikasi dengan akun GitHub Anda.

---

## 8. Menginstal dan Mengonfigurasi Docker
Docker digunakan untuk menjalankan aplikasi dalam kontainer. Langkah-langkah berikut menginstal dan mengonfigurasi Docker:

```bash
# Instal Docker dan Docker Compose
sudo pacman -S --noconfirm docker docker-compose

# Buat grup docker jika belum ada
getent group docker || sudo groupadd docker

# Tambahkan pengguna saat ini ke grup docker
sudo usermod -aG docker $USER

# Aktifkan dan jalankan layanan Docker
sudo systemctl enable --now docker.service
sudo systemctl enable --now containerd.service
```

**Catatan**: Anda mungkin perlu logout dan login kembali agar perubahan grup berlaku. Verifikasi instalasi dengan `docker --version` dan `docker compose version`.

---

## 9. Menginstal Fisher dan nvm.fish (Khusus Fish Shell)
Fisher adalah manajer plugin untuk Fish shell, dan `nvm.fish` digunakan untuk mengelola versi Node.js. Langkah-langkahnya:

```bash
# Instal Fisher
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher

# Instal nvm.fish
fisher install jorgebucaran/nvm.fish

# Instal Node.js LTS
nvm install lts

# Tetapkan versi default Node.js
set --universal nvm_default_version lts
```

**Catatan**: Pastikan Anda menggunakan Fish shell (`fish`) sebelum menjalankan perintah ini. Verifikasi instalasi dengan `node --version`.

---

## 10. Menginstal XAMPP
XAMPP adalah tumpukan solusi untuk pengembangan web (Apache, MySQL, PHP, Perl). Instal dengan langkah-langkah berikut:

```bash
# Instal dependensi yang diperlukan
sudo pacman -S --needed --noconfirm libxcrypt libxcrypt-compat

# Unduh installer XAMPP
wget https://sourceforge.net/projects/xampp/files/XAMPP%20Linux/7.4.33/xampp-linux-x64-7.4.33-0-installer.run -O xampp-installer.run

# Berikan izin eksekusi
chmod +x xampp-installer.run

# Jalankan installer
sudo ./xampp-installer.run

# Bersihkan file installer
rm xampp-installer.run
```

**Catatan**: XAMPP akan diinstal di `/opt/lampp`. Untuk menjalankan XAMPP, gunakan `sudo /opt/lampp/lampp start`.

---

## 11. Menginstal Composer
Composer adalah manajer dependensi untuk PHP. Langkah-langkah berikut menginstal Composer secara global:

```bash
# Buat direktori untuk binari lokal
mkdir -p ~/.local/bin

# Unduh installer Composer
php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"

# Verifikasi integritas installer
php -r "if (hash_file('sha384', 'composer-setup.php') === 'dac665fdc30fdd8ec78b38b9800061b4150413ff2e3b6f88543c636f7cd84f6db9189d43a81e5503cda447da73c7e5b6') { echo 'Installer terverifikasi'.PHP_EOL; } else { echo 'Installer korup'.PHP_EOL; unlink('composer-setup.php'); exit(1); }"

# Instal Composer
php composer-setup.php --install-dir=~/.local/bin --filename=composer

# Bersihkan file installer
php -r "unlink('composer-setup.php');"
```

**Catatan**: Pastikan `~/.local/bin` ada di `$PATH` Anda. Tambahkan `export PATH="$HOME/.local/bin:$PATH"` ke `~/.bashrc` atau `~/.zshrc` jika belum ada. Verifikasi instalasi dengan `composer --version`.

---

## 12. AI Agent

```
npm install -g @qwen-code/qwen-code@latest
qwen --version

npm install -g @google/gemini-cli
```

**Link**: [Qwen](https://github.com/QwenLM/qwen-code) dan [Gemini CLI](https://github.com/google-gemini/gemini-cli)

---

## Penyelesaian
Setelah menyelesaikan langkah-langkah di atas, sistem Anda seharusnya sudah memiliki semua perangkat lunak yang diperlukan. Jika ada masalah, periksa pesan kesalahan atau konsultasikan dokumentasi resmi dari masing-masing perangkat lunak.

**Tips Tambahan**:
- Selalu perbarui sistem secara berkala dengan `sudo pacman -Syu`.
- Cadangkan konfigurasi penting sebelum membuat perubahan besar.
- Untuk bantuan lebih lanjut, kunjungi [Arch Wiki](https://wiki.archlinux.org/) atau forum komunitas Arch Linux.