import streamlit as st
import pandas as pd
import altair as alt
from io import StringIO

st.set_page_config(page_title="CSV Cleaner & Chart App", layout="wide")
st.title("📂 CSV Cleaner & Chart App")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# Initialize session state variables
if "cleaned_data" not in st.session_state:
    st.session_state.cleaned_data = None
if "show_chart" not in st.session_state:
    st.session_state.show_chart = False

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ CSV file uploaded successfully!")
        st.subheader("🔍 Original Data Preview")
        st.dataframe(df, use_container_width=True)

        if st.button("🧹 Clean File (Remove -9999.0 rows)"):
            df_cleaned = df.replace(-9999.0, pd.NA).dropna()
            if df_cleaned.empty:
                st.warning("⚠️ All rows were removed after cleaning.")
            else:
                st.session_state.cleaned_data = df_cleaned
                st.success(f"✅ Cleaned data has {len(df_cleaned)} rows.")

        # If cleaned data is available
        if st.session_state.cleaned_data is not None:
            df_cleaned = st.session_state.cleaned_data
            st.subheader("📋 Cleaned Data Preview")
            st.dataframe(df_cleaned, use_container_width=True)

            # Download button
            csv = df_cleaned.to_csv(index=False)
            st.download_button(
                label="📥 Download Cleaned CSV",
                data=csv,
                file_name="cleaned_file.csv",
                mime="text/csv"
            )

            st.markdown("---")
            st.subheader("📊 Create a Chart from Cleaned Data")

            # Numeric columns for charting
            numeric_cols = df_cleaned.select_dtypes(include=["float64", "int64"]).columns.tolist()

            if len(numeric_cols) < 2:
                st.info("❗ Not enough numeric columns to generate a chart.")
            else:
                x_col = st.selectbox("Select X-axis column", numeric_cols, key="xcol")
                y_options = [col for col in numeric_cols if col != x_col]
                y_col = st.selectbox("Select Y-axis column", y_options, key="ycol")
                chart_type = st.radio("Select Chart Type", ["Line", "Bar", "Scatter"], horizontal=True)

                # Button to generate chart
                if st.button("📈 Generate Chart"):
                    st.session_state.show_chart = True

                if st.session_state.show_chart:
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
