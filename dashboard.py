import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Mostrans Monthly Dashboard",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 Mostrans Monthly Dashboard")
st.markdown("Upload file Excel bulanan untuk melihat ringkasan operasional.")

uploaded = st.file_uploader("Upload file Excel (.xlsx)", type="xlsx")

if uploaded:
    try:
        wb = pd.ExcelFile(uploaded)
        sheet_names_clean = {s.strip().lower(): s for s in wb.sheet_names}

        if "raw data transaction" not in sheet_names_clean:
            st.error(f"Sheet 'Raw Data Transaction' tidak ditemukan. Sheet yang ada: {', '.join(wb.sheet_names)}")
            st.stop()

        actual_sheet = sheet_names_clean["raw data transaction"]
        df = pd.read_excel(uploaded, sheet_name=actual_sheet)

        col_map = {c.strip().lower(): c for c in df.columns}

        def get_col(keywords):
            for k in keywords:
                for col_lower, col_orig in col_map.items():
                    if k in col_lower:
                        return col_orig
            return None

        col_plat       = get_col(["plat nomor", "plat_nomor"])
        col_trans      = get_col(["nama transporter", "nama_transporter"])
        col_vendor     = get_col(["vendor_transporter", "vendor transporter"])
        col_shipper    = get_col(["group shipper"])
        col_moda       = get_col(["moda"])

        total_order = len(df)

        nopol_unik = 0
        if col_plat:
            nopol_unik = df[col_plat].dropna().astype(str).str.strip().str.upper()
            nopol_unik = nopol_unik[~nopol_unik.isin(["", "NULL", "[NULL]"])].nunique()

        trans_unik = 0
        if col_trans:
            nama = df[col_trans].dropna().astype(str).str.strip().str.upper()
            nama = nama[~nama.isin(["", "NULL", "[NULL]"])]
            combined = nama
            if col_vendor:
                vendor = df[col_vendor].dropna().astype(str).str.strip().str.upper()
                vendor = vendor[~vendor.isin(["", "NULL", "[NULL]"])]
                combined = pd.concat([nama, vendor])
            trans_unik = combined.nunique()

        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Order", f"{total_order:,}".replace(",", "."))
        m2.metric("Nopol Unik (Active Trucks)", f"{nopol_unik:,}".replace(",", "."))
        m3.metric("Transporter Unik", f"{trans_unik:,}".replace(",", "."))
        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Distribusi Group Shipper")
            if col_shipper:
                shipper_df = df[col_shipper].dropna().astype(str).str.strip()
                shipper_df = shipper_df[~shipper_df.isin(["", "NULL", "[NULL]"])]
                shipper_count = shipper_df.value_counts().reset_index()
                shipper_count.columns = ["Group Shipper", "Jumlah"]
                fig1 = px.pie(
                    shipper_count, names="Group Shipper", values="Jumlah",
                    hole=0.5, color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig1.update_traces(textposition="outside", textinfo="percent+label")
                fig1.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.warning("Kolom 'Group Shipper' tidak ditemukan.")

        with c2:
            st.subheader("Moda Pengiriman")
            if col_moda:
                moda_df = df[col_moda].dropna().astype(str).str.strip()
                moda_df = moda_df[~moda_df.isin(["", "NULL", "[NULL]"])]
                moda_count = moda_df.value_counts().reset_index()
                moda_count.columns = ["Moda", "Jumlah"]
                fig2 = px.pie(
                    moda_count, names="Moda", values="Jumlah",
                    hole=0.5, color_discrete_sequence=["#378ADD", "#D4537E", "#EF9F27"]
                )
                fig2.update_traces(textposition="outside", textinfo="percent+label")
                fig2.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("Kolom 'Moda' tidak ditemukan.")

        st.subheader("Top 10 Transporter berdasarkan Jumlah Trip")
        if col_trans:
            top_trans = df[col_trans].dropna().astype(str).str.strip()
            top_trans = top_trans[~top_trans.isin(["", "NULL", "[NULL]"])]
            top_trans = top_trans.value_counts().head(10).reset_index()
            top_trans.columns = ["Transporter", "Jumlah Trip"]
            top_trans = top_trans.sort_values("Jumlah Trip")
            fig3 = px.bar(
                top_trans, x="Jumlah Trip", y="Transporter",
                orientation="h", color_discrete_sequence=["#1D9E75"],
                text="Jumlah Trip"
            )
            fig3.update_traces(textposition="outside")
            fig3.update_layout(margin=dict(t=20, b=20, l=20, r=40), height=420)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Kolom 'Nama Transporter' tidak ditemukan.")

    except Exception as e:
        st.error(f"Terjadi error: {e}")

else:
    st.info("Silakan upload file Excel untuk memulai.")