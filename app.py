from __future__ import annotations

import html
import os
from datetime import datetime
from typing import Any, Dict

import pandas as pd
import streamlit as st

from opportunity_engine import convert_df_to_csv_bytes, generate_opportunity, load_opportunities
from translations import LANGUAGES, T

st.set_page_config(
    page_title="Global Opportunity Radar AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
.hero {padding: 1.4rem 1.6rem; border-radius: 1.2rem; background: linear-gradient(135deg, rgba(75,85,255,.16), rgba(0,200,150,.10)); border: 1px solid rgba(120,120,160,.22); margin-bottom: 1rem;}
.card {padding: 1rem 1.1rem; border-radius: 1rem; border: 1px solid rgba(130,130,130,.24); margin-bottom: 1rem; background: rgba(255,255,255,.03);}
.score {font-size: 1.9rem; font-weight: 800; line-height: 1.0;}
.badge {display: inline-block; padding: .16rem .55rem; border-radius: 999px; border: 1px solid rgba(120,120,120,.25); margin-right: .3rem; margin-top: .2rem; font-size: .78rem;}
.locked {padding: .85rem; border-radius: .8rem; border: 1px dashed rgba(200,170,60,.55); background: rgba(255,200,0,.07);}
.small {font-size:.9rem; opacity:.82;}
.sim-script {padding: .85rem; border-radius: .8rem; background: rgba(100,100,140,.08); border: 1px solid rgba(120,120,160,.18); font-size: .92rem; line-height: 1.55;}
.price-card {padding: 1rem; border-radius: 1rem; border: 1px solid rgba(130,130,130,.24); min-height: 250px;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def get_secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
        return str(value) if value else default
    except Exception:
        return os.getenv(name, default)


def L(labels: Dict[str, str], key: str, fallback: str) -> str:
    return str(labels.get(key, fallback))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def safe_text(row: Any, key: str, fallback: str = "") -> str:
    try:
        value = row.get(key, fallback) if hasattr(row, "get") else fallback
    except Exception:
        value = fallback
    if value is None:
        return fallback
    text = str(value)
    if text.strip() == "" or text.lower() == "nan":
        return fallback
    return text


def safe_score(row: Any) -> int:
    try:
        return max(0, min(100, int(float(safe_text(row, "score", "0")))))
    except Exception:
        return 0


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    required = [
        "title", "category", "region", "tier", "score", "difficulty", "summary",
        "why_now", "revenue_model", "tools", "action_step", "risk",
        "source_url", "created_at", "full_script",
    ]
    df = df.copy()
    for col in required:
        if col not in df.columns:
            df[col] = ""
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
    return df


def is_unlocked() -> bool:
    return bool(st.session_state.get("premium_unlocked", False))


def build_full_script(row: pd.Series) -> str:
    full_script = safe_text(row, "full_script")
    if full_script:
        return full_script
    return (
        f"[요약]\n{safe_text(row, 'summary', '요약 정보가 아직 없습니다.')}\n\n"
        f"[왜 지금 뜨는가]\n{safe_text(row, 'why_now', '정보가 아직 없습니다.')}\n\n"
        f"[수익모델]\n{safe_text(row, 'revenue_model', '정보가 아직 없습니다.')}\n\n"
        f"[필요 도구]\n{safe_text(row, 'tools', '정보가 아직 없습니다.')}\n\n"
        f"[오늘 당장 할 일]\n{safe_text(row, 'action_step', '정보가 아직 없습니다.')}\n\n"
        f"[위험요소]\n{safe_text(row, 'risk', '정보가 아직 없습니다.')}"
    )


def unlock_box(labels: Dict[str, str]) -> None:
    st.markdown(f"### 🔐 {L(labels, 'paid_locked', '유료회원 전용 분석')}")
    st.caption(L(labels, "unlock_hint", "결제 후 받은 Access Code를 입력하면 Pro/Biz 내용을 볼 수 있습니다."))
    code = st.text_input(L(labels, "access_code", "Access Code 입력"), type="password")
    valid_codes = {
        get_secret("STARTER_ACCESS_CODE", "starter-demo-2026"),
        get_secret("PRO_ACCESS_CODE", "pro-demo-2026"),
        get_secret("BUSINESS_ACCESS_CODE", "business-demo-2026"),
    }
    if st.button(L(labels, "unlock", "잠금 해제")):
        if code and code in valid_codes:
            st.session_state["premium_unlocked"] = True
            st.success(L(labels, "unlocked", "유료 콘텐츠가 열렸습니다."))
        else:
            st.error("Access Code가 맞지 않습니다. / Invalid Access Code")


def render_card(row: pd.Series, labels: Dict[str, str], premium: bool) -> None:
    score = safe_score(row)
    tier = safe_text(row, "tier", "Free")
    unlocked = tier.lower() == "free" or premium
    full_script_safe = build_full_script(row)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown(f"### {esc(safe_text(row, 'title', 'Untitled Opportunity'))}")
        badges = "".join([
            f"<span class='badge'>{esc(safe_text(row, 'category', 'General'))}</span>",
            f"<span class='badge'>{esc(safe_text(row, 'region', 'Global'))}</span>",
            f"<span class='badge'>{esc(tier)}</span>",
            f"<span class='badge'>{esc(safe_text(row, 'difficulty', ''))}</span>" if safe_text(row, "difficulty") else "",
            f"<span class='badge'>{esc(safe_text(row, 'created_at', ''))}</span>" if safe_text(row, "created_at") else "",
        ])
        st.markdown(badges, unsafe_allow_html=True)
    with top_right:
        st.markdown(f"<div class='score'>{score}</div><div class='small'>{esc(L(labels, 'score', 'AI 기회점수'))}</div>", unsafe_allow_html=True)

    st.markdown(f"**{L(labels, 'summary', '요약')}**")
    st.write(safe_text(row, "summary", "요약 정보가 아직 없습니다."))

    if unlocked:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{L(labels, 'why_now', '왜 지금 뜨는가')}**")
            st.write(safe_text(row, "why_now", "정보가 아직 없습니다."))
            st.markdown(f"**{L(labels, 'revenue_model', '수익모델')}**")
            st.write(safe_text(row, "revenue_model", "정보가 아직 없습니다."))
            st.markdown(f"**{L(labels, 'tools', '필요 도구')}**")
            st.write(safe_text(row, "tools", "정보가 아직 없습니다."))
        with c2:
            st.markdown(f"**{L(labels, 'action_step', '오늘 당장 할 일')}**")
            st.write(safe_text(row, "action_step", "정보가 아직 없습니다."))
            st.markdown(f"**{L(labels, 'risk', '위험요소')}**")
            st.write(safe_text(row, "risk", "정보가 아직 없습니다."))
            st.markdown(f"**{L(labels, 'source', '출처/참고')}**")
            source = safe_text(row, "source_url", "")
            if source.startswith("http://") or source.startswith("https://"):
                st.markdown(f"[Source link]({source})")
            else:
                st.write(source if source else "정보가 아직 없습니다.")

        with st.expander("📄 실행 대본 / Full opportunity script"):
            st.markdown(
                f"<div class='sim-script'>{esc(full_script_safe[:220])}... (아래에서 전문 확인 가능)</div>",
                unsafe_allow_html=True,
            )
            st.text_area("Script", value=full_script_safe, height=260, label_visibility="collapsed")
    else:
        st.markdown(f"<div class='locked'>🔒 {esc(L(labels, 'paid_locked', '유료회원 전용 분석'))}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def dashboard_page(df: pd.DataFrame, labels: Dict[str, str]) -> None:
    st.markdown(
        f"<div class='hero'><h1>📡 {esc(L(labels, 'app_title', 'Global Opportunity Radar AI'))}</h1>"
        f"<p>{esc(L(labels, 'tagline', 'AI가 매일 전 세계 돈 되는 사업기회를 찾아 점수화합니다.'))}</p></div>",
        unsafe_allow_html=True,
    )
    if df.empty:
        st.warning("아직 데이터가 없습니다. AI 생성 메뉴에서 첫 기회 카드를 만들어보세요.")
        return
    df = ensure_columns(df)
    m1, m2, m3 = st.columns(3)
    m1.metric(L(labels, "total_opportunities", "전체 기회"), f"{len(df):,}")
    m2.metric(L(labels, "avg_score", "평균 기회점수"), f"{df['score'].mean():.1f}")
    top_category = df["category"].mode().iloc[0] if not df["category"].mode().empty else "-"
    m3.metric(L(labels, "top_category", "상위 카테고리"), top_category)
    st.subheader("🔥 Top Signals")
    for _, row in df.head(3).iterrows():
        render_card(row, labels, is_unlocked())


def opportunities_page(df: pd.DataFrame, labels: Dict[str, str]) -> None:
    st.header("🔎 " + L(labels, "nav_opportunities", "기회 탐색"))
    if df.empty:
        st.warning("표시할 기회 데이터가 없습니다.")
        return
    df = ensure_columns(df)

    if not is_unlocked():
        unlock_box(labels)
        st.divider()

    query = st.text_input(L(labels, "search", "검색"), placeholder="AI agent, SaaS, healthcare, video...")
    c1, c2, c3 = st.columns(3)
    with c1:
        categories = ["All"] + sorted([x for x in df["category"].dropna().astype(str).unique().tolist() if x])
        category = st.selectbox(L(labels, "category", "카테고리"), categories)
    with c2:
        regions = ["All"] + sorted([x for x in df["region"].dropna().astype(str).unique().tolist() if x])
        region = st.selectbox(L(labels, "region", "지역"), regions)
    with c3:
        tiers = ["All"] + sorted([x for x in df["tier"].dropna().astype(str).unique().tolist() if x])
        tier = st.selectbox(L(labels, "tier", "공개 범위"), tiers)

    filtered = df.copy()
    if query:
        q = query.lower().strip()
        blob = filtered.astype(str).agg(" ".join, axis=1).str.lower()
        filtered = filtered[blob.str.contains(q, na=False, regex=False)]
    if category != "All":
        filtered = filtered[filtered["category"] == category]
    if region != "All":
        filtered = filtered[filtered["region"] == region]
    if tier != "All":
        filtered = filtered[filtered["tier"] == tier]

    st.download_button(L(labels, "download_csv", "CSV 다운로드"), convert_df_to_csv_bytes(filtered), "global_opportunity_radar.csv", "text/csv")
    if filtered.empty:
        st.info("검색 조건에 맞는 결과가 없습니다.")
        return
    for _, row in filtered.iterrows():
        render_card(row, labels, is_unlocked())


def generate_page(labels: Dict[str, str], lang_name: str) -> None:
    st.header("🤖 " + L(labels, "generate_title", "AI로 새 기회 생성"))
    st.caption(L(labels, "generate_help", "뉴스, 제품 설명, 트렌드 메모를 붙여넣으면 AI가 사업기회 카드로 바꿉니다."))
    if not get_secret("OPENAI_API_KEY", ""):
        st.info(L(labels, "no_api_key", "OPENAI_API_KEY가 없어 규칙 기반 데모 결과를 생성합니다."))

    c1, c2 = st.columns(2)
    with c1:
        category = st.selectbox(L(labels, "category", "카테고리"), ["AI", "SaaS", "Automation", "B2B", "Creator Economy", "Education", "Healthcare", "Finance", "E-commerce"])
    with c2:
        region = st.selectbox(L(labels, "target_region", "대상 지역"), ["Global", "United States", "Korea", "Japan", "Europe", "Southeast Asia", "Latin America"])

    source_text = st.text_area(
        L(labels, "source_text", "분석할 원문/메모"),
        height=180,
        placeholder="Paste Product Hunt launch notes, trend memo, customer pain point, news summary, or your own idea...",
    )
    if st.button(L(labels, "generate_button", "기회 카드 생성"), type="primary"):
        with st.spinner("AI가 기회 카드를 만들고 있습니다..."):
            row = generate_opportunity(source_text, category, region, lang_name)
        st.success("Generated")
        render_card(pd.Series(row), labels, premium=True)
        one = pd.DataFrame([row])
        st.download_button(L(labels, "download_csv", "CSV 다운로드"), convert_df_to_csv_bytes(one), "new_opportunity.csv", "text/csv")


def pricing_page(labels: Dict[str, str]) -> None:
    st.header("💳 " + L(labels, "pricing_title", "요금제"))
    free_name = L(labels, "free_plan", "Free")
    plans = [
        (free_name, "0", "오늘의 기회 3개 / 3 free signals", ""),
        (L(labels, "starter_plan", "Starter"), "19,000원 / $19", "매일 기회 10개, 기본 점수", get_secret("STARTER_PAYMENT_URL")),
        (L(labels, "pro_plan", "Pro"), "49,000원 / $49", "전체 분석, 실행법, 키워드, 주간 리포트", get_secret("PRO_PAYMENT_URL")),
        (L(labels, "business_plan", "Business"), "149,000원 / $149", "업종별 맞춤 기회, 이메일 알림, 리포트 전체", get_secret("BUSINESS_PAYMENT_URL")),
    ]
    cols = st.columns(4)
    for col, (name, price, desc, url) in zip(cols, plans):
        with col:
            st.markdown("<div class='price-card'>", unsafe_allow_html=True)
            st.markdown(f"### {esc(name)}")
            st.markdown(f"## {esc(price)}")
            st.write(desc)
            if url:
                st.link_button(L(labels, "buy", "결제하기"), url)
            elif name != free_name:
                st.caption(L(labels, "payment_missing", "결제 링크가 아직 설정되지 않았습니다."))
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### MVP 결제 방식")
    st.write(
        "초기에는 Paddle, Lemon Squeezy, PayPal, 포트원 같은 결제 서비스에서 만든 결제 링크를 "
        "Streamlit Secrets에 넣고, 결제 완료 고객에게 Access Code를 이메일로 보내는 방식으로 시작합니다. "
        "정식 SaaS 단계에서는 결제 웹훅 + 회원 DB를 연결합니다."
    )
    st.markdown("### 테스트용 Access Code")
    st.caption("실제 서비스 오픈 전 테스트용입니다. 실제 판매 시에는 Streamlit Secrets에서 코드를 바꾸세요.")
    st.code("starter-demo-2026\npro-demo-2026\nbusiness-demo-2026", language="text")


def about_page(labels: Dict[str, str]) -> None:
    st.header("ℹ️ " + L(labels, "about_title", "이 프로그램의 목적"))
    st.write(L(labels, "about_body", "사용자가 돈 되는 기회를 놓치지 않게 돕는 MVP입니다."))
    st.markdown(
        """
### 핵심 구조
1. GitHub 저장소에 코드와 데이터 저장  
2. Streamlit Community Cloud에서 GitHub 저장소를 연결해 배포  
3. Streamlit Secrets에 API Key와 결제 링크 저장  
4. GitHub Actions가 매일 데이터 파일을 갱신  
5. 사용자는 여러 언어 UI로 기회를 탐색하고 결제 링크로 Pro/Biz 가입  

### 주의
이 MVP는 시장정보와 사업기회 탐색 도구입니다. 수익을 보장하지 않으며, 투자·법률·의료 자문으로 사용하면 안 됩니다.
"""
    )


def main() -> None:
    language_label = st.sidebar.selectbox("Language / 언어", list(LANGUAGES.keys()))
    lang_code = LANGUAGES[language_label]["code"]
    lang_name = LANGUAGES[language_label]["name"]
    labels = T.get(lang_code, T.get("en", {}))

    nav_dashboard = L(labels, "nav_dashboard", "대시보드")
    nav_opportunities = L(labels, "nav_opportunities", "기회 탐색")
    nav_generate = L(labels, "nav_generate", "AI 생성")
    nav_pricing = L(labels, "nav_pricing", "유료 결제")
    nav_about = L(labels, "nav_about", "서비스 설명")

    st.sidebar.title("📡 Radar")
    page = st.sidebar.radio("Menu", [nav_dashboard, nav_opportunities, nav_generate, nav_pricing, nav_about])
    st.sidebar.caption(f"Last loaded: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        df = ensure_columns(load_opportunities())
    except Exception as exc:
        st.error("데이터를 불러오는 중 문제가 발생했습니다. data/opportunities.csv 파일을 확인하세요.")
        st.exception(exc)
        df = pd.DataFrame()

    if page == nav_dashboard:
        dashboard_page(df, labels)
    elif page == nav_opportunities:
        opportunities_page(df, labels)
    elif page == nav_generate:
        generate_page(labels, lang_name)
    elif page == nav_pricing:
        pricing_page(labels)
    else:
        about_page(labels)


if __name__ == "__main__":
    main()
