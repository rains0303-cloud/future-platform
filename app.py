import streamlit as st
import openai

st.set_page_config(page_title="AI 심장 이식 테스트", layout="wide")
st.title("🚀 미래사업 플랫폼 - AI 엔진 최종 결합")
st.write("---")
st.success("1단계 검증 완료: Streamlit 화면 엔진이 정상 가동 중입니다.")

# ⚠️ [대표님 필수 조치] 아래 따옴표 안을 지우고 sk-proj...로 시작하는 새 키를 넣어주세요.
MY_SECRET_KEY = "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"

st.info("아래 버튼을 누르면 이 컴퓨터에서 OpenAI 본사 서버로 직접 신호를 보냅니다.")

if st.button("🤖 AI 엔진 실시간 가동 테스트 시작"):
    with st.spinner("미국 OpenAI 본사 서버 연결 중..."):
        try:
            # 신형/구형 파이썬 라이브러리 자동 호환 코딩
            if hasattr(openai, 'OpenAI'):
                client = openai.OpenAI(api_key=MY_SECRET_KEY)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "연결 성공이라고 짧게 답해줘."}]
                )
                answer = response.choices[0].message.content
            else:
                openai.api_key = MY_SECRET_KEY
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "연결 성공이라고 짧게 답해줘."}]
                )
                answer = response.choices[0].message.content
            
            st.success(f"🎯 [최종 합격] AI가 정상 응답했습니다! -> {answer}")
            st.balloons() # 성공 축하 풍선 발사
        except Exception as e:
            st.error(f"❌ [가동 실패] 열쇠 거부됨. 원인: {e}")
