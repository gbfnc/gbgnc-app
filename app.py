import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="검침표 자동 추출", layout="centered")
st.title("수도 및 전기 검침표 자동 추출기")

# 사이드바에 API 키 입력란 배치
api_key = st.sidebar.text_input("발급받은 Gemini API 키를 입력하세요", type="password")

# 메인 화면에 사진 업로드 기능 추가
uploaded_file = st.file_uploader("검침표 사진 업로드 (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and api_key:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 사진", use_container_width=True)
    
    if st.button("표 데이터 추출 시작"):
        genai.configure(api_key=api_key)
        # 제미나이 2.5 플래시 모델 사용
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        with st.spinner("사진을 분석하고 있습니다..."):
            prompt = "이 사진은 건물 검침표야. 표 안의 데이터를 추출해서 쉼표로 구분된 CSV 형식 텍스트로만 정확하게 출력해줘. 다른 설명은 하지 마."
            
            try:
                response = model.generate_content([prompt, image])
                extracted_text = response.text.strip()
                
                st.success("추출 완료")
                st.text_area("추출된 데이터 미리보기", value=extracted_text, height=200)
                
                # utf-8-sig 인코딩을 적용하여 엑셀에서 한글 깨짐 방지
                st.download_button(
                    label="엑셀용 CSV 파일 다운로드",
                    data=extracted_text.encode("utf-8-sig"),
                    file_name="검침표_추출결과.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"오류 발생: {e}")

elif not api_key:
    st.info("왼쪽 화살표를 눌러 사이드바를 열고 API 키를 먼저 입력해 주세요.")
