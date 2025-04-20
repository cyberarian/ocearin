import streamlit as st

def get_app_title():
    return "📝 OCEARIN"

def get_app_content():
    # Create container for content to avoid None return
    content_container = st.container()
    
    # Place expander inside container
    with content_container:
        with st.expander("ℹ️ About OCEARIN, OCR with Vision Language Models", expanded=False):
            st.markdown("""
            ## Transformasi OCR dengan Vision Language Models

            Pemanfaatan Vision Language Models (VLMs) dalam Optical Character Recognition (OCR) menandai lompatan besar dalam pemrosesan dokumen. Tidak lagi terbatas pada ekstraksi teks seperti halnya OCR tradisional, VLMs menghadirkan kemampuan pemahaman dokumen secara multimodal. 
            
            Dengan integrasi kecerdasan visual dan linguistik, VLMs mampu menafsirkan teks dalam konteksnya, memahami struktur tabel dan formulir, serta menganalisis elemen visual seperti diagram dan grafik. 
            
            Pendekatan ini tidak hanya meningkatkan akurasi ekstraksi informasi tetapi juga membuka peluang baru dalam digitalisasi, pencarian, dan analisis dokumen kompleks.            
            
            ### 📌 Implementasi: Kombinasi VLMs dan OCR Tradisional
            
            Aplikasi ini menyediakan dua pilihan VLMs (Mistral-OCR dan Gemini 2.5 Flash Preview 04-17) serta beberapa tool OCR tradisional untuk perbandingan. Meskipun tersedia lebih banyak lagi model VLMs dan OCR, kami memilih untuk menjaga kesederhanaan dan fokus pada pengalaman pengguna.
            
            ### 🔍 Keunggulan VLMs dalam OCR
            
            ✅ Pemahaman Kontekstual & Multibahasa – VLMs memahami struktur dokumen, bukan sekadar mengenali teks.
            
            ✅ Pengenalan Tulisan Tangan & Font Kompleks – Termasuk tulisan bersambung (cursive) dan karakter non-standar.
            
            ✅ Ekstraksi Data Terstruktur – Mampu menangkap informasi dari tabel, formulir, dan diagram.
            
            ✅ Integrasi Visual & Tekstual – Memungkinkan analisis gambar dan teks dalam satu model.
            
            ✅ Preservasi Format Asli – Menjaga tata letak dokumen untuk akurasi lebih tinggi.
            
            ### 🚀 Integrasi VLMs dengan RAG untuk Pemrosesan Dokumen
            
            > VLMs dapat dioptimalkan untuk Retrieval-Augmented Generation (RAG), yang menggabungkan pencarian informasi dengan pemahaman multimodal. Pendekatan ini meningkatkan akurasi dan relevansi dalam menafsirkan dokumen kompleks seperti kontrak, laporan keuangan, dan arsip historis.
            
            ### 💡 Kasus Penggunaan
            
            📖 Digitalisasi Riset Ilmiah – AI mengonversi makalah akademik ke format siap analisis.
            
            📜 Pelestarian Dokumen Sejarah – Manuskrip dan arsip bersejarah terdigitalisasi dengan akurasi lebih tinggi.
            
            👨‍💼 Peningkatan Layanan Pelanggan – Manual produk menjadi basis pengetahuan interaktif.
            
            📂 Manajemen Rekod & Arsip – Memudahkan pencarian dan pengelolaan dokumen di perusahaan & institusi pemerintah.
            
            ⚖ Automasi Pengolahan Dokumen Hukum – Mempercepat ekstraksi data dari kontrak dan regulasi.

            ### 🔻 Keterbatasan OCR Tradisional

            ❌ Sulit mengenali tulisan tangan & font kompleks.
            
            ❌ Tidak mampu menangkap konteks dan struktur dokumen.
            
            ❌ Kualitas hasil menurun pada dokumen dengan noise tinggi.
                        
            ❌ Terbatas pada teks, mengabaikan elemen visual.

            Dengan pendekatan berbasis VLMs, OCR tidak lagi sekadar membaca teks, tetapi memahami dokumen secara holistik.

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
