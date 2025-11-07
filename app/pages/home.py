import streamlit as st

def render():
    st.title("📝 OCEARIN - OCR Evaluator")
  
    st.markdown("""
        
        Pemanfaatan Vision Language Models (VLMs) dalam Optical Character Recognition (OCR) menandai lompatan besar dalam pemrosesan dokumen. Tidak lagi terbatas pada ekstraksi teks seperti halnya OCR tradisional, VLMs menghadirkan kemampuan pemahaman dokumen secara multimodal. 
            
        Dengan integrasi kecerdasan visual dan linguistik, VLMs mampu menafsirkan teks dalam konteksnya, memahami struktur tabel dan formulir, serta menganalisis elemen visual seperti diagram dan grafik. 
            
        Pendekatan ini tidak hanya meningkatkan akurasi ekstraksi informasi tetapi juga membuka peluang baru dalam digitalisasi, pencarian, dan analisis dokumen kompleks.
        
        ### 🔻 Keterbatasan OCR Tradisional

        ❌ Sulit mengenali tulisan tangan & font kompleks.
            
        ❌ Tidak mampu menangkap konteks dan struktur dokumen.
            
        ❌ Kualitas hasil menurun pada dokumen dengan noise tinggi.
                        
        ❌ Terbatas pada teks, mengabaikan elemen visual.

        ### 🔍 Keunggulan VLMs dalam OCR
            
        ✅ Pemahaman Kontekstual & Multibahasa – VLMs memahami struktur dokumen, bukan sekadar mengenali teks.
            
        ✅ Pengenalan Tulisan Tangan & Font Kompleks – Termasuk tulisan bersambung (cursive) dan karakter non-standar.
            
        ✅ Ekstraksi Data Terstruktur – Mampu menangkap informasi dari tabel, formulir, dan diagram.
            
        ✅ Integrasi Visual & Tekstual – Memungkinkan analisis gambar dan teks dalam satu model.
            
        ✅ Preservasi Format Asli – Menjaga tata letak dokumen untuk akurasi lebih tinggi.
            
        ### 🚀 Integrasi VLMs dengan RAG untuk Pemrosesan Dokumen
            
        > VLMs dapat dioptimalkan untuk Retrieval-Augmented Generation (RAG), yang menggabungkan pencarian informasi dengan pemahaman multimodal. Pendekatan ini meningkatkan akurasi dan relevansi dalam menafsirkan dokumen kompleks seperti kontrak, laporan keuangan, dan arsip historis.
            
        ### 💡 Beberapa Contoh Kasus Penggunaan
            
        📖 Digitalisasi Riset Ilmiah – AI mengonversi makalah akademik ke format siap analisis.
            
        📜 Pelestarian Dokumen Sejarah – Manuskrip dan arsip bersejarah terdigitalisasi dengan akurasi lebih tinggi.
            
        👨‍💼 Peningkatan Layanan Pelanggan – Manual produk menjadi basis pengetahuan interaktif.
            
        📂 Manajemen Rekod & Arsip – Memudahkan pencarian dan pengelolaan dokumen di perusahaan & institusi pemerintah.
            
        ⚖ Automasi Pengolahan Dokumen Hukum – Mempercepat ekstraksi data dari kontrak dan regulasi.
        
        Dengan pendekatan berbasis VLMs, OCR tidak lagi sekadar membaca teks, tetapi memahami dokumen secara holistik.
    """)

        # Footer stays inside container but outside expander
    # Footer
    st.markdown("---")
    st.caption(
        "Dikembangkan oleh Adnuri Mohamidi dengan bantuan AI :orange_heart: interested? #HireMe", 
        help="cyberariani@gmail.com"
    )
