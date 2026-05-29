import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="세계 지진 위험도 분석",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------
# 스타일
# -----------------------------
st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1 {
    color: #1f2937;
    font-weight: 800;
}

.stButton > button {
    width: 100%;
    height: 3.2em;
    border-radius: 12px;
    border: none;
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    color: white;
    font-size: 17px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton > button:hover {
    transform: scale(1.01);
    background: linear-gradient(90deg, #1d4ed8, #2563eb);
}

.info-box {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.risk-high {
    background: #fee2e2;
    color: #b91c1c;
    padding: 18px;
    border-radius: 16px;
    font-size: 24px;
    font-weight: 700;
    text-align: center;
}

.risk-mid {
    background: #fef3c7;
    color: #b45309;
    padding: 18px;
    border-radius: 16px;
    font-size: 24px;
    font-weight: 700;
    text-align: center;
}

.risk-low {
    background: #dcfce7;
    color: #15803d;
    padding: 18px;
    border-radius: 16px;
    font-size: 24px;
    font-weight: 700;
    text-align: center;
}

.small-text {
    color: #6b7280;
    font-size: 15px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# 데이터 불러오기
# -----------------------------
df_new = pd.read_csv("earthquake.csv")

# 위험도 사전
risk_dict = {
    0: '높음',
    1: '낮음',
    2: '중간'
}

# 색상
colors = {
    0: '#ef4444',  # 빨강
    1: '#3b82f6',  # 파랑
    2: '#f59e0b'   # 주황
}

# -----------------------------
# 제목
# -----------------------------
st.title("🌍 세계 지진 위험도 분석 시스템")

st.markdown("""
<div class="info-box">
<div class="small-text">
입력한 위치 주변의 지진 데이터를 분석하여 예상 위험도를 시각적으로 보여줍니다.
</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 입력 영역
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    lat = st.number_input(
        "위도 입력",
        value=37.5,
        step=0.1,
        format="%.2f"
    )

with col2:
    lon = st.number_input(
        "경도 입력",
        value=127.0,
        step=0.1,
        format="%.2f"
    )

# -----------------------------
# 분석 버튼
# -----------------------------
if st.button("🔍 위험도 분석 시작"):

    # 주변 지진 찾기
    near_df = df_new[
        (df_new['위도'] >= lat - 5) &
        (df_new['위도'] <= lat + 5) &
        (df_new['경도'] >= lon - 5) &
        (df_new['경도'] <= lon + 5)
    ]

    # 데이터 없는 경우
    if len(near_df) == 0:

        st.warning("주변 지진 데이터가 없습니다.")

    else:

        # 군집 비율 계산
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)

        # 가장 많은 군집
        main_cluster = cluster_ratio.idxmax()

        # 위험도
        risk = risk_dict[main_cluster]

        # 위험도 박스 스타일
        if risk == "높음":
            risk_class = "risk-high"
            emoji = "🚨"

        elif risk == "중간":
            risk_class = "risk-mid"
            emoji = "⚠️"

        else:
            risk_class = "risk-low"
            emoji = "✅"

        # 결과 출력
        st.markdown(f"""
        <div class="{risk_class}">
        {emoji} 예상 위험도 : {risk}
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        # 통계 카드
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("주변 지진 데이터", f"{len(near_df)}개")

        with c2:
            st.metric(
                "평균 규모",
                round(near_df['규모'].mean(), 2)
            )

        with c3:
            st.metric(
                "최대 규모",
                round(near_df['규모'].max(), 2)
            )

        # -----------------------------
        # 지도 생성
        # -----------------------------
        m = folium.Map(
            location=[lat, lon],
            zoom_start=4,
            tiles="CartoDB positron"
        )

        # 샘플링
        df_sample = df_new.sample(500, random_state=42)

        # 지진 표시
        for i in range(len(df_sample)):

            cluster = df_sample.iloc[i]['cluster']

            folium.CircleMarker(
                location=[
                    df_sample.iloc[i]['위도'],
                    df_sample.iloc[i]['경도']
                ],
                radius=max(
                    df_sample.iloc[i]['규모'] * 1.5,
                    2
                ),
                color=colors[cluster],
                fill=True,
                fill_color=colors[cluster],
                fill_opacity=0.6,
                popup=f"""
                규모: {df_sample.iloc[i]['규모']}<br>
                위험군: {risk_dict[cluster]}
                """
            ).add_to(m)

        # 사용자 위치
        folium.Marker(
            location=[lat, lon],
            popup="입력 위치",
            tooltip="분석 위치",
            icon=folium.Icon(
                color='black',
                icon='info-sign'
            )
        ).add_to(m)

        # 원 표시
        folium.Circle(
            radius=500000,
            location=[lat, lon],
            color="#2563eb",
            fill=True,
            fill_opacity=0.08
        ).add_to(m)

        # 지도 출력
        st.write("")
        st.subheader("🗺️ 지진 분포 지도")

        st_folium(
            m,
            width=1200,
            height=650,
            returned_objects=[]
        )
