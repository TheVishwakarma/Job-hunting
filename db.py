import sqlite3, os
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

try:
    import streamlit as st
    for k, v in st.secrets.items():
        if k not in os.environ:
            os.environ[k] = str(v)
except Exception:
    pass

DB_PATH = Path(__file__).parent / "data" / "job_tracker.db"


def conn():
    c = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def setup():
    """Ensure all tables exist — safe to call on every startup."""
    db = conn()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            job_title TEXT,
            job_id TEXT,
            referrer TEXT,
            applied INTEGER DEFAULT 0,
            apply_date TEXT,
            deadline TEXT,
            job_link TEXT,
            status TEXT DEFAULT 'Saved',
            notes TEXT,
            fit_score INTEGER,
            source TEXT DEFAULT 'manual',
            added_date TEXT
        );
        CREATE TABLE IF NOT EXISTS resume_profile (
            id INTEGER PRIMARY KEY,
            name TEXT,
            skills TEXT,
            target_roles TEXT,
            experience_years REAL,
            resume_text TEXT,
            updated_date TEXT
        );
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            website TEXT,
            email TEXT,
            source TEXT,
            added_date TEXT
        );
    """)
    # Seed profile if empty
    row = db.execute("SELECT id FROM resume_profile WHERE id=1").fetchone()
    if not row:
        db.execute("""INSERT INTO resume_profile VALUES (
            1,'Sunil Kumar',
            'SQL,Python,Power BI,pandas,NumPy,Scikit-learn,XGBoost,Streamlit,RAG,LLMs,Excel,Git,Data Validation,ETL,KPI Tracking',
            'Data Analyst,Junior Data Analyst,Business Intelligence Analyst,MIS Analyst,Data Research Analyst',
            1.6, '', ?)""", (str(datetime.now().date()),))
    db.commit()
    db.close()


# ── Applications ──────────────────────────────────────────────
def get_apps(status=None, search=None):
    db = conn()
    q = "SELECT * FROM applications WHERE 1=1"
    p = []
    if status and status != "All":
        q += " AND status=?"; p.append(status)
    if search:
        q += " AND (company LIKE ? OR job_title LIKE ?)"; p += [f"%{search}%"]*2
    q += " ORDER BY COALESCE(apply_date, added_date) DESC"
    rows = [dict(r) for r in db.execute(q, p).fetchall()]
    db.close()
    return rows


def add_app(data: dict):
    db = conn()
    data.setdefault("added_date", str(datetime.now().date()))
    db.execute("""INSERT INTO applications
        (company,job_title,job_id,referrer,applied,apply_date,deadline,
         job_link,status,notes,fit_score,source,added_date)
        VALUES(:company,:job_title,:job_id,:referrer,:applied,:apply_date,:deadline,
               :job_link,:status,:notes,:fit_score,:source,:added_date)""", data)
    db.commit(); db.close()


def update_status(app_id, status, notes=None):
    db = conn()
    if notes is not None:
        db.execute("UPDATE applications SET status=?,notes=? WHERE id=?", (status, notes, app_id))
    else:
        db.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
    db.commit(); db.close()


def delete_app(app_id):
    db = conn()
    db.execute("DELETE FROM applications WHERE id=?", (app_id,))
    db.commit(); db.close()


def get_stats():
    db = conn()
    total   = db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    active  = db.execute("SELECT COUNT(*) FROM applications WHERE status IN ('Applied','In Progress','Interview Scheduled')").fetchone()[0]
    offers  = db.execute("SELECT COUNT(*) FROM applications WHERE status='Offer'").fetchone()[0]
    rejected= db.execute("SELECT COUNT(*) FROM applications WHERE status='Rejected'").fetchone()[0]
    status_counts = dict(db.execute("SELECT status, COUNT(*) FROM applications GROUP BY status").fetchall())
    db.close()
    return {"total": total, "active": active, "offers": offers,
            "rejected": rejected, "status_counts": status_counts}


# ── Resume Profile ─────────────────────────────────────────────
def get_profile():
    db = conn()
    row = db.execute("SELECT * FROM resume_profile WHERE id=1").fetchone()
    db.close()
    return dict(row) if row else {}


def save_profile(name, skills, roles, exp, resume_text=""):
    db = conn()
    db.execute("""INSERT OR REPLACE INTO resume_profile
        (id,name,skills,target_roles,experience_years,resume_text,updated_date)
        VALUES(1,?,?,?,?,?,?)""",
        (name, skills, roles, exp, resume_text, str(datetime.now().date())))
    db.commit(); db.close()


# ── Fit scoring (local, no API needed) ────────────────────────
def fit_score(job_title: str, job_desc: str, skills: list) -> int:
    text = (job_title + " " + job_desc).lower()
    matched = sum(1 for s in skills if s.strip().lower() in text)
    score = int(matched / max(len(skills), 1) * 100)
    boost = sum(4 for w in ["sql","python","power bi","data analyst","analytics","excel","ml","ai"] if w in text)
    return min(score + boost, 100)
