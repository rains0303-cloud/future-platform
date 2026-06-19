# Global Opportunity Radar AI

Streamlit + GitHub + OpenAI API로 운영하는 글로벌 사업기회 탐색 MVP입니다.

## 필요한 파일

- app.py
- requirements.txt

## requirements.txt

```txt
streamlit
openai
pandas
```

## Streamlit Secrets

Streamlit Cloud > Manage app > Settings > Secrets 에 아래처럼 입력합니다.

```toml
OPENAI_API_KEY = "여기에_OpenAI_API_Key_입력"
OPENAI_MODEL = "gpt-4o-mini"
MASTER_LICENSE_KEY = "EB74"
PAYMENT_URL = "https://rainscape5.gumroad.com/l/ycgff"
```

## 중요

GitHub의 app.py 안에 아래 줄이 남아 있으면 예전 파일이 실행 중입니다.

```python
from opportunity_engine import convert_df_to_csv_bytes, generate_opportunity, load_opportunities
```

위 줄이 없는 새 app.py로 전체 교체한 뒤 Streamlit Cloud에서 Reboot app을 누르세요.
