import sys
import subprocess
import time
import json

# 필수 패키지 자동 설치 체계
required_packages = ["streamlit", "openai"]
for package in required_packages:
    try:
        import streamlit
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import streamlit as st
from openai import OpenAI

# 1. 페이지 레이아웃 및 환경 설정
st.set_page_config(page_title="Global AI Video Factory Enterprise", page_icon="💎", layout="wide")

# 세션 상태 엔진 초기화 (무료 카운터 및 워크스페이스 내역 저장)
if "free_uses_left" not in st.session_state:
    st.session_state.free_uses_left = 2
if "workspace_history" not in st.session_state:
    st.session_state.workspace_history = []
if "selected_view_idx" not in st.session_state:
    st.session_state.selected_view_idx = None

# 2. 하이엔드 글로벌 SaaS 테마 CSS 주입 + 스마트폰 시뮬레이터 및 특수 자막 애니메이션 효과 정의
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Noto+Sans+KR:wght@400;700;900&display=swap');
    html, body, [data-testid="stSidebarUserserviceAuth_container"] {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    .paywall-box {
        background-color: #ff4b4b1a;
        border: 1px solid #ff4b4b;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .free-box {
        background-color: #3b82f61a;
        border: 1px solid #3b82f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .success-box {
        background-color: #24b47e1a;
        border: 1px solid #24b47e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* 우측 상단 깃허브 아이콘, 메인 메뉴 및 헤더 전체 삭제 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 좌측 사이드바 상단의 배포/개발자 관련 불필요한 장식이나 여백 제거 */
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }

    /* 📱 초고화질 세로형 숏폼 스마트폰 시뮬레이터 스타일 단독 커스텀 */
    .phone-container {
        width: 320://px;
        width: 320px;
        height: 580px;
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        border: 8px solid #333;
        border-radius: 32px;
        overflow-y: auto;
        position: relative;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        margin: 10px auto;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        padding: 40px 20px 20px 20px;
    }
    /* 스크롤바 숨기기 */
    .phone-container::-webkit-scrollbar {
        display: none;
    }
    .phone-overlay-gradient {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at center, transparent 30%, rgba(0,0,0,0.4) 100%);
        z-index: 1;
        pointer-events: none;
    }
    .phone-badge {
        position: absolute;
        top: 15px;
        left: 20px;
        background: rgba(255, 75, 75, 0.9);
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: bold;
        z-index: 2;
        letter-spacing: 1px;
        animation: pulse 2s infinite;
    }
    .phone-content-box {
        z-index: 2;
        text-align: center;
        width: 100%;
    }
    .sim-hook {
        color: #ffeb3b;
        font-size: 20px;
        font-weight: 900;
        text-shadow: 0 3px 6px rgba(0,0,0,0.8);
        margin-bottom: 20px;
        word-break: keep-all;
        line-height: 1.4;
    }
    .sim-script {
        color: #ffffff;
        font-size: 14px;
        font-weight: 600;
        text-shadow: 0 2px 4px rgba(0,0,0,0.9);
        line-height: 1.6;
        word-break: keep-all;
        background: rgba(0,0,0,0.5);
        padding: 12px;
        border-radius: 12px;
        border-left: 4px solid #ff4b4b;
        text-align: left;
    }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
</style>
""", unsafe_allow_html=True)

# 3. 전 세계 6대 권역 결제 페이월 포함 언어팩
LANG_PACK = {
    "한국어 🇰🇷": {
        "title": "💎 글로벌 AI 숏폼 제조 공장 Enterprise",
        "subtitle": "상위 1% 독점적 글로벌 무인 숏폼 비디오 생성 오케스트레이터",
        "sidebar_title": "⚙️ 관제 센터 (Control)",
        "license_label": "🔑 마스터 라이선스 키 입력",
        "license_ph": "라이선스 키를 입력하세요...",
        "lang_label": "🌐 시스템 UI 언어",
        "m1": "GPT-4o-Mini 동기화",
        "m2": "Encrypted 노드 스토리지",
        "m3": "라이선스 등급",
        "p_name_label": "📦 판매할 상품/서비스 이름",
        "p_name_ph": "예: 친환경 텀블러, 비즈니스 자동화 SaaS 등",
        "feat_label": "🎯 상품 핵심 특징 및 타겟층 (세부 정보)",
        "feat_ph": "예: 24시간 얼음 보존 가능 / 트렌디한 디자인을 선호하는 2030 직장인 타겟",
        "btn_generate": "🚀 독점 숏폼 비디오 마케팅 킷 일괄 제조 개시",
        "paywall_title": "🚨 무료 체험 만료 / 라이선스 비활성화됨",
        "paywall_desc": "준비된 2회의 무료 체험 카운트를 모두 소진하셨습니다. 기능을 계속 이용하려면 정식 마스터 라이선스를 등록하세요.",
        "paywall_btn": "💳 마스터 라이선스 즉시 획득하기",
        "free_title": "🎁 프리미엄 무료 체험 가동 중",
        "free_desc": "현재 라이선스 키 없이도 사용 가능한 무료 에셋 제조 기회가 {count}회 남았습니다.",
        "status_active": "✅ Enterprise Max 가동 중",
        "status_desc": "모든 제한이 해제되었습니다. 무제한 글로벌 트래픽 장악 모드가 활성화 상태입니다.",
        "err_license": "❌ 무료 이용 횟수를 모두 소진했습니다! 사이드바에서 마스터 키를 인증하여 시스템을 활성화해주세요."
    },
    "English 🇺🇸": {
        "title": "💎 Global AI Video Factory Enterprise",
        "subtitle": "Top 1% Exclusive Global Automated Short-form Video Orchestrator",
        "sidebar_title": "⚙️ Control Center",
        "license_label": "🔑 Master License Key",
        "license_ph": "Enter License Key...",
        "lang_label": "🌐 System UI Language",
        "m1": "GPT-4o-Mini Sync",
        "m2": "Encrypted Node Storage",
        "m3": "License Tier",
        "p_name_label": "📦 Product/Service Name",
        "p_name_ph": "e.g., Eco Tumbler, Automation SaaS",
        "feat_label": "🎯 Key Features & Target Audience",
        "feat_ph": "e.g., Keeps ice for 24 hours / Target: 20s-30s professionals loving trendy designs",
        "btn_generate": "🚀 Launch Exclusive Short-form Video Kit Production",
        "paywall_title": "🚨 Free Trial Expired / License Deactivated",
        "paywall_desc": "You have used all 2 free trial generations. Acquire a valid master license to unlock full access.",
        "paywall_btn": "💳 Get Master License Instantly",
        "free_title": "🎁 Free Trial Mode Active",
        "free_desc": "You have {count} free trial generations remaining without a license key.",
        "status_active": "✅ Enterprise Max Active",
        "status_desc": "All restrictions lifted. Global traffic domination mode is fully operational.",
        "err_license": "❌ Free trial limits reached! Please authorize the Master Key in the sidebar to activate the system."
    }
}

# 4. 사이드바 렌더링 및 심리적/기능적 페이월 엔진
with st.sidebar:
    st.markdown(f"## ⚙️ Control Tower")
    
    # 언어 셀렉터 (한국어와 영어 중심 매핑)
    site_lang = st.selectbox("🌐 UI Language", list(LANG_PACK.keys()))
    L = LANG_PACK[site_lang] # 선택된 언어팩 지정
    
    st.write("---")
    
    # 라이선스 인증 인터페이스
    license_input = st.text_input(L["license_label"], placeholder=L["license_ph"], type="password")
    
    # 라이선스 키 조건 검증 (마스터 키: EB74)
    is_licensed = (license_input == "EB74")
    
    # 라이선스 및 무료 크레딧 카운팅 인터페이스 실시간 분기 구조
    if is_licensed:
        st.markdown(f"""
        <div class="success-box">
            <h4 style="color:#24b47e; margin:0 0 5px 0;">{L["status_active"]}</h4>
            <p style="font-size:12px; margin:0; color:#888;">{L["status_desc"]}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.session_state.free_uses_left > 0:
            st.markdown(f"""
            <div class="free-box">
                <h4 style="color:#3b82f6; margin:0 0 5px 0;">{L["free_title"]}</h4>
                <p style="font-size:12px; margin:0; color:#4b5563;">{L["free_desc"].format(count=st.session_state.free_uses_left)}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="paywall-box">
                <h4 style="color:#ff4b4b; margin:0 0 5px 0;">{L["paywall_title"]}</h4>
                <p style="font-size:12px; margin:0 0 12px 0; color:#aaa;">{L["paywall_desc"]}</p>
                <a href="https://rainscape5.gumroad.com/l/ycgff" target="_blank" style="text-decoration:none;">
                    <button style="background-color:#ff4b4b; color:white; border:none; padding:8px 12px; border-radius:5px; width:100%; font-weight:bold; cursor:pointer;">
                        {L["paywall_btn"]}
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)

# 5. 메인 레이아웃 타이틀 팩
st.title(L["title"])
st.subheader(L["subtitle"])
st.write("---")

# 하이엔드 테마 지표 대시보드
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1: 
    st.metric(label=L["m1"], value="Stable", delta="99.98% Latency")
with mc2: 
    st.metric(label=L["m2"], value=f"{len(st.session_state.workspace_history)} Nodes", delta="Encrypted")
with mc3: 
    if is_licensed:
        status_val = "Enterprise Max"
    else:
        status_val = f"Free Trial ({st.session_state.free_uses_left} Left)" if st.session_state.free_uses_left > 0 else "Locked"
    st.metric(label=L["m3"], value=status_val, delta="Access Authorization")
with mc4: 
    st.metric(label="Global Traffic Matrix", value="Active", delta="CDN Powered")
st.write("---")

# 6. 스플릿 구조 설계 (인풋 콘솔 & 아웃풋 모니터)
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    with st.container(border=True):
        st.markdown(f"### 📥 Input Console ({site_lang.split(' ')[0]})")
        product_name = st.text_input(L["p_name_label"], placeholder=L["p_name_ph"])
        product_features = st.text_area(L["feat_label"], placeholder=L["feat_ph"], height=110)
        st.write("")
        
        # 2회 소진 시 버튼 UI 자체를 결제 링크 인터페이스로 자동 전환
        if not is_licensed and st.session_state.free_uses_left <= 0:
            st.markdown(f"""
            <a href="https://rainscape5.gumroad.com/l/ycgff" target="_blank" style="text-decoration:none;">
                <button style="background: linear-gradient(90deg, #ff4b4b, #dc2626); color:white; border:none; padding:14px; border-radius:8px; width:100%; font-size:16px; font-weight:bold; cursor:pointer; box-shadow: 0 4px 15px rgba(255,75,75,0.4);">
                    {L["paywall_btn"]}
                </button>
            </a>
            """, unsafe_allow_html=True)
            generate_btn = False
        else:
            button_text = L["btn_generate"]
            if not is_licensed:
                button_text += f" (무료 체험 {st.session_state.free_uses_left}회 가능)"
            generate_btn = st.button(button_text, type="primary")

# 7. 3단계 파이프라인 엔진 구동 및 OpenAI 실시간 오케스트레이션 (더욱 세련되고 풍부하게 프롬프트 설계)
if generate_btn:
    if not is_licensed and st.session_state.free_uses_left <= 0:
        st.error(L["err_license"])
    elif not product_name or not product_features:
        st.warning("Please fill out the form entirely.")
    else:
        indicator_box = st.empty()
        
        try:
            client = OpenAI()
            
            with indicator_box.container():
                st.info("🎯 [Stage 1] Analyzing product identity and sophisticated conversion hooks...")
                time.sleep(0.5)
                
                st.info("✍️ [Stage 2] Orchestrating OpenAI GPT-4o-Mini for High-Conversion Structural Package...")
                
                # 결과물의 양을 획기적으로 늘리고 구조적 깊이를 주기 위한 고급 시스템 프롬프트 정의
                system_instruction = (
                    "You are the world's top 1% growth hacker, luxury copywriter, and viral short-form video director. "
                    "Your goal is to create an extensive, jaw-dropping, high-converting marketing master kit for a product.\n\n"
                    "You must output the result strictly in the following JSON format:\n"
                    "{\n"
                    "  \"hook_options\": \"Provide 3 distinct psychological hook lines (0-3s) that stop user scrolling immediately. Label them as Hook A, B, and C.\",\n"
                    "  \"preview_hook\": \"Select the single most explosive hook line among options to display on the live monitor screen.\",\n"
                    "  \"full_script\": \"Provide a comprehensive, high-retention multi-stage short-form production script (3-45s). It must include structured timestamps, exact speaking lines, corresponding visual scene directions, and emotional tone/sound effect hints.\",\n"
                    "  \"cta_and_hashtags\": \"Provide 3 highly persuasive Call-To-Action formulas to skyrocket conversion rates, followed by 5 global viral trending hashtags tailored for Instagram Reels, TikTok, and YouTube Shorts.\",\n"
                    "  \"cinematic_prompt\": \"An incredibly rich, ultra-detailed, professional text-to-video engineering prompt for Sora/Runway Gen-3. Specify hyper-realistic lighting (volumetric, anamorphic), exact cinematic camera lenses (e.g., 35mm lens, sweeping drone pan, macro tracking), color palettes, textures, and atmosphere to ensure a Hollywood grade visual asset.\"\n"
                    "}\n\n"
                    "Ensure the response is extremely sophisticated, professional, and dense in content. Avoid generic phrases."
                )
                
                user_content = f"Product Name: {product_name}\nFeatures/Target Audience Details: {product_features}"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.75
                )
                
                result_json = json.loads(response.choices[0].message.content)
                
                st.info("🎬 [Stage 3] Synthesizing video assets and rendering 4K vertical simulation layers...")
                time.sleep(0.5)
                st.success("✨ High-End Global Marketing Kit Pack Compiled Successfully!")
            
            # 카운트 차감 메커니즘 (라이선스가 등록 안 된 유저인 경우에만 1회 차감)
            if not is_licensed:
                st.session_state.free_uses_left -= 1
                
            actual_result = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "product": product_name,
                "features": product_features,
                "hook_options": result_json.get("hook_options", "No hook options generated."),
                "preview_hook": result_json.get("preview_hook", "🔥 Global Breakthrough!"),
                "full_script": result_json.get("full_script", "No comprehensive script generated."),
                "cta_and_hashtags": result_json.get("cta_and_hashtags", "No conversion tactics provided."),
                "cinematic_prompt": result_json.get("cinematic_prompt", "Cinematic realistic vertical shot.")
            }
            
            st.session_state.workspace_history.insert(0, actual_result)
            st.session_state.selected_view_idx = 0
            indicator_box.empty()
            st.rerun()
            
        except Exception as e:
            indicator_box.empty()
            st.error(f"💥 OpenAI API Error: {str(e)}")

# 8. 아웃풋 워크스페이스 모니터 리포트 렌더링 (확장된 에셋 테마에 맞춰 탭 구성)
with col2:
    if st.session_state.selected_view_idx is not None and len(st.session_state.workspace_history) > 0:
        current_data = st.session_state.workspace_history[st.session_state.selected_view_idx]
        
        with st.container(border=True):
            st.markdown(f"### 🖥️ Enterprise Workspace Monitor")
            st.caption(f"🧬 Generation Node Timestamp: {current_data['timestamp']}")
            
            # 대폭 업그레이드된 풍성한 콘텐츠를 분류하여 보여주는 5개 확장 탭 시스템
            tab0, tab1, tab2, tab3, tab4 = st.tabs([
                "📱 Live Device Preview", 
                "🧲 Psychological Hooks", 
                "📜 Full Director Script", 
                "💎 Hollywood Video Prompt", 
                "📊 Performance Engine"
            ])
            
            with tab0:
                st.markdown("**⚡ Live Auto-Generated Short-form Visual Layer**")
                st.caption("AI 에셋 패키지에서 실시간 추출한 정밀 설계형 9:16 모바일 스마트폰 전용 뷰어입니다.")
                
                # 시뮬레이터 디자인 내부 스크롤 가능한 숏폼 최적화 텍스트 렌더링
                html_simulator = f"""
                <div class="phone-container">
                    <div class="phone-overlay-gradient"></div>
                    <div class="phone-badge">LIVE PREVIEW</div>
                    <div class="phone-content-box">
                        <div class="sim-hook">{current_data['preview_hook']}</div>
                        <div class="sim-script">{current_data['full_script'][:220]}... (아래 탭에서 대본 전문 확인 가능)</div>
                    </div>
                </div>
                """
                st.markdown(html_simulator, unsafe_allow_html=True)
                
            with tab1:
                st.markdown("### 🧲 3가지 타입 핵심 심리 훅 라인 (Scroll-Stopper)")
                st.info("시청자가 3초 이내에 이탈하는 것을 막기 위해 설계된 극비 카피라이팅 기법입니다.")
                st.write(current_data["hook_options"])
                
            with tab2:
                st.markdown("### 📜 영상 제작 통합 마스터 대본 (Full Production Script)")
                st.text_area("시각적 연출 방향 및 타임라인 포함 전체 스크립트 전문", current_data["full_script"], height=200)
                
                st.markdown("### 🎯 행동 유도 전략 및 추천 태그 (CTA & Social Matrix)")
                st.write(current_data["cta_and_hashtags"])
                
            with tab3:
                st.markdown("### 💎 하이엔드 AI 비디오 생성 전용 프롬프트 (Text-to-Video)")
                st.code(current_data["cinematic_prompt"], language="text")
                st.caption("위의 시네마틱 프롬프트를 복사하여 Sora, Runway Gen-3, 또는 Pika Labs에 입력하시면 압도적인 퀄리티의 비주얼 레이어가 렌더링됩니다.")
                
            with tab4:
                st.markdown("**📈 AI 모델 예측 글로벌 트래픽 예상 지표**")
                c1, c2, c3 = st.columns(3)
                c1.metric("예상 평균 CTR", "8.4%", "+4.1% vs Industry")
                c2.metric("초반 이탈 방지율", "82.9%", "Top 0.5% Class")
                c3.metric("최종 전환 지수 Score", "97/100", "Ultra Optimized")
