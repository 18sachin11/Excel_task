import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from io import StringIO

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Multi-Y CSV Plotter", page_icon="📊", layout="wide")

# ----------------------------
# HEADER
# ----------------------------
st.markdown("<h1 style='text-align: center;'>📂 CSV Cleaner & Multi-Y Chart Generator</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Visualize multiple time-series or parameters in one place</h4>", unsafe_allow_html=True)
st.markdown("---")

# ----------------------------
# FILE UPLOAD
# ----------------------------
uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv")

# Session state
if "cleaned_data" not in st.session_state:
    st.session_state.cleaned_data = None
if "show_chart" not in st.session_state:
    st.session_state.show_chart = False

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")

        with st.expander("🔍 View Raw Data"):
            st.dataframe(df, use_container_width=True)

        st.markdown("### 🧹 Data Cleaning")

        if st.button("🚿 Remove rows with `-9999.0`"):
            df_cleaned = df.replace(-9999.0, pd.NA).dropna()
            if df_cleaned.empty:
                st.warning("⚠️ All rows were removed after cleaning.")
            else:
                st.session_state.cleaned_data = df_cleaned
                st.session_state.show_chart = False
                st.success(f"✅ Cleaned data contains {len(df_cleaned)} rows.")

        # ----------------------------
        # POST-CLEANING
        # ----------------------------
        if st.session_state.cleaned_data is not None:
            df_cleaned = st.session_state.cleaned_data

            st.markdown("### 📋 Cleaned Data Preview")
            st.dataframe(df_cleaned, use_container_width=True)

            # Download cleaned CSV
            csv = df_cleaned.to_csv(index=False)
            st.download_button("📥 Download Cleaned CSV", data=csv, file_name="cleaned_file.csv", mime="text/csv")

            # ----------------------------
            # CHARTING SECTION
            # ----------------------------
            st.markdown("---")
            st.markdown("### 📊 Chart Creation Panel")

            all_cols = df_cleaned.columns.tolist()

            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("🟦 Select X-axis column", all_cols, key="xcol")
            with col2:
                y_cols = st.multiselect("🟥 Select One or More Y-axis Columns", [col for col in all_cols if col != x_col], key="ycol")

            chart_type = st.radio("📐 Choose Chart Type", ["Line", "Scatter"], horizontal=True)

            if st.button("📈 Generate Chart"):
                if not y_cols:
                    st.warning("❗ Please select at least one Y-axis column.")
                else:
                    st.session_state.show_chart = True

            if st.session_state.show_chart and y_cols:
                # Prepare melted DataFrame
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
                    # Show Correlations
                    st.markdown("### 🔗 Pearson Correlation (r)")
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
                    base = alt.Chart(melted_df).encode(
                        x=alt.X(x_col, title=x_col),
                        y=alt.Y("Value", title="Y-axis Value"),
                        color=alt.Color("Variable", legend=alt.Legend(title="Y Variables")),
                        tooltip=[x_col, "Variable", "Value"]
                    )

                    if chart_type == "Line":
                        chart = base.mark_line(size=2)
                    else:
                        chart = base.mark_circle(size=70, opacity=0.8)

                    st.altair_chart(chart.interactive(), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.9em;">
    App developed by <b>Dr. Sachchidanand Singh</b>, Scientist B, NIH-WHRC Jammu
</div>
""", unsafe_allow_html=True)
