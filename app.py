import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="검침표 자동 추출", layout="centered")
st.title("수도 및 전기 검침표 자동 추출기")

api_key = st.secrets["API_KEY"]

uploaded_file = st.file_uploader("검침표 사진 업로드 (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 사진", use_container_width=True)
    
    if st.button("표 데이터 추출 시작"):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        with st.spinner("사진을 분석하고 있습니다..."):
            # 가로줄 인식을 강제하고 중간 데이터를 완전히 무시하도록 지시사항 강화
            prompt = """이 사진은 건물 검침표 이미지입니다. 
            데이터가 옆으로 밀리거나 어긋나지 않도록 각 가로줄(행)을 독립적으로 인식하는 것이 가장 중요합니다.
            
            1. 각 가로줄의 맨 왼쪽에서 3자리 또는 4자리의 호실 번호를 찾으세요.
            2. 해당 호실과 가로로 일직선 상에 위치한 맨 오른쪽 끝의 숫자(가장 최근 검침값)만 찾으세요.
            3. 중간에 있는 8개월치 과거 데이터나 빈칸은 시각적으로 완전히 무시하세요.
            
            결과는 호실,최근검침값 형태의 쉼표로 구분된 CSV로만 출력하고 다른 설명은 절대 추가하지 마세요."""
            
            try:
                response = model.generate_content([prompt, image])
                extracted_text = response.text.strip()
                
                st.success("추출 완료")
                st.text_area("추출된 데이터 미리보기", value=extracted_text, height=200)
                
                st.download_button(
                    label="엑셀용 CSV 파일 다운로드",
                    data=extracted_text.encode("utf-8-sig"),
                    file_name="검침표_최근값_추출결과.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"오류 발생: {e}")
