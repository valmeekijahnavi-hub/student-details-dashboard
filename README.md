# Student Details Data Visualization Dashboard

An interactive student performance dashboard built using Python, Streamlit, Pandas, NumPy and Plotly.

## Features
- Sidebar filters for available student categories and numeric ranges
- KPI cards: total students, average score, highest score and percentage scoring 40+
- Exam score distribution
- Study hours vs exam score
- Average exam score by motivation level
- Attendance vs exam score (only if the dataset contains an `Attendance` column)
- Numerical correlation heatmap
- Filtered student records table
- Download filtered records as CSV

## Dataset
Place `StudentPerformanceFactors.csv` in the same folder as `app.py`.

The app requires an `Exam_Score` column. Other charts and filters appear when their corresponding columns exist in the CSV. This allows the dashboard to work with versions of the Student Performance Factors dataset that have slightly different columns.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt`, `README.md`, and `StudentPerformanceFactors.csv` to a GitHub repository.
2. Open https://share.streamlit.io/
3. Sign in with GitHub and select **Create app**.
4. Choose your repository, branch, and `app.py`.
5. Select **Deploy**.

## Important
Use a dataset you are permitted to share publicly before making the GitHub repository public. The dashboard describes patterns in the uploaded dataset; it does not establish that attendance or any other factor causes exam performance.
