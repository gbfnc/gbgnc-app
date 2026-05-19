import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json

st.set_page_config(page_title="검침표 자동 추출", layout="centered")
st.title("수도 및 전기 검침표 자동 추출기")

api_key = st.secrets["API_KEY"]
uploaded_file = st.file_uploader("검침표 사진 업로드 (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 사진", use_container_width=True)
    
    if st.button("표 데이터 추출 시작"):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        with st.spinner("정밀 분석 중입니다..."):
            prompt = """이 사진은 건물 검침표입니다.
            각 가로줄에서 맨 왼쪽 호실 번호와 맨 오른쪽 최근 검침값만 짝지어 추출하세요.
            결과는 다른 설명 없이 오직 아래와 같은 JSON 배열 형태로만 출력하세요.
            
            [
              {"호실": "101", "최근검침값": "1504"},
              {"호실": "102", "최근검침값": "188"}
            ]
            """
            
            try:
                response = model.generate_content([prompt, image])
                raw_text = response.text.strip()
                
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:-3].strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:-3].strip()
                
                data = json.loads(raw_text)
                df = pd.DataFrame(data)
                
                st.success("추출 완료")
                
                # 1. 화면에서 마우스 드래그로 복사 가능한 표 시각화
                st.subheader("1. 추출된 데이터 표")
                st.data_editor(df, use_container_width=True)
                
                # 2. 엑셀 붙여넣기 전용 텍스트 창 (탭으로 구분되어 그대로 붙여넣으면 칸이 나눠짐)
                st.subheader("2. 엑셀 붙여넣기용 텍스트")
                tsv_text = "호실\t최근검침값\n" + "\n".join([f"{row['호실']}\t{row['최근검침값']}" for index, row in df.iterrows()])
                st.text_area("아래 상자 안을 클릭 후 전체 선택(Ctrl+A)하여 복사(Ctrl+C)한 뒤, 엑셀에 바로 붙여넣으세요.", value=tsv_text, height=300)
                
            except json.JSONDecodeError:
                st.error("데이터 변환 실패. 사진을 다시 확인해 주세요.")
                st.text_area("AI 원본 결과", value=raw_text)
            except Exception as e:
                st.error(f"오류 발생: {e}")
