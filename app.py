# ====================================================================
# 4. [완벽 통합] 사이드바 제어, 다국어 매트릭스 및 24/7 무인 AI CS 엔진
# ====================================================================

st.sidebar.title("⚙️ Global Control Center")

# [시스템 UI 언어 선택 스위치]
site_lang = st.sidebar.selectbox("🗺️ Choose System UI Language", list(LANG_PACK.keys()), index=0)
L = LANG_PACK[site_lang]
st.sidebar.write("---")

# [OpenAI API 키 입력창]
api_key_input = st.sidebar.text_input("🔑 OpenAI API KEY", type="password", placeholder="sk-...")
st.sidebar.write("")


# --------------------------------------------------------------------
# 🔥 [EB74 LABS 독점 특허] 24/7 글로벌 무인 AI CS 헬프데스크 엔진 자동 구동 구간
# --------------------------------------------------------------------
st.sidebar.write("---")
st.sidebar.markdown("### 🎧 24/7 Global AI Support (Auto-CS)")

# 전 세계 6개국 사용자가 자국어로 자유롭게 질문을 입력하는 현실 창
cs_inquiry = st.sidebar.text_area(
    "Inquiry / Support", 
    placeholder="Ask anything in your language... (e.g., How to upgrade?)"
)

if st.sidebar.button("⚡ Submit Inquiry", use_container_width=True):
    if not api_key_input:
        st.sidebar.error("Please enter OpenAI API KEY first.")
    elif not cs_inquiry:
        st.sidebar.warning("Please type your question.")
    else:
        with st.sidebar.spinner("AI Agent processing..."):
            try:
                # 파트너님의 OpenAI API 키를 시스템에 실시간 동적 연결
                client = OpenAI(api_key=api_key_input)
                
                # 6개국 언어를 자동 감지하여 현지어로 완벽 대응하는 시스템 마스터 프롬프트 주입
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "You are the 24/7 AI Customer Support Agent for 'Global AI Short-form Video Factory'. "
                                "The master activation key is EB74. The official support email is rains0303@gmail.com. "
                                "Detect the user's language and reply perfectly in that same language. "
                                "Be extremely polite, professional, and helpful. If the issue is critical, "
                                "tell them to contact rains0303@gmail.com, but resolve 99% of user usage inquiries here."
                            )
                        },
                        {"role": "user", "content": cs_inquiry}
                    ],
                    temperature=0.3
                )
                
                # 무인 답변 출력 (현실에서 파트너님의 노동력 0% 달성)
                st.sidebar.success("🤖 AI Agent Response:")
                st.sidebar.write(response.choices[0].message.content)
                
            except Exception as e:
                st.sidebar.error(f"System Error: {str(e)}")
# --------------------------------------------------------------------


st.sidebar.write("---")
st.sidebar.markdown("### 📂 Enterprise Workspace")

# [프로젝트 아카이브 히스토리 제어 엔진]
if not st.session_state.workspace_history:
    st.sidebar.caption("No archived project. Please generate content.")
else:
    for idx, item in enumerate(st.session_state.workspace_history):
        icon = "🔥" if st.session_state.selected_view_idx == idx else "📄"
        if st.sidebar.button(f"{icon} {item['name']} ({item['lang']})", key=f"hist_{idx}", use_container_width=True):
            st.session_state.selected_view_idx = idx
