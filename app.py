import streamlit as st
import pandas as pd
import altair as alt
from io import StringIO

st.set_page_config(page_title="CSV Cleaner & Chart App", layout="wide")
st.title("📂 CSV Cleaner & Chart App")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read the CSV
        df = pd.read_csv(uploaded_file)
        st.success("✅ CSV file uploaded successfully!")

        st.subheader("🔍 Original Data Preview")
        st.dataframe(df, use_container_width=True)

        # Clean data
        if st.button("🧹 Clean File (Remove Rows with -9999.0)"):
            df_cleaned = df.replace(-9999.0, pd.NA).dropna()

            if df_cleaned.empty:
                st.warning("⚠️ All rows were removed after cleaning.")
            else:
                st.success(f"✅ Cleaned data has {len(df_cleaned)} rows.")
                st.subheader("📋 Cleaned Data Preview")
                st.dataframe(df_cleaned, use_container_width=True)

                # Download cleaned CSV
                csv = df_cleaned.to_csv(index=False)
                st.download_button(
                    label="📥 Download Cleaned CSV",
                    data=csv,
                    file_name="cleaned_file.csv",
                    mime="text/csv"
                )

                # --------------------------------------
                # 📊 Chart Generation Section
                st.markdown("---")
                st.subheader("📊 Create a Chart from Cleaned Data")

                # Get numeric columns only
                numeric_cols = df_cleaned.select_dtypes(include=["int64", "float64"]).columns.tolist()

                if len(numeric_cols) < 2:
                    st.info("❗ Not enough numeric columns to generate charts.")
                else:
                    # Step 1: Select X column
                    x_axis = st.selectbox("Select X-axis column", numeric_cols, key="x_axis")

                    # Step 2: Select Y column (different from X)
                    y_axis_options = [col for col in numeric_cols if col != x_axis]
                    y_axis = st.selectbox("Select Y-axis column", y_axis_options, key="y_axis")

                    # Step 3: Select Chart Type
                    chart_type = st.radio("Select Chart Type", ["Line", "Bar", "Scatter"], horizontal=True)

                    # Step 4: Generate chart on button click
                    if st.button("📈 Generate Chart"):
                        chart_data = df_cleaned[[x_axis, y_axis]]
                        
                        if chart_type == "Line":
                            chart = alt.Chart(chart_data).mark_line().encode(
                                x=x_axis,
                                y=y_axis,
                                tooltip=[x_axis, y_axis]
                            ).interactive()

                        elif chart_type == "Bar":
                            chart = alt.Chart(chart_data).mark_bar().encode(
                                x=x_axis,
                                y=y_axis,
                                tooltip=[x_axis, y_axis]
                            ).interactive()

                        elif chart_type == "Scatter":
                            chart = alt.Chart(chart_data).mark_circle(size=60).encode(
                                x=x_axis,
                                y=y_axis,
                                tooltip=[x_axis, y_axis]
                            ).interactive()

                        st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
