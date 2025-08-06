import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="CSV Cleaner", layout="wide")
st.title("📂 CSV Cleaner App: Remove Rows with -9999.0")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read CSV
        df = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")

        st.subheader("📄 Original Data Preview")
        st.dataframe(df, use_container_width=True)

        # Cleaning step
        if st.button("🧹 Clean File (Remove -9999.0 Rows)"):
            df_cleaned = df.replace(-9999.0, pd.NA).dropna()

            if df_cleaned.empty:
                st.warning("⚠️ All rows were removed. No data left after cleaning.")
            else:
                st.success(f"✅ Cleaned data contains {len(df_cleaned)} rows.")
                st.subheader("📋 Cleaned Data Table")
                st.dataframe(df_cleaned, use_container_width=True)

                # Convert to CSV and provide download button
                csv = df_cleaned.to_csv(index=False)
                st.download_button(
                    label="📥 Download Cleaned CSV",
                    data=csv,
                    file_name="cleaned_file.csv",
                    mime="text/csv"
                )

    except Exception as e:
        st.error(f"❌ Error processing CSV: {e}")
