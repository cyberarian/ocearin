import streamlit as st

def render():
    st.title("Tentang OCEARIN")
    st.markdown("""
OCEARIN adalah platform evaluasi OCR (Optical Character Recognition) yang dirancang untuk membandingkan dan menganalisis hasil ekstraksi teks dari berbagai penyedia OCR, baik berbasis AI modern maupun solusi tradisional. Framework ini bersifat agnostic—artinya, Anda dapat memilih dan membandingkan hasil dari berbagai provider tanpa terikat pada satu vendor.

### Provider OCR yang Didukung
OCEARIN terintegrasi dengan beragam penyedia OCR, meliputi:
- **NVIDIA**: Vision-Language Model mutakhir untuk ekstraksi dan pemahaman dokumen gambar.
- **Mistral**: Model AI untuk dokumen terstruktur dan analisis layout.
- **Google Gemini**: Model bahasa-visual generasi terbaru dari Google.
- **Tesseract**: Solusi OCR open-source untuk pemrosesan lokal.
- **PyMuPDF**: Ekstraksi teks dan gambar dari PDF multi-halaman.
- **PyPDF2**: Ekstraksi teks dari PDF dengan dukungan berbagai format.

### Fungsi Utama
- **Evaluasi Kualitas OCR**: Sistem menganalisis hasil ekstraksi teks secara real-time menggunakan metrik seperti jumlah kata, preservasi struktur, retensi format, dan skor kepercayaan.
- **Perbandingan Provider**: Pengguna dapat membandingkan hasil dari berbagai provider untuk dokumen yang sama.
- **Visualisasi & Benchmarking**: Hasil dievaluasi dan divisualisasikan dengan metrik yang relevan untuk membantu pemilihan provider terbaik sesuai kebutuhan.

### Fitur Teknis
- Pemrosesan PDF multi-halaman dan gambar
- Analisis tata letak dan format dokumen
- Sistem caching dan batch processing untuk performa optimal
- Penanganan error yang robust dan notifikasi real-time
- Privasi: Pemrosesan lokal bila memungkinkan, cloud processing dengan persetujuan pengguna

OCEARIN dibangun dengan Streamlit untuk antarmuka yang interaktif dan responsif, serta mengintegrasikan berbagai pustaka Python untuk pemrosesan dokumen dan analisis kualitas OCR.
    """)
    st.markdown("---")
    st.markdown("""          
        ### ⚠️ Perhatian
        Framework ini dikembangkan untuk tujuan edukasi dan evaluasi OCR. Pengembang tidak bertanggung jawab atas penyalahgunaan atau dampak dari penggunaan framework ini.
    """)
    
    st.markdown("---")
    st.markdown("""
        ### 📜 Lisensi & Kontribusi
        Proyek ini bersifat open-source dan tersedia untuk tujuan pendidikan dan penelitian. Kontribusi sangat disambut! Silakan kunjungi repositori GitHub kami untuk panduan kontribusi.
    """)
    
    # Footer
    st.markdown("---")
    st.caption(
        "Dikembangkan oleh Adnuri Mohamidi dengan bantuan AI :orange_heart: #OpenToWork #HireMe", 
        help="cyberariani@gmail.com"
    )
