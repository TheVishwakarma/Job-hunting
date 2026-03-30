# 🎯 Job Hunter

Personal job tracking & discovery tool — dark UI, 3 tabs, zero bloat.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy free (Streamlit Cloud)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select repo → `app.py`
3. In App Settings → Secrets:

```toml
ADZUNA_APP_ID = "your_id"
ADZUNA_API_KEY = "your_key"
ANTHROPIC_API_KEY = "your_key"
```

## API keys (all free)

| Key | Where | Free tier |
|---|---|---|
| Adzuna | [developer.adzuna.com](https://developer.adzuna.com) | 1,000 calls/month |
| Anthropic | [console.anthropic.com](https://console.anthropic.com) | $5 free credits |

App works without keys — just no live job search or AI analysis.
