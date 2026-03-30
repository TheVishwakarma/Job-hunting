import streamlit as st
import os, json, requests
from datetime import datetime, date
import pandas as pd
import db

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Job Hunter",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

db.setup()

# ── Dark theme CSS ────────────────────────────────────────────
st.markdown("""
<style>
/* Base dark */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0f1117 !important;
    color: #e2e2e2 !important;
}
[data-testid="stHeader"] { background: #0f1117 !important; }
section[data-testid="stSidebar"] { background: #161b27 !important; }

/* Cards */
.jh-card {
    background: #1a1f2e;
    border: 1px solid #2a2f3f;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color .2s;
}
.jh-card:hover { border-color: #4a7cf7; }

/* Score pill */
.score { display:inline-block; padding:2px 10px; border-radius:20px;
         font-size:12px; font-weight:600; }
.score-high { background:#1a3a2a; color:#4ade80; }
.score-mid  { background:#3a2f10; color:#facc15; }
.score-low  { background:#3a1a1a; color:#f87171; }

/* Status badge */
.badge { display:inline-block; padding:2px 9px; border-radius:6px;
         font-size:11px; font-weight:500; margin-left:6px; }
.badge-applied     { background:#1e3a5f; color:#60a5fa; }
.badge-progress    { background:#3a2a10; color:#fb923c; }
.badge-interview   { background:#2a1a4a; color:#c084fc; }
.badge-offer       { background:#1a3a2a; color:#4ade80; }
.badge-rejected    { background:#3a1a1a; color:#f87171; }
.badge-saved       { background:#1a2030; color:#94a3b8; }

/* Metric cards */
.metric-row { display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }
.metric { background:#1a1f2e; border:1px solid #2a2f3f; border-radius:10px;
          padding:14px 20px; flex:1; min-width:120px; }
.metric-val { font-size:28px; font-weight:700; color:#4a7cf7; }
.metric-lbl { font-size:12px; color:#64748b; margin-top:2px; }

/* Tab styling */
[data-testid="stTabs"] [role="tablist"] {
    background: #161b27;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-weight: 500;
    padding: 8px 20px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #4a7cf7 !important;
    color: #fff !important;
}

/* Inputs */
input, textarea, select, [data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #1a1f2e !important;
    color: #e2e2e2 !important;
    border: 1px solid #2a2f3f !important;
    border-radius: 8px !important;
}
input:focus, textarea:focus { border-color: #4a7cf7 !important; }

/* Buttons */
.stButton > button {
    background: #4a7cf7 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.stButton > button:hover { background: #3a6ce7 !important; }
button[kind="secondary"] {
    background: #1a1f2e !important;
    color: #94a3b8 !important;
    border: 1px solid #2a2f3f !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #1a1f2e !important;
    border: 1px solid #2a2f3f !important;
    color: #e2e2e2 !important;
}

/* Divider */
hr { border-color: #2a2f3f !important; }

/* Hide hamburger & footer */
#MainMenu, footer { visibility: hidden; }

/* Apply button pill */
.apply-pill {
    display:inline-block; padding:4px 14px; background:#4a7cf7;
    color:#fff; border-radius:6px; font-size:12px; font-weight:600;
    text-decoration:none;
}
.apply-pill:hover { background:#3a6ce7; }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div style='display:flex;align-items:center;gap:12px;margin-bottom:4px;'>
  <span style='font-size:28px;font-weight:700;color:#e2e2e2;'>🎯 Job Hunter</span>
  <span style='font-size:13px;color:#64748b;padding-top:6px;'>Sunil Kumar · Data Analyst</span>
</div>
""", unsafe_allow_html=True)

# ── Stats strip ───────────────────────────────────────────────
stats = db.get_stats()
sc = stats["status_counts"]
response_rate = int((stats["active"] + stats["offers"]) / max(stats["total"], 1) * 100)

st.markdown(f"""
<div class="metric-row">
  <div class="metric"><div class="metric-val">{stats['total']}</div><div class="metric-lbl">Total tracked</div></div>
  <div class="metric"><div class="metric-val">{stats['active']}</div><div class="metric-lbl">Active pipeline</div></div>
  <div class="metric"><div class="metric-val">{sc.get('Interview Scheduled',0)}</div><div class="metric-lbl">Interviews</div></div>
  <div class="metric"><div class="metric-val">{stats['offers']}</div><div class="metric-lbl">Offers</div></div>
  <div class="metric"><div class="metric-val">{response_rate}%</div><div class="metric-lbl">Response rate</div></div>
</div>
""", unsafe_allow_html=True)

# ── Three tabs ────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔍  Discover Jobs", "🧠  Gap Analyser", "📋  My Applications"])


# ═══════════════════════════════════════════════════════════════
# TAB 1 — DISCOVER
# ═══════════════════════════════════════════════════════════════
with tab1:
    profile = db.get_profile()
    skills  = [s.strip() for s in profile.get("skills","").split(",") if s.strip()]
    roles   = [r.strip() for r in profile.get("target_roles","Data Analyst").split(",") if r.strip()]

    c1, c2, c3, c4 = st.columns([2, 1.5, 1, 1])
    role_choice = c1.selectbox("Role", roles + ["Custom…"], label_visibility="collapsed")
    if role_choice == "Custom…":
        role_choice = st.text_input("Enter role", placeholder="e.g. MIS Analyst")
    location = c2.selectbox("Location", ["India","Bangalore","Hyderabad","Pune","Mumbai","Delhi","Remote"], label_visibility="collapsed")
    results_n = c3.selectbox("Results", [10,20,30,50], index=1, label_visibility="collapsed")
    fetch = c4.button("Search Jobs", type="primary", use_container_width=True)

    # API key check
    az_id  = os.environ.get("ADZUNA_APP_ID","")
    az_key = os.environ.get("ADZUNA_API_KEY","")

    if not az_id or not az_key:
        st.markdown("""
<div class="jh-card" style="border-color:#facc15;">
  <div style="color:#facc15;font-weight:600;margin-bottom:6px;">⚡ Add Adzuna API keys to fetch live jobs</div>
  <div style="color:#94a3b8;font-size:13px;">
    Free at <a href="https://developer.adzuna.com/" target="_blank" style="color:#4a7cf7;">developer.adzuna.com</a> (1,000 calls/month).<br>
    Add <code>ADZUNA_APP_ID</code> and <code>ADZUNA_API_KEY</code> to your <code>.env</code> file or Streamlit Cloud secrets.
  </div>
</div>
""", unsafe_allow_html=True)

    if fetch and az_id and az_key:
        with st.spinner(f"Searching '{role_choice}' in {location}…"):
            try:
                resp = requests.get(
                    "https://api.adzuna.com/v1/api/jobs/in/search/1",
                    params={"app_id": az_id, "app_key": az_key,
                            "results_per_page": results_n,
                            "what": role_choice, "where": location,
                            "content-type": "application/json"},
                    timeout=12
                )
                jobs = resp.json().get("results", [])
                if not jobs:
                    st.warning("No results. Try a different role or location.")
                else:
                    st.markdown(f"<div style='color:#64748b;font-size:13px;margin-bottom:12px;'>Found {len(jobs)} jobs — ranked by fit score</div>", unsafe_allow_html=True)
                    jobs_scored = sorted(
                        [(j, db.fit_score(j.get("title",""), j.get("description",""), skills)) for j in jobs],
                        key=lambda x: x[1], reverse=True
                    )
                    for job, score in jobs_scored:
                        title   = job.get("title","")
                        company = job.get("company",{}).get("display_name","Unknown")
                        loc_str = job.get("location",{}).get("display_name","")
                        desc    = job.get("description","")
                        link    = job.get("redirect_url","")
                        posted  = job.get("created","")[:10]
                        sal_min = job.get("salary_min")
                        sal_max = job.get("salary_max")

                        score_cls = "score-high" if score>=70 else "score-mid" if score>=45 else "score-low"
                        sal_str = f"₹{int(sal_min):,}–{int(sal_max):,}/yr" if sal_min and sal_max else ""

                        with st.expander(f"**{title}** · {company}"):
                            st.markdown(f"""
<div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px;'>
  <div>
    <div style='color:#94a3b8;font-size:13px;'>📍 {loc_str} &nbsp;·&nbsp; 📅 {posted} {f'&nbsp;·&nbsp; 💰 {sal_str}' if sal_str else ''}</div>
  </div>
  <div style='display:flex;gap:8px;align-items:center;'>
    <span class="score {score_cls}">{score}/100 fit</span>
    <a class="apply-pill" href="{link}" target="_blank">Apply ↗</a>
  </div>
</div>
<div style='color:#cbd5e1;font-size:13px;line-height:1.7;'>{desc[:500]}{'…' if len(desc)>500 else ''}</div>
""", unsafe_allow_html=True)
                            if st.button("➕ Save to tracker", key=f"save_{job.get('id',title[:20])}"):
                                db.add_app({
                                    "company": company, "job_title": title,
                                    "job_id": str(job.get("id","")),
                                    "referrer": "", "applied": 0,
                                    "apply_date": None, "deadline": None,
                                    "job_link": link, "status": "Saved",
                                    "notes": f"Found via Adzuna · {loc_str}",
                                    "fit_score": score, "source": "adzuna"
                                })
                                st.success("Saved!")
            except Exception as e:
                st.error(f"API error: {e}")

    elif fetch and not (az_id and az_key):
        st.error("Add your Adzuna API keys first (see the card above).")


# ═══════════════════════════════════════════════════════════════
# TAB 2 — GAP ANALYSER
# ═══════════════════════════════════════════════════════════════
with tab2:
    profile = db.get_profile()
    ant_key = os.environ.get("ANTHROPIC_API_KEY","")

    col_l, col_r = st.columns([1,1], gap="large")

    with col_l:
        st.markdown("<div style='color:#94a3b8;font-size:13px;font-weight:600;margin-bottom:6px;'>YOUR SKILLS</div>", unsafe_allow_html=True)
        skills_txt = st.text_area("", value=profile.get("skills",""), height=130,
                                   placeholder="SQL, Python, Power BI…", label_visibility="collapsed")
        st.markdown("<div style='color:#94a3b8;font-size:13px;font-weight:600;margin-bottom:6px;margin-top:12px;'>RESUME TEXT (optional — improves accuracy)</div>", unsafe_allow_html=True)
        resume_txt = st.text_area("", value=profile.get("resume_text",""), height=160,
                                   placeholder="Paste your resume here…", label_visibility="collapsed")

    with col_r:
        st.markdown("<div style='color:#94a3b8;font-size:13px;font-weight:600;margin-bottom:6px;'>JOB DESCRIPTION</div>", unsafe_allow_html=True)
        jd_txt = st.text_area("", height=310,
                               placeholder="Paste any JD from LinkedIn, Naukri, company site…",
                               label_visibility="collapsed")

    analyse = st.button("🔍 Analyse Gap", type="primary")

    if analyse:
        if not jd_txt.strip():
            st.error("Paste a job description on the right first.")
        else:
            # Save skills back to profile
            db.save_profile(
                profile.get("name","Sunil Kumar"), skills_txt,
                profile.get("target_roles",""), profile.get("experience_years",1.6),
                resume_txt
            )

            if ant_key:
                with st.spinner("Analysing with Claude AI…"):
                    try:
                        prompt = f"""You are a senior technical recruiter. Analyse this JD against the candidate's profile.

CANDIDATE SKILLS: {skills_txt}
{f'RESUME: {resume_txt[:1500]}' if resume_txt.strip() else ''}

JOB DESCRIPTION:
{jd_txt[:3000]}

Reply ONLY with valid JSON — no markdown fences, no preamble:
{{"fit_score":0-100,"summary":"2 sentences","matched":["skill"],"missing":["skill"],"nice_to_have":["skill"],"top_action":"single most impactful thing to do"}}"""

                        r = requests.post(
                            "https://api.anthropic.com/v1/messages",
                            headers={"x-api-key": ant_key,
                                     "anthropic-version":"2023-06-01",
                                     "content-type":"application/json"},
                            json={"model":"claude-haiku-4-5-20251001","max_tokens":800,
                                  "messages":[{"role":"user","content":prompt}]},
                            timeout=30
                        )
                        raw = r.json()["content"][0]["text"].strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                        res = json.loads(raw)
                        use_ai = True
                    except Exception as e:
                        st.warning(f"AI call failed ({e}) — falling back to local analysis.")
                        use_ai = False
            else:
                use_ai = False

            if not use_ai:
                # Local keyword analysis
                SKILL_POOL = ["sql","python","r","tableau","power bi","excel","pandas","numpy",
                              "scikit-learn","xgboost","machine learning","deep learning","spark",
                              "aws","azure","gcp","airflow","dbt","snowflake","looker","qlik",
                              "statistics","regression","nlp","etl","data pipeline","a/b testing",
                              "git","docker","rest api","mongodb","postgresql","mysql","kafka"]
                user_skills_l = skills_txt.lower()
                jd_l = jd_txt.lower()
                matched  = [s for s in SKILL_POOL if s in jd_l and s in user_skills_l]
                missing  = [s for s in SKILL_POOL if s in jd_l and s not in user_skills_l]
                score    = int(len(matched)/max(len(matched)+len(missing),1)*100)
                res = {"fit_score": score,
                       "summary": f"You match {len(matched)} of {len(matched)+len(missing)} detected skills.",
                       "matched": matched, "missing": missing, "nice_to_have": [],
                       "top_action": f"Add '{missing[0]}' to your resume — it's the most common missing skill." if missing else "Strong match! Tailor your cover letter to the JD language."}

            # ── Results ──
            score = res.get("fit_score", 0)
            score_col = "#4ade80" if score>=70 else "#facc15" if score>=45 else "#f87171"
            st.markdown(f"""
<div style='display:flex;align-items:center;gap:20px;margin:20px 0 16px;flex-wrap:wrap;'>
  <div style='text-align:center;'>
    <div style='font-size:52px;font-weight:800;color:{score_col};line-height:1;'>{score}</div>
    <div style='color:#64748b;font-size:12px;'>/ 100 fit score</div>
  </div>
  <div style='flex:1;min-width:200px;'>
    <div style='background:#1a1f2e;border-radius:8px;height:10px;overflow:hidden;margin-bottom:8px;'>
      <div style='background:{score_col};width:{score}%;height:100%;border-radius:8px;'></div>
    </div>
    <div style='color:#cbd5e1;font-size:14px;'>{res.get("summary","")}</div>
  </div>
</div>
""", unsafe_allow_html=True)

            ca, cb = st.columns(2)
            with ca:
                st.markdown("**✅ Skills you have**")
                for s in res.get("matched",[]):
                    st.markdown(f"<div style='color:#4ade80;font-size:13px;'>✓ {s}</div>", unsafe_allow_html=True)
                if res.get("nice_to_have"):
                    st.markdown("**💡 Nice-to-have (you lack, but not critical)**")
                    for s in res["nice_to_have"]:
                        st.markdown(f"<div style='color:#facc15;font-size:13px;'>◐ {s}</div>", unsafe_allow_html=True)

            with cb:
                st.markdown("**❌ Missing skills**")
                for s in res.get("missing",[]):
                    st.markdown(f"<div style='color:#f87171;font-size:13px;'>✗ {s}</div>", unsafe_allow_html=True)

            if res.get("top_action"):
                st.markdown(f"""
<div class="jh-card" style="border-color:#4a7cf7;margin-top:16px;">
  <div style='color:#4a7cf7;font-weight:600;font-size:13px;margin-bottom:4px;'>🎯 TOP ACTION</div>
  <div style='color:#e2e2e2;'>{res['top_action']}</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 3 — MY APPLICATIONS
# ═══════════════════════════════════════════════════════════════
with tab3:
    STATUSES = ["All","Saved","Applied","In Progress","Interview Scheduled","Offer","Rejected","Withdrawn"]
    STATUS_BADGE = {
        "Saved":"saved","Applied":"applied","In Progress":"progress",
        "Interview Scheduled":"interview","Offer":"offer",
        "Rejected":"rejected","Withdrawn":"saved"
    }

    # ── Controls row ──
    fc1, fc2, fc3 = st.columns([2.5, 1.5, 1])
    search  = fc1.text_input("", placeholder="🔍  Search company or role…", label_visibility="collapsed")
    sfilt   = fc2.selectbox("", STATUSES, label_visibility="collapsed")
    show_add= fc3.button("➕ Add manually", use_container_width=True)

    # ── Add form ──
    if show_add:
        st.session_state["show_add_form"] = not st.session_state.get("show_add_form", False)

    if st.session_state.get("show_add_form"):
        with st.container():
            st.markdown("<div class='jh-card'>", unsafe_allow_html=True)
            a1,a2,a3 = st.columns(3)
            nc = a1.text_input("Company *", key="nc")
            nt = a2.text_input("Job title *", key="nt")
            nj = a3.text_input("Job ID", key="nj")
            b1,b2,b3 = st.columns(3)
            nd = b1.date_input("Apply date", value=date.today(), key="nd")
            ns = b2.selectbox("Status", ["Saved","Applied","In Progress","Interview Scheduled","Offer","Rejected"], key="ns")
            nr = b3.text_input("Referrer", key="nr")
            nl = st.text_input("Job link", key="nl")
            nn = st.text_area("Notes", height=68, key="nn")
            if st.button("Save application", type="primary"):
                if nc and nt:
                    db.add_app({"company":nc,"job_title":nt,"job_id":nj,
                                "referrer":nr,"applied":1,"apply_date":str(nd),
                                "deadline":None,"job_link":nl,"status":ns,
                                "notes":nn,"fit_score":None,"source":"manual"})
                    st.session_state["show_add_form"] = False
                    st.success("Added!"); st.rerun()
                else:
                    st.error("Company and title are required.")
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Application list ──
    apps = db.get_apps(status=sfilt if sfilt!="All" else None, search=search or None)
    st.markdown(f"<div style='color:#64748b;font-size:13px;margin:8px 0;'>{len(apps)} application{'s' if len(apps)!=1 else ''}</div>", unsafe_allow_html=True)

    for app in apps:
        badge_cls = STATUS_BADGE.get(app["status"],"saved")
        score_str = f"<span class='score {'score-high' if (app.get('fit_score') or 0)>=70 else 'score-mid' if (app.get('fit_score') or 0)>=45 else 'score-low'}'>{app['fit_score']}/100</span>" if app.get("fit_score") else ""

        with st.container():
            st.markdown(f"""
<div class="jh-card">
  <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;'>
    <div>
      <span style='font-weight:600;font-size:15px;color:#e2e2e2;'>{app['company']}</span>
      <span class='badge badge-{badge_cls}'>{app['status']}</span>
      {score_str}
      <div style='color:#94a3b8;font-size:13px;margin-top:2px;'>{app.get('job_title') or '—'} {'· 📅 '+app['apply_date'] if app.get('apply_date') else ''} {'· 👤 '+app['referrer'] if app.get('referrer') and app['referrer'] not in ['','nan','None'] else ''}</div>
      {f"<div style='color:#64748b;font-size:12px;margin-top:4px;'>💬 {app['notes']}</div>" if app.get('notes') and app['notes'] not in ['','nan','None'] else ''}
    </div>
    <div style='display:flex;gap:8px;align-items:center;'>
      {f'<a class="apply-pill" href="{app["job_link"]}" target="_blank">🔗 Link</a>' if app.get('job_link') and app['job_link'] not in ['','nan','None'] else ''}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

            sc1, sc2, sc3 = st.columns([2, 1, 0.4])
            new_status = sc1.selectbox(
                "Status",
                ["Saved","Applied","In Progress","Interview Scheduled","Offer","Rejected","Withdrawn"],
                index=["Saved","Applied","In Progress","Interview Scheduled","Offer","Rejected","Withdrawn"].index(app["status"]) if app["status"] in ["Saved","Applied","In Progress","Interview Scheduled","Offer","Rejected","Withdrawn"] else 0,
                key=f"st_{app['id']}",
                label_visibility="collapsed"
            )
            if new_status != app["status"]:
                db.update_status(app["id"], new_status)
                st.rerun()

            note_edit = sc2.text_input("Notes", value=app.get("notes","") or "", key=f"nt_{app['id']}", label_visibility="collapsed", placeholder="Add a note…")
            if note_edit != (app.get("notes") or ""):
                db.update_status(app["id"], app["status"], note_edit)

            if sc3.button("🗑", key=f"del_{app['id']}"):
                db.delete_app(app["id"])
                st.rerun()
