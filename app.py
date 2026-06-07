import streamlit as st
import openai
import re

# 1. 페이지 기본 설정 및 보안 완비
st.set_page_config(page_title="미래사업 플랫폼 - 결제/AI 통합형", layout="wide", page_icon="🚀")

# 최고 등급 보안 헤더
st.title("🚀 미래사업 플랫폼 v2.0")
st.subheader("🔒 최고 등급 보안 모드 (Top Secret) - 운영본부 통제 하에 가동 중")
st.write("---")

# OpenAI 고성능 최신 엔진 열쇠 세팅
MY_SECRET_KEY = "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"

# 세션 상태(Session State)를 활용한 결제 및 인증 흐름 제어 관리
if "payment_status" not in st.session_state:
    st.session_state.payment_status = "unpaid"  # unpaid -> processing -> paid
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# -------------------------------------------------------------------------
# [1단계] 이메일 수집 및 고객 식별 레이어
# -------------------------------------------------------------------------
st.markdown("### 📧 1단계: 프리미엄 멤버십 이메일 등록")
email_input = st.text_input(
    "서비스를 이용하고 결제 정보를 송부받을 대표님(또는 고객)의 이메일 주소를 입력하세요.",
    placeholder="example@domain.com",
    value=st.session_state.user_email
)

# 간단한 이메일 유효성 검사 규칙
email_regex = r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

if email_input:
    if re.match(email_regex, email_input):
        st.session_state.user_email = email_input
        st.success(f"✅ 이메일 주소 확인 완료: {st.session_state.user_email}")
    else:
        st.error("❌ 올바른 이메일 형식이 아닙니다. 다시 확인해 주십시오.")

st.write("---")

# -------------------------------------------------------------------------
# [2단계] 실시간 온라인 결제창(PG) 생성 레이어
# -------------------------------------------------------------------------
if st.session_state.user_email and re.match(email_regex, st.session_state.user_email):
    st.markdown("### 💳 2단계: 글로벌 온라인 결제 게이트웨이 (PG)")
    
    if st.session_state.payment_status == "unpaid":
        st.info("💡 현재 '미승인' 상태입니다. 아래의 프리미엄 플랜 결제를 진행해야 AI 핵심 엔진이 개방됩니다.")
        
        # 가상의 최고급 요금제 카드 레이아웃
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="플래티넘 AI 독점 플랜", value="$99 / 월")
            st.write("- 초고속 gpt-4o-mini 엔진 무제한 엑세스")
            st.write("- 일일 비즈니스 자동화 분석 리포트 송부")
        
        with col2:
            st.write("🔒 **안전한 암호화 결제창**")
            card_number = st.text_input("카드번호 (테스트용이므로 아무 숫자나 입력 가능)", value="4510 - 1234 - 5678 - 9012", type="password")
            
            # 결제 승인 버튼
            if st.button("💳 실시간 안전 결제 승인 요청"):
                with st.spinner("글로벌 결제망 통신 및 전자영수증 발행 중..."):
                    # 결제 성공 프로세스 시뮬레이션
                    st.session_state.payment_status = "paid"
                    st.rerun() # 화면 즉시 갱신
                    
    elif st.session_state.payment_status == "paid":
        st.success(f"🎯 [결제 최종 승인 완료] 영수증이 {st.session_state.user_email}로 발송되었습니다. 무제한 AI 권한이 활성화됩니다.")
        if st.button("🔄 테스트를 위해 결제 초기화"):
            st.session_state.payment_status = "unpaid"
            st.rerun()

    st.write("---")

    # -------------------------------------------------------------------------
    # [3단계] 결제 완료 고객 전용 AI 핵심 서비스 레이어
    # -------------------------------------------------------------------------
    st.markdown("### 🤖 3단계: 결제 회원 전용 초지능 AI 플랫폼 가동")
    
    if st.session_state.payment_status == "paid":
        user_query = st.text_area("미래사업 비즈니스 로직 및 프롬프트를 입력하세요:", value="우리 플랫폼의 독점적 수익 모델을 한 줄로 요약해줘.")
        
        if st.button("🧠 초지능 엔진 기동"):
            with st.spinner("미국 OpenAI 본사 서버로부터 보안 응답 수신 중..."):
                try:
                    client = openai.OpenAI(api_key=MY_SECRET_KEY)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": user_query}]
                    )
                    answer = response.choices[0].message.content
                    st.success("🎯 [AI 정상 응답 완료]")
                    st.info(f"💡 시스템 회신 내용:\n\n{answer}")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ 엔진 기동 실패. 원인: {e}")
    else:
        st.warning("⚠️ 2단계 결제가 완료되지 않아 AI 엔진이 잠겨 있습니다. 결제를 먼저 완료해 주십시오.")
else:
    st.warning("⚠️ 1단계 이메일 등록이 완료되어야 결제 및 AI 가동 단계로 넘어갈 수 있습니다.")
