"""Memecah naskah skripsi (hasil pandoc DOCX ke Markdown GFM) menjadi berkas per bab di laporan/draf-7-bab.

Pemakaian:
    pandoc Skripsi_KD_OP3_vNN.docx -t gfm --wrap=none -o naskah.md
    python3 laporan/alat/konversi_naskah_ke_markdown.py naskah.md laporan/draf-7-bab "Skripsi_KD_OP3_vNN (tanggal)"

Keluaran: HALAMAN_AWAL.md, BAB_1 sampai BAB_7, DAFTAR_REFERENSI.md, dan LAMPIRAN.md. Gambar dibuang dan keterangannya
dipertahankan; subbab diberi nomor seperti pada naskah. Berkas lama di folder keluaran ditimpa, dan README.md tidak
disentuh.
"""
import re, sys
from pathlib import Path

src, out, versi = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
L = Path(src).read_text(encoding="utf-8").split("\n")

BAB = ["PENDAHULUAN", "LANDASAN KEPUSTAKAAN", "METODOLOGI PENELITIAN", "REKAYASA KEBUTUHAN",
       "PERANCANGAN DAN IMPLEMENTASI", "PENGUJIAN", "PENUTUP"]
BERKAS = ["BAB_1_PENDAHULUAN.md", "BAB_2_LANDASAN_KEPUSTAKAAN.md", "BAB_3_METODOLOGI.md",
          "BAB_4_REKAYASA_KEBUTUHAN.md", "BAB_5_PERANCANGAN_IMPLEMENTASI.md",
          "BAB_6_PENGUJIAN_DAN_PEMBAHASAN.md", "BAB_7_PENUTUP.md"]
h1 = [i for i, l in enumerate(L) if l.startswith("# ")]


def bersih(baris):
    hasil = []
    for l in baris:
        if re.match(r"^\s*<img ", l):
            continue
        l = l.replace("<sub>\u00ad</sub>", "").replace("\u00ad", "")
        l = re.sub(r'<span id="[^"]*" class="anchor"></span>', "", l)
        m = re.match(r"^(Gambar|Tabel|Kode Program) ([0-9A-D]+\.[0-9]+) (.*)$", l)
        if m and not l.rstrip().endswith(".") and len(l) < 220:
            l = f"**{m.group(1)} {m.group(2)}** {m.group(3)}"
        hasil.append(l)
    teks = "\n".join(hasil)
    teks = re.sub(r"\n{3,}", "\n\n", teks)
    return teks.strip() + "\n"


def nomori(baris, awalan):
    """Beri nomor subbab: ## -> n.m, ### -> n.m.k, #### -> n.m.k.l."""
    c = [0, 0, 0]
    keluar = []
    for l in baris:
        m = re.match(r"^(#{2,4}) (.*)$", l)
        if m:
            lv = len(m.group(1)) - 2
            c[lv] += 1
            for j in range(lv + 1, 3):
                c[j] = 0
            no = ".".join([awalan] + [str(x) for x in c[: lv + 1]])
            l = f"{m.group(1)} {no} {m.group(2)}"
        keluar.append(l)
    return keluar


KEPALA = ("> Isi berkas ini disalin dari naskah skripsi **{v}**. Sumber kebenaran tetap berkas DOCX dan PDF di "
          "`E:\\Kuliah\\Thesis\\Laporan\\Skripsi\\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan "
          "supaya nomor dan rujukannya dapat dicocokkan dengan PDF.\n\n")

# Bab 1 sampai 7
for n in range(7):
    a = h1[n]; b = h1[n + 1]
    assert L[a][2:].strip().startswith(BAB[n]), L[a]
    isi = nomori(L[a + 1:b], str(n + 1))
    (out / BERKAS[n]).write_text(f"# BAB {n + 1} {BAB[n]}\n\n" + KEPALA.format(v=versi) + bersih(isi), encoding="utf-8")

# Daftar referensi
a, b = h1[7], h1[8]
assert "DAFTAR REFERENSI" in L[a]
(out / "DAFTAR_REFERENSI.md").write_text("# DAFTAR REFERENSI\n\n" + KEPALA.format(v=versi) + bersih(L[a + 1:b]), encoding="utf-8")

# Lampiran A-D
bagian = []
for k, i in enumerate(h1[8:]):
    j = h1[8 + k + 1] if 8 + k + 1 < len(h1) else len(L)
    huruf = "ABCD"[k]
    judul = L[i][2:].strip()
    bagian.append(f"# LAMPIRAN {huruf} {judul}\n\n" + bersih(nomori(L[i + 1:j], huruf)))
(out / "LAMPIRAN.md").write_text("# LAMPIRAN\n\n" + KEPALA.format(v=versi) + "\n".join(b.replace("# LAMPIRAN", "## LAMPIRAN", 1).replace("\n## ", "\n### ").replace("\n### LAMPIRAN", "\n## LAMPIRAN") for b in bagian), encoding="utf-8")

# Halaman awal: abstrak, abstract, dan daftar istilah utuh; pengesahan, pernyataan, dan prakata hanya diringkas.
# Data pribadi (nama, NIM, NIK, email, nama pihak di prakata) sengaja tidak disalin karena repositori ini publik.
awal = L[: h1[0]]


def blok(nama, akhir):
    i = next(k for k, l in enumerate(awal) if l.strip() == nama or l.strip().endswith(nama))
    j = next((k for k, l in enumerate(awal) if k > i and akhir(l)), len(awal))
    return bersih(awal[i + 1:j]).strip().split("\n\n")


abs_id = blok("ABSTRAK", lambda l: l.strip() == "ABSTRACT")[2:]        # buang baris nama penulis dan pembimbing
abs_en = blok("ABSTRACT", lambda l: "DAFTAR ISI" in l)[2:]
istilah = "\n\n".join(blok("DAFTAR ISTILAH DAN SINGKATAN", lambda l: False))
judul = [l for l in awal if l.startswith("IMPLEMENTASI ")][0]
teks = ("# HALAMAN AWAL\n\n" + KEPALA.format(v=versi)
        + "> Data pribadi (nama, NIM, NIK, email, dan nama pihak dalam prakata) sengaja tidak dicantumkan di repositori "
          "publik. Bagian pengesahan, pernyataan, dan prakata hanya diringkas isinya; teks lengkapnya ada di naskah DOCX/PDF.\n\n"
        + f"**Judul:** {judul}\n\n"
        + "## Lembar Pengesahan (ringkasan)\n\n"
          "- Skripsi diajukan untuk memenuhi sebagian persyaratan memperoleh gelar Sarjana Teknik, Program Studi Teknik "
          "Komputer, Departemen Teknik Informatika, Fakultas Ilmu Komputer, Universitas Brawijaya, Malang, 2026.\n"
          "- Disetujui oleh dosen pembimbing tunggal dan diketahui oleh Ketua Departemen Teknik Informatika.\n\n"
        + "## Pernyataan Orisinalitas (ringkasan)\n\n"
          "- Penulis menyatakan naskah tidak memuat karya ilmiah orang lain yang pernah diajukan untuk gelar akademik, "
          "kecuali yang dikutip dan disebut dalam Daftar Referensi.\n"
          "- Penulis bersedia skripsi digugurkan dan gelar dibatalkan bila terbukti ada unsur plagiasi.\n\n"
        + "## Prakata (ringkasan)\n\n"
          "- Ucapan syukur, tujuan penyusunan skripsi, ucapan terima kasih kepada pihak yang membantu menurut perannya, "
          "dan harapan atas kritik serta saran. Nama pihak tidak disalin.\n\n"
        + "## Abstrak\n\n" + "\n\n".join(abs_id) + "\n\n"
        + "## Abstract\n\n" + "\n\n".join(abs_en) + "\n\n"
        + "## Daftar Istilah dan Singkatan\n\n" + istilah + "\n")
(out / "HALAMAN_AWAL.md").write_text(teks, encoding="utf-8")
print("selesai")
