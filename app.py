import streamlit as st
import pandas as pd
from io import BytesIO

# Set the title
st.title("Excel Cleaner App: Remove Rows with -9999.0")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    st.success("File uploaded successfully!")
    
    # Read Excel
    df = pd.read_excel(uploaded_file)
    st.subheader("Original Data Preview:")
    st.dataframe(df.head())

    # Clean data on button click
    if st.button("Run Cleaning"):
        # Replace -9999.0 with NaN and drop rows with any NaN
        df_cleaned = df.replace(-9999.0, pd.NA).dropna()

        # Preview cleaned data
        st.subheader("Cleaned Data Preview:")
        st.dataframe(df_cleaned.head())

        # Convert cleaned DataFrame to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_cleaned.to_excel(writer, index=False, sheet_name='CleanedData')
            writer.save()
        output.seek(0)

        # Download button
        st.download_button(
            label="📥 Download Cleaned Excel",
            data=output,
            file_name="cleaned_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
