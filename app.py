# app.py
# Global Opportunity Radar AI - Self-contained Streamlit MVP
# 이 파일 하나만으로 실행되도록 설계했습니다.
# 외부 opportunity_engine.py / translations.py 없이 작동합니다.

from __future__ import annotations

import json
import os
import re
import time
import html
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


# =========================================================
# 1. 기본 설정
# =========================================================

st.set_page_config(
    page_title="Global Opportunity Radar AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. 다국어 UI 언어팩
# =========================================================

LANG_PACK: Dict[str, Dict[str, str]] = {
    "한국어 🇰🇷": {
        "app_title": "📡 Global Opportunity Radar AI",
        "app_subtitle": "AI가 전 세계 돈 되는 사업기회·트렌드·수익 키워드를 찾아 점수화합니다.",
        "control": "⚙️ 관제 센터",
        "ui_language": "🌐 UI 언어",
        "license_label": "🔑 마스터 라이선스 키",
        "license_ph": "라이선스 키를 입력하세요",
        "payment_link": "💳 유료 라이선스 결제하기",
        "free_mode": "🎁 무료 체험 모드",
        "free_desc": "라이선스 없이도 {count}회 AI 기회 분석을 생성할 수 있습니다.",
        "locked": "🚨 무료 체험 종료",
        "locked_desc": "무료 생성 횟수를 모두 사용했습니다. 계속 이용하려면 라이선스 키를 입력하거나 결제 링크를 연결하세요.",
        "active": "✅ Enterprise Pro 활성화",
        "active_desc": "모든 생성 제한이 해제되었습니다.",
        "dashboard": "대시보드",
        "generate": "AI 기회 생성",
        "explore": "기회 탐색",
        "pricing": "유료 결제",
        "guide": "운영 가이드",
        "input_title": "📥 기회 분석 입력",
        "idea_label": "분석할 아이디어·뉴스·제품·트렌드",
        "idea_ph": "예: AI 에이전트가 중소기업 고객응대를 자동화하는 흐름이 커지고 있다...",
        "category_label": "카테고리",
        "region_label": "대상 지역",
        "target_label": "대상 고객",
        "target_ph": "예: 1인 창업자, 중소기업, 쇼핑몰 운영자, 병원, 학원 등",
        "generate_btn": "🚀 AI 사업기회 리포트 생성",
        "need_input": "아이디어/트렌드 내용을 입력해주세요.",
        "api_missing": "OPENAI_API_KEY가 없어 데모 분석을 생성합니다. 실제 품질을 높이려면 Streamlit Secrets에 API Key를 넣으세요.",
        "workspace": "🖥️ 기회 분석 워크스페이스",
        "empty": "아직 생성된 기회 분석이 없습니다.",
        "score": "AI 기회점수",
        "download": "CSV 다운로드",
        "search": "검색",
        "all": "전체",
        "paywall_notice": "🔒 이 영역은 유료회원에게 제공할 핵심 분석 영역입니다.",
        "tab_summary": "📌 핵심요약",
        "tab_money": "💰 수익화",
        "tab_execution": "🛠 실행계획",
        "tab_keywords": "🔎 키워드",
        "tab_risk": "⚠️ 리스크",
        "tab_full": "📄 전체 리포트",
        "footer_warning": "※ 본 서비스는 사업기회 탐색용 정보 서비스입니다. 수익을 보장하지 않으며 법률·투자·세무 자문이 아닙니다.",
    },
    "English 🇺🇸": {
        "app_title": "📡 Global Opportunity Radar AI",
        "app_subtitle": "AI discovers, scores, and explains global money-making opportunities.",
        "control": "⚙️ Control Center",
        "ui_language": "🌐 UI Language",
        "license_label": "🔑 Master License Key",
        "license_ph": "Enter license key",
        "payment_link": "💳 Buy Paid License",
        "free_mode": "🎁 Free Trial Mode",
        "free_desc": "You can generate {count} AI opportunity reports without a license.",
        "locked": "🚨 Free Trial Expired",
        "locked_desc": "Your free generations are used. Enter a license key or connect a payment link.",
        "active": "✅ Enterprise Pro Active",
        "active_desc": "All generation limits are unlocked.",
        "dashboard": "Dashboard",
        "generate": "AI Generator",
        "explore": "Explore",
        "pricing": "Pricing",
        "guide": "Operating Guide",
        "input_title": "📥 Opportunity Input",
        "idea_label": "Idea, news, product, or trend to analyze",
        "idea_ph": "e.g. AI agents are increasingly automating customer support for SMBs...",
        "category_label": "Category",
        "region_label": "Target Region",
        "target_label": "Target Customer",
        "target_ph": "e.g. solopreneurs, SMBs, ecommerce owners, clinics, schools...",
        "generate_btn": "🚀 Generate AI Opportunity Report",
        "need_input": "Please enter an idea or trend first.",
        "api_missing": "OPENAI_API_KEY is missing, so a demo analysis will be generated. Add your key in Streamlit Secrets for better quality.",
        "workspace": "🖥️ Opportunity Analysis Workspace",
        "empty": "No opportunity reports generated yet.",
        "score": "AI Opportunity Score",
        "download": "Download CSV",
        "search": "Search",
        "all": "All",
        "paywall_notice": "🔒 This is the premium analysis area for paid members.",
        "tab_summary": "📌 Summary",
        "tab_money": "💰 Monetization",
        "tab_execution": "🛠 Execution",
        "tab_keywords": "🔎 Keywords",
        "tab_risk": "⚠️ Risks",
        "tab_full": "📄 Full Report",
        "footer_warning": "※ This is an opportunity discovery information service. It does not guarantee revenue and is not legal, investment, or tax advice.",
    },
    "日本語 🇯🇵": {
        "app_title": "📡 Global Opportunity Radar AI",
        "app_subtitle": "AIが世界中の収益機会・トレンド・収益キーワードを発見しスコア化します。",
        "control": "⚙️ コントロールセンター",
        "ui_language": "🌐 UI言語",
        "license_label": "🔑 マスターライセンスキー",
        "license_ph": "ライセンスキーを入力",
        "payment_link": "💳 有料ライセンスを購入",
        "free_mode": "🎁 無料体験モード",
        "free_desc": "ライセンスなしで{count}回のAI分析を生成できます。",
        "locked": "🚨 無料体験終了",
        "locked_desc": "無料生成回数を使い切りました。ライセンスキーを入力してください。",
        "active": "✅ Enterprise Pro 有効",
        "active_desc": "すべての生成制限が解除されました。",
        "dashboard": "ダッシュボード",
        "generate": "AI生成",
        "explore": "探索",
        "pricing": "料金",
        "guide": "運用ガイド",
        "input_title": "📥 機会分析入力",
        "idea_label": "分析するアイデア・ニュース・製品・トレンド",
        "idea_ph": "例: AIエージェントが中小企業の顧客対応を自動化している...",
        "category_label": "カテゴリ",
        "region_label": "対象地域",
        "target_label": "対象顧客",
        "target_ph": "例: 個人起業家、中小企業、EC運営者、病院、学校など",
        "generate_btn": "🚀 AI機会レポート生成",
        "need_input": "アイデアまたはトレンドを入力してください。",
        "api_missing": "OPENAI_API_KEYがないためデモ分析を生成します。",
        "workspace": "🖥️ 機会分析ワークスペース",
        "empty": "まだレポートがありません。",
        "score": "AI機会スコア",
        "download": "CSVダウンロード",
        "search": "検索",
        "all": "すべて",
        "paywall_notice": "🔒 この領域は有料会員向けの分析です。",
        "tab_summary": "📌 要約",
        "tab_money": "💰 収益化",
        "tab_execution": "🛠 実行計画",
        "tab_keywords": "🔎 キーワード",
        "tab_risk": "⚠️ リスク",
        "tab_full": "📄 全文レポート",
        "footer_warning": "※ 本サービスは情報提供用であり、収益を保証するものではありません。",
    },
    "Español 🇪🇸": {
        "app_title": "📡 Global Opportunity Radar AI",
        "app_subtitle": "La IA descubre y puntúa oportunidades globales para generar ingresos.",
        "control": "⚙️ Centro de Control",
        "ui_language": "🌐 Idioma",
        "license_label": "🔑 Clave de licencia",
        "license_ph": "Introduce la clave",
        "payment_link": "💳 Comprar licencia",
        "free_mode": "🎁 Modo gratuito",
        "free_desc": "Puedes generar {count} informes sin licencia.",
        "locked": "🚨 Prueba gratuita terminada",
        "locked_desc": "Has usado tus generaciones gratuitas. Introduce una licencia.",
        "active": "✅ Enterprise Pro activo",
        "active_desc": "Todos los límites están desbloqueados.",
        "dashboard": "Panel",
        "generate": "Generador IA",
        "explore": "Explorar",
        "pricing": "Precios",
        "guide": "Guía",
        "input_title": "📥 Entrada de oportunidad",
        "idea_label": "Idea, noticia, producto o tendencia",
        "idea_ph": "Ej: los agentes de IA automatizan soporte para pymes...",
        "category_label": "Categoría",
        "region_label": "Región objetivo",
        "target_label": "Cliente objetivo",
        "target_ph": "Ej: emprendedores, pymes, ecommerce, clínicas...",
        "generate_btn": "🚀 Generar informe",
        "need_input": "Introduce una idea o tendencia.",
        "api_missing": "Falta OPENAI_API_KEY, se generará una demo.",
        "workspace": "🖥️ Espacio de análisis",
        "empty": "Aún no hay informes.",
        "score": "Puntuación IA",
        "download": "Descargar CSV",
        "search": "Buscar",
        "all": "Todo",
        "paywall_notice": "🔒 Área premium para miembros de pago.",
        "tab_summary": "📌 Resumen",
        "tab_money": "💰 Monetización",
        "tab_execution": "🛠 Ejecución",
        "tab_keywords": "🔎 Palabras clave",
        "tab_risk": "⚠️ Riesgos",
        "tab_full": "📄 Informe completo",
        "footer_warning": "※ Servicio informativo. No garantiza ingresos ni es asesoría legal, fiscal o de inversión.",
    },
    "Deutsch 🇩🇪": {
        "app_title": "📡 Global Opportunity Radar AI",
        "app_subtitle": "KI entdeckt und bewertet globale Geschäftschancen.",
        "control": "⚙️ Kontrollzentrum",
        "ui_language": "🌐 Sprache",
        "license_label": "🔑 Lizenzschlüssel",
        "license_ph": "Lizenzschlüssel eingeben",
        "payment_link": "💳 Lizenz kaufen",
        "free_mode": "🎁 Testmodus",
        "free_desc": "Du kannst {count} Berichte ohne Lizenz erstellen.",
        "locked": "🚨 Testphase beendet",
        "locked_desc": "Kostenlose Generierungen verbraucht. Lizenz eingeben.",
        "active": "✅ Enterprise Pro aktiv",
        "active_desc": "Alle Limits sind aufgehoben.",
        "dashboard": "Dashboard",
        "generate": "KI Generator",
        "explore": "Entdecken",
        "pricing": "Preise",
        "guide": "Anleitung",
        "input_title": "📥 Chancen-Eingabe",
        "idea_label": "Idee, Nachricht, Produkt oder Trend",
        "idea_ph": "z.B. KI-Agenten automatisieren Kundenservice für KMU...",
        "category_label": "Kategorie",
        "region_label": "Zielregion",
        "target_label": "Zielkunde",
        "target_ph": "z.B. Gründer, KMU, E-Commerce, Kliniken...",
        "generate_btn": "🚀 Bericht generieren",
        "need_input": "Bitte Idee oder Trend eingeben.",
        "api_missing": "OPENAI_API_KEY fehlt, Demoanalyse wird erstellt.",
        "workspace": "🖥️ Analyse Workspace",
        "empty": "Noch keine Berichte.",
        "score": "KI Chancen-Score",
        "download": "CSV herunterladen",
        "search": "Suche",
        "all": "Alle",
        "paywall_notice": "🔒 Premium-Analysebereich für zahlende Mitglieder.",
        "tab_summary": "📌 Zusammenfassung",
        "tab_money": "💰 Monetarisierung",
        "tab_execution": "🛠 Umsetzung",
        "tab_keywords": "🔎 Keywords",
        "tab_risk": "⚠️ Risiken",
        "tab_full": "📄 Vollbericht",
        "footer_warning": "※ Informationsservice. Keine Umsatzgarantie und keine Rechts-, Steuer- oder Anlageberatung.",
    },
    "中文 🇨🇳": {
        "app_title": "📡 Global Opportunity Radar AI",
        "app_subtitle": "AI发现并评分全球赚钱机会、趋势和关键词。",
        "control": "⚙️ 控制中心",
        "ui_language": "🌐 界面语言",
        "license_label": "🔑 许可证密钥",
        "license_ph": "输入许可证密钥",
        "payment_link": "💳 购买许可证",
        "free_mode": "🎁 免费试用模式",
        "free_desc": "无需许可证可生成 {count} 次AI机会分析。",
        "locked": "🚨 免费试用结束",
        "locked_desc": "免费次数已用完，请输入许可证。",
        "active": "✅ Enterprise Pro 已激活",
        "active_desc": "所有限制已解除。",
        "dashboard": "仪表盘",
        "generate": "AI生成",
        "explore": "机会探索",
        "pricing": "付费",
        "guide": "运营指南",
        "input_title": "📥 机会分析输入",
        "idea_label": "要分析的想法、新闻、产品或趋势",
        "idea_ph": "例如：AI代理正在自动化中小企业客服...",
        "category_label": "类别",
        "region_label": "目标地区",
        "target_label": "目标客户",
        "target_ph": "例如：创业者、中小企业、电商、诊所、学校等",
        "generate_btn": "🚀 生成AI机会报告",
        "need_input": "请输入想法或趋势。",
        "api_missing": "缺少OPENAI_API_KEY，将生成演示分析。",
        "workspace": "🖥️ 机会分析工作区",
        "empty": "还没有生成报告。",
        "score": "AI机会分数",
        "download": "下载CSV",
        "search": "搜索",
        "all": "全部",
        "paywall_notice": "🔒 这是付费会员的高级分析区域。",
        "tab_summary": "📌 摘要",
        "tab_money": "💰 变现",
        "tab_execution": "🛠 执行",
        "tab_keywords": "🔎 关键词",
        "tab_risk": "⚠️ 风险",
        "tab_full": "📄 完整报告",
        "footer_warning": "※ 本服务仅为信息服务，不保证收益，也不是法律、投资或税务建议。",
    },
}


# =========================================================
# 3. CSS 디자인
# =========================================================

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebarHeader"] {display: none !important;}

    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 26px 30px;
        border-radius: 26px;
        background:
          radial-gradient(circle at top left, rgba(74, 144, 226, 0.35), transparent 38%),
          linear-gradient(135deg, rgba(9, 18, 44, 0.96), rgba(19, 33, 72, 0.92));
        border: 1px solid rgba(150,180,255,0.28);
        box-shadow: 0 18px 40px rgba(0,0,0,0.20);
        margin-bottom: 20px;
    }

    .hero h1 {
        font-size: 2.3rem;
        line-height: 1.08;
        margin-bottom: 8px;
        color: #ffffff;
        font-weight: 900;
    }

    .hero p {
        color: rgba(255,255,255,0.84);
        font-size: 1.05rem;
        margin: 0;
    }

    .soft-card {
        padding: 18px 18px;
        border-radius: 18px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(130,150,200,0.24);
        margin-bottom: 16px;
    }

    .result-card {
        padding: 20px 22px;
        border-radius: 22px;
        border: 1px solid rgba(120,140,210,0.28);
        background:
            linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
        box-shadow: 0 14px 32px rgba(0,0,0,0.10);
        margin-bottom: 20px;
    }

    .score-circle {
        width: 112px;
        height: 112px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        background: linear-gradient(135deg, #4f46e5, #06b6d4);
        color: white;
        box-shadow: 0 12px 26px rgba(79,70,229,0.36);
        margin-left: auto;
        margin-right: auto;
    }

    .score-number {
        font-size: 2.2rem;
        font-weight: 900;
        line-height: 1;
    }

    .score-label {
        font-size: .75rem;
        opacity: .92;
        margin-top: 4px;
    }

    .badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        margin: 0 5px 5px 0;
        background: rgba(79,70,229,0.12);
        border: 1px solid rgba(79,70,229,0.24);
    }

    .paywall-box {
        background-color: rgba(255, 75, 75, 0.10);
        border: 1px solid rgba(255,75,75,0.75);
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 18px;
    }

    .free-box {
        background-color: rgba(59,130,246,0.10);
        border: 1px solid rgba(59,130,246,0.72);
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 18px;
    }

    .success-box {
        background-color: rgba(36,180,126,0.10);
        border: 1px solid rgba(36,180,126,0.72);
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 18px;
    }

    .locked-premium {
        background: rgba(251,191,36,0.10);
        border: 1px dashed rgba(251,191,36,0.80);
        padding: 14px;
        border-radius: 14px;
        margin: 12px 0;
    }

    .report-box {
        padding: 16px;
        border-radius: 16px;
        border: 1px solid rgba(130,150,200,0.22);
        background: rgba(80, 95, 160, 0.07);
        line-height: 1.7;
        white-space: pre-wrap;
    }

    .phone-container {
        width: 330px;
        min-height: 620px;
        max-height: 720px;
        background:
            radial-gradient(circle at 30% 10%, rgba(255,255,255,0.16), transparent 28%),
            linear-gradient(135deg, #0f172a, #1e293b, #334155);
        border: 8px solid #111827;
        border-radius: 34px;
        overflow-y: auto;
        position: relative;
        box-shadow: 0 22px 44px rgba(0,0,0,0.42);
        margin: 10px auto;
        padding: 44px 20px 22px 20px;
    }

    .phone-container::-webkit-scrollbar {display: none;}

    .phone-badge {
        position: absolute;
        top: 16px;
        left: 20px;
        background: rgba(14,165,233,0.94);
        color: white;
        padding: 5px 11px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 1px;
    }

    .sim-title {
        color: #fef08a;
        font-size: 19px;
        line-height: 1.35;
        font-weight: 900;
        margin-top: 20px;
        margin-bottom: 16px;
        text-shadow: 0 3px 8px rgba(0,0,0,0.70);
        word-break: keep-all;
    }

    .sim-script {
        color: #ffffff;
        font-size: 13px;
        line-height: 1.66;
        font-weight: 600;
        background: rgba(0,0,0,0.48);
        padding: 13px;
        border-radius: 14px;
        border-left: 4px solid #38bdf8;
        white-space: pre-wrap;
    }

    .small-note {
        opacity: 0.78;
        font-size: 0.88rem;
    }

    .price-card {
        min-height: 260px;
        padding: 18px;
        border-radius: 20px;
        border: 1px solid rgba(130,150,200,0.28);
        background: rgba(255,255,255,0.04);
        margin-bottom: 12px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 4. 유틸 함수
# =========================================================

def get_secret(name: str, default: str = "") -> str:
    """Streamlit Secrets 또는 환경변수에서 값을 안전하게 가져옵니다."""
    try:
        value = st.secrets.get(name, default)
        return str(value) if value else default
    except Exception:
        return os.getenv(name, default)


def esc(value: Any) -> str:
    """HTML 렌더링 시 깨지거나 위험한 문자를 안전하게 바꿉니다."""
    return html.escape(str(value), quote=True)


def safe_get(data: Dict[str, Any], key: str, default: str = "") -> str:
    """딕셔너리에서 키가 없어도 오류 없이 문자열을 가져옵니다."""
    value = data.get(key, default)
    if value is None:
        return default
    text = str(value)
    if text.strip() == "" or text.lower() == "nan":
        return default
    return text


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def clamp_score(value: Any) -> int:
    return max(0, min(100, safe_int(value, 70)))


def csv_bytes(records: List[Dict[str, Any]]) -> bytes:
    if not records:
        return pd.DataFrame().to_csv(index=False).encode("utf-8-sig")
    return pd.DataFrame(records).to_csv(index=False).encode("utf-8-sig")


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """OpenAI 응답에서 JSON만 추출합니다."""
    if not text:
        return None

    try:
        return json.loads(text)
    except Exception:
        pass

    # ```json ... ``` 형태 제거
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except Exception:
            pass

    # 가장 바깥 JSON 객체 추정
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return None

    return None


def get_openai_client():
    api_key = get_secret("OPENAI_API_KEY", "")
    if not api_key:
        return None

    try:
        from openai import OpenAI  # requirements.txt에 openai가 있으면 사용
        return OpenAI(api_key=api_key)
    except Exception:
        return None


def selected_language_name(site_lang: str) -> str:
    if site_lang.startswith("한국어"):
        return "Korean"
    if site_lang.startswith("English"):
        return "English"
    if site_lang.startswith("日本語"):
        return "Japanese"
    if site_lang.startswith("Español"):
        return "Spanish"
    if site_lang.startswith("Deutsch"):
        return "German"
    if site_lang.startswith("中文"):
        return "Chinese"
    return "Korean"


# =========================================================
# 5. 세션 상태 초기화
# =========================================================

if "free_uses_left" not in st.session_state:
    st.session_state.free_uses_left = 3

if "opportunity_history" not in st.session_state:
    st.session_state.opportunity_history = []

if "selected_view_idx" not in st.session_state:
    st.session_state.selected_view_idx = None


# =========================================================
# 6. 샘플 데이터
# =========================================================

SAMPLE_OPPORTUNITIES: List[Dict[str, Any]] = [
    {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": "AI Customer Support Agent for Small Businesses",
        "one_liner": "중소기업 고객응대를 AI 상담원으로 자동화하는 월 구독형 B2B 서비스",
        "category": "AI / B2B",
        "region": "Global",
        "target_customer": "중소기업, 쇼핑몰, 병원, 학원, 예약 기반 서비스업",
        "opportunity_score": 88,
        "why_now": "AI 에이전트 기술이 빠르게 보급되고, 인건비와 고객응대 부담이 동시에 증가하고 있습니다. 고객은 24시간 빠른 답변을 원하지만 소규모 사업자는 상담 인력을 계속 늘리기 어렵습니다.",
        "revenue_models": "월 구독형 챗봇 구축비, 초기 세팅비, 업종별 FAQ 템플릿 판매, 유지보수형 관리 서비스, CRM 연동 대행",
        "execution_steps": "1) 업종 하나를 정합니다.\n2) 해당 업종 FAQ 100개를 만듭니다.\n3) 랜딩페이지를 만듭니다.\n4) 무료 데모를 제공합니다.\n5) 월 19~99달러 구독으로 전환합니다.",
        "tools": "ChatGPT API, Streamlit, Zapier/Make, Google Sheets, Notion, WhatsApp 또는 카카오 상담 채널",
        "keyword_pack": "AI customer support, AI chatbot for SMB, automated customer service, FAQ automation, ecommerce support bot",
        "risk": "개인정보 처리, 잘못된 답변, 업종별 규정, 고객 데이터 보안 이슈를 주의해야 합니다.",
        "full_report": "이 기회는 전 세계 소규모 사업자가 공통으로 겪는 고객응대 문제를 해결합니다. 초기는 특정 업종 하나에 집중해야 합니다. 예를 들어 영어권 Shopify 쇼핑몰, 한국 학원, 일본 미용실처럼 좁은 대상을 잡고 FAQ 자동화부터 시작하는 것이 좋습니다. 첫 유료 고객 확보 후에는 FAQ 템플릿과 상담 로그 분석 기능을 붙여 객단가를 높일 수 있습니다.",
    },
    {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": "AI Short-form Content Repurposing Service",
        "one_liner": "긴 영상·블로그·강의를 쇼츠·릴스·틱톡 콘텐츠로 자동 변환하는 서비스",
        "category": "Creator Economy",
        "region": "Global",
        "target_customer": "강사, 유튜버, 코치, 온라인 교육자, 브랜드 마케터",
        "opportunity_score": 84,
        "why_now": "쇼트폼 콘텐츠 수요는 계속 증가하지만 제작자는 편집 시간이 부족합니다. AI 요약·자막·영상 편집 도구가 성숙하면서 대행 자동화가 가능해졌습니다.",
        "revenue_models": "월 관리형 패키지, 영상당 편집비, 템플릿 판매, AI툴 제휴수수료, 교육 콘텐츠 판매",
        "execution_steps": "1) 유튜브 강의 채널 30곳을 찾습니다.\n2) 샘플 쇼츠 3개를 만듭니다.\n3) DM 또는 이메일로 제안합니다.\n4) 월 30~150만원 패키지로 판매합니다.",
        "tools": "ChatGPT, CapCut, Canva, Descript, OpusClip, Runway, Google Drive",
        "keyword_pack": "AI shorts generator, content repurposing, YouTube to Shorts, TikTok automation, reels editing service",
        "risk": "저작권, 초상권, 플랫폼 정책, 과장 광고를 주의해야 합니다.",
        "full_report": "이 기회는 콘텐츠가 이미 있는 사람들의 시간을 줄여주는 서비스입니다. 완전히 새로운 콘텐츠를 만드는 것보다 기존 자산을 재활용하기 때문에 고객 설득이 쉽습니다. 초기에는 특정 고객군에 집중하고, 샘플 결과물을 보여주는 방식이 가장 효과적입니다.",
    },
    {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": "Global Grant & Tender Alert AI",
        "one_liner": "정부지원금·입찰·보조금·공모전을 AI가 조건별로 찾아주는 알림 서비스",
        "category": "Grant / Tender",
        "region": "Global",
        "target_customer": "스타트업, 중소기업, 연구소, 프리랜서, 비영리단체",
        "opportunity_score": 91,
        "why_now": "지원사업과 공공 입찰 정보는 흩어져 있고, 많은 기업이 놓치고 있습니다. 정보가 곧 돈으로 연결되기 때문에 유료 전환 가능성이 높습니다.",
        "revenue_models": "월 구독 알림, 성공보수, 업종별 리포트 판매, 제안서 작성 대행, B2B 프리미엄 계정",
        "execution_steps": "1) 국가 하나와 고객군 하나를 정합니다.\n2) 지원사업 정보를 수집합니다.\n3) 조건 매칭표를 만듭니다.\n4) 이메일 알림을 제공합니다.\n5) 신청서 작성 템플릿을 유료로 판매합니다.",
        "tools": "Streamlit, Google Sheets, Make, OpenAI API, Gmail, Notion, Airtable",
        "keyword_pack": "startup grants, government funding, tender alerts, RFP finder, small business grants",
        "risk": "공식 출처 확인, 마감일 정확성, 법률 자문 오해 방지, 국가별 규정 확인이 필요합니다.",
        "full_report": "이 기회는 사람들이 실제 돈을 받을 가능성과 직접 연결됩니다. 그래서 단순 트렌드보다 결제 의향이 높습니다. 다만 정보 정확도가 매우 중요하므로 공식 출처 링크, 마감일, 자격 조건, 면책문구를 반드시 제공해야 합니다.",
    },
]


# =========================================================
# 7. AI 생성 엔진
# =========================================================

def demo_generate_report(
    idea: str,
    category: str,
    region: str,
    target_customer: str,
    output_language: str,
) -> Dict[str, Any]:
    """API Key가 없을 때도 앱이 멈추지 않도록 데모 리포트를 생성합니다."""
    base_score = 82
    if any(word.lower() in idea.lower() for word in ["ai", "자동", "automation", "agent", "saas"]):
        base_score += 6
    if any(word.lower() in idea.lower() for word in ["grant", "지원금", "입찰", "funding", "tender"]):
        base_score += 5
    if len(idea) > 180:
        base_score += 3

    score = min(96, base_score)

    title = f"{category} Opportunity: {idea[:42].strip()}..."
    if output_language == "Korean":
        title = f"{category} 기반 글로벌 수익기회"
        one_liner = "입력한 트렌드를 바탕으로 AI가 수익화 가능한 온라인 사업기회로 재구성했습니다."
        why_now = (
            "이 기회가 지금 중요한 이유는 세 가지입니다.\n"
            "첫째, AI 도구 보급으로 과거보다 적은 인력으로 서비스 운영이 가능해졌습니다.\n"
            "둘째, 전 세계 사용자는 시간을 줄여주거나 돈을 벌 가능성을 높여주는 정보에 비용을 지불합니다.\n"
            "셋째, 초기 MVP를 Streamlit과 GitHub로 빠르게 공개하고 시장 반응을 테스트할 수 있습니다."
        )
        revenue = (
            "1) 월 구독형 정보 서비스: 월 19,000원~49,000원\n"
            "2) 프리미엄 리포트 판매: 건당 9,900원~29,000원\n"
            "3) B2B 맞춤 분석: 건당 30만~300만원\n"
            "4) 제휴 수익: 추천 툴·서비스 가입 수수료\n"
            "5) 템플릿 판매: 노션, 엑셀, 프롬프트 패키지"
        )
        steps = (
            "오늘 할 일:\n"
            "1. 이 아이디어의 고객군을 하나만 정합니다.\n"
            "2. 고객이 실제로 돈을 낼 문제를 한 문장으로 씁니다.\n"
            "3. 경쟁 사이트 3개를 찾습니다.\n"
            "4. 무료 샘플 리포트 3개를 만듭니다.\n"
            "5. 지인 또는 온라인 커뮤니티에 테스트 링크를 공유합니다.\n\n"
            "7일 실행계획:\n"
            "Day 1: 타깃 고객 확정\n"
            "Day 2: 샘플 데이터 20개 작성\n"
            "Day 3: Streamlit 화면 구성\n"
            "Day 4: 결제 링크 연결\n"
            "Day 5: 무료/유료 콘텐츠 분리\n"
            "Day 6: 테스트 사용자 5명 모집\n"
            "Day 7: 첫 유료 전환 실험"
        )
        tools = "Streamlit, GitHub, OpenAI API, Google Sheets, Make, Gumroad/Lemon Squeezy/Paddle, Google Analytics"
        keywords = "AI business opportunity, global trends, money keywords, SaaS ideas, startup trends, online business ideas, automation business"
        risk = (
            "주의할 점:\n"
            "- 수익 보장처럼 표현하면 안 됩니다.\n"
            "- 투자·법률·세무 조언처럼 보이지 않도록 면책문구가 필요합니다.\n"
            "- 자동 생성 정보는 사람이 최종 검수해야 신뢰도가 올라갑니다.\n"
            "- 결제 후 환불정책과 개인정보처리방침을 반드시 준비해야 합니다."
        )
        validation = (
            "검증 방법:\n"
            "1. 무료 리포트 3개를 공개합니다.\n"
            "2. 이메일 구독을 받습니다.\n"
            "3. 사람들이 가장 많이 클릭한 기회 카테고리를 확인합니다.\n"
            "4. 월 19,000원 결제 버튼을 노출합니다.\n"
            "5. 결제 전환이 없으면 가격보다 콘텐츠 구체성을 먼저 개선합니다."
        )
        full_report = (
            f"입력 내용:\n{idea}\n\n"
            f"대상 고객:\n{target_customer or '아직 명확하지 않음'}\n\n"
            "이 사업기회는 전 세계 사용자가 공통으로 원하는 '돈 되는 정보의 빠른 발견' 욕구를 기반으로 합니다. "
            "사람들은 일반 뉴스에는 돈을 잘 내지 않지만, 매출 증가, 비용 절감, 시간 절약, 지원금 확보, 고객 확보처럼 직접적인 이익과 연결되는 정보에는 비용을 지불합니다.\n\n"
            "따라서 단순히 정보를 모아 보여주는 사이트가 아니라, 각 정보를 '실행 가능한 사업기회'로 번역해야 합니다. "
            "핵심은 AI Opportunity Score입니다. 사용자가 이 점수를 보면 어떤 기회가 지금 가장 우선순위가 높은지 빠르게 판단할 수 있어야 합니다.\n\n"
            "초기 MVP는 복잡한 회원 DB 없이도 운영할 수 있습니다. Streamlit 앱에 결제 링크를 연결하고, 결제 고객에게 Access Code를 발송하는 방식으로 시작하면 됩니다. "
            "이후 고객이 늘어나면 Supabase, Firebase, Stripe/Paddle Webhook을 연결해 정식 SaaS로 확장할 수 있습니다.\n\n"
            "가장 먼저 해야 할 일은 완벽한 자동화가 아니라 유료로 사고 싶은 샘플 리포트를 만드는 것입니다. "
            "샘플 10개를 만들고 사람들이 어떤 주제에 반응하는지 확인하면, 다음 자동화 방향이 명확해집니다."
        )
    else:
        one_liner = "The input trend has been transformed into a monetizable global online business opportunity."
        why_now = (
            "This opportunity matters now because AI tools reduce execution costs, global users pay for time-saving and money-making insights, "
            "and a Streamlit/GitHub MVP can validate demand quickly."
        )
        revenue = (
            "1) Monthly subscription: $19~$49\n"
            "2) Premium reports: $9~$29 each\n"
            "3) B2B custom analysis: $300~$3,000\n"
            "4) Affiliate commissions\n"
            "5) Templates and prompt packs"
        )
        steps = (
            "Today:\n"
            "1. Pick one customer segment.\n"
            "2. Write the painful problem in one sentence.\n"
            "3. Research 3 competing sites.\n"
            "4. Create 3 free sample reports.\n"
            "5. Share the test link with early users.\n\n"
            "7-Day Plan:\n"
            "Day 1: Define customer\n"
            "Day 2: Build 20 sample records\n"
            "Day 3: Build Streamlit UI\n"
            "Day 4: Add payment links\n"
            "Day 5: Lock premium content\n"
            "Day 6: Recruit 5 testers\n"
            "Day 7: Test paid conversion"
        )
        tools = "Streamlit, GitHub, OpenAI API, Google Sheets, Make, Gumroad/Lemon Squeezy/Paddle, Google Analytics"
        keywords = "AI business opportunity, global trends, money keywords, SaaS ideas, startup trends, online business ideas, automation business"
        risk = (
            "Risks:\n"
            "- Do not promise guaranteed income.\n"
            "- Avoid presenting content as legal, tax, or investment advice.\n"
            "- AI-generated information needs human review.\n"
            "- Prepare refund policy and privacy policy before taking payments."
        )
        validation = (
            "Validation:\n"
            "1. Publish 3 free sample reports.\n"
            "2. Collect email subscribers.\n"
            "3. Track the most clicked categories.\n"
            "4. Show a $19/month payment button.\n"
            "5. If users do not convert, improve specificity before lowering price."
        )
        full_report = (
            f"Input:\n{idea}\n\n"
            f"Target customer:\n{target_customer or 'Not specified'}\n\n"
            "This opportunity is based on the universal need to discover profitable opportunities faster. "
            "Users rarely pay for generic information, but they do pay for insights connected to revenue, cost savings, time savings, funding, and customer acquisition.\n\n"
            "Therefore, the product should not simply aggregate information. It should translate each signal into a practical business opportunity with a clear score, monetization path, tools, risks, and first action.\n\n"
            "The first MVP can run without a complex membership database. Connect payment links and send access codes to paid users. "
            "Later, the product can evolve into a full SaaS with Supabase, Firebase, and payment webhooks.\n\n"
            "The first goal is not perfect automation; it is to create reports people would pay for. Build 10 strong examples, measure reactions, then automate the winning categories."
        )

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "one_liner": one_liner,
        "category": category,
        "region": region,
        "target_customer": target_customer,
        "opportunity_score": score,
        "market_growth_score": min(20, 15 + score // 20),
        "monetization_score": min(20, 14 + score // 20),
        "competition_score": 12,
        "execution_score": 13,
        "urgency_score": 8,
        "global_scale_score": 9,
        "ai_automation_score": 9,
        "why_now": why_now,
        "revenue_models": revenue,
        "pricing_ideas": "Free preview / Starter $19 / Pro $49 / Business $149 / One-time report $9~$29",
        "execution_steps": steps,
        "tools": tools,
        "keyword_pack": keywords,
        "content_ideas": "무료 샘플 리포트, 주간 트렌드 뉴스레터, 업종별 기회 리스트, Product Hunt 분석, AI툴 수익화 가이드",
        "validation_plan": validation,
        "risk": risk,
        "full_report": full_report,
        "source_notes": "Demo-generated analysis. Replace with official source URLs when publishing paid reports.",
    }


def generate_with_openai(
    idea: str,
    category: str,
    region: str,
    target_customer: str,
    output_language: str,
) -> Dict[str, Any]:
    client = get_openai_client()
    if client is None:
        return demo_generate_report(idea, category, region, target_customer, output_language)

    system_prompt = f"""
You are a top 1% global business opportunity analyst, SaaS strategist, and growth operator.

Create a very detailed paid-level opportunity report in {output_language}.
The user is building a Streamlit/GitHub MVP called "Global Opportunity Radar AI".
The report must help users feel: "If I see this, I won't miss money-making opportunities."

Return STRICT JSON only. No markdown outside JSON.

Required JSON keys:
timestamp,
title,
one_liner,
category,
region,
target_customer,
opportunity_score,
market_growth_score,
monetization_score,
competition_score,
execution_score,
urgency_score,
global_scale_score,
ai_automation_score,
why_now,
revenue_models,
pricing_ideas,
execution_steps,
tools,
keyword_pack,
content_ideas,
validation_plan,
risk,
source_notes,
full_report

Scoring:
- opportunity_score: 0-100
- market_growth_score: 0-20
- monetization_score: 0-20
- competition_score: 0-15
- execution_score: 0-15
- urgency_score: 0-10
- global_scale_score: 0-10
- ai_automation_score: 0-10

Make the output long, useful, practical, and premium.
Include:
- why users would pay
- exact monetization paths
- 7-day action plan
- first customer acquisition strategy
- free vs paid content split
- keywords for SEO
- risks and compliance warnings
- what to do today
Do not guarantee profit.
"""

    user_prompt = f"""
Idea / Trend / News:
{idea}

Category:
{category}

Target Region:
{region}

Target Customer:
{target_customer}
"""

    try:
        response = client.chat.completions.create(
            model=get_secret("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()},
            ],
            response_format={"type": "json_object"},
            temperature=0.72,
        )
        raw = response.choices[0].message.content or ""
        parsed = extract_json(raw)
        if not parsed:
            raise ValueError("OpenAI response was not valid JSON.")

        parsed["timestamp"] = parsed.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        parsed["category"] = parsed.get("category") or category
        parsed["region"] = parsed.get("region") or region
        parsed["target_customer"] = parsed.get("target_customer") or target_customer
        parsed["opportunity_score"] = clamp_score(parsed.get("opportunity_score", 80))
        return parsed

    except Exception as e:
        fallback = demo_generate_report(idea, category, region, target_customer, output_language)
        fallback["source_notes"] = f"OpenAI generation failed, demo fallback used. Error: {str(e)}"
        return fallback


# =========================================================
# 8. 렌더링 함수
# =========================================================

def render_status_box(L: Dict[str, str], is_licensed: bool, payment_url: str) -> None:
    if is_licensed:
        st.markdown(
            f"""
            <div class="success-box">
                <h4 style="margin:0 0 6px 0;">{esc(L["active"])}</h4>
                <p style="font-size:13px; margin:0; opacity:.82;">{esc(L["active_desc"])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif st.session_state.free_uses_left > 0:
        st.markdown(
            f"""
            <div class="free-box">
                <h4 style="margin:0 0 6px 0;">{esc(L["free_mode"])}</h4>
                <p style="font-size:13px; margin:0; opacity:.82;">{esc(L["free_desc"].format(count=st.session_state.free_uses_left))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="paywall-box">
                <h4 style="margin:0 0 6px 0;">{esc(L["locked"])}</h4>
                <p style="font-size:13px; margin:0 0 12px 0; opacity:.82;">{esc(L["locked_desc"])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if payment_url:
            st.link_button(L["payment_link"], payment_url, use_container_width=True)


def render_score_breakdown(data: Dict[str, Any]) -> None:
    rows = [
        ("Market Growth", safe_int(data.get("market_growth_score"), 0), 20),
        ("Monetization", safe_int(data.get("monetization_score"), 0), 20),
        ("Competition Advantage", safe_int(data.get("competition_score"), 0), 15),
        ("Execution Ease", safe_int(data.get("execution_score"), 0), 15),
        ("Urgency", safe_int(data.get("urgency_score"), 0), 10),
        ("Global Scale", safe_int(data.get("global_scale_score"), 0), 10),
        ("AI Automation", safe_int(data.get("ai_automation_score"), 0), 10),
    ]
    chart_df = pd.DataFrame(rows, columns=["Factor", "Score", "Max"])
    chart_df["Rate"] = chart_df["Score"] / chart_df["Max"]
    st.dataframe(chart_df, use_container_width=True, hide_index=True)
    st.bar_chart(chart_df.set_index("Factor")["Score"])


def render_report_card(data: Dict[str, Any], L: Dict[str, str], premium: bool = True) -> None:
    title = safe_get(data, "title", "Untitled Opportunity")
    one_liner = safe_get(data, "one_liner", "")
    score = clamp_score(data.get("opportunity_score", 0))

    st.markdown('<div class="result-card">', unsafe_allow_html=True)

    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown(f"## {esc(title)}")
        if one_liner:
            st.write(one_liner)

        badges = [
            safe_get(data, "category", "General"),
            safe_get(data, "region", "Global"),
            safe_get(data, "target_customer", "Target customer not specified"),
            safe_get(data, "timestamp", ""),
        ]
        badge_html = "".join([f"<span class='badge'>{esc(x)}</span>" for x in badges if x])
        st.markdown(badge_html, unsafe_allow_html=True)

    with top_right:
        st.markdown(
            f"""
            <div class="score-circle">
                <div class="score-number">{score}</div>
                <div class="score-label">{esc(L["score"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            L["tab_summary"],
            L["tab_money"],
            L["tab_execution"],
            L["tab_keywords"],
            L["tab_risk"],
            L["tab_full"],
        ]
    )

    with tab0:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("### Why now")
            st.markdown(f"<div class='report-box'>{esc(safe_get(data, 'why_now', ''))}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("### Score breakdown")
            render_score_breakdown(data)

    with tab1:
        st.markdown("### Revenue Models")
        st.markdown(f"<div class='report-box'>{esc(safe_get(data, 'revenue_models', ''))}</div>", unsafe_allow_html=True)
        st.markdown("### Pricing Ideas")
        st.markdown(f"<div class='report-box'>{esc(safe_get(data, 'pricing_ideas', ''))}</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("### Execution Steps")
        st.text_area("Execution Plan", value=safe_get(data, "execution_steps", ""), height=360, label_visibility="collapsed")
        st.markdown("### Tools")
        st.markdown(f"<div class='report-box'>{esc(safe_get(data, 'tools', ''))}</div>", unsafe_allow_html=True)
        st.markdown("### Validation Plan")
        st.text_area("Validation Plan", value=safe_get(data, "validation_plan", ""), height=240, label_visibility="collapsed")

    with tab3:
        st.markdown("### SEO / Money Keywords")
        st.text_area("Keyword Pack", value=safe_get(data, "keyword_pack", ""), height=220, label_visibility="collapsed")
        st.markdown("### Content Ideas")
        st.text_area("Content Ideas", value=safe_get(data, "content_ideas", ""), height=260, label_visibility="collapsed")

    with tab4:
        st.markdown("### Risk / Compliance")
        st.text_area("Risk", value=safe_get(data, "risk", ""), height=260, label_visibility="collapsed")
        st.markdown("### Source Notes")
        st.markdown(f"<div class='report-box'>{esc(safe_get(data, 'source_notes', ''))}</div>", unsafe_allow_html=True)

    with tab5:
        full_report = safe_get(data, "full_report", "")
        if premium:
            st.text_area("Full Premium Report", value=full_report, height=520, label_visibility="collapsed")
        else:
            st.markdown(f"<div class='locked-premium'>{esc(L['paywall_notice'])}</div>", unsafe_allow_html=True)
            preview = full_report[:500] + "..." if len(full_report) > 500 else full_report
            st.markdown(f"<div class='report-box'>{esc(preview)}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_phone_preview(data: Dict[str, Any]) -> None:
    title = safe_get(data, "title", "Opportunity Signal")
    script = (
        f"{safe_get(data, 'one_liner', '')}\n\n"
        f"Score: {safe_get(data, 'opportunity_score', '0')}/100\n\n"
        f"Why now:\n{safe_get(data, 'why_now', '')[:450]}\n\n"
        f"Today:\n{safe_get(data, 'execution_steps', '')[:350]}"
    )
    html_sim = f"""
    <div class="phone-container">
        <div class="phone-badge">LIVE SIGNAL</div>
        <div class="sim-title">{esc(title)}</div>
        <div class="sim-script">{esc(script)}</div>
    </div>
    """
    st.markdown(html_sim, unsafe_allow_html=True)


def dashboard_page(L: Dict[str, str], is_licensed: bool) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>{esc(L["app_title"])}</h1>
            <p>{esc(L["app_subtitle"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    records = st.session_state.opportunity_history
    total = len(records)
    avg_score = round(sum(clamp_score(x.get("opportunity_score", 0)) for x in records) / total, 1) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Generated Signals", total)
    c2.metric("Average Score", avg_score)
    c3.metric("Free Uses Left", st.session_state.free_uses_left)
    c4.metric("License", "Enterprise Pro" if is_licensed else "Free Trial")

    st.divider()
    st.subheader("🔥 Sample Global Opportunity Signals")
    for item in SAMPLE_OPPORTUNITIES:
        render_report_card(item, L, premium=False)


def generate_page(L: Dict[str, str], site_lang: str, is_licensed: bool, payment_url: str) -> None:
    output_language = selected_language_name(site_lang)

    col1, col2 = st.columns([0.92, 1.08], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown(f"### {L['input_title']}")

            categories = [
                "AI / SaaS",
                "Automation",
                "B2B",
                "E-commerce",
                "Creator Economy",
                "Education",
                "Healthcare",
                "Finance",
                "Grant / Tender",
                "Local Business",
                "Real Estate",
                "Travel",
            ]
            regions = [
                "Global",
                "United States",
                "Korea",
                "Japan",
                "Europe",
                "Southeast Asia",
                "Latin America",
                "Middle East",
            ]

            category = st.selectbox(L["category_label"], categories)
            region = st.selectbox(L["region_label"], regions)
            target_customer = st.text_input(L["target_label"], placeholder=L["target_ph"])
            idea = st.text_area(L["idea_label"], placeholder=L["idea_ph"], height=230)

            if not get_secret("OPENAI_API_KEY", ""):
                st.info(L["api_missing"])

            allowed_to_generate = is_licensed or st.session_state.free_uses_left > 0
            if not allowed_to_generate:
                st.markdown(f"<div class='locked-premium'>{esc(L['locked_desc'])}</div>", unsafe_allow_html=True)
                if payment_url:
                    st.link_button(L["payment_link"], payment_url, use_container_width=True)
                generate_btn = False
            else:
                label = L["generate_btn"]
                if not is_licensed:
                    label += f" ({st.session_state.free_uses_left})"
                generate_btn = st.button(label, type="primary", use_container_width=True)

    with col2:
        st.markdown(f"### {L['workspace']}")

        if generate_btn:
            if not idea.strip():
                st.warning(L["need_input"])
            else:
                progress = st.empty()
                with progress.container():
                    st.info("Stage 1/4: Collecting signal context...")
                    time.sleep(0.25)
                    st.info("Stage 2/4: Scoring market and monetization potential...")
                    time.sleep(0.25)
                    st.info("Stage 3/4: Building premium execution report...")
                    time.sleep(0.25)
                    st.info("Stage 4/4: Rendering multilingual opportunity card...")
                    time.sleep(0.25)

                report = generate_with_openai(
                    idea=idea,
                    category=category,
                    region=region,
                    target_customer=target_customer,
                    output_language=output_language,
                )

                if not is_licensed:
                    st.session_state.free_uses_left = max(0, st.session_state.free_uses_left - 1)

                st.session_state.opportunity_history.insert(0, report)
                st.session_state.selected_view_idx = 0
                progress.empty()
                st.rerun()

        if st.session_state.selected_view_idx is not None and st.session_state.opportunity_history:
            current = st.session_state.opportunity_history[st.session_state.selected_view_idx]
            render_phone_preview(current)
        else:
            st.info(L["empty"])

    if st.session_state.selected_view_idx is not None and st.session_state.opportunity_history:
        st.divider()
        current = st.session_state.opportunity_history[st.session_state.selected_view_idx]
        render_report_card(current, L, premium=True)


def explore_page(L: Dict[str, str], is_licensed: bool) -> None:
    st.header("🔎 " + L["explore"])

    records = st.session_state.opportunity_history + SAMPLE_OPPORTUNITIES

    if not records:
        st.info(L["empty"])
        return

    q = st.text_input(L["search"], placeholder="AI, SaaS, funding, healthcare...")
    categories = [L["all"]] + sorted({safe_get(x, "category", "General") for x in records})
    regions = [L["all"]] + sorted({safe_get(x, "region", "Global") for x in records})

    c1, c2 = st.columns(2)
    with c1:
        category = st.selectbox(L["category_label"], categories)
    with c2:
        region = st.selectbox(L["region_label"], regions)

    filtered = []
    for item in records:
        text_blob = " ".join(str(v) for v in item.values()).lower()
        if q and q.lower() not in text_blob:
            continue
        if category != L["all"] and safe_get(item, "category") != category:
            continue
        if region != L["all"] and safe_get(item, "region") != region:
            continue
        filtered.append(item)

    st.download_button(
        L["download"],
        data=csv_bytes(filtered),
        file_name="global_opportunity_radar_reports.csv",
        mime="text/csv",
        use_container_width=True,
    )

    for item in filtered:
        render_report_card(item, L, premium=is_licensed)


def pricing_page(L: Dict[str, str], payment_url: str) -> None:
    st.header("💳 " + L["pricing"])

    plans = [
        {
            "name": "Free",
            "price": "$0",
            "desc": "무료 샘플 기회 / 제한된 생성 / 일부 리포트 미리보기",
        },
        {
            "name": "Starter",
            "price": "$19 / 월",
            "desc": "매일 기회 카드, 기본 점수, 키워드 일부, CSV 다운로드",
        },
        {
            "name": "Pro",
            "price": "$49 / 월",
            "desc": "전체 리포트, 실행계획, 수익모델, 리스크, 키워드, 주간 리포트",
        },
        {
            "name": "Business",
            "price": "$149 / 월",
            "desc": "업종별 맞춤 분석, 이메일 알림, B2B 리포트, 우선 지원",
        },
    ]

    cols = st.columns(4)
    for col, plan in zip(cols, plans):
        with col:
            st.markdown("<div class='price-card'>", unsafe_allow_html=True)
            st.markdown(f"### {plan['name']}")
            st.markdown(f"## {plan['price']}")
            st.write(plan["desc"])
            if plan["name"] != "Free":
                if payment_url:
                    st.link_button(L["payment_link"], payment_url, use_container_width=True)
                else:
                    st.caption("Streamlit Secrets에 PAYMENT_URL을 넣으면 결제 버튼이 연결됩니다.")
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("초기 결제 운영 방식")
    st.write(
        "1차 MVP에서는 복잡한 회원 DB 없이 결제 링크 방식으로 시작합니다. "
        "Gumroad, Lemon Squeezy, Paddle, PayPal, 포트원 중 하나에서 상품을 만들고, "
        "결제 링크를 Streamlit Secrets의 PAYMENT_URL에 넣으면 됩니다. "
        "결제한 고객에게는 이메일로 Access Code를 보내고, 고객은 사이드바에 코드를 입력해 Pro 기능을 사용합니다."
    )
    st.code(
        """
Streamlit Secrets 예시:

OPENAI_API_KEY = "sk-..."
MASTER_LICENSE_KEY = "대표님이_정한_비밀키"
PAYMENT_URL = "https://..."
OPENAI_MODEL = "gpt-4o-mini"
""".strip(),
        language="toml",
    )


def guide_page(L: Dict[str, str]) -> None:
    st.header("📘 " + L["guide"])

    st.markdown(
        """
## 대표님이 해야 하는 부분

### 1단계. app.py 교체
GitHub 저장소에서 기존 `app.py` 내용을 전부 지우고, 이 전체 코드를 붙여넣습니다.

### 2단계. requirements.txt 확인
저장소에 `requirements.txt`가 있어야 합니다. 내용은 아래처럼 두 줄이면 됩니다.

```txt
streamlit
openai
pandas
```

### 3단계. Streamlit Cloud 재부팅
Streamlit Cloud에서 앱이 자동으로 다시 배포됩니다.  
오류가 계속되면 오른쪽 아래 `Manage app` → `Reboot app`을 누릅니다.

### 4단계. OpenAI API Key 넣기
Streamlit Cloud → Manage app → Settings → Secrets에 아래처럼 입력합니다.

```toml
OPENAI_API_KEY = "본인 API 키"
MASTER_LICENSE_KEY = "대표님이 정한 비밀키"
PAYMENT_URL = "결제 링크"
OPENAI_MODEL = "gpt-4o-mini"
```

### 5단계. 유료 결제 연결
처음에는 Gumroad, Lemon Squeezy, Paddle, PayPal 같은 결제 링크 방식으로 시작합니다.  
고객이 결제하면 이메일로 `MASTER_LICENSE_KEY` 또는 별도 고객용 Access Code를 보내는 방식입니다.

### 6단계. 운영 방식
처음에는 완전 자동화보다 반자동이 안전합니다.

- AI가 리포트 생성
- 대표님이 내용 확인
- 좋은 리포트만 유료 콘텐츠로 노출
- 반응 좋은 카테고리를 자동화
- 추후 Supabase/Firebase/Stripe Webhook으로 정식 SaaS화

### 중요
이 앱은 이제 `opportunity_engine.py`, `translations.py` 같은 별도 파일이 없어도 실행됩니다.  
따라서 ModuleNotFoundError가 발생하지 않아야 합니다.
"""
    )


# =========================================================
# 9. 사이드바 및 메인 실행
# =========================================================

with st.sidebar:
    st.markdown(f"## {LANG_PACK['한국어 🇰🇷']['control']}")
    site_lang = st.selectbox("🌐 UI Language", list(LANG_PACK.keys()))
    L = LANG_PACK[site_lang]

    st.divider()

    st.markdown(f"### {L['control']}")
    license_input = st.text_input(L["license_label"], placeholder=L["license_ph"], type="password")

    master_key = get_secret("MASTER_LICENSE_KEY", "EB74")
    is_licensed = bool(license_input) and license_input == master_key

    payment_url = get_secret("PAYMENT_URL", "https://rainscape5.gumroad.com/l/ycgff")

    render_status_box(L, is_licensed, payment_url)

    st.divider()

    page = st.radio(
        "Menu",
        [L["dashboard"], L["generate"], L["explore"], L["pricing"], L["guide"]],
    )

    st.caption(f"Loaded: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


if page == L["dashboard"]:
    dashboard_page(L, is_licensed)
elif page == L["generate"]:
    generate_page(L, site_lang, is_licensed, payment_url)
elif page == L["explore"]:
    explore_page(L, is_licensed)
elif page == L["pricing"]:
    pricing_page(L, payment_url)
else:
    guide_page(L)

st.divider()
st.caption(L["footer_warning"])
