import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json

# 페이지 기본 설정
st.set_page_config(page_title="GB F&C 검침표 자동 추출", layout="centered")

# 대시보드 스타일 지정을 위한 선언
st.markdown("""
    <style>
    .main-header {
        background-color: #1E3A8A;
        padding: 25px;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .company-tag {
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 3px;
        margin-bottom: 5px;
        color: #93C5FD;
    }
    .system-title {
        font-size: 26px;
        font-weight: bold;
        margin: 0;
    }
    .info-box {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 6px;
        border-left: 5px solid #1E3A8A;
        margin-bottom: 20px;
    }
    </style>
    
    <div class="main-header">
        <div class="company-tag">GB F&C PROPERTY MANAGEMENT</div>
        <div class="system-title">수도 · 전기 검침 데이터 자동 추출 시스템</div>
    </div>
    
    <div class="info-box">
        <strong>사용 안내:</strong> 현장에서 촬영한 검침표 사진을 업로드하면 최신 검침값만 자동으로 추출됩니다. 분석 완료 후 표 데이터를 복사하여 관리비 정산 엑셀에 붙여넣으세요.
    </div>
""", unsafe_allow_html=True)

api_key = st.secrets["API_KEY"]
uploaded_file = st.file_uploader("검침표 사진 등록 (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="등록된 검침표 이미지", use_container_width=True)
    
    if st.button("AI 정밀 분석 시작", use_container_width=True):
        genai.configure(api_key=api_key)
        # 최신 2.5 Pro 모델로 수정 완료
        model = genai.GenerativeModel("gemini-2.5-pro")
        
        with st.spinner("GB F&C 데이터 정밀 분석 중..."):
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
                
                st.markdown("### 📊 추출 결과 확인")
                
                # 결과 시각화 및 편집 가능한 표 제공
                st.data_editor(df, use_container_width=True)
                
                # 엑셀 붙여넣기 전용 텍스트 영역
                st.markdown("### 📋 엑셀 복사 전용 데이터")
                tsv_text = "호실\t최근검침값\n" + "\n".join([f"{row['호실']}\t{row['최근검침값']}" for index, row in df.iterrows()])
                st.text_area("아래 상자를 클릭하고 전체 선택(Ctrl+A) 후 복사(Ctrl+C)하여 엑셀에 바로 붙여넣으십시오.", value=tsv_text, height=250)
                
            except json.JSONDecodeError:
                st.error("데이터 변환에 실패했습니다. 사진 상태를 확인하고 다시 시도해 주십시오.")
                st.text_area("AI 원본 답변 데이터", value=raw_text)
            except Exception as e:
                st.error(f"시스템 오류 발생: {e}")
