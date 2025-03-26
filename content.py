import streamlit as st

def get_app_title():
    return "📝 OCEARIN"

def get_app_content():
    # Create container for content to avoid None return
    content_container = st.container()
    
    # Place expander inside container
    with content_container:
        with st.expander("ℹ️ About OCR with Vision Language Models", expanded=False):
            st.markdown("""
            # Transformasi OCR dengan Vision Language Models

            > Pemanfaatan Vision Language Models (VLMs) dalam Optical Character Recognition (OCR) membuka paradigma baru dalam pemrosesan dokumen, melampaui batasan OCR tradisional dan membawa kita ke era pemahaman dokumen yang lebih cerdas dan kontekstual. 
            
            > Aplikasi ini berinisiatif menyediakan dua pilihan VLMs (Mistral-OCR dan Gemini-2.0-flash) dan beberapa tool OCR tradisional sebagai pembanding. 
            
            > VLMs dirancang untuk terintegrasi secara mulus dengan sistem Retrieval-Augmented Generation (RAG), sehingga cocok untuk memproses dokumen multimodal yang berisi tabel, formulir, gambar dan elemen lainnya.
            
            > Beberapa contoh penggunaan
            > - Digitalisasi Riset Ilmiah: Lembaga riset mengonversi makalah akademik ke dalam format yang siap digunakan oleh AI, sehingga mempercepat kolaborasi.
            > - Pelestarian Dokumen Sejarah: Organisasi menggunakan OCR untuk mendigitalkan dan melestarikan manuskrip serta artefak bersejarah.
            > - Peningkatan Layanan Pelanggan: Tim layanan pelanggan mengubah manual menjadi basis pengetahuan yang dapat dicari, sehingga mempercepat waktu respons.
            > - Manajemen Rekod dan Arsip: Lembaga pemerintah, perusahaan, dan institusi arsip memanfaatkan OCR untuk mengonversi dokumen fisik ke format digital, meningkatkan efisiensi pencarian dan pengelolaan rekod.
            > - Automasi Pengolahan Dokumen Hukum dan Administratif: Firma hukum dan institusi administrasi menggunakan OCR untuk mengekstrak informasi dari kontrak, peraturan, dan surat-surat resmi, mempercepat analisis dan pengambilan keputusan.

            ## 💡 Keterbatasan OCR Tradisional

            * Gagal mengenali tulisan tangan dan font kompleks
            * Kesulitan dengan dokumen berkualitas rendah
            * Tidak bisa memahami konteks dan struktur
            * Terbatas pada teks, mengabaikan elemen visual

            ## ✨ Keunggulan OCR dengan VLMs

            * Pemahaman kontekstual dan pemrosesan multi-bahasa
            * Pengenalan tulisan tangan/bersambung (cursive) dan font kompleks
            * Ekstraksi informasi terstruktur (tabel, form, dll)
            * Integrasi pemahaman visual dan tekstual
            * Mempertahankan format asli dokumen dengan bantuan format markdown

            ---

            ### ⚠️ Disclaimer

            Aplikasi ini dikembangkan untuk tujuan edukasi dalam memperkenalkan OCR berbasis VLMs. 
            Pengembang tidak bertanggung jawab atas penyalahgunaan atau dampak dari penggunaan aplikasi ini.

            """)
        
        # Footer stays inside container but outside expander
        st.markdown("---")
        st.markdown(
            "Built by Adnuri Mohamidi with help from AI :orange_heart: #OpenToWork #HireMe", 
            help="cyberariani@gmail.com"
        )
    
    # Return empty string to prevent None
    return ""