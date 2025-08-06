import streamlit as st
import pandas as pd
import altair as alt
from io import StringIO

st.set_page_config(page_title="CSV Cleaner & Chart App", layout="wide")
st.title("📂 CSV Cleaner & Visualizer: Remove -9999.0 and Create Charts")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read the CSV
        df = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")

        st.subheader("📄 Original Data Preview")
        st.dataframe(df, use_container_width=True)

        # Cleaning
        if st.button("🧹 Clean File (Remove -9999.0 Rows)"):
            df_cleaned = df.replace(-9999.0, pd.NA).dropna()

            if df_cleaned.empty:
                st.warning("⚠️ All rows were removed. No data left after cleaning.")
            else:
                st.success(f"✅ Cleaned data contains {len(df_cleaned)} rows.")
                st.subheader("📋 Cleaned Data Table")
                st.dataframe(df_cleaned, use_container_width=True)

                # CSV Download
                csv = df_cleaned.to_csv(index=False)
                st.download_button(
                    label="📥 Download Cleaned CSV",
                    data=csv,
                    file_name="cleaned_file.csv",
                    mime="text/csv"
                )

                # Chart Section
                st.markdown("---")
                st.subheader("📊 Create Charts from Cleaned Data")

                # Select columns for X and Y axes
                numeric_cols = df_cleaned.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if len(numeric_cols) < 2:
                    st.info("Not enough numeric columns to create charts.")
                else:
                    x_col = st.selectbox("Choose X-axis column", numeric_cols, index=0)
                    y_col = st.selectbox("Choose Y-axis column", numeric_cols, index=1)

                    chart_type = st.radio("Chart Type", ["Line", "Bar", "Scatter"], horizontal=True)

                    if x_col and y_col:
                        chart_data = df_cleaned[[x_col, y_col]]

                        if chart_type == "Line":
                            chart = alt.Chart(chart_data).mark_line().encode(
                                x=x_col,
                                y=y_col,
                                tooltip=[x_col, y_col]
                            ).interactive()
                        elif chart_type == "Bar":
                            chart = alt.Chart(chart_data).mark_bar().encode(
                                x=x_col,
                                y=y_col,
                                tooltip=[x_col, y_col]
                            ).interactive()
                        elif chart_type == "Scatter":
                            chart = alt.Chart(chart_data).mark_circle(size=60).encode(
                                x=x_col,
                                y=y_col,
                                tooltip=[x_col, y_col]
                            ).interactive()

                        st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
