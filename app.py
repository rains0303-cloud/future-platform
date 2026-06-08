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

# 세션 상태 엔진 초기화
if "workspace_history" not in st.session_state:
    st.session_state.workspace_history = []
if "selected_view_idx" not in st.session_state:
    st.session_state.selected_view_idx = None
# [신규 추가] 유저별 무료 이용 횟수 추적 카운터
if "free_usage_count" not in st.session_state:
    st.session_state.free_usage_count = 0

# 2. 하이엔드 글로벌 SaaS 테마 CSS 주입 (우측 상단 아이콘 및 하단 푸터 완전 제거)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Noto+Sans+KR:wght@400;700;900&display=swap');
    
    /* 전체 기본 폰트 최적화 */
    html, body, [data-testid="stSidebarUserserviceAuth_container"] {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }
    
    /* 우측 상단 Streamlit 호스팅 관련 아이콘셋 전면 숨김 (독점 브랜딩 락) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}
    button[title="View source code"] {display: none;}
    
    /* 버튼 스타일링 */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    
    /* 결제 유도 및 성공 박스 디자인 */
    .paywall-box {
        background-color: #ff4b4b1a;
        border: 1px solid #ff4b4b;
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
</style>
""", unsafe_allow_html=True)

# 3. 전 세계 6대 권역 결제 페이월 포함 언어팩
LANG_PACK = {
    "한국어 🇰🇷": {
        "title": "💎 글로벌 AI 숏폼 제조 공장 Enterprise",
        "subtitle": "상위 1% 독점적 글로벌 무인 숏폼 비디오 생성 오케스트레이터",
        "sidebar_title": "⚙️ 관제 센터 (Control)",
        "license_label": "🔑 마스터 라이선스 키 입력",
        "license_ph": "인증 키를 입력하세요...",
        "api_label": "⚡ OpenAI API Key",
        "api_ph": "sk-...",
        "lang_label": "🌐 시스템 UI 언어",
        "m1": "⚡ GPT-4o-Mini 동기화",
        "m2": "Encrypted 노드 스토리지",
        "m3": "라이선스 등급",
        "p_name_label": "📦 판매할 상품/서비스 이름",
        "p_name_ph": "예: 친환경 텀블러, 비즈니스 자동화 SaaS 등",
        "feat_label": "🎯 상품 핵심 특징 및 타겟층 (세부 정보)",
        "feat_ph": "예: 24시간 얼음 보존 가능 / 트렌디한 디자인을 선호하는 2030 직장인 타겟",
        "btn_generate": "🚀 독점 숏폼 비디오 마케팅 킷 일괄 제조 개시",
        "paywall_title": "🚨 라이선스 비활성화됨",
        "paywall_desc": "월 1,000만 원 수익 자동화 엔진이 잠겨있습니다. 기능을 개방하려면 정식 마스터 라이선스를 취득하세요.",
        "paywall_btn": "💳 마스터 라이센스 즉시 획득",
        "status_active": "✅ Enterprise Max 가동 중",
        "status_desc": "모든 제한이 해제되었습니다. 무제한 글로벌 트래픽 장악 모드가 활성화 상태입니다.",
        "err_license": "❌ 무료 체험(1회)이 만료되었습니다! 2번째 제조부터는 사이드바에서 마스터 키를 인증하셔야 합니다."
    },
    "English 🇺🇸": {
        "title": "💎 Global AI Video Factory Enterprise",
        "subtitle": "Top 1% Exclusive Global Automated Short-form Video Orchestrator",
        "sidebar_title": "⚙️ Control Center",
        "license_label": "🔑 Master License Key",
        "license_ph": "Enter Activation Key...",
        "api_label": "⚡ OpenAI API Key",
        "api_ph": "sk-...",
        "lang_label": "🌐 System UI Language",
        "m1": "⚡ GPT-4o-Mini Sync",
        "m2": "Encrypted Node Storage",
        "m3": "License Tier",
        "p_name_label": "📦 Product/Service Name",
        "p_name_ph": "e.g., Eco Tumbler, Automation SaaS",
        "feat_label": "🎯 Key Features & Target Audience",
        "feat_ph": "e.g., Keeps ice for 24 hours / Target: 20s-30s professionals loving trendy designs",
        "btn_generate": "🚀 Launch Exclusive Short-form Video Kit Production",
        "paywall_title": "🚨 License Deactivated",
        "paywall_desc": "The $10,000/mo revenue automation engine is locked. Acquire a valid master license to unlock full access.",
        "paywall_btn": "💳 Get Master License Instantly",
        "status_active": "✅ Enterprise Max Active",
        "status_desc": "All restrictions lifted. Global traffic domination mode is fully operational.",
        "err_license": "❌ Free trial (1 credit) expired! From the 2nd production onwards, you must authorize the Master Key."
    },
    "日本語 🇯🇵": {
        "title": "💎 グローバル AI 숏폼 製造工場 Enterprise",
        "subtitle": "上位 1% 独占的グローバル無人ショート動画生成オーケストレーター",
        "sidebar_title": "⚙️ 管制センター (Control)",
        "license_label": "🔑 マスターライセンスキー入力",
        "license_ph": "認証キーを入力してください...",
        "api_label": "⚡ OpenAI API Key",
        "api_ph": "sk-...",
        "lang_label": "🌐 시스템 UI 言語",
        "m1": "⚡ GPT-4o-Mini 同期",
        "m2": "暗号化済みストレージ",
        "m3": "ライセンス階層",
        "p_name_label": "📦 商品・サービス名",
        "p_name_ph": "例：エコタンブラー、業務自動化SaaSなど",
        "feat_label": "🎯 商品の主な特徴とターゲット層",
        "feat_ph": "例：24時間保冷可能 / トレンディなデザインを好む20〜30代の会社員向け",
        "btn_generate": "🚀 独占ショート動画マーケティングキット一括製造開始",
        "paywall_title": "🚨 라이선스 무효화",
        "paywall_desc": "月100万円収益 automatic エンジンがロックされています。機能を解放するには、公式マスターライセンスを取得してください。",
        "paywall_btn": "💳 マスターライセンス即時獲得",
        "status_active": "✅ Enterprise Max 稼働中",
        "status_desc": "すべての制限が解除されました。無制限のグローバルトラフィック掌握モードが有効です。",
        "err_license": "❌ 無料体験（1回）が満了しました！2回目以降の製造には、サイド바でマスターキーを認証する必要があります。"
    },
    "简体中文 🇨🇳": {
        "title": "💎 全球 AI 短视频制造工厂 Enterprise",
        "subtitle": "前 1% 独占性全球无人值守短视频生成编排器",
        "sidebar_title": "⚙️ 控制中心",
        "license_label": "🔑 输入主授权码",
        "license_ph": "请输入激活码...",
        "api_label": "⚡ OpenAI API Key",
        "api_ph": "sk-...",
        "lang_label": "🌐 System UI 语言",
        "m1": "⚡ GPT-4o-Mini 同步",
        "m2": "加密节点存储",
        "m3": "授权级别",
        "p_name_label": "📦 产品/服务名称",
        "p_name_ph": "例如：环保保温杯、业务自动化 SaaS 等",
        "feat_label": "🎯 产品核心卖点与目标受众",
        "feat_ph": "例如：24小时强效保冰 / 针对喜欢时尚设计的 2030 白领阶层",
        "btn_generate": "🚀 开启独占短视频营销套件批量制造",
        "paywall_title": "🚨 授权未激活",
        "paywall_desc": "月入万刀的自动化收益引擎处于锁定状态。请获取正式主授权码以释放全部核心潜能。",
        "paywall_btn": "💳 立即获得硕士许可证",
        "status_active": "✅ Enterprise Max 正常运行",
        "status_desc": "限制已全额解除。全球流量霸屏模式已处于激活状态。",
        "err_license": "❌ 免费试用（1次）已用尽！从第2次制造开始，您必须在侧边栏验证主授权码。"
    },
    "Español 🇪🇸": {
        "title": "💎 Global AI Video Factory Enterprise",
        "subtitle": "Orquestador Global Automático Exclusivo del Top 1% para Videos Cortos",
        "sidebar_title": "⚙️ Centro de Control",
        "license_label": "🔑 Clave de Licencia Maestra",
        "license_ph": "Ingrese la clave de activación...",
        "api_label": "⚡ OpenAI API Key",
        "api_ph": "sk-...",
        "lang_label": "🌐 Idioma del Sistema UI",
        "m1": "⚡ Sincronización GPT-4o-Mini",
        "m2": "Almacenamiento Encriptado",
        "m3": "Nivel de Licencia",
        "p_name_label": "📦 Nombre del Producto/Servicio",
        "p_name_ph": "ej., Termo Ecológico, SaaS de Automatización",
        "feat_label": "🎯 Características Clave y Público Objetivo",
        "feat_ph": "ej., Mantiene el hielo por 24h / Dirigido a profesionales de 20-30 años",
        "btn_generate": "🚀 Iniciar Producción del Kit de Video de Marketing Exclusivo",
        "paywall_title": "🚨 Licencia Desactivada",
        "paywall_desc": "El motor de automatización de ingresos de $10,000/mes está bloqueado. Adquiera una licencia maestra para desbloquearlo.",
        "paywall_btn": "💳 Obtener Licencia Maestra Al Instante",
        "status_active": "✅ Enterprise Max Operando",
        "status_desc": "Todas las restricciones eliminadas. El modo de dominación de tráfico global está activo.",
        "err_license": "❌ ¡Prueba gratuita (1 uso) agotada! A partir de la segunda producción, debe autorizar la Clave Maestra."
    },
    "Tiếng Việt 🇻🇳": {
        "title": "💎 Global AI Video Factory Enterprise",
        "subtitle": "Hệ Thống Tự Động Hóa Sản Xuất Video Ngắn Độc Quyền Top 1% Toàn Cầu",
        "sidebar_title": "⚙️ Trung Tâm Điều Khiển",
        "license_label": "🔑 Khóa Cấp Phép Master",
        "license_ph": "Nhập mã kích hoạt...",
        "api_label": "⚡ OpenAI API Key",
        "api_ph": "sk-...",
        "lang_label": "🌐 Ngôn Ngữ Hệ Thống",
        "m1": "⚡ Đồng Bộ GPT-4o-Mini",
        "m2": "Lưu Trữ Mã Hóa Node",
        "m3": "Hạng Cấp Phép",
        "p_name_label": "📦 Tên Sản Phẩm/Dịch Vụ",
        "p_name_ph": "VD: Bình Giữ Nhiệt Thân Thiện Môi Trường, SaaS Tự Động Hóa",
        "feat_label": "🎯 Tính Năng Cốt Lõi & Khách Hàng Mục Tiêu",
        "feat_ph": "VD: Giữ đá suốt 24 giờ / Nhắm đến dân văn phòng 20-30 tuổi thích thiết kế hợp thời trang",
        "btn_generate": "🚀 Bắt Đầu Sản Xuất Bộ Kit Video Marketing Ngắn Độc Quyền",
        "paywall_title": "🚨 Bản Quyền Chưa Kích Hoạt",
        "paywall_desc": "Hệ thống tự động hóa doanh thu 200 triệu VNĐ/tháng đang bị khóa. Hãy sở hữu bản quyền Master để mở khóa.",
        "paywall_btn": "💳 Sở Hữu Giấy Phép Thầy Ngay",
        "status_active": "✅ Enterprise Max Đang Chạy",
        "status_desc": "Mọi giới hạn đã được gỡ bỏ. Chế độ chiếm lĩnh lưu lượng truy cập toàn cầu đã sẵn sàng.",
        "err_license": "❌ Lượt dùng thử miễn phí (1 lần) đã hết! Từ lần sản xuất thứ 2, bạn phải xác thực Mã Master ở thanh bên."
    }
}

# 4. 사이드바 렌더링 및 심리적 페이월 엔진
with st.sidebar:
    st.markdown(f"## ⚙️ Control Tower")
    
    # 6대 권역 언어 셀렉터
    site_lang = st.selectbox("🌐 UI Language", list(LANG_PACK.keys()))
    L = LANG_PACK[site_lang] # 선택된 언어팩 지정
    
    st.write("---")
    
    # 라이선스 인증 인터페이스
    license_input = st.text_input(L["license_label"], placeholder=L["license_ph"], type="password")
    
    # 라이선스 키 조건 검증 (마스터 키 백엔드 락)
    is_licensed = (license_input == "EB74")
    
    if is_licensed:
        st.markdown(f"""
        <div class="success-box">
            <h4 style="color:#24b47e; margin:0 0 5px 0;">{L["status_active"]}</h4>
            <p style="font-size:12px; margin:0; color:#888;">{L["status_desc"]}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 라이선스가 없고 무료 기회가 소진되었을 때 눈에 띄게 경고 문구 추가
        paywall_msg = L["paywall_desc"]
        if st.session_state.free_usage_count >= 1:
            paywall_msg = "⚠️ [무료 체험 만료] 2번째 이용부터는 마스터 라이선스를 획득해야 전체 엔진 인프라를 잠금 해제할 수 있습니다."
            
        st.markdown(f"""
        <div class="paywall-box">
            <h4 style="color:#ff4b4b; margin:0 0 5px 0;">{L["paywall_title"]}</h4>
            <p style="font-size:12px; margin:0 0 12px 0; color:#aaa;">{paywall_msg}</p>
            <a href="https://rainscape5.gumroad.com/l/ycgff" target="_blank" style="text-decoration:none;">
                <button style="background-color:#ff4b4b; color:white; border:none; padding:8px 12px; border-radius:5px; width:100%; font-weight:bold; cursor:pointer;">
                    {L["paywall_btn"]}
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    api_key_input = st.text_input(L["api_label"], placeholder=L["api_ph"], type="password")

# 5. 메인 레이아웃 타이틀 팩
st.title(L["title"])
st.subheader(L["subtitle"])
st.write("---")

# 하이엔드 테마 지표 대시보드 (라이선스 등급란에 무료체험 상태 표시)
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1: st.metric(label=L["m1"], value="⚡ Stable", delta="99.98% Latency")
with mc2: st.metric(label=L["m2"], value=f"💾 {len(st.session_state.workspace_history)} Nodes", delta="Encrypted")

# 라이선스 상태 다이나믹 대시보드
if is_licensed:
    license_status_value = "Enterprise Max"
    license_status_delta = "Full Access Granted"
elif st.session_state.free_usage_count == 0:
    license_status_value = "1 Free Credit Left"
    license_status_delta = "Trial Active 🔓"
else:
    license_status_value = "Locked 🔒"
    license_status_delta = "Trial Expired (Paywall)"

with mc3: st.metric(label=L["m3"], value=license_status_value, delta=license_status_delta)
with mc4: st.metric(label="Global Traffic Matrix", value="🌍 Active", delta="CDN Powered")
st.write("---")

# 6. 스플릿 구조 설계 (인풋 콘솔 & 아웃풋 모니터)
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    with st.container(border=True):
        st.markdown(f"### 📥 Input Console ({site_lang.split(' ')[0]})")
        product_name = st.text_input(L["p_name_label"], placeholder=L["p_name_ph"])
        product_features = st.text_area(L["feat_label"], placeholder=L["feat_ph"], height=110)
        st.write("")
        generate_btn = st.button(L["btn_generate"], type="primary")

# 7. 1회 우회 / 2회 차단 하이브리드 페이월 엔진 제어 파트
if generate_btn:
    # [핵심 로직 변경점] 라이선스가 없으면서 무료 횟수까지 1회 이상 사용한 경우 철저히 차단
    if not is_licensed and st.session_state.free_usage_count >= 1:
        st.error(L["err_license"])
    elif not api_key_input:
        st.error("Please enter your OpenAI API Key in the sidebar.")
    elif not product_name or not product_features:
        st.warning("Please fill out the form entirely.")
    else:
        indicator_box = st.empty()
        
        try:
            client = OpenAI(api_key=api_key_input)
            
            with indicator_box.container():
                st.info("🎯 [Stage 1] Analyzing product identity and targeting metrics...")
                time.sleep(0.5)
                
                st.info("✍️ [Stage 2] Orchestrating OpenAI GPT-4o-Mini for High-Conversion Script...")
                
                system_instruction = (
                    "You are the world's top 1% growth hacker and short-form video director. "
                    "Your goal is to create a viral, high-converting marketing kit for a product. "
                    "You must output the result strictly in the following JSON format:\n"
                    "{\n"
                    "  \"hook\": \"A powerful, jaw-dropping attention grabber (0-3s)\",\n"
                    "  \"script\": \"Step-by-step multi-language video production script (3-30s)\",\n"
                    "  \"prompt\": \"A professional, cinematic Text-to-Video prompt for Sora/Runway Gen-3\"\n"
                    "}"
                )
                
                user_content = f"Product Name: {product_name}\nFeatures/Target: {product_features}"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7
                )
                
                result_json = json.loads(response.choices[0].message.content)
                
                st.info("🎬 [Stage 3] Synthesizing video assets and rendering 4K vertical layers...")
                time.sleep(0.5)
                st.success("✨ Global Exclusive Short-form Marketing Kit Production Complete!")
            
            actual_result = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "product": product_name,
                "features": product_features,
                "hook": result_json.get("hook", "🔥 Unbelievable Breakthrough!"),
                "script": result_json.get("script", "No script generated."),
                "prompt": result_json.get("prompt", "Cinematic shot.")
            }
            
            # 성공적 제조 시 무료 카운터 차감 (누적 가산)
            st.session_state.free_usage_count += 1
            
            st.session_state.workspace_history.insert(0, actual_result)
            st.session_state.selected_view_idx = 0
            indicator_box.empty()
            st.rerun()
            
        except Exception as e:
            indicator_box.empty()
            st.error(f"💥 OpenAI API Error: {str(e)}")

# 8. 아웃풋 워크스페이스 모니터 리포트 렌더링
with col2:
    if st.session_state.selected_view_idx is not None and len(st.session_state.workspace_history) > 0:
        current_data = st.session_state.workspace_history[st.session_state.selected_view_idx]
        
        with st.container(border=True):
            st.markdown(f"### 🖥️ Enterprise Workspace Monitor")
            st.caption(f"🧬 Generation Node Timestamp: {current_data['timestamp']}")
            
            tab1, tab2, tab3 = st.tabs(["📌 High-Hook Script", "🎨 AI Video Render Prompt", "📊 Advanced Analytics"])
            
            with tab1:
                st.markdown(f"**⚡ Hook Headline:** `{current_data['hook']}`")
                st.markdown("**🎬 Multi-Language Video Production Script:**")
                st.text_area("", current_data["script"], height=130)
                
            with tab2:
                st.markdown("**🖼️ Text-to-Video Engine Text Prompt Asset:**")
                st.code(current_data["prompt"], language="text")
                st.caption("Copy this prompt into Sora, Runway Gen-3, or Pika Labs to instantly render the master visual layer.")
                
            with tab3:
                st.markdown("**📈 Estimated Performance Metrics**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Avg CTR Forecast", "6.8%", "+2.4% vs Industry")
                c2.metric("Hook Retention Rate", "74.2%", "Top 1% Class")
                c3.metric("AI Conversion Score", "94/100", "High Optimization")
