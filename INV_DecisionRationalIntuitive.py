import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import date

# Konfigurasi halaman
st.set_page_config(page_title="Tes Gaya Pengambilan Keputusan", layout="centered")

# Inisialisasi session state untuk menyimpan data responden
if "responses_df" not in st.session_state:
    st.session_state.responses_df = pd.DataFrame(columns=[
        "Nama", "Tanggal Tes", "Email",
        "Rational_Score", "Intuitive_Score", "Dominant_Style"
    ])

# === SIDEBAR: Area Admin ===
with st.sidebar:
    st.header("🔐 Admin Panel")
    admin_pass = st.text_input("Password Admin", type="password", key="admin_pass")
    if admin_pass == "admin234":
        st.success("✅ Akses diberikan")
        if not st.session_state.responses_df.empty:
            st.subheader("📊 Data Responden")
            st.dataframe(st.session_state.responses_df)
            csv = st.session_state.responses_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Unduh Semua Data (CSV)",
                data=csv,
                file_name="hasil_tes_pengambilan_keputusan.csv",
                mime="text/csv"
            )
        else:
            st.info("Belum ada data.")
    elif admin_pass:
        st.error("❌ Password salah")

# === ISI UTAMA ===
st.title("🧠 Tes Gaya Pengambilan Keputusan: Rasional vs Intuitif")
st.subheader("Pilih jawaban yang paling sesuai dengan cara Anda biasanya mengambil keputusan.")

# Identitas Responden
st.markdown("### 📝 Identitas Anda")
nama = st.text_input("Nama Lengkap")
tanggal = st.date_input("Tanggal Tes", value=date.today())
email = st.text_input("Email (opsional)")

# Petunjuk skala
st.markdown("""
**Petunjuk Jawaban:**
- **STS** = Sangat Tidak Setuju  
- **TS** = Tidak Setuju  
- **N** = Netral  
- **S** = Setuju  
- **SS** = Sangat Setuju  
""")

# Daftar pertanyaan (14 item valid berdasarkan kriteria Edward’s)
questions_pool = [
    {"text": "Saya membuat daftar kelebihan dan kekurangan sebelum memilih opsi.", "type": "rational"},
    {"text": "Saya memeriksa fakta atau data untuk mendukung keputusan saya.", "type": "rational"},
    {"text": "Saya lebih percaya pada angka atau bukti objektif daripada firasat.", "type": "rational"},
    {"text": "Saya mengevaluasi setiap pilihan secara sistematis, satu per satu.", "type": "rational"},
    {"text": "Saya sering bertanya, 'Apa bukti yang mendukung pilihan ini?'", "type": "rational"},
    {"text": "Saya menggunakan langkah-langkah logis saat memecahkan masalah.", "type": "rational"},
    {"text": "Saya mempertimbangkan konsekuensi jangka panjang sebelum memutuskan.", "type": "rational"},
    {"text": "Saya sering merasa 'tahu' jawabannya meski belum bisa menjelaskan alasannya.", "type": "intuitive"},
    {"text": "Saat memilih, saya memperhatikan perasaan dalam diri saya (misalnya: tenang vs gelisah).", "type": "intuitive"},
    {"text": "Saya mempercayai 'suara hati' saya dalam situasi yang tidak pasti.", "type": "intuitive"},
    {"text": "Gambaran mental atau bayangan membantu saya menemukan solusi.", "type": "intuitive"},
    {"text": "Saya merasa nyaman mengambil keputusan meski informasinya belum lengkap.", "type": "intuitive"},
    {"text": "Saya sering mendapat wawasan tiba-tiba setelah 'melepaskan' masalah sejenak.", "type": "intuitive"},
    {"text": "Saya mengenali pola atau makna dalam situasi tanpa harus menganalisis detailnya.", "type": "intuitive"},
]

# Acak urutan pertanyaan setiap sesi (tapi konsisten selama sesi berjalan)
# Gunakan seed berdasarkan nama untuk konsistensi jika nama diisi
if "shuffled_questions" not in st.session_state:
    if nama:
        random.seed(hash(nama) % (10 ** 9))  # agar urutan konsisten per responden
    shuffled = questions_pool.copy()
    random.shuffle(shuffled)
    st.session_state.shuffled_questions = shuffled

questions = st.session_state.shuffled_questions

# Formulir jawaban
responses = []
for i, q in enumerate(questions):
    st.write(f"**{i+1}. {q['text']}**")
    response = st.radio(
        "",
        options=["STS", "TS", "N", "S", "SS"],
        key=f"q{i}",
        horizontal=True
    )
    responses.append(response)

# Fungsi konversi skor
def convert_score(resp):
    return {"STS": 1, "TS": 2, "N": 3, "S": 4, "SS": 5}[resp]

# Tombol submit
if st.button("✅ Hitung Hasil"):
    if not nama.strip():
        st.error("Mohon isi nama Anda.")
    else:
        rational_score = sum(convert_score(responses[i]) for i, q in enumerate(questions) if q["type"] == "rational")
        intuitive_score = sum(convert_score(responses[i]) for i, q in enumerate(questions) if q["type"] == "intuitive")

        if rational_score > intuitive_score:
            dominant = "Rasional"
        elif intuitive_score > rational_score:
            dominant = "Intuitif"
        else:
            dominant = "Seimbang"

        # Simpan data
        new_row = pd.DataFrame([{
            "Nama": nama.strip(),
            "Tanggal Tes": tanggal,
            "Email": email.strip(),
            "Rational_Score": rational_score,
            "Intuitive_Score": intuitive_score,
            "Dominant_Style": dominant
        }])
        st.session_state.responses_df = pd.concat([st.session_state.responses_df, new_row], ignore_index=True)

        # Tampilkan hasil
        st.success("✅ Tes selesai! Berikut hasil dan analisis Anda:")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Skor Rasional", rational_score)
        with col2:
            st.metric("Skor Intuitif", intuitive_score)

        # Grafik
        fig, ax = plt.subplots(figsize=(8, 5))
        categories = ['Rasional', 'Intuitif']
        values = [rational_score, intuitive_score]
        colors = ['#2E7D32', '#D32F2F']  # Hijau tua & Merah tua
        bars = ax.bar(categories, values, color=colors, edgecolor='black')
        ax.set_title('Perbandingan Gaya Pengambilan Keputusan', fontsize=14, fontweight='bold')
        ax.set_ylabel('Total Skor')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom')
        st.pyplot(fig)

        # === INTERPRETASI ELABORATIF ===
        st.header("🔍 Interpretasi Mendalam")

        if dominant == "Rasional":
            st.markdown("""
            ### 🧠 Anda Cenderung **Rasional** dalam Mengambil Keputusan

            Anda adalah tipe pemikir analitis. Anda:
            - Lebih percaya pada **fakta, data, dan logika** daripada firasat.
            - Suka **menguraikan masalah** menjadi bagian-bagian kecil yang bisa dianalisis.
            - Mempertimbangkan **konsekuensi jangka panjang** dan risiko secara sistematis.
            - Merasa tidak nyaman jika harus memutuskan tanpa informasi yang cukup.

            **Kelebihan:**  
            Keputusan Anda cenderung **konsisten, dapat dipertanggungjawabkan, dan minim bias emosional**. Cocok untuk peran seperti analis, akuntan, insinyur, atau manajer proyek.

            **Tantangan:**  
            Terkadang Anda mungkin **terlalu lama menganalisis** (analysis paralysis) atau mengabaikan sinyal non-verbal/pola yang tidak terlihat secara eksplisit.

            **Saran Pengembangan:**  
            Latih diri untuk **mendengarkan tubuh dan perasaan Anda** sesekali. Tanyakan: *"Apa kata hati saya?"* meski tanpa alasan logis. Ini bisa membuka solusi kreatif yang tidak muncul dari data.
            """)
        elif dominant == "Intuitif":
            st.markdown("""
            ### 💫 Anda Cenderung **Intuitif** dalam Mengambil Keputusan

            Anda adalah tipe pemikir holistik. Anda:
            - Mengandalkan **perasaan, pola, dan wawasan spontan** saat memilih.
            - Sering merasa "tahu" jawabannya **sebelum bisa menjelaskan alasannya**.
            - Nyaman bekerja dalam **ketidakpastian** dan situasi yang informasinya tidak lengkap.
            - Mengenali makna dari **keseluruhan gambaran**, bukan hanya detail.

            **Kelebihan:**  
            Anda cepat, adaptif, dan sering menemukan **solusi inovatif** yang tidak terpikirkan oleh pendekatan analitis. Cocok untuk seniman, wirausahawan, konselor, atau pemimpin krisis.

            **Tantangan:**  
            Orang lain mungkin kesulitan memahami keputusan Anda karena **kurangnya penjelasan logis**. Terkadang, intuisi bisa dipengaruhi oleh bias tak sadar.

            **Saran Pengembangan:**  
            Coba **validasi intuisi Anda dengan fakta ringkas**. Tanyakan: *"Apa bukti kecil yang mendukung perasaan ini?"* Ini akan meningkatkan kepercayaan orang lain dan akurasi keputusan Anda.
            """)
        else:
            st.markdown("""
            ### ⚖️ Anda Memiliki **Keseimbangan** antara Rasional dan Intuitif

            Anda adalah **pemecah masalah yang fleksibel**. Anda:
            - Bisa beralih antara **analisis logis** dan **wawasan instan** tergantung konteks.
            - Tidak terjebak pada satu pendekatan — Anda memilih alat yang tepat untuk situasi.
            - Menggabungkan **kepala dan hati** secara harmonis.

            **Kelebihan:**  
            Anda sangat **adaptif**. Dalam situasi krisis, Anda bisa bertindak cepat; dalam perencanaan strategis, Anda bisa bersikap sistematis. Ini adalah **kemampuan langka dan sangat bernilai**.

            **Tantangan:**  
            Terkadang Anda mungkin bingung: *"Harus pakai logika atau perasaan?"* — terutama saat kedua sinyal bertentangan.

            **Saran Pengembangan:**  
            Kembangkan **kerangka kerja pribadi**:  
            - Untuk keputusan **berdampak tinggi & reversibel** → gunakan pendekatan rasional.  
            - Untuk keputusan **berdampak rendah & butuh kecepatan** → percayai intuisi.  
            Latih **kesadaran diri** untuk tahu kapan masing-masing gaya paling efektif.
            """)

        st.markdown("---")
        st.caption("Tes ini dikembangkan berdasarkan teori pengambilan keputusan oleh Kahneman (2011), Epstein (1994), dan prinsip psikometri Edward’s (1954). Hasil ini bersifat deskriptif, bukan diagnostik klinis.")