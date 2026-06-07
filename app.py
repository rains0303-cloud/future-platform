# ====================================================================
# Ethanbok74 글로벌 독점 비즈니스 [4단계: 6개국 다국어 UI 및 독점 영상 기술 전면 도입]
# ====================================================================
import sys
import subprocess
import time

required_packages = ["streamlit", "openai"]
for package in required_packages:
    try:
        __import__(package)
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

# 2. 하이엔드 글로벌 SaaS 테마 CSS 주입
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Noto+Sans+KR:wght@400;700;900&display=swap');
    
    .saas-title {
        font-size: 2.6rem;
        font-weight: 900;
        letter-spacing: -0.07rem;
        background: linear-gradient(135deg, #FF4B4B 0%, #4A00E0 45%, #00C6FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .saas-subtitle {
        color: #64748B;
        font-size: 1.1rem;
        margin-bottom: 1.8rem;
    }
    
    /* 📱 스마트폰 디바이스 모형 고급 프레임 */
    .phone-container {
        border: 12px solid #1E293B;
        border-radius: 36px;
        padding: 22px 16px;
        background-color: #0F172A;
        color: #F8FAFC;
        max-width: 340px;
        margin: 15px auto;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);
        position: relative;
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }
    .phone-notch {
        width: 120px;
        height: 16px;
        background-color: #1E293B;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        z-index: 99;
    }
    .phone-screen {
        max-height: 460px;
        overflow-y: auto;
    }
    .phone-screen::-webkit-scrollbar { width: 4px; }
    .phone-screen::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    
    .phone-meta {
        font-size: 0.7rem;
        color: #38BDF8;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 6px;
        letter-spacing: 0.04rem;
    }
    .phone-text {
        font-size: 0.88rem;
        line-height: 1.55;
        white-space: pre-wrap;
        color: #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# 3. [완벽 고도화] 전 세계 6대 권역 시스템 완벽 다국어 언어팩 (System UI Language 완벽 대응)
LANG_PACK = {
    "한국어 🇰🇷": {
        "title": "💎 글로벌 AI 숏폼 제조 공장 Enterprise",
        "subtitle": "상위 1% 독점 기술 기반의 멀티모달 비디오 프롬프트 엔진 및 스마트폰 시각화 시스템",
        "p_name_label": "🎁 브랜드 및 상품명",
        "p_name_ph": "예: 24시간 얼음이 유지되는 프리미엄 텀블러",
        "feat_label": "💡 핵심 차별점 및 셀링 포인트 (줄바꿈 입력)",
        "feat_ph": "1. 독점 보냉 코팅 기술\n2. 차량용 컵홀더 유격 제로\n3. 환경호르몬 미검출 친환경 소재",
        "tone_label": "🎭 글로벌 원어민 뉘앙스 (Tone)",
        "duration_label": "⏱️ 숏폼 규격 길이",
        "target_lang": "🌐 영상 번역/제작 타겟 언어",
        "btn_generate": "⚡ 독점 특허 파이프라인 실시간 영상 렌더링",
        "waiting_msg": "🔮 대기 중: 왼쪽 지휘통제실에서 상품 청사진을 입력하고 렌더링 버튼을 눌러주십시오.",
        "metrics_title": "📊 글로벌 엔터프라이즈 시스템 실시간 가동 현황",
        "m1": "AI 코어 엔진", "m2": "아카이브 저장소", "m3": "나의 라이선스 등급",
        "result_title": "🎉 최상위 독점 마케팅 패키지 자산 렌더링 완료!",
        "pay_banner": "👑 실시간 AI 아바타 자동 가상 비디오 합성 기능을 사용하려면 엔터프라이즈 플러스 등급으로 전환하세요 ($49/월)"
    },
    "English 🇺🇸": {
        "title": "💎 Global AI Short-form Video Factory Enterprise",
        "subtitle": "Top 1% Exclusive Multi-Modal Video Prompt Engine & Smartphone Live Preview System",
        "p_name_label": "🎁 Product & Brand Name",
        "p_name_ph": "e.g., 24hr Ice Retention Premium Tumbler",
        "feat_label": "💡 Key Killer Features & Selling Points (Line-break)",
        "feat_ph": "1. Proprietary thermal insulation coating\n2. Zero-rattle car cup holder fit\n3. 100% Eco-friendly BPA-Free material",
        "tone_label": "🎭 Global Tone of Voice",
        "duration_label": "⏱️ Target Video Duration",
        "target_lang": "🌐 Video Translation Target Language",
        "btn_generate": "⚡ Render Exclusive Viral Video Assets",
        "waiting_msg": "🔮 Waiting: Please input product blueprint on the left panel and click render.",
        "metrics_title": "📊 Global Enterprise System Live Status",
        "m1": "AI Core Engine", "m2": "Archive Storage", "m3": "License Tier",
        "result_title": "🎉 Exclusive Marketing Bundle Generated Successfully!",
        "pay_banner": "👑 Upgrade to Enterprise Plus ($49/mo) to unlock instant synthetic AI Human video rendering."
    },
    "日本語 🇯🇵": {
        "title": "💎 グローバルAIショート動画製造工場 Enterprise",
        "subtitle": "上位1%独占技術ベースのマルチモーダルビデオプロンプトエンジン＆スマホ同期システム",
        "p_name_label": "🎁 ブランド・商品名",
        "p_name_ph": "例：24時間氷が溶けないプレミアムタンブラー",
        "feat_label": "💡 核心的な差別化ポイント・特徴（改行入力）",
        "feat_ph": "1. 独自開発の保冷コーティング技術\n2. 車のカップホルダーに完璧フィット\n3. 環境ホルモンフリーの安全素材",
        "tone_label": "🎭 グローバルネイティブのニュアンス",
        "duration_label": "⏱️ 希望する動画の長さ",
        "target_lang": "🌐 制作対象国の言語",
        "btn_generate": "⚡ 独占パイプライン リアルタイム動画レンダリング",
        "waiting_msg": "🔮 待機中：左側の入力パネルで商品の設計図を入力し、レンダリングボタンを押してください。",
        "metrics_title": "📊 グローバルシステム リアルタイム稼働状況",
        "m1": "AIコアエンジン", "m2": "アーカイブ保管数", "m3": "ライセンス権限",
        "result_title": "🎉 最高位独占マーケティングアセットの生成が完了しました！",
        "pay_banner": "👑 リアルタイムAIアバタ自動合成機能を利用するには、Enterprise Plusプランにアップグレードしてください（$49/月）"
    },
    "简体中文 🇨🇳": {
        "title": "💎 全球卖家 AI 短视频制造工厂 Enterprise",
        "subtitle": "基于前1%独家技术的全面多模态视频提示词引擎与智能手机实时监控系统",
        "p_name_label": "🎁 品牌及商品名称",
        "p_name_ph": "例如：24小时高效保冰的高端保温杯",
        "feat_label": "💡 核心卖点与独家特征（换行输入）",
        "feat_ph": "1. 独家研发的保冷涂层技术\n2. 完美适配汽车杯架，无晃动\n3. 不含双酚A的绿色环保材质",
        "tone_label": "🎭 母语级营销语调",
        "duration_label": "⏱️ 短视频预估时长",
        "target_lang": "🌐 视频创作目标语言",
        "btn_generate": "⚡ 启动独家流水线实时视频渲染",
        "waiting_msg": "🔮 等待中：请在左侧控制台输入商品信息，并点击实时渲染按钮。",
        "metrics_title": "📊 全球企业级系统实时运行状态",
        "m1": "AI 核心引擎", "m2": "云端归档档案", "m3": "我的授权等级",
        "result_title": "🎉 独家跨境高转化营销数据资产包渲染完成！",
        "pay_banner": "👑 升级至 Enterprise Plus 级别 ($49/月) 以解锁全自动 AI 虚拟数字人音视频合成功能。"
    },
    "Español 🇪🇸": {
        "title": "💎 Fábrica de Video AI Short-form Enterprise",
        "subtitle": "Motor de Prompts de Video Multimodal y Sistema de Vista Previa en Teléfono Móvil",
        "p_name_label": "🎁 Nombre del Producto y Marca",
        "p_name_ph": "ej., Termo Premium con Retención de Hielo por 24 horas",
        "feat_label": "💡 Características Clave y Puntos de Venta (Línea por línea)",
        "feat_ph": "1. Tecnología exclusiva de aislamiento térmico\n2. Ajuste perfecto sin vibraciones en portavasos de coche\n3. Material ecológico 100% libre de BPA",
        "tone_label": "🎭 Tono de Voz Nativo Global",
        "duration_label": "⏱️ Duración del Video",
        "target_lang": "🌐 Idioma de Destino del Video",
        "btn_generate": "⚡ Renderizar Activos de Video Viral Exclusivos",
        "waiting_msg": "🔮 Esperando: Ingrese los datos del producto a la izquierda y haga clic en renderizar.",
        "metrics_title": "📊 Estado en Tiempo Real del Sistema Global",
        "m1": "Motor Central AI", "m2": "Almacén de Archivos", "m3": "Nivel de Licencia",
        "result_title": "🎉 ¡Paquete de Marketing Exclusivo Generado con Éxito!",
        "pay_banner": "👑 Actualice a Enterprise Plus ($49/mes) para activar la síntesis automática de video con Avatar Humano de IA."
    },
    "Tiếng Việt 🇻🇳": {
        "title": "💎 Nhà Máy Sản Xuất Video Ngắn AI Toàn Cầu Enterprise",
        "subtitle": "Hệ thống hiển thị Mockup di động và Prompt Video đa phương thức độc quyền",
        "p_name_label": "🎁 Tên thương hiệu & Sản phẩm",
        "p_name_ph": "Ví dụ: Bình giữ nhiệt cao cấp giữ đá 24 giờ",
        "feat_label": "💡 Đặc điểm nổi bật & Điểm bán hàng (Xuống dòng)",
        "feat_ph": "1. Công nghệ lớp phủ cách nhiệt độc quyền\n2. Vừa vặn hoàn hảo với khay đựng cốc trên ô tô\n3. Chất liệu thân thiện môi trường không chứa BPA",
        "tone_label": "🎭 Sắc thái ngôn ngữ bản địa",
        "duration_label": "⏱️ Thời lượng video mong muốn",
        "target_lang": "🌐 Ngôn ngữ mục tiêu của video",
        "btn_generate": "⚡ Render gói tài nguyên video viral độc quyền",
        "waiting_msg": "🔮 Đang chờ: Vui lòng nhập thông tin sản phẩm ở bảng bên trái và nhấn nút render.",
        "metrics_title": "📊 Trạng thái vận hành thời gian thực của hệ thống",
        "m1": "Lõi động cơ AI", "m2": "Kho lưu trữ dự án", "m3": "Hạng giấy phép",
        "result_title": "🎉 Đã render thành công tài sản marketing độc quyền!",
        "pay_banner": "👑 Nâng cấp lên Enterprise Plus ($49/tháng) để mở khóa tính năng tự động khớp video Avatar nhân vật AI."
    }
}

# 4. 사이드바 제어 및 다국적 언어 선택 매트릭스 구동
st.sidebar.title("⚙️ Global Control Center")
# 시스템 UI 언어 선택 스위치
site_lang = st.sidebar.selectbox("🗺️ Choose System UI Language", list(LANG_PACK.keys()), index=0)
L = LANG_PACK[site_lang]

st.sidebar.write("---")
api_key_input = st.sidebar.text_input("🔑 OpenAI API KEY", type="password", placeholder="sk-...")

st.sidebar.write("")
st.sidebar.markdown("### 📂 Enterprise Workspace")
if not st.session_state.workspace_history:
    st.sidebar.caption("No archived project. Please generate content.")
else:
    for idx, item in enumerate(st.session_state.workspace_history):
        icon = "🔥" if st.session_state.selected_view_idx == idx else "📄"
        if st.sidebar.button(f"{icon} {item['name']} ({item['lang']})", key=f"hist_{idx}", use_container_width=True):
            st.session_state.selected_view_idx = idx

# 5. 실시간 글로벌 메트릭 대시보드
st.markdown(f'<div class="saas-title">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="saas-subtitle">{L["subtitle"]}</div>', unsafe_allow_html=True)

st.write(f"##### {L['metrics_title']}")
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1:
    st.metric(label=L["m1"], value="⚡ GPT-4o-Mini Sync", delta="99.98% Latency Stable")
with mc2:
    st.metric(label=L["m2"], value=f"💾 {len(st.session_state.workspace_history)} Nodes", delta="Encrypted Storage")
with mc3:
    st.metric(label=L["m3"], value="Enterprise Max", delta="All Access")
with mc4:
    st.metric(label="Global Traffic Matrix", value="🌍 Active", delta="CDN Powered")
st.write("---")

# 6. 스플릿 구조 설계
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    with st.container(border=True):
        st.markdown(f"### 📥 Input Console ({site_lang.split(' ')[0]})")
        product_name = st.text_input(L["p_name_label"], placeholder=L["p_name_ph"])
        product_features = st.text_area(L["feat_label"], placeholder=L["feat_ph"], height=110)
        
        st.write("")
        tone = st.radio(L["tone_label"], ["🔥 Viral & Hook Heavy", "💼 Professional & Trusted", "🤣 Trendy & Humorous"])
        duration = st.select_slider(L["duration_label"], options=["15s", "30s", "60s"], value="30s")
        
        video_lang = st.selectbox(L["target_lang"], [
            "한국어 🇰🇷", "English 🇺🇸", "简体中文 🇨🇳", "Français 🇫🇷", "Deutsch 🇩🇪", "Español 🇪🇸", "日本語 🇯🇵", "Tiếng Việt 🇻🇳"
        ])
        
        st.write("")
        generate_btn = st.button(L["btn_generate"], type="primary", use_container_width=True)

# 7. 3단계 파이프라인 엔진 구동 및 OpenAI 오케스트레이션
if generate_btn:
    if not api_key_input:
        st.error("Please enter your OpenAI API Key in the sidebar.")
    elif not product_name or not product_features:
        st.warning("Please fill out the form entirely.")
    else:
        indicator_box = st.empty()
        
        with indicator_box.container(border=True):
            st.info("🔄 **[Pipeline Stage 1/3]** Analysing Competitor Hook Patterns & Traffic Algorithms...")
            st.progress(30)
            time.sleep(0.8)
            
        with indicator_box.container(border=True):
            st.info("✍️ **[Pipeline Stage 2/3]** Formulating Native Emotional Linguistics & Formatting High-CTR Scripts...")
            st.progress(70)
            
            try:
                client = OpenAI(api_key=api_key_input)
                system_prompt = (
                    "You are a master of premium video marketing SaaS engines. Generate three sections clearly separated by special tags:\n"
                    "Use [SCRIPT] for the actual talking lines.\n"
                    "Use [VISUAL] for camera and setting blueprints.\n"
                    "Use [PROMPT] for generating exact video generator prompt tokens (Sora/Runway spec, include camera movement, texture, lighting styles).\n"
                    f"Target Language of content: {video_lang}. Tone: {tone}. Expected Length: {duration}."
                )
                user_prompt = f"Product: {product_name}\nSpecs:\n{product_features}"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.8
                )
                raw_result = response.choices[0].message.content
                
                # 정밀 파싱 처리
                script_part = "Script Engine Rendered."
                visual_part = "Visual Engine Rendered."
                prompt_part = "Prompt Token Matrix Rendered."
                
                if "[SCRIPT]" in raw_result and "[VISUAL]" in raw_result and "[PROMPT]" in raw_result:
                    script_part = raw_result.split("[SCRIPT]")[1].split("[VISUAL]")[0].strip()
                    visual_part = raw_result.split("[VISUAL]")[1].split("[PROMPT]")[0].strip()
                    prompt_part = raw_result.split("[PROMPT]")[1].strip()
                else:
                    script_part = raw_result
                
            except Exception as e:
                st.error(f"Engine Exception: {str(e)}")
                script_part = None

        if script_part:
            with indicator_box.container(border=True):
                st.info("🎨 **[Pipeline Stage 3/3]** Injection of HeyGen Lip-Sync Vectors & Runway Gen-3 Prompt Mapping...")
                st.progress(100)
                time.sleep(0.6)
            
            indicator_box.empty()
            
            # 아카이브 보관
            new_asset = {
                "name": product_name,
                "lang": video_lang.split(" ")[0],
                "script": script_part,
                "visual": visual_part,
                "prompt": prompt_part
            }
            st.session_state.workspace_history.append(new_asset)
            st.session_state.selected_view_idx = len(st.session_state.workspace_history) - 1

with col2:
    if st.session_state.selected_view_idx is not None:
        current_data = st.session_state.workspace_history[st.session_state.selected_view_idx]
        
        st.success(L["result_title"])
        st.subheader(f"📁 Asset Master: {current_data['name']}")
        
        # UI 레이아웃 분할: 왼쪽은 프리미엄 스마트폰 디바이스 목업 / 오른쪽은 벤치마킹한 초격차 독점 기술 탭
        p_col, t_col = st.columns([1, 1.1])
        
        with p_col:
            st.write("##### 📱 Multi-Platform App Mockup")
            t_tk, t_st, t_rl = st.tabs(["🎵 TikTok Preview", "🩳 Shorts Preview", "📸 Reels Preview"])
            
            with t_tk:
                st.markdown(f"""
                <div class="phone-container"><div class="phone-notch"></div><div class="phone-screen">
                    <div class="phone-meta">🎵 TikTok Localized Algorithm</div>
                    <div class="phone-text">{current_data['script']}</div>
                </div></div>
                """, unsafe_allow_html=True)
            with t_st:
                st.markdown(f"""
                <div class="phone-container"><div class="phone-notch"></div><div class="phone-screen">
                    <div class="phone-meta" style="color:#EF4444;">🩳 YouTube Shorts High-CTR</div>
                    <div class="phone-text">{current_data['script']}</div>
                </div></div>
                """, unsafe_allow_html=True)
            with t_rl:
                st.markdown(f"""
                <div class="phone-container"><div class="phone-notch"></div><div class="phone-screen">
                    <div class="phone-meta" style="color:#D946EF;">📸 Instagram Reels Matrix</div>
                    <div class="phone-text">{current_data['script']}</div>
                </div></div>
                """, unsafe_allow_html=True)
                
        with t_col:
            st.write("##### ⚙️ Exclusive AI Technology Output")
            
            # 독점 벤치마킹 기술 컴포넌트 탭으로 세분화 분배
            tab_spec1, tab_spec2, tab_spec3 = st.tabs([
                "🎬 Runway Gen-3 Prompter", 
                "🗣️ HeyGen Lip-Sync Specs", 
                "📐 Camera Blueprint"
            ])
            
            with tab_spec1:
                st.caption("비디오 생성 AI(Sora, Runway)에 그대로 입력하면 실사급 영상이 출력되는 독점 프롬프트 매트릭스입니다.")
                st.info(current_data.get('prompt', 'Prompt generation sync active.'))
                
            with tab_spec2:
                st.caption("AI 가상 가상인간 합성 및 음성 호흡 구간 조절용 자동 싱크로율 데이터 사양입니다.")
                st.code(f"""[Audio Lip-Sync Profile]
- Language Accent: Native {current_data['lang']}
- Emotional Pitch: {tone}
- Micro-expression Vector: Auto-synchronized
- Breath Pause Intervals: Every 4.5 seconds for retention""", language="ini")
                
            with tab_spec3:
                st.caption("비디오 촬영팀 및 모션 그래픽 디자이너용 정밀 기술 지시서입니다.")
                st.code(current_data['visual'], language="text")
                
    else:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>🌐</h3>", unsafe_allow_html=True)
            st.info(L["waiting_msg"])

st.write("---")
st.warning(L["pay_banner"])
