import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from io import StringIO

st.set_page_config(page_title="CSV Cleaner & Multi-Chart App", layout="wide")
st.title("📂 CSV Cleaner & Multi-Y Chart App with Correlation")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# Session state
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
                st.session_state.show_chart = False
                st.success(f"✅ Cleaned data has {len(df_cleaned)} rows.")

        if st.session_state.cleaned_data is not None:
            df_cleaned = st.session_state.cleaned_data
            st.subheader("📋 Cleaned Data Preview")
            st.dataframe(df_cleaned, use_container_width=True)

            # Download
            csv = df_cleaned.to_csv(index=False)
            st.download_button("📥 Download Cleaned CSV", data=csv, file_name="cleaned_file.csv", mime="text/csv")

            # Charting
            st.markdown("---")
            st.subheader("📊 Create Chart with Multiple Y Columns")

            numeric_cols = df_cleaned.select_dtypes(include=["float64", "int64"]).columns.tolist()

            if len(numeric_cols) < 2:
                st.info("❗ Not enough numeric columns to generate charts.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("🟦 Select X-axis", numeric_cols, key="xcol")
                with col2:
                    y_cols = st.multiselect("🟥 Select One or More Y-axis Columns", [col for col in numeric_cols if col != x_col], key="ycol")

                chart_type = st.radio("📐 Chart Type", ["Line", "Scatter"], horizontal=True)

                if st.button("📈 Generate Chart"):
                    if not y_cols:
                        st.warning("❗ Please select at least one Y-axis column.")
                    else:
                        st.session_state.show_chart = True

                if st.session_state.show_chart and y_cols:
                    melted_df = df_cleaned[[x_col] + y_cols].melt(id_vars=x_col, var_name='Variable', value_name='Value')

                    # Correlation summary
                    st.markdown("### 🔗 Correlation Coefficients (Pearson r)")
                    for y in y_cols:
                        try:
                            r = np.corrcoef(df_cleaned[x_col], df_cleaned[y])[0, 1]
                            st.markdown(f"• **{y} vs {x_col}**: `r = {r:.3f}`")
                        except Exception as e:
                            st.warning(f"Could not compute correlation for {y}: {e}")

                    # Chart
                    if chart_type == "Line":
                        chart = alt.Chart(melted_df).mark_line().encode(
                            x=x_col,
                            y="Value",
                            color="Variable",
                            tooltip=[x_col, "Variable", "Value"]
                        ).interactive()
                    else:  # Scatter
                        chart = alt.Chart(melted_df).mark_circle(size=60).encode(
                            x=x_col,
                            y="Value",
                            color="Variable",
                            tooltip=[x_col, "Variable", "Value"]
                        ).interactive()

                    st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
