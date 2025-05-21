import streamlit as st

def render():
    st.title("Tentang OCEARIN")
    
    st.markdown("""
        OCEARIN dimaksudkan sebagai OCR Evaluator Framework, sebuah inisiatif yang dirancang untuk menganalisis dan membandingkan berbagai penyedia layanan OCR. Framework ini bersifat provider-agnostic,  dapat digunakan tanpa bergantung pada satu penyedia tertentu. Dengan mengintegrasikan teknologi Vision-Language Models (VLM) dan sistem OCR tradisional, OCEARIN menawarkan pemahaman yang lebih mendalam mengenai kualitas dan performa ekstraksi teks dari berbagai jenis dokumen.
        
        Provider OCR yang terintegrasi mencakup model-model AI mutakhir seperti Mistral OCR untuk 
        pemahaman dokumen terstruktur, Google Gemini untuk pemrosesan bahasa-visual, dan Groq untuk 
        OCR performa tinggi. Selain itu, sistem juga mendukung solusi OCR tradisional seperti 
        Tesseract untuk pemrosesan lokal, serta PyMuPDF dan PyPDF2 untuk ekstraksi teks PDF.
        
        ### Sistem Analisis
        
        Evaluasi kualitas dilakukan secara real-time dengan mempertimbangkan berbagai aspek seperti:
        - Perhitungan metrik secara real-time
        - Penilaian preservasi struktur dokumen
        - Analisis retensi format
        - Benchmarking spesifik per provider
        
        Dalam pemrosesan dokumen, sistem mampu menangani:
        - PDF multi-halaman
        - Pra-pemrosesan gambar
        - Analisis tata letak
        - Ekstraksi teks dan gambar
        
        ### Implementasi Teknis
        
        OCEARIN dibangun menggunakan teknologi sederhana tetapi modern dengan stack teknis yang mencakup:
        
        Frontend berbasis Streamlit untuk antarmuka yang responsif, OCR yang mengkombinasikan 
        Vision Language Models dan OCR tradisional, pemrosesan gambar menggunakan Pillow dan PyMuPDF, 
        penanganan PDF dengan PyPDF2 dan fitz, serta mesin analisis metrik kualitas yang dikustomisasi.
        
        ### Fitur Performa
        
        Sistem ini dilengkapi dengan kemampuan pemrosesan batch, sistem caching untuk peningkatan 
        performa, penanganan error yang robust, preservasi format, dan visualisasi metrik kualitas 
        yang komprehensif.
        
        ### Privasi & Keamanan
        
        OCEARIN memberikan perhatian khusus pada aspek privasi dan keamanan dengan menerapkan:
        - Pemrosesan file secara lokal bila memungkinkan
        - Pemrosesan cloud dengan persetujuan pengguna
        - Tanpa penyimpanan data permanen
        - Pengelolaan API key yang aman
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
