import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from io import StringIO

st.set_page_config(page_title="CSV Cleaner & Multi-Y Chart App", layout="wide")
st.title("📂 CSV Cleaner & Multi-Y Chart App with Correlation")

# File upload
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

            all_cols = df_cleaned.columns.tolist()

            # Column selections
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("🟦 Select X-axis column (any type)", all_cols, key="xcol")
            with col2:
                y_cols = st.multiselect("🟥 Select One or More Y-axis Columns (any type)", [col for col in all_cols if col != x_col], key="ycol")

            chart_type = st.radio("📐 Chart Type", ["Line", "Scatter"], horizontal=True)

            if st.button("📈 Generate Chart"):
                if not y_cols:
                    st.warning("❗ Please select at least one Y-axis column.")
                else:
                    st.session_state.show_chart = True

            if st.session_state.show_chart and y_cols:
                # Prepare melted dataframe
                melted_df = pd.DataFrame()

                for y in y_cols:
                    try:
                        x_vals = df_cleaned[x_col]
                        y_vals = pd.to_numeric(df_cleaned[y], errors="coerce")
                        temp = pd.DataFrame({x_col: x_vals, "Value": y_vals})
                        temp["Variable"] = y
                        melted_df = pd.concat([melted_df, temp])
                    except:
                        st.warning(f"⚠️ Could not process column {y} for plotting.")

                if melted_df.empty:
                    st.warning("⚠️ No valid Y data to plot.")
                else:
                    # Correlation Section
                    st.markdown("### 🔗 Pearson Correlation (r) between X and each Y")
                    for y in y_cols:
                        try:
                            x_data = pd.to_numeric(df_cleaned[x_col], errors="coerce")
                            y_data = pd.to_numeric(df_cleaned[y], errors="coerce")
                            valid = x_data.notna() & y_data.notna()
                            if valid.sum() > 1:
                                r = np.corrcoef(x_data[valid], y_data[valid])[0, 1]
                                st.markdown(f"• **{y} vs {x_col}**: `r = {r:.3f}`")
                            else:
                                st.markdown(f"• **{y} vs {x_col}**: Not enough valid data.")
                        except:
                            st.markdown(f"• **{y} vs {x_col}**: Cannot compute correlation.")

                    # Plotting
                    if chart_type == "Line":
                        chart = alt.Chart(melted_df).mark_line().encode(
                            x=x_col,
                            y="Value",
                            color="Variable",
                            tooltip=[x_col, "Variable", "Value"]
                        ).interactive()
                    else:
                        chart = alt.Chart(melted_df).mark_circle(size=60).encode(
                            x=x_col,
                            y="Value",
                            color="Variable",
                            tooltip=[x_col, "Variable", "Value"]
                        ).interactive()

                    st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
