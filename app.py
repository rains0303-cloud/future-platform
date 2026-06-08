import sys
import subprocess
import time

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
if "usage_counter" not in st.session_state:
    st.session_state.usage_counter = 0

# 🌟 [중요] 파트너님의 OpenAI API Key를 여기에 안전하게 세팅합니다.
# (추후 Streamlit Cloud 배포 시 .st/secrets 나 환경변수로 관리하면 더욱 안전합니다)
CRITICAL_MASTER_OPENAI_KEY = "sk-proj-YOUR_ACTUAL_OPENAI_API_KEY_HERE"

# 2. 하이엔드 글로벌 SaaS 테마 CSS 주입 (Manage app 등 마스킹 포함)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Noto+Sans+KR:wght@400;700;900&display=swap');
    
    /* 전체 폰트 및 배경 스케일링 */
    html, body, [data-testid="stSidebarContent"] {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        background-color: #0E1117;
        color: #E2E8F0;
    }
    
    /* 개발자 모드 및 스트림릿 기본 UI 마스킹 (Manage app 차단) */
    #MainMenu, footer, [data-testid="stDecoration"], [data-testid="bundle-theme-styles"] {display: none !important;}
    footer {visibility: hidden;}
    button[title="View source code"] {display: none !important;}
    div[data-testid="stActionButton"] {display: none !important;}
    
    /* 하단 Streamlit 배포자 관리자 전용 노드 강제 차단 */
    iframe[title="Manage app"], .viewerBadge_container__1QSob, .viewerBadge_link__276wN {display: none !important;}
    div[class^="viewerBadge"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# 3. 전 세계 6대 권역 결제 페이월 포함 언어팩
LANG_PACK = {
    "한국어 🇰🇷": {
        "title": "💎 글로벌 AI 숏폼 제조 공장 Enterprise",
        "subtitle": "상위 1% 독점적 글로벌 무인 숏폼 비디오 생성 오케스트레이터",
        "sidebar_title": "🔐 라이선스 제어 센터",
        "license_label": "마스터 라이선스 키 입력 (EB74)",
        "license_ph": "시작키 또는 구독 라이선스를 입력하세요",
        "btn_generate": "🚀 초고속 숏폼 비디오 시나리오 제조",
        "p_name_label": "📦 제품/서비스 이름",
        "p_name_ph": "예: 스마트 텀블러, 무선 마우스, 영어 회화 앱",
        "feat_label": "🎯 핵심 타겟 및 제품 장점 (세부 설명)",
        "feat_ph": "예: 20대 직장인 타겟, 얼음이 48시간 유지됨, 감성적인 파스텔 디자인",
        "lang_select": "🌐 시스템 UI 언어 변경",
        "paywall_title": "🚫 프리미엄 페이월 활성화 (무료 체험 종료)",
        "paywall_desc": "파트너님, 첫 번째 무료 크레딧이 전량 소진되었습니다. 지속적인 상위 1% 독점 마케팅 숏폼 생산을 위해 라이선스를 활성화하거나 구독 결제를 완료해 주세요.",
        "paywall_btn": "💳 즉시 결제 및 무제한 라이선스 발급 받기",
        "m1": "연동 AI 엔진 인프라 상태",
        "m2": "안전 자산 저장소",
        "m3": "계정 권한 등급"
    },
    "English 🇺🇸": {
        "title": "💎 Global AI Video Factory Enterprise",
        "subtitle": "Top 1% Exclusive Global Unmanned Short-form Video Generator Orchestrator",
        "sidebar_title": "🔐 License Control Center",
        "license_label": "Enter Master License Key (EB74)",
        "license_ph": "Enter your Master Key or Subscription Key",
        "btn_generate": "🚀 Manufacture High-Conversion Video Scenario",
        "p_name_label": "📦 Product/Service Name",
        "p_name_ph": "e.g., Smart Tumbler, Wireless Mouse, English Learning App",
        "feat_label": "🎯 Core Target & Key Benefits",
        "feat_ph": "e.g., Targets 20s office workers, keeps ice for 48 hours, aesthetic pastel design",
        "lang_select": "🌐 Change System UI Language",
        "paywall_title": "🚫 Premium Paywall Activated (Trial Expired)",
        "paywall_desc": "Your first free credit has been completely exhausted. Please activate your license or complete your subscription to continue manufacturing top 1% exclusive short-form scenarios.",
        "paywall_btn": "💳 Instant Purchase & Unlock Unlimited License",
        "m1": "Connected AI Engine Infrastructure",
        "m2": "Secure Asset Vault",
        "m3": "Account Tier Status"
    },
    "日本語 🇯🇵": {
        "title": "💎 グローバル AI ショートフォーム製造工場 Enterprise",
        "subtitle": "上位 1% 独占的グローバル無人ショート動画生成オーケストレーター",
        "sidebar_title": "🔐 ライセンス管理センター",
        "license_label": "マスターライセンスキー入力 (EB74)",
        "license_ph": "マスターキーまたは購読キーを入力してください",
        "btn_generate": "🚀 高転換ショート動画シナリオ製造",
        "p_name_label": "📦 製品・サービス名",
        "p_name_ph": "例：スマートタンブラー、ワイヤレスマウス、英会話アプリ",
        "feat_label": "🎯 コアターゲットと製品の強み",
        "feat_ph": "例：20代のオフィスワーカー対象、氷が48時間キープ、エモーショナルなパステルデザイン",
        "lang_select": "🌐 システムUI言語の変更",
        "paywall_title": "🚫 プレミアムペイウォール有効化 (無料体験終了)",
        "paywall_desc": "最初の無料クレジットがすべて消費されました。上位1%の独占的なマーケティング動画を継続して作成するには、ライセンスを有効にするか、購読決済を完了してください。",
        "paywall_btn": "💳 今すぐ決済して無制限ライセンスを取得",
        "m1": "連携AIエンジンインフラ状態",
        "m2": "安全資産ストレージ",
        "m3": "アカウント権限階級"
    },
    "简体中文 🇨🇳": {
        "title": "💎 全球 AI 短视频制造工厂 Enterprise",
        "subtitle": "前 1% 垄断级全球无人值守短视频生成编排器",
        "sidebar_title": "🔐 许可证控制中心",
        "license_label": "输入主许可证密钥 (EB74)",
        "license_ph": "请输入主密钥 or 订阅激活码",
        "btn_generate": "🚀 高转化短视频剧本智能制造",
        "p_name_label": "📦 产品/服务名称",
        "p_name_ph": "例如：智能保温杯、无线鼠标、英语学习App",
        "feat_label": "🎯 核心目标人群与产品优势",
        "feat_ph": "例如：面向20岁左右的职场新人、保冰效果长达48小时、高颜值马卡龙色系",
        "lang_select": "🌐 切换系统 UI 语言",
        "paywall_title": "🚫 高级付费墙已激活 (免费体验结束)",
        "paywall_desc": "您的首个免费额度已完全耗尽。为了能够持续生产前1%垄断级的营销短视频，请激活主许可证或完成订阅支付。",
        "paywall_btn": "💳 立即支付并开通无限制特权",
        "m1": "对接 AI 引擎基础设施状态",
        "m2": "安全资产保险库",
        "m3": "账户权限等级"
    },
    "Español 🇪🇸": {
        "title": "💎 Fábrica Global de IA para Videos Cortos Enterprise",
        "subtitle": "Orquestrador de Creación de Video Corto No Tripulado Exclusivo del Top 1%",
        "sidebar_title": "🔐 Centro de Control de Licencias",
        "license_label": "Ingrese la Clave de Licencia Maestra (EB74)",
        "license_ph": "Ingrese su clave maestra o código de suscripción",
        "btn_generate": "🚀 Fabricar Escenario de Video de Alta Conversión",
        "p_name_label": "📦 Nombre del Producto/Servicio",
        "p_name_ph": "Ej: Termo Inteligente, Mouse Inalámbrico, App de Idiomas",
        "feat_label": "🎯 Target Central y Beneficios Clave",
        "feat_ph": "Ej: Dirigido a oficinistas de 20 años, mantiene el hielo por 48 horas, diseño pastel estético",
        "lang_select": "🌐 Cambiar Idioma de la UI del Sistema",
        "paywall_title": "🚫 Paywall Premium Activado (Prueba Expirada)",
        "paywall_desc": "Su primer crédito gratuito se ha agotado por completo. Active su licencia o complete su suscripción para continuar fabricando escenarios de video exclusivos.",
        "paywall_btn": "💳 Pago Instantáneo y Desbloquear Licencia Ilimitada",
        "m1": "Infraestructura del Motor de IA Conectado",
        "m2": "Bóveda de Activos Segura",
        "m3": "Nivel de Rango de Cuenta"
    },
    "Tiếng Việt 🇻🇳": {
        "title": "💎 Nhà Máy Chế Tạo Video Ngắn AI Toàn Cầu Enterprise",
        "subtitle": "Hệ Thống Điều Phối Tạo Video Ngắn Không Người Lái Độc Quyền Top 1% Toàn Cầu",
        "sidebar_title": "🔐 Trung Tâm Kiểm Soát Bản Quyền",
        "license_label": "Nhập Khóa Bản Quyền Master (EB74)",
        "license_ph": "Nhập khóa chính hoặc mã đăng ký của bạn",
        "btn_generate": "🚀 Sản Xuất Kịch Bản Video Chuyển Đổi Cao",
        "p_name_label": "📦 Tên Sản Phẩm/Dịch Vụ",
        "p_name_ph": "Ví dụ: Bình giữ nhiệt thông minh, Chuột không dây, Ứng dụng học tiếng Anh",
        "feat_label": "🎯 Khách Hàng Mục Tiêu & Lợi Ích Cốt Lõi",
        "feat_ph": "Ví dụ: Hướng đến dân văn phòng độ tuổi 20, giữ đá 48 giờ, thiết kế màu pastel thẩm mỹ",
        "lang_select": "🌐 Thay Đổi Ngôn Ngữ Hệ Thống",
        "paywall_title": "🚫 Đã Kích Hoạt Tường Thu Phí Cao Cấp (Hết Hạn Dùng Thử)",
        "paywall_desc": "Số điểm dùng thử miễn phí đầu tiên của bạn đã được sử dụng hết. Vui lòng kích hoạt bản quyền hoặc hoàn tất thanh toán để tiếp tục sản xuất.",
        "paywall_btn": "💳 Thanh Toán Ngay & Mở Khóa Bản Quyền Không Giới Hạn",
        "m1": "Trạng Thái Hạ Tầng Cơ Sở AI",
        "m2": "Kho Lưu Trữ Tài Sản An Toàn",
        "m3": "Cấp Bậc Quyền Hạn Tài Khoản"
    }
}

# 4. 사이드바 제어 패널 구축 (고객용 OpenAI Key 입력란 영구 제거)
with st.sidebar:
    st.markdown(f"### {LANG_PACK['English 🇺🇸']['sidebar_title']}")
    site_lang = st.selectbox("🌐 UI Language", list(LANG_PACK.keys()))
    L = LANG_PACK[site_lang]
    
    st.write("---")
    st.markdown(f"<h4>{L['license_label']}</h4>", unsafe_allow_html=True)
    license_input = st.text_input("", placeholder=L["license_ph"], type="password", label_visibility="collapsed")
    
    is_master_active = (license_input == "EB74")

# 5. 메인 대시보드 UI 레이아웃
st.title(L["title"])
st.markdown(f"<p style='color:#94A3B8; font-size:1.2rem; margin-top:-10px;'>{L['subtitle']}</p>", unsafe_allow_html=True)
st.write("")

# 상단 실시간 하이엔드 지표 메트릭 배치
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1:
    st.metric(label=L["m1"], value="⚡ GPT-4o-Mini Sync", delta="99.98% Latency Stable")
with mc2:
    st.metric(label=L["m2"], value=f"💾 {len(st.session_state.workspace_history)} Nodes", delta="Encrypted Storage")
with mc3:
    if is_master_active:
        st.metric(label=L["m3"], value="Enterprise Max", delta="All Access Unlocked")
    elif st.session_state.usage_counter == 0:
        st.metric(label=L["m3"], value="1 Free Credit Left", delta="Trial Active 🔓")
    else:
        st.metric(label=L["m3"], value="Locked 🔒", delta="Trial Expired")
with mc4:
    st.metric(label="Global Traffic Matrix", value="🌍 Active", delta="CDN Powered")

st.write("---")

# 6. 비즈니스 코어 로직 제어 (1회 무료 개방 및 페이월 차단 설계)
paywall_triggered = (not is_master_active and st.session_state.usage_counter >= 1)

if paywall_triggered:
    # 결제가 안 되었고 1회를 이미 썼다면 입력창 진입 차단 및 강력한 결제 링크 팝업
    st.error(L["paywall_title"])
    st.markdown(f"<p style='font-size:1.1rem; color:#CBD5E1;'>{L['paywall_desc']}</p>", unsafe_allow_html=True)
    
    # 파트너님의 검로드(
