---
title: "Pengamatan Permukaan Es"
description: Artikel ini memberikan gambaran umum tentang metode simulasi (Dinamika Molekuler) untuk mengamati permukaan es.
pubDatetime: 2023-08-22T10:00:00Z
modDatetime:
author: Muhammad Ruslan Novianto
slug: "Simulasi-Dinamika-Molekuler-Permukaan-Es"
featured: false
draft: false
tags:
  - "Simulasi Komputer"
  - "Dinamika Molekuler"
  - "Permukaan Es"
  - "TIP4P/Ice"
  - "Gromacs"
  - "GenIce"
ogImage: ""
canonicalURL: ""
---

Kita akan menumbuhkan es dan mengamati permukaan es (antarmuka gas-padat).

## 0. Pengaturan Lingkungan

### 0-0 Tentang dokumen ini

Bagian yang ditampilkan seperti di bawah ini, kecuali dinyatakan lain, menunjukkan perintah yang diketik di Terminal.

```shell
cd MeltingPoint
```

### 0-1 Persiapan lingkungan eksekusi

1. Unduh kode dan ekstrak di salah satu server komputasi. (Ketika Anda menekan tombol hijau, tombol Download ZIP akan muncul.)

    ![Code](https://i.gyazo.com/1c3a92c8494e362c636f41b393be6a0a.png)

    Silakan ekstrak file ZIP di disk yang memiliki ruang kosong pada server komputasi.

### 0-2 Persiapan komputer lokal

1. Instal VSCode di komputer lokal Anda, dan akses server komputasi secara remote dari VSCode untuk membuka folder IceGrowth.
2. Instal terlebih dahulu alat visualisasi hasil simulasi [VMD](https://www.ks.uiuc.edu/Research/vmd/alpha/).

## 1. Memilih model molekul air

Ada banyak jenis model molekul air yang digunakan dalam simulasi komputer. Sebagian besar dirancang untuk mereproduksi sifat-sifat air cair dan larutan pada suhu kamar, sehingga tidak cocok untuk mengamati transisi fasa kristalisasi.

Di sini, kita akan menggunakan model TIP4P/Ice yang baru-baru ini dikembangkan dan memiliki keandalan tinggi. Titik leleh model ini pada tekanan 1 atmosfer dikatakan 270 K [^1], dan sering digunakan untuk mempelajari perilaku air, es, dan hidrat (kristal terhidrasi) pada suhu di bawah suhu kamar.

Bukankah titik leleh es sudah diketahui dari eksperimen? Benar sekali. Tapi yang ingin kita ketahui adalah titik leleh model molekul air yang digunakan dalam simulasi komputer. Jika kualitas model buruk, titik lelehnya tidak akan sesuai dengan nilai eksperimen. Tujuan simulasi molekuler __bukan untuk mendapatkan data yang sesuai dengan eksperimen__. Nilainya terletak pada mendapatkan informasi yang tidak terlihat dalam eksperimen sambil menjamin reproduksi eksperimen. Jika modelnya membatasi sifat-sifat seperti titik leleh dengan baik, dapat dianggap bahwa gerakan molekulpun direproduksi dengan cukup akurat. Jika demikian, kita dapat mempercayai hasil pengamatan langsung tentang bagaimana air membeku dari antarmuka padat-cair (yang tidak terlihat dalam eksperimen).

Untuk detail bentuk TIP4P/Ice, lihat [tautan ini](http://www.sklogwiki.org/SklogWiki/index.php/TIP4P/Ice_model_of_water).

Meskipun molekul air terdiri dari 3 atom, ciri khas model air empat titik adalah penambahan satu titik interaksi tambahan untuk mendekati interaksi antara titik-titik massa secara aproksimasi.

![4-site model of water](http://www.sklogwiki.org/SklogWiki/images/a/a5/Four_site_water_model.png)

Model molekul TIP4P/Ice tertulis dalam `ice.top`.

```
; taken from http://www.sklogwiki.org/SklogWiki/index.php/GROMACS_topology_file_for_the_TIP4P/Ice_model
[ defaults ]
; nbfunc        comb-rule       gen-pairs       fudgeLJ fudgeQQ
1             2               no              1.0     1.0

[atomtypes]
;name     mass      charge   ptype    sigma        epsilon
IW     0             0.000       D   0.0           0.0
OWT4   15.99940      0.000       A   0.31668       0.88211
HW     1.00800       0.000       A   0.00000E+00   0.00000E+00

...
```

File data ini berisi sekitar 50 baris, dan berisi informasi berikut:

* Berapa banyak titik yang digunakan untuk mendekati satu molekul air.
* Jarak relatif titik-titik dalam molekul.
* Bagaimana titik-titik berinteraksi satu sama lain (gaya Coulomb dan Lennard-Jones).
* Apakah molekul diperlakukan sebagai benda fleksibel dengan titik-titik yang dihubungkan oleh pegas, atau sebagai benda kaku yang tidak berubah bentuk.

Untuk [TIP4P/Ice](http://www.sklogwiki.org/SklogWiki/index.php/TIP4P/Ice_model_of_water):

* Ada 4 titik interaksi.
* Jarak H-H sekitar 0,15 nm, jarak O-H sekitar 0,1 nm.
* 3 titik berinteraksi Coulomb, 1 titik lainnya berinteraksi Lennard-Jones.
* Diperlakukan sebagai benda kaku.

## 2. Menempatkan molekul

Bagaimana kita menempatkan molekul di awal sangat mempengaruhi keberhasilan simulasi selanjutnya.

Ketika memperkirakan titik leleh, jika kita memilih konfigurasi awal di mana semua molekul tersusun dalam struktur kristal es, es tidak akan meleleh bahkan jika suhu dinaikkan 10 K atau 20 K di atas titik leleh (fenomena pemanasan berlebih). Ini karena waktu yang dibutuhkan untuk terjadinya kerusakan struktur secara kebetulan, yang menjadi pemicu awal pelelehan, terlalu lama. Tentu saja, jika waktu perhitungan mendekati tak terbatas, es akan mulai meleleh pada suhu di atas titik leleh, tetapi perhitungan selama itu tidak mungkin dilakukan dengan komputer saat ini.

Demikian pula, jika kita mulai dari keadaan cairan sempurna, akan membutuhkan waktu yang sangat lama untuk kristal terbentuk secara alami, berapa pun suhu diturunkan. (fenomena pendinginan berlebih)

Oleh karena itu, ketika ingin memperkirakan titik leleh, kita mempersiapkan keadaan di mana es dan air sudah ada bersama. Dengan cara ini, jika suhu yang ditetapkan lebih tinggi dari titik leleh, es akan perlahan-lahan meleleh, dan jika lebih rendah, kita akan melihat pertumbuhan es.

<!-- Penting juga bahwa antarmuka antara es dan air datar. Jika antarmuka antara dua fase melengkung, akan timbul tekanan yang disebut tekanan Laplace. Intinya, meskipun kita menentukan tekanan, tekanan akan berubah karena antarmuka melengkung, sehingga kita tidak dapat memperkirakan titik leleh dengan tepat pada tekanan yang kita tentukan. -->

Konfigurasi awal disiapkan dengan langkah-langkah berikut:

1. Gunakan alat [GenIce](https://github.com/vitroid/GenIce) untuk membuat struktur kristal es. Kristal dibuat dalam bentuk balok panjang dengan rasio 1:1:2.
2. "Tetapkan" setengah dari molekul air. Ini berarti mereka tidak bisa bergerak dari posisi awal mereka.
3. Naikkan suhu hingga 800 K dan lakukan simulasi dinamika molekuler singkat. Bagian yang ditetapkan akan mempertahankan strukturnya, tetapi molekul air lainnya akan segera meleleh.
4. Kembalikan suhu dan lepaskan fiksasi. Ini menghasilkan struktur awal dengan setengah cairan dan setengah padat.
5. Lakukan simulasi selama beberapa waktu pada sekitar 270 K (titik leleh) dengan fiksasi dilepas untuk merelaksasi struktur.

![Alt text](https://i.gyazo.com/bb923db531fb195e68574f636c4c1ef1.png)

> Es yang setengah meleleh. Bagian es di tengah ditetapkan dan tidak bergerak. Karena kondisi batas periodik, ujung kiri dan kanan, atas dan bawah, depan dan belakang masing-masing terhubung dan molekul dapat keluar masuk.

Berikut adalah langkah-langkah spesifik:

### 2-1 Membuat kristal es

[GenIce](https://github.com/vitroid/GenIce) adalah alat untuk menghasilkan berbagai struktur kristal es. Kita akan menggunakannya untuk menghasilkan es Ih (es I heksagonal, jenis es yang paling umum ditemui).

Masukkan yang berikut di Terminal:

```shell
genice2 1h -r 4 4 6 -w tip4p > ice.gro
```

Opsi `-r` menentukan berapa banyak sel satuan yang akan disusun dalam arah x, y, dan z. Opsi `-w` menentukan jenis model molekul air.

Di akhir `ice.gro`, ukuran kotak ditulis dalam satuan nm seperti ini:
```
...
 1535ICE    HW1 6138   3.090   2.720   5.304
 1535ICE    HW2 6139   3.000   2.842   5.305
 1535ICE     MW 6140   3.010   2.755   5.304
 1536ICE     OW 6141   2.482   2.391   5.301
 1536ICE    HW1 6142   2.523   2.357   5.380
 1536ICE    HW2 6143   2.393   2.357   5.304
 1536ICE     MW 6144   2.476   2.382   5.312
    3.12913551 2.94142906 5.42191111
```

Ini adalah sel dengan dimensi 3,1 nm, 2,9 nm, dan 5,4 nm dalam arah sumbu x, y, dan z, sedikit lebih panjang dalam arah z.

Mari kita visualisasikan struktur ini untuk sementara. Klik kanan `ice.gro` di browser file di sisi kiri jendela VSCode dan unduh. Buka file tersebut dengan VMD.

![ice Ih](https://i.gyazo.com/d30d131bc64aaf09ab4a7e356bf0b299.png)


### 2-2 Menetapkan molekul

`Gromacs` memiliki fitur untuk membuat atom tidak bergerak dengan menentukan nomor atomnya. Karena akan merepotkan untuk menentukan secara manual, kita akan menggunakan skrip Python untuk menetapkan hanya atom-atom dengan koordinat Z kurang dari 2,7 nm.

#### 2-2-1 Memberi indeks pada atom

Perintah make_ndx dari Gromacs menghasilkan file `.ndx` yang mengklasifikasikan atom berdasarkan jenisnya.

Jalankan:

```shell
gmx make_ndx -f ice.gro -o ice.ndx
```

dan tekan q ketika prompt ditampilkan untuk keluar. ice.ndx akan berisi konten seperti berikut:

```
[ System ]
   1    2    3    4    5    6    7    8    9   10   11   12   13   14   15
  16   17   18   19   20   21   22   23   24   25   26   27   28   29   30
  31   32   33   34   35   36   37   38   39   40   41   42   43   44   45
...
```

File ini mengelompokkan atom-atom. Grup System berisi semua atom.

Mari kita siapkan grup FIX baru yang berisi daftar atom yang ingin kita tetapkan dengan cara yang sama.

#### 2-2-2 Menambahkan indeks atom yang ditetapkan

Tambahkan indeks atom yang ingin ditetapkan ke akhir file ini.

```shell
python3 zfix.py 2.0 3.4 < ice.gro >> ice.ndx
```

Ini akan menambahkan baris-baris berikut ke akhir file `ice.ndx`:

```
...
[FIX]
2049  2050  2051  2052  2057  2058  2059  2060  2061  2062  2063  2064  2065
2066  2067  2068  2069  2070  2071  2072  2077  2078  2079  2080  2081  2082
2083  2084  2085  2086  2087  2088  2097  2098  2099  2100  2101  2102  2103
2104  2105  2106  2107  2108  2109  2110  2111  2112  2113  2114  2115  2116
2121  2122  2123  2124  2125  2126  2127  2128  2129  2130  2131  2132  2133
2134  2135  2136  2141  2142  2143  2144  2145  2146  2147  2148  2149  2150
...
```

### 2-3 Melelehkan setengah sisanya

Kita akan menaikkan suhu hingga 800 K sambil menjaga volume tetap. Biasanya ini akan menyebabkan pendidihan, tetapi karena tidak bisa mengembang, air hanya akan menjadi cair. Langkah ini hanya untuk merusak struktur, jadi tidak perlu dijalankan terlalu lama.

Eksekusi metode dinamika molekuler di Gromacs selalu terdiri dari tiga langkah:

1. "Kompilasi" file konfigurasi untuk mengubahnya menjadi format data yang mudah dibaca oleh Gromacs.
2. Membaca data tersebut dan menjalankan simulasi dinamika molekuler utama (mdrun).
3. Mengubah data yang dihasilkan menjadi format yang mudah dibaca manusia.

#### 2-3-1 Kompilasi

File dengan ekstensi `.mdp` berisi detail tentang bagaimana melakukan dinamika molekuler. Penjelasan untuk masing-masing parameter ditulis sebagai komentar dalam file `fix.mdp`. Hampir semua informasi selain konfigurasi molekul dan interaksi, seperti waktu perhitungan, interval perekaman, pengaturan suhu, pengaturan tekanan, dll., ditulis dalam `.mdp`. Dalam kasus `fix.mdp`, selain itu juga ada instruksi untuk menetapkan grup atom `FIX` yang ditentukan dalam file `.ndx`.

Kompilasi ini dengan perintah berikut untuk membuat file `.tpr`:

```shell
gmx grompp -maxwarn 1 -f fix.mdp -p ice.top -c ice.gro -n ice.ndx -o fixed.tpr
```

Ini akan membuat file `fixed.tpr` yang akan dibaca oleh Gromacs.

#### 2-3-2 Eksekusi

Sekarang kita akan menjalankan simulasi dengan membaca 00001.tpr yang dibuat di 2-3-1!

```shell
gmx mdrun -deffnm fixed
```

Ketika ini dijalankan, banyak file lain yang dimulai dengan `fixed.` akan dihasilkan. (-deffnm kemungkinan adalah singkatan dari default file name, yang menginstruksikan untuk menambahkan `fixed.` ke semua file output yang tidak ditentukan secara eksplisit.)

* `fixed.cpt`: File checkpoint, diperlukan untuk melanjutkan perhitungan.
* `fixed.edr`: File yang berisi informasi statistik seperti suhu dan tekanan.
* `fixed.trr`: Data koordinat dan kecepatan atom (disebut trajektori).
* `fixed.log`: Catatan lainnya. Waktu eksekusi juga dicatat dalam file ini.

Di bagian akhir `fixed.log`, informasi waktu eksekusi dicatat seperti berikut:

```
starting mdrun 'water TIP4P/Ice'
50000 steps,    100.0 ps.

Writing final coordinates.

               Core t (s)   Wall t (s)        (%)
       Time:      792.815       99.102      800.0
                 (ns/day)    (hour/ns)
Performance:       87.185        0.275
```

Ini adalah kasus yang dijalankan di MacBook Air, dan kita dapat melihat bahwa:

* Menggunakan 800% CPU (menggunakan 8 core)
* 50000 langkah dijalankan. Karena 1 langkah adalah 0,002 ps, simulasi 100 ps telah dilakukan.
* Waktu yang dibutuhkan adalah 100 detik. Pada kecepatan ini, perhitungan untuk 90 ns dapat dilakukan dalam satu hari.

#### 2-3-3 Konfirmasi

Mari kita visualisasikan gerakan molekul menggunakan alat visualisasi hasil simulasi [VMD](https://www.ks.uiuc.edu/Research/vmd/alpha/).

Pertama, kita akan mengubah konfigurasi molekul yang diperoleh dari perhitungan dinamika molekuler menjadi format yang mudah divisualisasikan.

```shell
gmx trjconv -f fixed.trr -s fixed.tpr -pbc whole -o fixed-snapshots.gro
```

Ketika diminta input, tekan 0 dan kemudian enter. (Ini akan memvisualisasikan seluruh Sistem)

Ini akan membuat file `fixed-snapshots.gro`. Ini adalah file yang cukup besar.

1. Di VSCode, klik kanan `fixed-snapshots.gro` dan unduh.
2. Buka VMD.
3. Seret dan lepas file yang diunduh ke jendela Utama VMD.

Anda akan melihat bahwa molekul di bagian yang ditetapkan sama sekali tidak bergerak. Di sisi lain, bagian yang tidak ditetapkan menjadi benar-benar acak.

![Alt text](https://i.gyazo.com/bb923db531fb195e68574f636c4c1ef1.png)

#### 2-3-4 Relaksasi

Kita akan menurunkan suhu, melepaskan fiksasi atom, dan membiarkan struktur berelaksasi. Pada saat ini, kita juga akan memungkinkan volume berubah, dan beralih ke simulasi tekanan konstan.

Seperti sebelumnya, pengaturan simulasi ditulis dalam `.mdp`. Kali ini kita akan menggunakan `relax.mdp`.

Anda dapat menggunakan [fitur perbandingan file VSCode](https://www.mytecbits.com/microsoft/dot-net/compare-contents-of-two-files-in-vs-code) untuk melihat perbedaan antara `relax.mdp` dan `fix.mdp`.

Ada tiga perubahan:

1. Suhu diturunkan menjadi 270 K.
2. Beralih dari volume konstan ke tekanan konstan.
3. Fiksasi molekul dilepaskan.

Mari kita kompilasi lagi menggunakan ini dan jalankan.

```shell
gmx grompp -maxwarn 1 -f relax.mdp -p ice.top -c fixed.tpr -t fixed.cpt -o relaxed.tpr
gmx mdrun -deffnm relaxed
```

Seperti di 2-3-3, buatlah `relaxed.gro` dan amati dengan VMD. Kali ini, Anda akan melihat bahwa molekul di bagian es juga bergetar sedikit.

```shell
gmx trjconv -f relaxed.trr -s relaxed.tpr -pbc whole -o relaxed-snapshots.gro
```

## 2.5 Menambahkan fase gas

Kita akan memperpanjang sel dan menyiapkan area untuk fase gas.

Salin `relaxed.gro` dan simpan dengan nama `stretch.gro`.

Perbesar ukuran z di bagian akhir `stretch.gro` sekitar 2 kali lipat (tidak perlu terlalu tepat).

```
 1536water   OW 6141   1.862   2.746   5.038  0.2622  0.0469  0.2826
 1536water  HW1 6142   1.818   2.718   5.118  1.7875 -0.9183  0.8374
 1536water  HW2 6143   1.835   2.837   5.026  0.6920  0.5086  2.4287
 1536water   MW 6144   1.853   2.755   5.047  0.5253 -0.0208  0.6461
   3.14308   2.95454   10
```

Kemudian, kita akan merelaksasi struktur lagi, tetapi kali ini tanpa mengubah volume. Pengaturan ini ditulis dalam `stretch.mdp`.

Gunakan [fitur perbandingan file VSCode](https://www.mytecbits.com/microsoft/dot-net/compare-contents-of-two-files-in-vs-code) untuk membandingkan `relax.mdp` dan `stretch.mdp`.

Mari kita kompilasi dan jalankan lagi.

```shell
gmx grompp -maxwarn 1 -f stretch.mdp -p ice.top -c stretch.gro -o stretched.tpr
gmx mdrun -deffnm stretched
```

Konfirmasi dengan VMD bahwa sistem telah stabil dengan tiga fase yang ada bersama.

```shell
gmx trjconv -f stretched.trr -s stretched.tpr -pbc whole -o stretched.gro
```

## 3. Melakukan simulasi pada suhu target

Menggunakan struktur yang dibuat di 2.5 sebagai konfigurasi awal, kita akan melakukan simulasi jangka panjang pada berbagai suhu.

Target tekanan adalah 1 atmosfer, dan waktu simulasi adalah 3-10 ns. Dalam simulasi ini, kita menggunakan dt=0.002 ps, jadi 1 ns setara dengan 500.000 langkah.

Di sini, sebagai contoh, kita akan menjelaskan perhitungan pada 250 K. Ini 20 K lebih rendah dari titik leleh TIP4P/Ice [^1], jadi es diharapkan akan segera tumbuh. (Untuk suhu selain 250 K, silakan sesuaikan sesuai kebutuhan.)

### 3-1 Persiapan lingkungan kerja

Buka file pengaturan perhitungan berkelanjutan `continue.mdp` di VSCode, ubah pengaturan suhu menjadi 250 K seperti yang ditunjukkan di bawah ini, dan **simpan dengan nama file yang berbeda** sebagai `T250.mdp`.

```
...

ref_t                    = xxxx      ; Suhu sistem. Satuan dalam K.

...
```

Juga, di bagian awal `T250.mdp`, ada instruksi untuk jumlah langkah perhitungan. Jumlah langkah yang diperlukan berbeda untuk suhu rendah dan tinggi. Untuk saat ini, kita akan melakukan simulasi 3 ns untuk 280 K ke atas, dan 10 ns untuk di bawah itu, jadi silakan ubah bagian itu sesuai kebutuhan.

```
...

nsteps                   = 5000000     ; Jumlah langkah MD.
nstxout                  = 5000        ; Koordinat dioutput setiap nstxout langkah.
nstlog                   = 5000        ; Frekuensi informasi ditulis ke log.

...
```

Bandingkan `relax.mdp` dan `continue.mdp`.

### 3-2 Menjalankan simulasi

Kemudian, kompilasi file pengaturan. Kita akan menamai file yang dihasilkan `T250.tpr`.

```shell
gmx grompp -maxwarn 1 -f T250.mdp -p ice.top -c relaxed.tpr -t relaxed.cpt -o T250.tpr
```

Jalankan!

```shell
gmx mdrun -deffnm T250 -nt 8
```

Kita menentukan jumlah proses paralel dengan `-nt 8`. (Jika tidak ditentukan, kadang-kadang ada kasus yang menghasilkan error di tengah jalan. Tapi mungkin tidak diperlukan.) Dalam praktikum ini, kita menggunakan komputer dengan 32 core, jadi bisa menentukan hingga 32, tetapi karena ada kemungkinan semua orang menjalankan secara bersamaan, harap batasi hingga 8 atau 16 ketika sedang sibuk.

Ini seharusnya memakan waktu 30 sampai 100 kali lebih lama dari sebelumnya. Mari kita tunggu dengan sabar sambil minum kopi.

### 3-3 Perpanjangan

Jika dalam analisis selanjutnya ternyata waktu simulasi masih kurang, kita bisa memperpanjang perhitungan dengan cara berikut.

Pertama, berdasarkan file `.tpr` yang dihasilkan oleh `grompp` sebelumnya, kita buat file `.tpr` baru dengan waktu eksekusi yang diperpanjang. Opsi `-extend` menentukan waktu tambahan perhitungan dalam satuan ps. Kita akan memperpanjang 2000 ps = 1 ns.

```shell
gmx convert-tpr -extend 2000 -s T250.tpr -o extended.tpr
```

Kemudian jalankan! (Untuk perhitungan lanjutan, sepertinya perlu menentukan beberapa opsi.)

```shell
gmx mdrun -deffnm extended -cpi T250.cpt -s extended.tpr -noappend
```

Kali ini mungkin memakan waktu cukup lama untuk bisa makan.

## 4. Visualisasi hasil

Untuk mengonfirmasi apa yang sebenarnya terjadi, mari kita transfer data koordinat molekul ke komputer lokal dan tampilkan gerakan molekul menggunakan VMD.

Pertama, kita ubah data trajektori `.trr` menjadi format `.gro`.

```shell
gmx trjconv -f T250.trr -s T250.tpr -pbc whole -o T250-snapshots.gro
```

Unduh ini dan buka dengan VMD.

Dengan perhitungan 1 ns, mungkin sulit untuk menentukan apakah sedang meleleh atau membeku, tetapi dengan perhitungan 10 ns, biasanya bisa ditentukan.

Menurunkan suhu tidak selalu berarti pembekuan lebih cepat, karena pada suhu rendah, gerakan molekul menjadi lebih lambat, yang juga memperlambat pertumbuhan kristal. Cobalah beberapa suhu untuk menemukan suhu di mana pembekuan terjadi paling cepat.

## 5. Analisis

### 5.1 Jumlah ikatan hidrogen melintang

Dalam es yang sepenuhnya memenuhi aturan es dan tidak terpolarisasi, jumlah ikatan masuk dan keluar yang melintasi bidang apapun seharusnya sama.

Kita akan memeriksa keseimbangan jumlah ikatan hidrogen.

`hbbalance.py` memotong sel simulasi dalam arah sumbu z dengan interval 0,01 nm dan menghitung jumlah ikatan hidrogen yang melintasi setiap bidang irisan.

Jalankan:

```
python3 hbbalance.py < T250.gro
```

Ini akan menghasilkan file (dengan ekstensi `.hbb.txt`) sebanyak jumlah frame dalam `.gro`. Isinya seperti ini:

```
0.0 -2.0 1.0 3.0
0.01 -4.0 9.0 13.0
0.02 -4.0 12.0 16.0
0.03 -3.0 20.0 23.0
0.04 -3.0 25.0 28.0
0.05 -4.0 28.0 32.0
0.06 -2.0 32.0 34.0
0.07 -3.0 35.0 38.0
0.08 -2.0 41.0 43.0
...
```

Kolom pertama adalah koordinat z dari bidang irisan, kolom ketiga adalah jumlah ikatan hidrogen yang melintasi bidang ke arah positif, kolom keempat adalah jumlah yang melintasi ke arah negatif, dan kolom kedua adalah selisih antara keduanya.

Dalam es yang memenuhi aturan es dan memiliki polarisasi total nol, nilai ini seharusnya selalu 0 tidak peduli di mana bidang dipotong. Sebaliknya, jika indikator ini tidak nol, itu berarti aturan es tidak terpenuhi atau polarisasi total tidak nol.

### 5.2 Statistik fase cincin

Kita akan menggunakan statistik fase cincin untuk menentukan apakah es yang tumbuh dapat disebut es tak teratur hidrogen yang homogen.

`cycles.py` mengklasifikasikan semua cincin enam anggota irredusibel (cincin 6 anggota yang tidak dapat dinyatakan sebagai kombinasi cincin yang lebih kecil) dalam jaringan ikatan hidrogen berdasarkan arah ikatan hidrogen dan menghitung jumlahnya.

Jalankan:

```
python3 cycles.py < T250.gro
```

Ini akan menghasilkan file (dengan ekstensi `.cyc.txt`) sebanyak jumlah frame dalam `.gro`. Isinya seperti ini:

```
0 276 291.94520547945206
1 423 437.917808219178
3 456 437.917808219178
5 115 109.4794520547945
7 215 218.958904109589
9 55 54.73972602739725
11 121 109.4794520547945
21 4 4.561643835616438
```

Kolom pertama adalah fase, kolom kedua adalah frekuensi kemunculan dalam file `.gro`, kolom ketiga adalah distribusi ideal untuk jumlah total cincin yang sama dengan kolom kedua.

Dalam konfigurasi awal, ada daerah cair yang juga mengandung cincin enam anggota, jadi jumlah total ini mencakup jumlah cincin enam anggota dalam cairan. Dalam es yang dihasilkan oleh GenIce, jumlah cincin per jenis harus cocok dengan distribusi ideal (lihat lampiran terpisah), dan tidak ada alasan distribusi dalam cairan menyimpang dari distribusi ideal, jadi distribusi jenis cincin dalam konfigurasi awal diharapkan hampir cocok dengan distribusi ideal. Di sisi lain, jika jenis cincin tertentu cenderung terbentuk lebih banyak selama pertumbuhan es, distribusi ini akan menyimpang dari distribusi ideal seiring pertumbuhan kristal.

Cara untuk mengurutkan beberapa file `.cyc.txt` dan hanya mencantumkan jumlah cincin dengan fase 3. Misalnya, skrip berikut akan mengurutkan 10~10000.cyc.txt (setiap 10) secara berurutan dan hanya mengekstrak informasi fase 3:

```shell
seq 1 1000 | sed -e 's/$/0.cyc.txt/' | xargs cat | grep '^3 ' > cyclestat.3.txt
```

Mari kita uraikan:
* `seq 1 1000` menghasilkan urutan angka 1~1000 ke output standar.
* `sed -e 's/$/0.cyc.txt/'` mengganti akhir baris (`$`) input standar dengan `0.cyc.txt` dan mengirimkannya ke output standar.
* `xargs cat` memperlakukan konten input standar sebagai argumen untuk perintah `cat`. Ini akan menghasilkan file teks besar yang berisi 10~10000.cyc.txt secara berurutan ke output standar.
* `grep '^3 '` mengekstrak hanya baris yang dimulai dengan `3 ` dari input standar.

Jika Anda melihat hasil ini dengan `gnuplot`, Anda dapat melihat perubahan jumlah cincin dari waktu ke waktu.

## 6. Mengganti orientasi permukaan pertumbuhan

Struktur Ih yang dihasilkan oleh GenIce tampaknya memiliki arah $(11\bar 20)$ pada sumbu z, bukan permukaan prisma $(1010)$. Untuk mengubah arah pertumbuhan menjadi permukaan basal $(0001)$ atau permukaan prisma, kita perlu menukar sumbu z dengan sumbu x atau y.

GenIce memiliki fungsi untuk mengubah orientasi sel satuan. Misalnya, operasi menukar sumbu x dan z dapat ditulis dalam bentuk matriks sebagai berikut:

$$\left(\begin{matrix}0& 0&1\\0&1&0\\1&0&0 \end{matrix}\right)$$

Demikian pula, menukar sumbu y dan z dapat ditulis sebagai berikut:

$$\left(\begin{matrix}1& 0&0\\0&0&1\\0&1&0 \end{matrix}\right)$$

GenIce memiliki fungsi untuk membaca informasi struktur kristal, mengubahnya, dan menghasilkan plugin struktur kristal baru. → [https://github.com/vitroid/GenIce/wiki/Transform-the-unit-cell](https://github.com/vitroid/GenIce/wiki/Transform-the-unit-cell)

Jika Anda menyimpan plugin yang baru dibuat di `lattices`, Anda dapat menggunakannya untuk menghasilkan struktur kristal yang diubah.

```shell
mkdir lattices
genice2 1h -f 'reshape[0,0,1,0,1,0,1,0,0]' > lattices/1hprism.py
genice2 1h -f 'reshape[1,0,0,0,0,1,0,1,0]' > lattices/1hbasal.py
```

Ini membuat plugin struktur kristal baru, yang kemudian dapat digunakan untuk menghasilkan kristal.

```shell
genice2 1hbasal -r 4 4 6 -w tip4p > basal.gro
genice2 1hprism -r 4 4 6 -w tip4p > prism.gro
```

Untuk konfirmasi, mari kita tampilkan dengan VMD. basal.gro seharusnya menunjukkan susunan heksagonal reguler ketika dilihat dari arah sumbu z.

## 9. Lampiran

### 9-1 Koneksi VPN

Akses remote ke server komputasi milik Laboratorium Kimia Teoritis Universitas Okayama (Xeon 96 core, IP `192.168.3.220`). Informasi pengaturan akan diberikan secara terpisah.

Jika Anda tidak dapat terhubung dengan baik, gunakan Amazon EC2.

#### 9-1-1 Untuk Mac

Masukkan pengaturan di System Settings->VPN->Add VPN Configuration.

https://www.cc.uec.ac.jp/ug/ja/remote/vpn/l2tp/macos114/index.html

mungkin berguna sebagai referensi (silakan ganti konten yang dimasukkan sesuai kebutuhan)

#### 9-1-2 Untuk Windows

https://www.seil.jp/saw-mpc/doc/sa/pppac/use/pppac-client/win11_l2tp.html

mungkin berguna sebagai referensi (silakan ganti konten yang dimasukkan sesuai kebutuhan)

Control Panel → Network and Sharing Center → Change adapter settings → Pilih VPN → Properties → Security → Allow these protocols → Centang CHAP!!! (Fuh. Kenapa harus begitu dalam)

### 9-2 Penggunaan pribadi Amazon EC2

Bahkan dengan kuota gratis Amazon EC2, Anda masih bisa melakukan perhitungan yang cukup baik.

1. Buat akun di AWS. Anda akan membutuhkan nomor kartu kredit.
2. Di dashboard EC2, buat instans EC2. Anda dapat menggunakan tipe instans t2.micro (2 core) secara gratis.
3. Pilih Ubuntu untuk OS. (Ini cocok untuk digunakan sebagai platform komputasi)
4. Sebagian besar pengaturan lainnya bisa dibiarkan default, tapi tanyakan instruktur jika ada yang tidak jelas.

### 9-3 Instalasi Gromacs dan alat lainnya

Bahkan tanpa menggunakan cloud, Anda dapat dengan mudah menginstal Gromacs dan GenIce di sistem operasi berbasis Unix.

#### 9-3-1 Untuk Ubuntu/Debian Linux

(Perlu dijalankan dengan hak administrator.)

```shell
apt update
apt install gromacs python3 python3-pip
pip install numpy
pip install genice2
```

#### 9-3-2 Untuk Redhat/Amazon Linux/CentOS7

Paket gromacs tidak ditemukan di EC2 Amazon Linux/RedHat Linux. Sepertinya Anda perlu menginstal yang diperlukan secara individual dari [RPM](https://rpmfind.net/linux/rpm2html/search.php?query=gromacs).

#### 9-3-3 Untuk MacOS

Siapkan Homebrew terlebih dahulu.

Dengan HomeBrew, Anda dapat menginstal tanpa hak administrator.

```shell
brew install gromacs python3
pip install genice2
```

#### 9-3-4 Untuk Windows

(Informasi dibutuhkan!)

## Referensi

[^1] Conde, M. M., Rovere, M. & Gallo, P. High precision determination of the melting points of water TIP4P/2005 and water TIP4P/Ice models by the direct coexistence technique. J. Chem. Phys. 147, 244506 (2017).

[^2] Yagasaki, T., Matsumoto, M. & Tanaka, H. Spontaneous liquid-liquid phase separation of water. Phys. Rev. E Stat. Nonlin. Soft Matter Phys. 89, 020301 (2014).

[^3] Yeyue Xiong, Parviz Seifpanahi Shabane, and Alexey V. Onufriev*, Melting Points of OPC and OPC3 Water Models, ACS Omega 39, 25087–25094 (2020).

[^4] Espinosa, J. R., Sanz, E., Valeriani, C. & Vega, C. Homogeneous ice nucleation evaluated for several water models. J. Chem. Phys. 141, 18C529 (2014).