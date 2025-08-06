import streamlit as st
import pandas as pd
from io import BytesIO, StringIO

st.set_page_config(page_title="File Cleaner", layout="wide")
st.title("📂 File Cleaner: Remove Rows with -9999.0")

# File upload
uploaded_file = st.file_uploader("Upload your Excel (.xlsx) or CSV (.csv) file", type=["xlsx", "csv"])

if uploaded_file is not None:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    try:
        # Read file based on extension
        if file_ext == "xlsx":
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif file_ext == "csv":
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Unsupported file format.")
            st.stop()

        st.success(f"{file_ext.upper()} file uploaded successfully!")
        st.subheader("📄 Original Data Preview")
        st.dataframe(df, use_container_width=True)

        # Run cleaning
        if st.button("🧹 Clean File (Remove -9999.0 Rows)"):
            df_cleaned = df.replace(-9999.0, pd.NA).dropna()

            if df_cleaned.empty:
                st.warning("All rows were removed. No data to display.")
            else:
                st.success(f"✅ Cleaned data contains {len(df_cleaned)} rows.")
                st.subheader("📋 Cleaned Data Table")
                st.dataframe(df_cleaned, use_container_width=True)

                # Prepare download
                if file_ext == "xlsx":
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_cleaned.to_excel(writer, index=False, sheet_name='CleanedData')
                        writer.save()
                    output.seek(0)
                    st.download_button(
                        label="📥 Download Cleaned Excel",
                        data=output,
                        file_name="cleaned_file.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                elif file_ext == "csv":
                    output = StringIO()
                    df_cleaned.to_csv(output, index=False)
                    st.download_button(
                        label="📥 Download Cleaned CSV",
                        data=output.getvalue(),
                        file_name="cleaned_file.csv",
                        mime="text/csv"
                    )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
