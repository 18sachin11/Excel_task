import streamlit as st
import pandas as pd
from io import BytesIO, StringIO

st.title("📂 File Cleaner")

# Upload section
uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Detect file type
    file_ext = uploaded_file.name.split(".")[-1].lower()

    try:
        if file_ext == "xlsx":
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif file_ext == "csv":
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload .xlsx or .csv")
            st.stop()

        st.success(f"{file_ext.upper()} file uploaded successfully!")
        st.subheader("Original Data Preview:")
        st.dataframe(df.head())

        # Cleaning
        if st.button("🧹 Clean File (Remove -9999.0 Rows)"):
            df_cleaned = df.replace(-9999.0, pd.NA).dropna()
            st.subheader("✅ Cleaned Data Preview:")
            st.dataframe(df_cleaned.head())

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
