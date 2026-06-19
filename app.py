import json
import os
import time
import hashlib
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# ============================================================
# Global Opportunity Radar AI
# Single-file Streamlit MVP
# - No local imports such as opportunity_engine.py or translations.py
# - Works with or without OpenAI API Key
# - Supports multilingual UI
# - Includes demo data, AI generation, paywall, CSV download
# ============================================================

st.set_page_config(
    page_title="Global Opportunity Radar AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Basic CSS
# -----------------------------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', 'Noto Sans KR', sans-serif;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .hero {
        padding: 28px 30px;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(37,99,235,.18), rgba(16,185,129,.13), rgba(168,85,247,.12));
        border: 1px solid rgba(120,120,160,.22);
        margin-bottom: 18px;
    }
    .hero-title {font-size: 38px; line-height: 1.15; font-weight: 900; margin-bottom: 8px;}
    .hero-sub {font-size: 17px; line-height: 1.6; opacity: .88;}
    .card {
        padding: 20px 22px;
        border-radius: 18px;
        border: 1px solid rgba(140,140,160,.25);
        background: rgba(255,255,255,.035);
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,.06);
    }
    .score-box {
        padding: 15px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(140,140,160,.22);
        background: rgba(37,99,235,.08);
    }
    .score-num {font-size: 34px; font-weight: 900; line-height: 1;}
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid rgba(140,140,160,.28);
        font-size: 12px;
        margin: 3px 4px 3px 0;
        background: rgba(255,255,255,.04);
    }
    .locked {
        padding: 15px;
        border-radius: 14px;
        border: 1px dashed rgba(245,158,11,.65);
        background: rgba(245,158,11,.08);
    }
    .success-box {
        padding: 14px;
        border-radius: 14px;
        border: 1px solid rgba(16,185,129,.55);
        background: rgba(16,185,129,.09);
    }
    .pay-box {
        padding: 14px;
        border-radius: 14px;
        border: 1px solid rgba(239,68,68,.55);
        background: rgba(239,68,68,.08);
    }
    .mini-title {font-size: 13px; opacity: .72; margin-bottom: 4px;}
    .metric-note {font-size: 12px; opacity: .66;}
    .report-block {
        padding: 14px;
        border-radius: 14px;
        border: 1px solid rgba(140,140,160,.16);
        background: rgba(100,116,139,.06);
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Utilities
# -----------------------------
def get_secret(name: str, default: str = "") -> str:
    """Read Streamlit Secret first, then environment variable, then default."""
    try:
        value = st.secrets.get(name, default)
        if value:
            return str(value)
    except Exception:
        pass
    return str(os.getenv(name, default) or default)


def safe_get(data: Dict[str, Any], key: str, default: str = "") -> str:
    value = data.get(key, default)
    if value is None:
        return default
    text = str(value)
    if text.strip() == "" or text.lower() == "nan":
        return default
    return text


def make_key(data: Dict[str, Any], field: str, extra: str = "") -> str:
    raw = "|".join([
        safe_get(data, "id", ""),
        safe_get(data, "title", ""),
        safe_get(data, "timestamp", ""),
        field,
        extra,
    ])
    digest = hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]
    return f"{field}_{digest}"


def csv_bytes(rows: List[Dict[str, Any]]) -> bytes:
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8-sig")


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_json_safely(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass
    return {}

# -----------------------------
# Language Pack
# -----------------------------
LANG_PACK = {
    "한국어 🇰🇷": {
        "app_title": "Global Opportunity Radar AI",
        "hero": "AI가 매일 전 세계 돈 되는 사업기회를 찾아드립니다",
        "hero_sub": "신제품, AI툴, 검색 트렌드, 스타트업 흐름을 분석해 돈 될 가능성·실행 난이도·수익모델을 한 번에 보여주는 글로벌 기회 탐색 MVP입니다.",
        "dashboard": "대시보드",
        "generate": "AI 기회 생성",
        "explore": "기회 탐색",
        "pricing": "유료 결제",
        "guide": "운영 가이드",
        "license": "라이선스 키",
        "unlock": "유료 잠금 해제",
        "locked": "유료회원 전용 상세 분석입니다. 라이선스 키를 입력하면 전체 리포트를 볼 수 있습니다.",
        "active": "Enterprise 라이선스 활성화",
        "trial": "무료 체험 모드",
        "pay": "결제하기",
        "product": "분석할 사업 아이디어/제품/서비스",
        "details": "특징, 타깃고객, 시장 상황, 참고 내용",
        "create": "AI 기회 리포트 생성",
        "fill": "아이디어와 세부 내용을 입력하세요.",
        "score": "AI 기회점수",
        "summary": "핵심 요약",
        "why_now": "왜 지금 뜨는가",
        "money": "수익화 방법",
        "plan": "실행계획",
        "keywords": "키워드/시장 신호",
        "risk": "리스크",
        "report": "전체 리포트",
        "download": "CSV 다운로드",
        "api_missing": "OpenAI API Key가 없어 데모 리포트를 생성합니다. Streamlit Secrets에 OPENAI_API_KEY를 넣으면 실제 AI 생성이 됩니다.",
    },
    "English 🇺🇸": {
        "app_title": "Global Opportunity Radar AI",
        "hero": "AI discovers global money-making opportunities every day",
        "hero_sub": "Analyze launches, AI tools, search trends, startup signals, monetization paths, and execution difficulty in one radar dashboard.",
        "dashboard": "Dashboard",
        "generate": "AI Generator",
        "explore": "Explore",
        "pricing": "Pricing",
        "guide": "Operator Guide",
        "license": "License Key",
        "unlock": "Unlock Premium",
        "locked": "Premium analysis is locked. Enter a valid license key to unlock full reports.",
        "active": "Enterprise License Active",
        "trial": "Free Trial Mode",
        "pay": "Pay Now",
        "product": "Business idea / product / service to analyze",
        "details": "Features, target customers, market context, notes",
        "create": "Generate AI Opportunity Report",
        "fill": "Please enter an idea and details.",
        "score": "AI Opportunity Score",
        "summary": "Summary",
        "why_now": "Why Now",
        "money": "Monetization",
        "plan": "Execution Plan",
        "keywords": "Keywords / Signals",
        "risk": "Risks",
        "report": "Full Report",
        "download": "Download CSV",
        "api_missing": "No OpenAI API Key found. Demo report will be generated. Add OPENAI_API_KEY to Streamlit Secrets for real AI generation.",
    },
    "日本語 🇯🇵": {
        "app_title": "Global Opportunity Radar AI",
        "hero": "AIが世界中の収益機会を毎日発見します",
        "hero_sub": "新製品、AIツール、検索トレンド、スタートアップ信号を分析し、収益化方法と実行難易度を提示します。",
        "dashboard": "ダッシュボード",
        "generate": "AI生成",
        "explore": "探索",
        "pricing": "料金",
        "guide": "運営ガイド",
        "license": "ライセンスキー",
        "unlock": "プレミアム解除",
        "locked": "詳細分析は有料会員専用です。",
        "active": "Enterpriseライセンス有効",
        "trial": "無料体験モード",
        "pay": "決済する",
        "product": "分析する事業アイデア/製品/サービス",
        "details": "特徴、ターゲット、市場状況、参考内容",
        "create": "AI機会レポート生成",
        "fill": "アイデアと詳細を入力してください。",
        "score": "AI機会スコア",
        "summary": "要約",
        "why_now": "なぜ今か",
        "money": "収益化",
        "plan": "実行計画",
        "keywords": "キーワード/市場信号",
        "risk": "リスク",
        "report": "全体レポート",
        "download": "CSVダウンロード",
        "api_missing": "OpenAI API Keyがないためデモレポートを生成します。",
    },
    "Español 🇪🇸": {
        "app_title": "Global Opportunity Radar AI",
        "hero": "La IA encuentra oportunidades globales de negocio cada día",
        "hero_sub": "Analiza lanzamientos, herramientas de IA, tendencias de búsqueda y señales de startups para mostrar monetización y dificultad de ejecución.",
        "dashboard": "Panel",
        "generate": "Generador IA",
        "explore": "Explorar",
        "pricing": "Precios",
        "guide": "Guía",
        "license": "Clave de licencia",
        "unlock": "Desbloquear Premium",
        "locked": "El análisis premium está bloqueado.",
        "active": "Licencia Enterprise activa",
        "trial": "Modo de prueba gratuita",
        "pay": "Pagar",
        "product": "Idea/producto/servicio a analizar",
        "details": "Características, clientes objetivo, contexto de mercado",
        "create": "Generar informe de oportunidad",
        "fill": "Introduce una idea y detalles.",
        "score": "Puntuación IA",
        "summary": "Resumen",
        "why_now": "Por qué ahora",
        "money": "Monetización",
        "plan": "Plan de ejecución",
        "keywords": "Palabras clave / señales",
        "risk": "Riesgos",
        "report": "Informe completo",
        "download": "Descargar CSV",
        "api_missing": "No se encontró OpenAI API Key. Se generará un informe demo.",
    },
    "Deutsch 🇩🇪": {
        "app_title": "Global Opportunity Radar AI",
        "hero": "KI entdeckt täglich globale Geschäftschancen",
        "hero_sub": "Analysiert Produktstarts, KI-Tools, Suchtrends und Startup-Signale inklusive Monetarisierung und Umsetzungsaufwand.",
        "dashboard": "Dashboard",
        "generate": "KI Generator",
        "explore": "Chancen",
        "pricing": "Preise",
        "guide": "Leitfaden",
        "license": "Lizenzschlüssel",
        "unlock": "Premium freischalten",
        "locked": "Premium-Analyse ist gesperrt.",
        "active": "Enterprise-Lizenz aktiv",
        "trial": "Kostenloser Testmodus",
        "pay": "Bezahlen",
        "product": "Idee/Produkt/Service analysieren",
        "details": "Funktionen, Zielkunden, Markt Kontext",
        "create": "Chancenbericht generieren",
        "fill": "Bitte Idee und Details eingeben.",
        "score": "KI Chancen-Score",
        "summary": "Zusammenfassung",
        "why_now": "Warum jetzt",
        "money": "Monetarisierung",
        "plan": "Ausführungsplan",
        "keywords": "Keywords / Signale",
        "risk": "Risiken",
        "report": "Vollständiger Bericht",
        "download": "CSV herunterladen",
        "api_missing": "Kein OpenAI API Key gefunden. Demo-Bericht wird erstellt.",
    },
    "中文 🇨🇳": {
        "app_title": "Global Opportunity Radar AI",
        "hero": "AI 每天发现全球赚钱机会",
        "hero_sub": "分析新产品、AI工具、搜索趋势和创业信号，并给出变现方法与执行难度。",
        "dashboard": "仪表盘",
        "generate": "AI生成",
        "explore": "机会探索",
        "pricing": "付费",
        "guide": "运营指南",
        "license": "许可证密钥",
        "unlock": "解锁高级版",
        "locked": "高级分析已锁定。",
        "active": "企业许可证已激活",
        "trial": "免费试用模式",
        "pay": "支付",
        "product": "要分析的商业想法/产品/服务",
        "details": "特点、目标客户、市场情况、备注",
        "create": "生成AI机会报告",
        "fill": "请输入想法和详细信息。",
        "score": "AI机会评分",
        "summary": "摘要",
        "why_now": "为什么是现在",
        "money": "变现方式",
        "plan": "执行计划",
        "keywords": "关键词/市场信号",
        "risk": "风险",
        "report": "完整报告",
        "download": "下载CSV",
        "api_missing": "未找到 OpenAI API Key，将生成演示报告。",
    },
}

# -----------------------------
# Demo Data
# -----------------------------
DEMO_OPPORTUNITIES: List[Dict[str, Any]] = [
    {
        "id": "demo-001",
        "timestamp": now_stamp(),
        "title": "AI 검색노출 분석 서비스",
        "category": "B2B SaaS",
        "region": "Global",
        "score": 91,
        "difficulty": "Medium",
        "summary": "기업들이 Google 검색뿐 아니라 ChatGPT, Gemini, Perplexity 같은 AI 답변에서 자사 브랜드가 어떻게 노출되는지 확인하고 싶어 하는 수요를 겨냥한 B2B SaaS 기회입니다.",
        "why_now": "AI 검색과 답변형 검색이 확대되면서 기업의 기존 SEO 전략이 바뀌고 있습니다. 앞으로는 검색결과 1페이지보다 AI가 추천하는 브랜드인지가 중요해질 수 있습니다.",
        "monetization": "월 구독형 리포트, 경쟁사 비교 분석, 브랜드 노출 개선 컨설팅, 기업용 대시보드 판매가 가능합니다. 초기 가격은 월 49~299달러 구간으로 테스트할 수 있습니다.",
        "execution_plan": "1) 특정 업종 1개 선택 2) 대표 검색질문 30개 작성 3) AI 답변에서 브랜드 노출 여부 기록 4) 경쟁사 비교표 작성 5) 개선 제안 리포트 샘플 제작 6) LinkedIn과 이메일로 B2B 고객에게 제안",
        "keywords": "AI SEO, GEO, Generative Engine Optimization, AI visibility, brand monitoring, ChatGPT search ranking",
        "risk": "AI 플랫폼별 답변이 변동될 수 있고 자동 수집 방식은 약관 확인이 필요합니다. 초기에는 수동/반자동 리포트로 시작하는 것이 안전합니다.",
        "full_report": "이 기회는 단순 트렌드가 아니라 기업의 마케팅 예산과 연결됩니다. 고객은 '우리 회사가 AI에게 추천되는가?'를 알고 싶어합니다. MVP는 자동화된 SaaS가 아니라 월간 PDF 리포트로 시작해도 됩니다. 첫 고객은 마케팅 에이전시, SaaS 기업, 병원, 로펌, B2B 제조사입니다.",
    },
    {
        "id": "demo-002",
        "timestamp": now_stamp(),
        "title": "정부지원금·입찰·보조금 글로벌 매칭",
        "category": "Opportunity Data",
        "region": "Korea / Global",
        "score": 88,
        "difficulty": "Medium",
        "summary": "중소기업, 스타트업, 프리랜서, 비영리단체에게 받을 수 있는 지원금·공모전·입찰 정보를 조건별로 찾아주는 유료 정보 서비스입니다.",
        "why_now": "지원사업 정보는 흩어져 있고 마감일이 짧습니다. 사람들은 자신에게 해당되는 기회를 놓치지 않기 위해 돈을 낼 가능성이 높습니다.",
        "monetization": "월 19,000원 개인 플랜, 월 99,000원 기업 플랜, 지원사업 요약 PDF, 신청서 초안 작성 대행, 전문가 연결 수수료가 가능합니다.",
        "execution_plan": "1) 한국 창업지원사업부터 시작 2) 대상 고객을 스타트업/소상공인으로 제한 3) 매일 10개 공고 수집 4) 지원 가능성 점수화 5) 이메일 알림 제공 6) 첫 달은 수동 큐레이션으로 품질 확보",
        "keywords": "grant finder, startup grant, government support, R&D funding, tender alerts, small business subsidy",
        "risk": "공고 정보의 최신성, 자격요건 오류, 법률·행정 자문 오인 위험이 있습니다. 반드시 '정보 제공이며 최종 확인은 공식 공고 기준' 문구가 필요합니다.",
        "full_report": "이 모델의 장점은 고객의 지불 이유가 강하다는 점입니다. '돈 받을 기회'를 알려주는 서비스라서 무료 뉴스보다 결제 전환이 쉽습니다. 초기에는 국가를 넓히기보다 한국 또는 미국 스타트업 지원사업 하나로 좁혀야 합니다.",
    },
    {
        "id": "demo-003",
        "timestamp": now_stamp(),
        "title": "직업별 AI툴 수익화 레이더",
        "category": "AI Tools",
        "region": "Global",
        "score": 84,
        "difficulty": "Low-Medium",
        "summary": "수많은 AI툴을 단순 목록으로 보여주는 것이 아니라, 직업별로 실제 돈을 벌거나 업무 시간을 줄이는 조합을 추천하는 정보 사이트입니다.",
        "why_now": "AI툴은 너무 많아졌지만 사용자는 '내 일에 뭘 써야 하는지'를 모릅니다. 직업별 추천과 실행 템플릿은 유료화 가능성이 있습니다.",
        "monetization": "AI툴 제휴수익, 월 구독, 직업별 템플릿 판매, 강의, 컨설팅 리드 연결이 가능합니다.",
        "execution_plan": "1) 쇼핑몰 운영자, 학원장, 영업사원 중 한 직업 선택 2) 업무 10개 분류 3) 각 업무별 AI툴 조합 작성 4) 실제 사용 프롬프트 제공 5) 무료 3개 공개, 나머지 유료 잠금",
        "keywords": "best AI tools for marketers, AI tools for small business, workflow automation, prompt templates, AI stack",
        "risk": "AI툴 디렉터리 경쟁이 많습니다. 단순 목록은 경쟁력이 없고, 반드시 '실제 사용법·프롬프트·수익화 예시'가 있어야 합니다.",
        "full_report": "이 기회는 콘텐츠 SEO와 제휴수익이 결합되는 구조입니다. Futurepedia류의 단순 디렉터리와 달리 '업종별 실행 패키지'를 판매해야 합니다. 가장 좋은 시작점은 한국 소상공인 또는 글로벌 크리에이터입니다.",
    },
]

# -----------------------------
# Session State
# -----------------------------
if "free_uses_left" not in st.session_state:
    st.session_state.free_uses_left = 3
if "workspace_history" not in st.session_state:
    st.session_state.workspace_history = []
if "premium_unlocked" not in st.session_state:
    st.session_state.premium_unlocked = False

# -----------------------------
# AI Engine
# -----------------------------
def demo_generate(idea: str, details: str, language_name: str, category: str, region: str) -> Dict[str, Any]:
    title = idea.strip()[:80] if idea.strip() else "AI Opportunity"
    return {
        "id": hashlib.md5((title + now_stamp()).encode("utf-8")).hexdigest()[:10],
        "timestamp": now_stamp(),
        "title": title,
        "category": category,
        "region": region,
        "score": 82,
        "difficulty": "Medium",
        "summary": f"'{title}' 아이디어는 특정 고객의 시간 절약, 매출 증가, 정보 탐색 비용 절감과 연결될 때 유료화 가능성이 있습니다. 초기에는 범위를 좁혀 빠르게 검증하는 것이 중요합니다.",
        "why_now": "AI 자동화 도구가 대중화되면서 혼자서도 데이터 수집, 요약, 리포트 생성, 랜딩페이지 제작, 이메일 발송까지 구현할 수 있는 환경이 만들어졌습니다.",
        "monetization": "월 구독, 1회 리포트 판매, 템플릿 판매, B2B 맞춤 리포트, 제휴수익, 컨설팅 연결 수수료를 조합할 수 있습니다.",
        "execution_plan": "1) 고객군 하나 선택\n2) 고객이 돈을 내는 이유를 한 문장으로 정의\n3) 무료 샘플 3개 제작\n4) 랜딩페이지에 가격표 게시\n5) 이메일/커뮤니티로 30명에게 테스트\n6) 결제 의향이 있는 사람만 인터뷰\n7) 반복 구매 가능한 구독형으로 전환",
        "keywords": "AI business opportunity, niche SaaS, paid report, trend radar, opportunity scoring, automation service",
        "risk": "수익을 보장하는 표현은 피해야 하며, 데이터 출처와 최신성 확인이 필요합니다. 처음부터 완전 자동화보다 사람이 검수하는 반자동 구조가 안정적입니다.",
        "full_report": f"분석 대상: {title}\n\n입력 세부내용:\n{details}\n\n이 아이디어는 전 세계 사용자를 대상으로 확장 가능하지만, 초기에는 반드시 특정 고객군 하나로 좁혀야 합니다. 예를 들어 '모든 창업자'가 아니라 'AI툴을 활용하려는 1인 사업자', 'B2B SaaS 마케터', '해외 사업기회를 찾는 직장인'처럼 구체화해야 합니다. 핵심은 정보량이 아니라 의사결정 도움입니다. 고객은 뉴스 100개보다 지금 실행할 기회 3개와 구체적 첫 행동을 원합니다.",
    }


def ai_generate(idea: str, details: str, language_name: str, category: str, region: str) -> Dict[str, Any]:
    api_key = get_secret("OPENAI_API_KEY", "")
    model = get_secret("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key or OpenAI is None:
        return demo_generate(idea, details, language_name, category, region)

    system_prompt = f"""
You are a top-tier global business opportunity analyst and SaaS growth strategist.
Create a very detailed opportunity report in {language_name}.
Return ONLY valid JSON with these keys:
- title
- category
- region
- score: integer 0-100
- difficulty
- summary
- why_now
- monetization
- execution_plan
- keywords
- risk
- full_report

Scoring criteria:
Market growth 20, monetization 20, competition gap 15, execution difficulty 15, urgency 10, global scalability 10, AI automation potential 10.
The report must be practical, specific, and useful enough that a paid subscriber feels they will not miss a money-making opportunity.
Do not guarantee profit. Include realistic risks.
"""
    user_prompt = f"""
Idea/Product/Service: {idea}
Category: {category}
Target Region: {region}
Details:
{details}
"""
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.72,
        )
        content = response.choices[0].message.content or "{}"
        data = parse_json_safely(content)
        if not data:
            return demo_generate(idea, details, language_name, category, region)
        data["id"] = hashlib.md5((safe_get(data, "title", idea) + now_stamp()).encode("utf-8")).hexdigest()[:10]
        data["timestamp"] = now_stamp()
        data["category"] = safe_get(data, "category", category)
        data["region"] = safe_get(data, "region", region)
        try:
            data["score"] = int(float(data.get("score", 80)))
        except Exception:
            data["score"] = 80
        return data
    except Exception as exc:
        fallback = demo_generate(idea, details + f"\n\nAI Error: {exc}", language_name, category, region)
        fallback["summary"] += "\n\n참고: OpenAI 호출 중 오류가 발생해 데모 엔진으로 생성했습니다."
        return fallback

# -----------------------------
# Rendering
# -----------------------------
def render_hero(L: Dict[str, str]) -> None:
    st.markdown(
        f"""
<div class="hero">
    <div class="hero-title">📡 {L['hero']}</div>
    <div class="hero-sub">{L['hero_sub']}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_report_card(data: Dict[str, Any], L: Dict[str, str], premium: bool = False, compact: bool = False) -> None:
    score = int(data.get("score", 0) or 0)
    score = max(0, min(100, score))
    with st.container(border=True):
        top1, top2 = st.columns([4, 1])
        with top1:
            st.markdown(f"### {safe_get(data, 'title', 'Untitled Opportunity')}")
            st.markdown(
                f"<span class='badge'>{safe_get(data, 'category', 'General')}</span>"
                f"<span class='badge'>{safe_get(data, 'region', 'Global')}</span>"
                f"<span class='badge'>{safe_get(data, 'difficulty', 'Medium')}</span>"
                f"<span class='badge'>{safe_get(data, 'timestamp', '')}</span>",
                unsafe_allow_html=True,
            )
        with top2:
            st.markdown(
                f"<div class='score-box'><div class='score-num'>{score}</div><div class='metric-note'>{L['score']}</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown(f"**{L['summary']}**")
        st.write(safe_get(data, "summary", "No summary."))

        if not premium:
            st.markdown(f"<div class='locked'>🔒 {L['locked']}</div>", unsafe_allow_html=True)
            return

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔥 " + L["why_now"],
            "💰 " + L["money"],
            "🧭 " + L["plan"],
            "🔎 " + L["keywords"],
            "⚠️ " + L["risk"],
            "📄 " + L["report"],
        ])
        with tab1:
            st.markdown("<div class='report-block'>", unsafe_allow_html=True)
            st.write(safe_get(data, "why_now", ""))
            st.markdown("</div>", unsafe_allow_html=True)
        with tab2:
            st.text_area(
                L["money"],
                value=safe_get(data, "monetization", ""),
                height=230,
                label_visibility="collapsed",
                key=make_key(data, "monetization"),
            )
        with tab3:
            st.text_area(
                L["plan"],
                value=safe_get(data, "execution_plan", ""),
                height=260,
                label_visibility="collapsed",
                key=make_key(data, "execution_plan"),
            )
        with tab4:
            st.text_area(
                L["keywords"],
                value=safe_get(data, "keywords", ""),
                height=220,
                label_visibility="collapsed",
                key=make_key(data, "keywords"),
            )
        with tab5:
            st.text_area(
                L["risk"],
                value=safe_get(data, "risk", ""),
                height=240,
                label_visibility="collapsed",
                key=make_key(data, "risk"),
            )
        with tab6:
            st.text_area(
                L["report"],
                value=safe_get(data, "full_report", ""),
                height=360,
                label_visibility="collapsed",
                key=make_key(data, "full_report"),
            )


def all_rows() -> List[Dict[str, Any]]:
    return st.session_state.workspace_history + DEMO_OPPORTUNITIES


def sidebar_ui() -> tuple:
    with st.sidebar:
        st.markdown("## 📡 Radar Control")
        language = st.selectbox("🌐 Language", list(LANG_PACK.keys()))
        L = LANG_PACK[language]
        st.divider()

        master_key = get_secret("MASTER_LICENSE_KEY", "EB74")
        user_key = st.text_input("🔑 " + L["license"], type="password", placeholder="Enter license key")
        if st.button("🔓 " + L["unlock"]):
            if user_key and user_key == master_key:
                st.session_state.premium_unlocked = True
                st.success(L["active"])
            else:
                st.error("Invalid license key")

        if st.session_state.premium_unlocked:
            st.markdown(f"<div class='success-box'>✅ {L['active']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='pay-box'>🎁 {L['trial']}: {st.session_state.free_uses_left} generations left</div>", unsafe_allow_html=True)
            payment_url = get_secret("PAYMENT_URL", "https://rainscape5.gumroad.com/l/ycgff")
            st.link_button("💳 " + L["pay"], payment_url)

        st.divider()
        page = st.radio("Menu", [L["dashboard"], L["generate"], L["explore"], L["pricing"], L["guide"]])
        return L, language, page


def dashboard_page(L: Dict[str, str], premium: bool) -> None:
    render_hero(L)
    rows = all_rows()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Signals", len(rows))
    c2.metric("Avg Score", f"{sum(int(r.get('score', 0)) for r in rows) / max(len(rows), 1):.1f}")
    c3.metric("Premium", "Unlocked" if premium else "Locked")
    c4.metric("Updated", datetime.now().strftime("%H:%M"))

    st.subheader("🔥 Top Opportunity Signals")
    top_rows = sorted(rows, key=lambda x: int(x.get("score", 0) or 0), reverse=True)[:5]
    for item in top_rows:
        render_report_card(item, L, premium=premium)


def generate_page(L: Dict[str, str], language: str, premium: bool) -> None:
    st.header("🤖 " + L["generate"])
    if not get_secret("OPENAI_API_KEY", ""):
        st.info(L["api_missing"])

    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["AI", "SaaS", "B2B", "E-commerce", "Finance", "Healthcare", "Education", "Creator Economy", "Local Business", "Investment Info"])
    with col2:
        region = st.selectbox("Region", ["Global", "United States", "Korea", "Japan", "Europe", "Southeast Asia", "Latin America", "Middle East"])

    idea = st.text_input(L["product"], placeholder="예: AI 검색노출 분석 서비스, 글로벌 지원금 알림 사이트")
    details = st.text_area(L["details"], height=180, placeholder="누가 고객인지, 어떤 문제를 해결하는지, 어떤 정보를 참고했는지 적어주세요.")

    disabled = (not premium and st.session_state.free_uses_left <= 0)
    if disabled:
        st.warning("무료 생성 횟수를 모두 사용했습니다. 라이선스 키를 입력하거나 결제 링크를 연결하세요.")

    if st.button("🚀 " + L["create"], type="primary", disabled=disabled):
        if not idea.strip() or not details.strip():
            st.warning(L["fill"])
        else:
            with st.spinner("AI Opportunity Report 생성 중..."):
                time.sleep(0.3)
                result = ai_generate(idea, details, language, category, region)
            if not premium:
                st.session_state.free_uses_left = max(0, st.session_state.free_uses_left - 1)
            st.session_state.workspace_history.insert(0, result)
            st.success("Report generated successfully")
            render_report_card(result, L, premium=True)


def explore_page(L: Dict[str, str], premium: bool) -> None:
    st.header("🔎 " + L["explore"])
    rows = all_rows()
    q = st.text_input("Search", placeholder="AI, SaaS, funding, SEO...")
    c1, c2 = st.columns(2)
    categories = ["All"] + sorted(set(safe_get(r, "category", "General") for r in rows))
    regions = ["All"] + sorted(set(safe_get(r, "region", "Global") for r in rows))
    with c1:
        category = st.selectbox("Category", categories)
    with c2:
        region = st.selectbox("Region", regions)

    filtered = rows
    if q.strip():
        qq = q.lower().strip()
        filtered = [r for r in filtered if qq in json.dumps(r, ensure_ascii=False).lower()]
    if category != "All":
        filtered = [r for r in filtered if safe_get(r, "category") == category]
    if region != "All":
        filtered = [r for r in filtered if safe_get(r, "region") == region]

    st.download_button(L["download"], data=csv_bytes(filtered), file_name="opportunities.csv", mime="text/csv")
    for item in filtered:
        render_report_card(item, L, premium=premium)


def pricing_page(L: Dict[str, str]) -> None:
    st.header("💳 " + L["pricing"])
    payment_url = get_secret("PAYMENT_URL", "https://rainscape5.gumroad.com/l/ycgff")
    plans = [
        ("Free", "0", "데모 기회 열람 + 무료 AI 생성 3회"),
        ("Starter", "$19 / 월", "매일 기회 10개 + 기본 점수"),
        ("Pro", "$49 / 월", "전체 리포트 + 실행계획 + 키워드 + 리스크"),
        ("Business", "$149 / 월", "업종별 맞춤 리포트 + B2B 분석"),
    ]
    cols = st.columns(4)
    for col, (name, price, desc) in zip(cols, plans):
        with col:
            with st.container(border=True):
                st.markdown(f"### {name}")
                st.markdown(f"## {price}")
                st.write(desc)
                if name != "Free":
                    st.link_button("💳 " + L["pay"], payment_url)
    st.info("초기 MVP는 결제 서비스에서 결제 링크를 만들고, 결제 고객에게 라이선스 키를 이메일로 전달하는 방식으로 운영합니다. 이후 결제 웹훅과 회원 DB를 붙이면 완전 자동화가 가능합니다.")


def guide_page(L: Dict[str, str]) -> None:
    st.header("🧭 " + L["guide"])
    st.markdown(
        """
### 1단계: GitHub 파일 확인
반드시 GitHub 저장소의 `app.py` 11번째 줄 근처에 아래 문장이 없어야 합니다.

```python
from opportunity_engine import convert_df_to_csv_bytes, generate_opportunity, load_opportunities
```

이 문장이 보이면 아직 예전 파일이 실행 중입니다.

### 2단계: 필요한 파일
```text
app.py
requirements.txt
```

### 3단계: requirements.txt
```text
streamlit
openai
pandas
```

### 4단계: Streamlit Secrets
Streamlit Cloud > Manage app > Settings > Secrets 에 아래처럼 입력합니다.

```toml
OPENAI_API_KEY = "여기에_본인_OpenAI_API_Key"
OPENAI_MODEL = "gpt-4o-mini"
MASTER_LICENSE_KEY = "EB74"
PAYMENT_URL = "https://rainscape5.gumroad.com/l/ycgff"
```

### 5단계: Reboot
파일 교체 후 Streamlit Cloud에서 `Manage app → Reboot app`을 누르세요.
"""
    )

# -----------------------------
# Main
# -----------------------------
L, language, page = sidebar_ui()
premium = bool(st.session_state.premium_unlocked)

if page == L["dashboard"]:
    dashboard_page(L, premium)
elif page == L["generate"]:
    generate_page(L, language, premium)
elif page == L["explore"]:
    explore_page(L, premium)
elif page == L["pricing"]:
    pricing_page(L)
else:
    guide_page(L)
