import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Student Details Dashboard",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Details & Performance Dashboard")
st.markdown(
    "Interactive analysis of student performance. Use the sidebar filters; "
    "**all KPI cards, charts, and the summary table update together.**"
)

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_csv("StudentPerformanceFactors.csv")

    # Clean column names and remove fully empty rows
    data.columns = data.columns.str.strip()
    data = data.dropna(how="all").copy()

    # Convert known numeric columns when present
    numeric_candidates = [
        "Hours_Studied", "Attendance", "Exam_Score", "Previous_Scores",
        "Sleep_Hours", "Tutoring_Sessions", "Physical_Activity"
    ]
    for col in numeric_candidates:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # Remove rows without an exam score if that column exists
    if "Exam_Score" in data.columns:
        data["Exam_Score"] = pd.to_numeric(data["Exam_Score"], errors="coerce")
        data = data.dropna(subset=["Exam_Score"])

    return data

st.sidebar.header("📂 Dataset")
uploaded_file = st.sidebar.file_uploader("Upload student CSV (optional)", type=["csv"])

try:
    df = load_data(uploaded_file)
except FileNotFoundError:
    st.error("StudentPerformanceFactors.csv was not found. Add it to the same GitHub repository as app.py.")
    st.stop()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

if df.empty:
    st.warning("The dataset is empty. Please upload a valid student CSV file.")
    st.stop()

if "Exam_Score" not in df.columns:
    st.error("The dataset must contain an 'Exam_Score' column.")
    st.stop()

# ---------------- Sidebar filters ----------------
st.sidebar.header("🎛️ Dashboard Filters")

categorical_filters = [
    ("Gender", "Select Gender"),
    ("School_Type", "Select School Type"),
    ("Motivation_Level", "Select Motivation Level"),
    ("Internet_Access", "Select Internet Access"),
    ("Parental_Involvement", "Select Parental Involvement"),
    ("Access_to_Resources", "Select Access to Resources"),
    ("Extracurricular_Activities", "Select Extracurricular Activities"),
    ("Teacher_Quality", "Select Teacher Quality"),
    ("Peer_Influence", "Select Peer Influence"),
]

selected_filters = {}
for col, label in categorical_filters:
    if col in df.columns:
        values = sorted(df[col].dropna().astype(str).unique().tolist())
        selected_filters[col] = st.sidebar.multiselect(
            label, options=values, default=values, key=f"filter_{col}"
        )

# Numeric range filters, only when a usable column exists
numeric_filter_columns = ["Hours_Studied", "Attendance", "Sleep_Hours", "Previous_Scores"]
numeric_ranges = {}
for col in numeric_filter_columns:
    if col in df.columns:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if not series.empty and series.min() < series.max():
            numeric_ranges[col] = st.sidebar.slider(
                f"{col.replace('_', ' ')} range",
                min_value=float(series.min()),
                max_value=float(series.max()),
                value=(float(series.min()), float(series.max())),
                key=f"range_{col}"
            )

st.sidebar.caption("All selected filters are applied to every dashboard section.")

# ---------------- Apply all filters once ----------------
filtered_df = df.copy()

for col, selected_values in selected_filters.items():
    if selected_values:
        filtered_df = filtered_df[
            filtered_df[col].astype(str).isin(selected_values)
        ]

for col, (low, high) in numeric_ranges.items():
    numeric_series = pd.to_numeric(filtered_df[col], errors="coerce")
    filtered_df = filtered_df[numeric_series.between(low, high)]

if filtered_df.empty:
    st.warning("No student records match the selected filters. Change the sidebar selections.")
    st.stop()

# ---------------- KPI cards ----------------
total_students = len(filtered_df)
average_score = filtered_df["Exam_Score"].mean()
highest_score = filtered_df["Exam_Score"].max()
pass_mark = 40
pass_percentage = (filtered_df["Exam_Score"].ge(pass_mark).mean()) * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Students", f"{total_students:,}")
k2.metric("Average Exam Score", f"{average_score:.2f}")
k3.metric("Highest Exam Score", f"{highest_score:.2f}")
k4.metric("Students Scoring 40+", f"{pass_percentage:.1f}%")

st.markdown("---")

# ---------------- Main visualizations ----------------
left, right = st.columns(2)

with left:
    score_fig = px.histogram(
        filtered_df, x="Exam_Score", nbins=20,
        title="Exam Score Distribution",
        labels={"Exam_Score": "Exam Score"},
        color_discrete_sequence=["#4285F4"]
    )
    score_fig.update_layout(height=420)
    st.plotly_chart(score_fig, use_container_width=True)

with right:
    if "Hours_Studied" in filtered_df.columns:
        study_fig = px.scatter(
            filtered_df, x="Hours_Studied", y="Exam_Score",
            color="Gender" if "Gender" in filtered_df.columns else None,
            hover_data=[c for c in ["School_Type", "Motivation_Level"] if c in filtered_df.columns],
            title="Study Hours vs Exam Score",
            labels={"Hours_Studied": "Hours Studied", "Exam_Score": "Exam Score"}
        )
        study_fig.update_layout(height=420)
        st.plotly_chart(study_fig, use_container_width=True)
    else:
        st.info("Study-hours chart requires an Hours_Studied column.")

left, right = st.columns(2)

with left:
    if "Motivation_Level" in filtered_df.columns:
        motivation_data = (
            filtered_df.groupby("Motivation_Level", as_index=False)["Exam_Score"]
            .mean().sort_values("Exam_Score", ascending=False)
        )
        motivation_fig = px.bar(
            motivation_data, x="Motivation_Level", y="Exam_Score",
            title="Average Exam Score by Motivation Level",
            labels={"Motivation_Level": "Motivation Level", "Exam_Score": "Average Exam Score"},
            text_auto=".2f"
        )
        motivation_fig.update_layout(height=420)
        st.plotly_chart(motivation_fig, use_container_width=True)
    else:
        st.info("Motivation chart requires a Motivation_Level column.")

with right:
    if "Attendance" in filtered_df.columns:
        attendance_fig = px.scatter(
            filtered_df, x="Attendance", y="Exam_Score",
            title="Attendance vs Exam Score",
            labels={"Attendance": "Attendance", "Exam_Score": "Exam Score"}
        )
        attendance_fig.update_layout(height=420)
        st.plotly_chart(attendance_fig, use_container_width=True)
    else:
        st.info("This dataset does not contain an Attendance column, so the attendance chart is skipped.")

# ---------------- Correlation heatmap ----------------
st.markdown("---")
st.subheader("📊 Numerical Feature Correlation")

numeric_df = filtered_df.select_dtypes(include=np.number)
if numeric_df.shape[1] >= 2:
    corr = numeric_df.corr(numeric_only=True)
    heatmap = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        hoverongaps=False
    ))
    heatmap.update_layout(title="Correlation Heatmap", height=550)
    st.plotly_chart(heatmap, use_container_width=True)
else:
    st.info("At least two numerical columns are required for a correlation heatmap.")

# ---------------- Summary table ----------------
st.markdown("---")
st.subheader("📋 Student Details Table")
st.caption("Showing records after applying all sidebar filters.")

st.dataframe(filtered_df, use_container_width=True, height=380)

# ---------------- Download ----------------
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Student Data (CSV)",
    data=csv_data,
    file_name="filtered_student_details.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Student Details Data Visualization Dashboard | Python • Pandas • Plotly • Streamlit")
