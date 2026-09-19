import streamlit as st
import pandas as pd

st.set_page_config(page_title="KBO 순위 검색", layout="wide")
st.title("⚾ KBO 연도별/지표별 선수 순위 검색")

@st.cache_data
def load_data():
    excel_path = 'KBO_타자투수_통합_마스터_2010_2025.xlsx'
    df_batter = pd.read_excel(excel_path, sheet_name='타자_MASTER_2010_2025')
    df_pitcher = pd.read_excel(excel_path, sheet_name='투수_MASTER_2010_2025')
    return df_batter, df_pitcher

df_batter, df_pitcher = load_data()

# 사이드바 설정
st.sidebar.header("검색 옵션")
pos = st.sidebar.radio("구분", ["타자", "투수"])

df = df_batter if pos == "타자" else df_pitcher

years = ["전체 연도"] + sorted([str(int(y)) for y in df['연도'].dropna().unique()])
selected_year = st.sidebar.selectbox("연도 선택", years, index=len(years)-5 if len(years)>5 else 0)

num_cols = df.select_dtypes(include=['number']).columns.tolist()
exclude_cols = ['연도', 'playerId', '세이버순위', '순위']
metrics = [c for c in num_cols if c not in exclude_cols]

default_metric = "AVG" if pos == "타자" and "AVG" in metrics else ("평균자책" if "평균자책" in metrics else metrics[0])
selected_metric = st.sidebar.selectbox("기록 지표 선택", metrics, index=metrics.index(default_metric) if default_metric in metrics else 0)

default_order = "낮은순 (오름차순)" if pos == "투수" and selected_metric == "평균자책" else "높은순 (내림차순)"
order = st.sidebar.radio("정렬 방식", ["높은순 (내림차순)", "낮은순 (오름차순)"], index=0 if default_order == "높은순 (내림차순)" else 1)

# 데이터 필터링 및 정렬
filtered_df = df.copy()
if selected_year != "전체 연도":
    filtered_df = filtered_df[filtered_df['연도'] == int(selected_year)]

filtered_df = filtered_df.dropna(subset=[selected_metric])
ascending = (order == "낮은순 (오름차순)")
sorted_df = filtered_df.sort_values(by=selected_metric, ascending=ascending).reset_index(drop=True)

sorted_df.index = sorted_df.index + 1
team_col = '팀명' if '팀명' in sorted_df.columns else '팀'

display_df = sorted_df[['연도', '선수명', team_col, selected_metric]]

st.subheader(f"📊 {selected_year} {pos} - {selected_metric} 기준 순위")
st.dataframe(display_df, use_container_width=True)