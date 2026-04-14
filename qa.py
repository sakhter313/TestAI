import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import re
import csv
import io
from urllib.parse import urljoin, urlparse
from datetime import datetime

# ════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="QA Pro — Senior Test Case Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --bg:        #f0f4f8;
  --surface:   #ffffff;
  --surface2:  #f8fafc;
  --border:    #e2e8f0;
  --border2:   #cbd5e1;
  --accent:    #0f766e;
  --accent2:   #7c3aed;
  --accent3:   #dc2626;
  --amber:     #d97706;
  --blue:      #1d4ed8;
  --text:      #0f172a;
  --muted:     #64748b;
  --mono:      'IBM Plex Mono', monospace;
  --sans:      'Plus Jakarta Sans', sans-serif;
}

html, body, [class*="css"] { font-family: var(--sans); background: var(--bg); color: var(--text); }
.stApp { background: var(--bg); }

/* HERO */
.hero {
  background: var(--text);
  border-radius: 16px;
  padding: 2.2rem 2.8rem;
  margin-bottom: 1.8rem;
  position: relative; overflow: hidden;
}
.hero::before {
  content:''; position:absolute; inset:0;
  background:
    radial-gradient(ellipse 50% 100% at 90% 50%, rgba(124,58,237,.25) 0%, transparent 65%),
    radial-gradient(ellipse 40% 80% at 5%  80%, rgba(15,118,110,.2)  0%, transparent 65%);
}
.hero-tag  { font-family:var(--mono); font-size:.65rem; color:#94a3b8; text-transform:uppercase; letter-spacing:.15em; margin-bottom:.6rem; }
.hero-title { font-size:2.2rem; font-weight:800; color:#f8fafc; line-height:1.15; margin:0 0 .4rem; }
.hero-title em { font-style:normal; color:#5eead4; }
.hero-sub   { font-family:var(--mono); font-size:.78rem; color:#64748b; }
.hero-chips { margin-top:1.1rem; display:flex; gap:.5rem; flex-wrap:wrap; }
.chip { font-size:.7rem; font-family:var(--mono); padding:.22rem .65rem; border-radius:20px; border:1px solid #334155; color:#94a3b8; }
.chip.hi { border-color:#5eead4; color:#5eead4; background:rgba(94,234,212,.08); }

/* CARDS */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.4rem 1.6rem;
  margin-bottom: 1rem;
}
.card-title {
  font-size:.65rem; font-family:var(--mono);
  text-transform:uppercase; letter-spacing:.12em;
  color:var(--muted); margin-bottom:.8rem;
}

/* KPI ROW */
.kpi-row { display:flex; gap:.8rem; margin:1rem 0; }
.kpi {
  flex:1; background:var(--surface); border:1px solid var(--border);
  border-radius:12px; padding:.9rem 1.1rem;
  border-top: 3px solid var(--accent);
}
.kpi.amber { border-top-color: var(--amber); }
.kpi.red   { border-top-color: var(--accent3); }
.kpi.blue  { border-top-color: var(--blue); }
.kpi.purple{ border-top-color: var(--accent2); }
.kpi-val { font-family:var(--mono); font-size:1.7rem; font-weight:600; color:var(--text); line-height:1; }
.kpi-lbl { font-size:.65rem; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); margin-top:.25rem; }

/* TEST CARD */
.tc {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.2rem 1.5rem;
  margin-bottom: .8rem;
  border-left: 4px solid var(--border2);
  transition: box-shadow .2s;
}
.tc:hover { box-shadow: 0 4px 20px rgba(0,0,0,.07); }
.tc.boundary     { border-left-color: #0f766e; }
.tc.equivalence  { border-left-color: #1d4ed8; }
.tc.state        { border-left-color: #7c3aed; }
.tc.negative     { border-left-color: #dc2626; }
.tc.positive     { border-left-color: #16a34a; }
.tc.error        { border-left-color: #ea580c; }
.tc.performance  { border-left-color: #0891b2; }
.tc.security     { border-left-color: #9333ea; }

.tc-id    { font-family:var(--mono); font-size:.62rem; color:var(--muted); margin-bottom:.25rem; }
.tc-title { font-size:.97rem; font-weight:700; color:var(--text); margin-bottom:.5rem; }

.badge {
  display:inline-block; font-size:.6rem; font-family:var(--mono);
  padding:.15rem .5rem; border-radius:4px; font-weight:600;
  text-transform:uppercase; letter-spacing:.07em; margin-right:.3rem;
}
.b-boundary    { background:#f0fdf4; color:#0f766e; border:1px solid #bbf7d0; }
.b-equivalence { background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; }
.b-state       { background:#faf5ff; color:#7c3aed; border:1px solid #ddd6fe; }
.b-negative    { background:#fff1f2; color:#dc2626; border:1px solid #fecaca; }
.b-positive    { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.b-error       { background:#fff7ed; color:#ea580c; border:1px solid #fed7aa; }
.b-performance { background:#ecfeff; color:#0891b2; border:1px solid #a5f3fc; }
.b-security    { background:#fdf4ff; color:#9333ea; border:1px solid #e9d5ff; }
.b-high   { background:#fff1f2; color:#dc2626; }
.b-medium { background:#fffbeb; color:#d97706; }
.b-low    { background:#f0fdf4; color:#16a34a; }
.b-critical { background:#dc2626; color:#fff; }

.tc-row { display:flex; gap:1.5rem; margin-top:.8rem; flex-wrap:wrap; }
.tc-col { flex:1; min-width:200px; }
.tc-lbl { font-size:.6rem; font-family:var(--mono); text-transform:uppercase; letter-spacing:.1em; color:var(--muted); margin-bottom:.25rem; }
.tc-val { font-size:.82rem; color:#334155; line-height:1.55; }
.step   { padding:.12rem 0; }
.step::before { content:"→ "; color:var(--accent); font-weight:600; }

/* RISK METER */
.risk-bar-wrap { background:#e2e8f0; border-radius:4px; height:6px; margin:.3rem 0; overflow:hidden; }
.risk-bar { height:100%; border-radius:4px; }
.risk-low  { background:#16a34a; }
.risk-med  { background:#d97706; }
.risk-high { background:#dc2626; }
.risk-crit { background:#7c3aed; }

/* COVERAGE MATRIX */
.matrix-wrap { overflow-x:auto; margin-top:.5rem; }
.matrix-table { border-collapse:collapse; width:100%; font-size:.75rem; font-family:var(--mono); }
.matrix-table th {
  background:#f1f5f9; padding:.5rem .8rem;
  border:1px solid var(--border); text-align:left;
  font-weight:600; color:var(--muted); white-space:nowrap;
}
.matrix-table td { padding:.45rem .8rem; border:1px solid var(--border); }
.cell-yes  { background:#dcfce7; color:#15803d; font-weight:700; text-align:center; }
.cell-no   { background:#fef2f2; color:#b91c1c; text-align:center; }
.cell-part { background:#fef9c3; color:#a16207; text-align:center; }

/* AREA TAG */
.area-tag {
  display:inline-block; background:#f1f5f9; color:#475569;
  border:1px solid var(--border2); border-radius:6px;
  padding:.2rem .6rem; font-size:.72rem;
  font-family:var(--mono); margin:.15rem;
}

/* SECTION LABEL */
.sec-lbl {
  font-family:var(--mono); font-size:.62rem;
  text-transform:uppercase; letter-spacing:.12em;
  color:var(--muted); margin-bottom:.5rem; margin-top:1.2rem;
}

/* INPUTS */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div {
  background:var(--surface) !important;
  border:1px solid var(--border2) !important;
  color:var(--text) !important;
  border-radius:8px !important;
  font-family:var(--mono) !important;
  font-size:.82rem !important;
}
/* BUTTONS */
.stButton>button {
  background: var(--text) !important;
  color:#f8fafc !important; border:none !important;
  border-radius:8px !important; font-family:var(--sans) !important;
  font-weight:700 !important; font-size:.88rem !important;
  padding:.55rem 1.4rem !important; width:100%;
  transition: background .2s !important;
}
.stButton>button:hover { background:#1e293b !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
  background:var(--surface); border-radius:10px;
  padding:.3rem; border:1px solid var(--border); gap:.2rem;
}
.stTabs [data-baseweb="tab"] {
  background:transparent; border-radius:7px;
  color:var(--muted); font-family:var(--sans);
  font-weight:600; font-size:.83rem;
  padding:.45rem 1.1rem; border:none;
}
.stTabs [aria-selected="true"] {
  background:var(--text) !important; color:#f8fafc !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
  background:var(--surface) !important;
  border-right:1px solid var(--border) !important;
}
hr { border-color:var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════════════════

AREA_MAP = {
    "Authentication":  ["login","signin","signup","register","password","logout","auth","otp","2fa","verify","forgot"],
    "Search & Filter": ["search","filter","query","find","sort","results","keyword","autocomplete","facet"],
    "Forms & Input":   ["form","input","submit","field","validate","required","placeholder","checkbox","radio","dropdown"],
    "Navigation":      ["menu","nav","breadcrumb","pagination","tab","link","redirect","routing"],
    "API / Data":      ["api","endpoint","json","fetch","response","payload","request","status","schema","rest","graphql"],
    "Media / Audio":   ["audio","video","stream","player","upload","download","bitrate","codec","buffer","playback","track"],
    "E-commerce":      ["cart","checkout","payment","order","price","discount","coupon","invoice","shipping","promo"],
    "User Profile":    ["profile","account","settings","preference","avatar","subscription","plan","role","permission"],
    "Security":        ["token","csrf","xss","https","cookie","session","cors","injection","sql","auth","header","sanitize"],
    "Accessibility":   ["aria","alt","role","label","tabindex","wcag","contrast","keyboard","focus","screen"],
    "Performance":     ["load","speed","cache","cdn","timeout","latency","optimize","response time","throttle"],
    "Error Handling":  ["error","404","500","exception","retry","fallback","message","alert","warning","validation"],
}

GROQ_MODELS = {
    "LLaMA 3.3 70B (Recommended)": "llama-3.3-70b-versatile",
    "LLaMA 3.1 8B (Fast)":         "llama-3.1-8b-instant",
    "Gemma 2 9B":                   "gemma2-9b-it",
    "Mixtral 8x7B":                 "mixtral-8x7b-32768",
}

HF_MODELS = {
    "Mistral 7B Instruct": "mistralai/Mistral-7B-Instruct-v0.3",
    "Zephyr 7B Beta":      "HuggingFaceH4/zephyr-7b-beta",
}

# Risk scoring weights per test type
RISK_WEIGHTS = {
    "Boundary Value":       {"risk": "High",     "score": 8},
    "Equivalence Class":    {"risk": "Medium",   "score": 6},
    "State Transition":     {"risk": "High",     "score": 8},
    "Negative":             {"risk": "High",     "score": 7},
    "Positive":             {"risk": "Low",      "score": 3},
    "Error Handling":       {"risk": "Medium",   "score": 6},
    "Performance":          {"risk": "Medium",   "score": 5},
    "Security":             {"risk": "Critical", "score": 10},
}

# Coverage matrix axes
COVERAGE_AXES = {
    "Boundary Value":    ["Min Value", "Max Value", "Min-1", "Max+1", "Zero/Null"],
    "Equivalence Class": ["Valid Class", "Invalid Class", "Edge of Class"],
    "State Transition":  ["Initial State", "Valid Transition", "Invalid Transition", "End State"],
    "Negative":          ["Empty Input", "Special Chars", "SQL Injection", "XSS Payload", "Oversized Input"],
    "Security":          ["Auth Bypass", "CSRF", "XSS", "SQLi", "Broken Access"],
}


# ════════════════════════════════════════════════════════════════════════════
# SCRAPER
# ════════════════════════════════════════════════════════════════════════════

def scrape_url(url: str) -> dict:
    if not url.startswith("http"):
        url = "https://" + url
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=12,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        data = {
            "url": url,
            "title": (soup.title.string.strip() if soup.title else "Unknown"),
            "status_code": resp.status_code,
            "forms": [], "inputs": [], "buttons": [],
            "links": [], "headings": [], "tables": [],
            "selects": [], "error_messages": [],
            "page_text": "", "areas": [],
        }

        # Forms — rich extraction
        for form in soup.find_all("form"):
            fd = {
                "action": form.get("action", ""),
                "method": form.get("method", "GET").upper(),
                "fields": [], "has_file": False,
            }
            for inp in form.find_all(["input", "select", "textarea"]):
                t = inp.get("type", inp.name)
                if t == "file":
                    fd["has_file"] = True
                fd["fields"].append({
                    "type":        t,
                    "name":        inp.get("name", ""),
                    "placeholder": inp.get("placeholder", ""),
                    "required":    inp.has_attr("required"),
                    "minlength":   inp.get("minlength", ""),
                    "maxlength":   inp.get("maxlength", ""),
                    "min":         inp.get("min", ""),
                    "max":         inp.get("max", ""),
                    "pattern":     inp.get("pattern", ""),
                })
            data["forms"].append(fd)

        # Inputs
        for inp in soup.find_all("input"):
            data["inputs"].append({
                "type": inp.get("type", "text"),
                "name": inp.get("name", ""),
                "placeholder": inp.get("placeholder", ""),
                "min":  inp.get("min",""),
                "max":  inp.get("max",""),
            })

        # Selects
        for sel in soup.find_all("select"):
            opts = [o.get_text(strip=True) for o in sel.find_all("option")][:8]
            data["selects"].append({"name": sel.get("name",""), "options": opts})

        # Buttons
        for btn in soup.find_all(["button", "a"]):
            txt = btn.get_text(strip=True)
            if txt and len(txt) < 60:
                data["buttons"].append(txt)

        # Links
        for a in soup.find_all("a", href=True)[:15]:
            data["links"].append({
                "text": a.get_text(strip=True)[:40],
                "href": urljoin(base, a["href"])
            })

        # Headings
        for h in soup.find_all(["h1", "h2", "h3"]):
            txt = h.get_text(strip=True)
            if txt:
                data["headings"].append(txt[:100])

        # Tables
        for tbl in soup.find_all("table")[:3]:
            headers = [th.get_text(strip=True) for th in tbl.find_all("th")]
            if headers:
                data["tables"].append({"headers": headers, "rows": len(tbl.find_all("tr"))})

        # Error / alert messages
        for el in soup.find_all(class_=re.compile(r"error|alert|warning|danger|invalid", re.I)):
            txt = el.get_text(strip=True)
            if txt and len(txt) < 200:
                data["error_messages"].append(txt)

        # Page text
        data["page_text"] = " ".join(soup.get_text(separator=" ").split())[:3500]

        # Detect test areas
        txt_lower = data["page_text"].lower()
        for area, keywords in AREA_MAP.items():
            if any(kw in txt_lower for kw in keywords):
                data["areas"].append(area)
        if not data["areas"]:
            data["areas"] = ["General"]

        return {"success": True, "data": data}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out (12s)."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to the URL."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.response.status_code} from server."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ════════════════════════════════════════════════════════════════════════════
# AI PROMPT — SENIOR-LEVEL
# ════════════════════════════════════════════════════════════════════════════

def build_prompt(scraped: dict, area: str, count: int, tc_types: list) -> str:
    # Extract boundary-relevant field info
    numeric_fields = [
        f for inp in scraped["inputs"]
        for f in [inp] if inp.get("min") or inp.get("max") or inp.get("type") in ["number","range","date"]
    ]
    constrained_fields = [
        f for form in scraped["forms"]
        for f in form["fields"]
        if f.get("minlength") or f.get("maxlength") or f.get("pattern")
    ]

    return f"""You are a QA engineer with 5 years of experience, specializing in structured test design techniques.
Generate exactly {count} test cases for the area "{area}" using these techniques: {', '.join(tc_types)}.

WEBSITE SCRAPED DATA:
- URL: {scraped['url']}
- Title: {scraped['title']}
- Forms: {json.dumps(scraped['forms'][:4], indent=2)}
- Numeric/Range inputs (important for Boundary Value): {json.dumps(numeric_fields[:5])}
- Constrained fields (minlength/maxlength/pattern): {json.dumps(constrained_fields[:5])}
- Select dropdowns: {json.dumps(scraped['selects'][:4])}
- Buttons: {scraped['buttons'][:12]}
- Headings: {scraped['headings'][:8]}
- Error messages on page: {scraped['error_messages'][:5]}
- Tables: {json.dumps(scraped['tables'][:3])}
- Page text: {scraped['page_text'][:1200]}

TECHNIQUE GUIDANCE:
- Boundary Value Analysis: Test min, max, min-1, max+1, nominal values for numeric/length fields
- Equivalence Class Partitioning: Identify valid/invalid partitions, test one from each class
- State Transition: Map page states (logged out → login → logged in → logout), test valid and invalid transitions
- Negative: Invalid data, empty fields, SQL injection, XSS, special characters
- Error Handling: Trigger error states, verify messages are specific and actionable

Return ONLY a valid JSON array. No markdown fences, no explanation.
Each object must have EXACTLY these keys:
- "id": "TC-001" format
- "title": precise test case title referencing actual field/feature
- "type": one of {tc_types}
- "technique": e.g. "Boundary Value — maxlength", "Equivalence — invalid partition", "State: logged_in → logout"
- "precondition": specific setup state required
- "steps": array of 3-7 precise steps with actual test data inline
- "expected_result": specific, verifiable expected outcome
- "priority": "Critical", "High", "Medium", or "Low"
- "risk_area": the functional risk being covered
- "area": "{area}"
- "test_data": concrete test data values (actual values, not placeholders)
- "equivalence_class": partition or boundary being tested (empty string if not applicable)
"""


# ════════════════════════════════════════════════════════════════════════════
# AI ENGINES
# ════════════════════════════════════════════════════════════════════════════

def _clean_json(raw: str) -> list:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        raw = match.group(0)
    return json.loads(raw)


def call_groq(prompt: str, api_key: str, model_id: str) -> dict:
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 4500,
            },
            timeout=45,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        tcs = _clean_json(content)
        return {"success": True, "test_cases": tcs, "model": f"Groq / {model_id}"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Malformed JSON from Groq: {e}"}
    except requests.exceptions.HTTPError as e:
        msgs = {401: "Invalid Groq API key.", 429: "Groq rate limit. Wait a moment.", 503: "Groq unavailable."}
        return {"success": False, "error": msgs.get(e.response.status_code, f"Groq HTTP {e.response.status_code}")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def call_hf(prompt: str, api_key: str, model_id: str) -> dict:
    hf_prompt = f"[INST] {prompt} [/INST]"
    try:
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "inputs": hf_prompt,
                "parameters": {"max_new_tokens": 3500, "temperature": 0.3,
                               "return_full_text": False, "do_sample": True},
            },
            timeout=60,
        )
        if resp.status_code == 503:
            wait = resp.json().get("estimated_time", 20)
            return {"success": False, "error": f"HF model loading. Retry in ~{int(wait)}s."}
        resp.raise_for_status()
        data = resp.json()
        raw  = (data[0].get("generated_text","") if isinstance(data, list) else data.get("generated_text",""))
        tcs  = _clean_json(raw)
        return {"success": True, "test_cases": tcs, "model": f"HuggingFace / {model_id}"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"HF returned malformed JSON: {e}. Groq is more reliable for JSON."}
    except requests.exceptions.HTTPError as e:
        msgs = {401: "Invalid HF token.", 429: "HF rate limit.", 404: "Model not found on HF."}
        return {"success": False, "error": msgs.get(e.response.status_code, f"HF HTTP {e.response.status_code}")}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "HF timed out. Model may be cold. Retry."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate(scraped: dict, area: str, count: int, tc_types: list,
             provider: str, groq_key: str, groq_model: str,
             hf_key: str, hf_model: str) -> dict:

    prompt = build_prompt(scraped, area, count, tc_types)

    if provider == "Groq":
        result = call_groq(prompt, groq_key, GROQ_MODELS[groq_model])
    else:
        result = call_hf(prompt, hf_key, HF_MODELS[hf_model])

    if result["success"]:
        for i, tc in enumerate(result["test_cases"]):
            tc["id"] = f"TC-{i+1:03d}"
            tc.setdefault("source_model", result["model"])
            # Compute risk score
            rw = RISK_WEIGHTS.get(tc.get("type","Positive"), {"risk":"Low","score":3})
            tc["risk_level"] = tc.get("priority","Medium") if tc.get("priority") in ["Critical","High","Medium","Low"] else rw["risk"]
            tc["risk_score"]  = rw["score"]

    return result


# ════════════════════════════════════════════════════════════════════════════
# RISK SCORING HELPERS
# ════════════════════════════════════════════════════════════════════════════

def risk_bar_html(score: int) -> str:
    pct = int(score * 10)
    cls = "risk-crit" if score >= 9 else "risk-high" if score >= 7 else "risk-med" if score >= 5 else "risk-low"
    return f'<div class="risk-bar-wrap"><div class="risk-bar {cls}" style="width:{pct}%"></div></div>'


def risk_summary(tcs: list) -> dict:
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for tc in tcs:
        lvl = tc.get("risk_level","Low")
        if lvl in counts:
            counts[lvl] += 1
    return counts


# ════════════════════════════════════════════════════════════════════════════
# COVERAGE MATRIX BUILDER
# ════════════════════════════════════════════════════════════════════════════

def build_coverage_matrix(tcs: list, selected_types: list) -> dict:
    """
    For each selected technique, check which coverage dimensions are addressed.
    Returns dict: { technique -> { dimension -> covered_bool } }
    """
    matrix = {}
    for technique, dimensions in COVERAGE_AXES.items():
        if technique not in selected_types:
            continue
        coverage = {}
        relevant_tcs = [tc for tc in tcs if tc.get("type","") == technique]
        for dim in dimensions:
            dim_lower = dim.lower()
            covered = any(
                dim_lower in str(tc.get("technique","")).lower() or
                dim_lower in str(tc.get("test_data","")).lower() or
                dim_lower in str(tc.get("title","")).lower() or
                dim_lower in str(tc.get("steps","")).lower()
                for tc in relevant_tcs
            )
            coverage[dim] = "✓" if covered else "✗" if relevant_tcs else "—"
        matrix[technique] = coverage
    return matrix


def render_coverage_matrix(matrix: dict):
    if not matrix:
        st.info("Generate test cases first to see the coverage matrix.")
        return

    all_dims = list({dim for dims in matrix.values() for dim in dims})

    html = '<div class="matrix-wrap"><table class="matrix-table"><thead><tr>'
    html += "<th>Technique</th>"
    for dim in all_dims:
        html += f"<th>{dim}</th>"
    html += "<th>Count</th></tr></thead><tbody>"

    for technique, dims in matrix.items():
        html += f"<tr><td><strong>{technique}</strong></td>"
        covered = 0
        for dim in all_dims:
            val = dims.get(dim, "—")
            cls = "cell-yes" if val == "✓" else "cell-no" if val == "✗" else ""
            if val == "✓":
                covered += 1
            html += f'<td class="{cls}">{val}</td>'
        html += f'<td style="text-align:center;font-weight:700;">{covered}/{len(dims)}</td></tr>'

    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# EXPORT HELPERS
# ════════════════════════════════════════════════════════════════════════════

def export_csv(tcs: list) -> str:
    buf = io.StringIO()
    w   = csv.writer(buf)
    w.writerow([
        "ID","Title","Type","Technique","Priority","Risk Level","Risk Score",
        "Area","Risk Area","Precondition","Steps","Expected Result",
        "Test Data","Equivalence Class","Model"
    ])
    for tc in tcs:
        w.writerow([
            tc.get("id",""), tc.get("title",""), tc.get("type",""),
            tc.get("technique",""), tc.get("priority",""),
            tc.get("risk_level",""), tc.get("risk_score",""),
            tc.get("area",""), tc.get("risk_area",""),
            tc.get("precondition",""),
            " | ".join(tc.get("steps",[])),
            tc.get("expected_result",""),
            tc.get("test_data",""),
            tc.get("equivalence_class",""),
            tc.get("source_model",""),
        ])
    return buf.getvalue()


def export_markdown(tcs: list, url: str) -> str:
    lines = [
        "# Senior QA Test Cases",
        f"**URL:** {url}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "", "---", ""
    ]
    for tc in tcs:
        lines += [
            f"## {tc.get('id','')} — {tc.get('title','')}",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| Type | {tc.get('type','')} |",
            f"| Technique | {tc.get('technique','')} |",
            f"| Priority | {tc.get('priority','')} |",
            f"| Risk Level | {tc.get('risk_level','')} ({tc.get('risk_score','')})/10 |",
            f"| Area | {tc.get('area','')} |",
            f"| Risk Area | {tc.get('risk_area','')} |",
            f"| Precondition | {tc.get('precondition','')} |",
            f"| Test Data | {tc.get('test_data','')} |",
            f"| Equivalence Class | {tc.get('equivalence_class','')} |",
            "", "**Steps:**",
        ]
        for i, s in enumerate(tc.get("steps",[]), 1):
            lines.append(f"{i}. {s}")
        lines += [f"", f"**Expected Result:** {tc.get('expected_result','')}", "", "---", ""]
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════

for k, v in {
    "scraped": None,
    "test_cases": [],
    "last_tc_types": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
<div style="font-family:'IBM Plex Mono',monospace;font-size:.62rem;color:#0f766e;
            text-transform:uppercase;letter-spacing:.15em;margin-bottom:1rem;">
🎯 QA Pro — Senior Edition
</div>
""", unsafe_allow_html=True)

    st.markdown("### 🔑 API Keys")

    default_groq = ""
    default_hf   = ""
    try:
        default_groq = st.secrets.get("GROQ_API_KEY", "")
        default_hf   = st.secrets.get("HF_API_KEY", "")
    except Exception:
        pass

    groq_key = st.text_input("Groq API Key",        value=default_groq, type="password", placeholder="gsk_...",  help="Free at console.groq.com")
    hf_key   = st.text_input("HuggingFace Token",   value=default_hf,   type="password", placeholder="hf_...",   help="Free at huggingface.co/settings/tokens")

    st.markdown("---")

    st.markdown("### 🤖 AI Provider")
    provider = st.radio("Provider", ["Groq", "Hugging Face"], label_visibility="collapsed")

    if provider == "Groq":
        groq_model = st.selectbox("Groq Model", list(GROQ_MODELS.keys()))
        hf_model   = list(HF_MODELS.keys())[0]
    else:
        hf_model   = st.selectbox("HF Model", list(HF_MODELS.keys()))
        groq_model = list(GROQ_MODELS.keys())[0]
        st.caption("⚠ HF free tier may need warm-up time. Groq is faster.")

    st.markdown("---")

    st.markdown("### 🧪 Test Techniques")
    tc_types = st.multiselect(
        "Select techniques",
        ["Boundary Value", "Equivalence Class", "State Transition",
         "Negative", "Positive", "Error Handling", "Performance", "Security"],
        default=["Boundary Value", "Equivalence Class", "State Transition", "Negative"],
        help="Techniques a 5-year QA engineer is expected to master"
    )

    st.markdown("---")

    st.markdown("### ⚙️ Settings")
    tc_count = st.slider("Test cases per run", 5, 25, 10)

    st.markdown("---")
    st.markdown("""
<div style="font-size:.68rem;color:#94a3b8;line-height:1.9;">
Techniques: BVA · ECP · State Transition<br>
Risk scoring: 1–10 per technique<br>
Coverage matrix: auto-generated<br>
Export: CSV · JSON · Markdown
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="hero">
  <div class="hero-tag">Senior QA Engineer Edition · 5 Years Experience</div>
  <div class="hero-title">AI <em>Test Case</em> Generator</div>
  <div class="hero-sub">
    boundary value · equivalence partitioning · state transition · risk scoring · coverage matrix
  </div>
  <div class="hero-chips">
    <span class="chip hi">🤖 {provider}</span>
    <span class="chip hi">📋 {tc_count} TCs / run</span>
    {''.join(f'<span class="chip hi">{t}</span>' for t in tc_types[:4])}
    {'<span class="chip">+more</span>' if len(tc_types) > 4 else ''}
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════

tab_scrape, tab_generate, tab_risk, tab_matrix, tab_export = st.tabs([
    "🔍 Scrape", "⚡ Generate", "📊 Risk Analysis", "🗺 Coverage Matrix", "📥 Export"
])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — SCRAPE
# ────────────────────────────────────────────────────────────────────────────
with tab_scrape:
    st.markdown("### Enter Website URL")
    st.caption("The scraper extracts forms, inputs, constraints, dropdowns, and page state signals — all used to build accurate BVA and state transition test cases.")

    c1, c2 = st.columns([4, 1])
    with c1:
        url_input = st.text_input("URL", placeholder="https://the-internet.herokuapp.com/login", label_visibility="collapsed")
    with c2:
        scrape_btn = st.button("🔍 Scrape", use_container_width=True)

    if scrape_btn:
        if not url_input:
            st.error("Enter a URL.")
        else:
            with st.spinner("Scraping..."):
                result = scrape_url(url_input)
            if result["success"]:
                st.session_state.scraped    = result["data"]
                st.session_state.test_cases = []
                st.success(f"✅ **{result['data']['title']}** · HTTP {result['data']['status_code']}")
            else:
                st.error(f"❌ {result['error']}")

    if st.session_state.scraped:
        d = st.session_state.scraped

        # Metrics
        st.markdown(f"""
<div class="kpi-row">
  <div class="kpi">         <div class="kpi-val">{len(d['forms'])}</div><div class="kpi-lbl">Forms</div></div>
  <div class="kpi blue">   <div class="kpi-val">{len(d['inputs'])}</div><div class="kpi-lbl">Inputs</div></div>
  <div class="kpi amber">  <div class="kpi-val">{len(d['buttons'])}</div><div class="kpi-lbl">Buttons</div></div>
  <div class="kpi purple"> <div class="kpi-val">{len(d['selects'])}</div><div class="kpi-lbl">Dropdowns</div></div>
  <div class="kpi red">    <div class="kpi-val">{len(d['areas'])}</div><div class="kpi-lbl">Test Areas</div></div>
</div>
""", unsafe_allow_html=True)

        # Detected areas
        st.markdown('<div class="sec-lbl">Detected Test Areas</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<span class="area-tag">{a}</span>' for a in d["areas"]), unsafe_allow_html=True)

        # BVA-relevant fields callout
        numeric = [i for i in d["inputs"] if i.get("min") or i.get("max") or i.get("type") in ["number","range","date"]]
        constrained = [f for form in d["forms"] for f in form["fields"] if f.get("minlength") or f.get("maxlength")]

        if numeric or constrained:
            st.markdown('<div class="sec-lbl" style="margin-top:1rem;">Boundary Value Candidates</div>', unsafe_allow_html=True)
            bv_data = []
            for f in numeric:
                bv_data.append(f"**{f['name'] or f['type']}** — min:`{f.get('min','?')}` max:`{f.get('max','?')}`")
            for f in constrained:
                bv_data.append(f"**{f['name'] or f['type']}** — minlen:`{f.get('minlength','?')}` maxlen:`{f.get('maxlength','?')}`")
            for item in bv_data[:6]:
                st.markdown(f"- {item}")

        with st.expander("🔎 Full Scraped Data"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Forms:** {len(d['forms'])}\n\n**Buttons:** {d['buttons'][:8]}\n\n**Selects:** {[s['name'] for s in d['selects'][:5]]}")
            with col_b:
                st.markdown(f"**Headings:** {d['headings'][:5]}\n\n**Error messages:** {d['error_messages'][:3]}\n\n**Tables:** {[t['headers'] for t in d['tables'][:3]]}")
    else:
        st.markdown("""
<div style="text-align:center;padding:3rem;color:#94a3b8;">
  <div style="font-size:3rem;margin-bottom:1rem;">🕷</div>
  <div style="color:#64748b;">Enter a URL and click Scrape to begin</div>
  <div style="font-size:.8rem;margin-top:.4rem;color:#94a3b8;">
    Best practice sites: the-internet.herokuapp.com · demoqa.com · reqres.in · opencart.abstracta.us
  </div>
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — GENERATE
# ────────────────────────────────────────────────────────────────────────────
with tab_generate:
    if not st.session_state.scraped:
        st.info("Scrape a URL first in the **Scrape** tab.")
    else:
        d = st.session_state.scraped
        st.markdown(f"### Generate Test Cases — `{d['title']}`")

        g1, g2 = st.columns([3, 1])
        with g1:
            area_opts   = d["areas"] + ["General", "Custom"]
            chosen_area = st.selectbox("Test Area", area_opts)
            if chosen_area == "Custom":
                chosen_area = st.text_input("Custom area name", placeholder="e.g. Audio Streaming Player")
        with g2:
            st.markdown("<br>", unsafe_allow_html=True)
            gen_btn = st.button("⚡ Generate", use_container_width=True)

        # Show what will be generated
        if tc_types:
            st.markdown('<div class="sec-lbl">Techniques that will be applied</div>', unsafe_allow_html=True)
            for t in tc_types:
                rw = RISK_WEIGHTS.get(t, {"risk":"Low","score":3})
                st.markdown(
                    f'<span class="badge b-{t.lower().replace(" ","").replace("value","").replace("class","").replace("transition","")}">{t}</span>'
                    f' Risk: **{rw["risk"]}** ({rw["score"]}/10)',
                    unsafe_allow_html=True
                )

        if gen_btn:
            if not tc_types:
                st.error("Select at least one technique in the sidebar.")
            elif provider == "Groq" and not groq_key:
                st.error("Add your Groq API key in the sidebar.")
            elif provider == "Hugging Face" and not hf_key:
                st.error("Add your HuggingFace token in the sidebar.")
            else:
                with st.spinner(f"Generating {tc_count} test cases via {provider}..."):
                    result = generate(
                        d, chosen_area, tc_count, tc_types,
                        provider, groq_key, groq_model, hf_key, hf_model
                    )
                if result["success"]:
                    st.session_state.test_cases   = result["test_cases"]
                    st.session_state.last_tc_types = tc_types
                    st.success(f"✅ {len(result['test_cases'])} test cases via **{result['model']}** — check Risk Analysis and Coverage Matrix tabs")
                else:
                    st.error(f"❌ {result['error']}")

        # Display generated TCs
        if st.session_state.test_cases:
            tcs = st.session_state.test_cases
            st.markdown("---")

            # Filter row
            all_types = list({tc.get("type","?") for tc in tcs})
            f1, f2 = st.columns([2, 2])
            with f1:
                f_type = st.selectbox("Filter by type", ["All"] + all_types, key="gen_f_type")
            with f2:
                f_pri  = st.selectbox("Filter by priority", ["All","Critical","High","Medium","Low"], key="gen_f_pri")

            filtered = [
                tc for tc in tcs
                if (f_type == "All" or tc.get("type") == f_type)
                and (f_pri  == "All" or tc.get("priority") == f_pri)
            ]

            st.markdown(f'<div style="font-family:var(--mono);font-size:.7rem;color:var(--muted);margin:.5rem 0;">Showing {len(filtered)} of {len(tcs)}</div>', unsafe_allow_html=True)

            for tc in filtered:
                tc_type  = tc.get("type","Positive")
                type_key = tc_type.lower().replace(" ","").replace("value","").replace("class","").replace("transition","").replace("handling","")
                card_cls = {
                    "boundaryvalue": "boundary",
                    "equivalenceclass": "equivalence",
                    "statetransition": "state",
                    "errorhandling": "error",
                }.get(tc_type.lower().replace(" ",""), type_key)
                b_cls = f"b-{card_cls}"
                pri   = tc.get("priority","Medium")

                steps_html = "".join(f'<div class="step">{s}</div>' for s in tc.get("steps",[]))
                eq_html    = f'<div class="tc-lbl">Equivalence Class</div><div class="tc-val" style="font-family:var(--mono);font-size:.75rem;">{tc.get("equivalence_class","—")}</div>' if tc.get("equivalence_class") else ""

                st.markdown(f"""
<div class="tc {card_cls}">
  <div class="tc-id">{tc.get('id','')} · {tc.get('area','')}</div>
  <div class="tc-title">{tc.get('title','')}</div>
  <div style="margin-bottom:.6rem;">
    <span class="badge {b_cls}">{tc_type}</span>
    <span class="badge b-{pri.lower()}">{pri}</span>
    <span class="badge" style="background:#f1f5f9;color:#475569;border:1px solid #e2e8f0;">{tc.get('technique','')}</span>
  </div>
  {risk_bar_html(tc.get('risk_score',3))}
  <div style="font-family:var(--mono);font-size:.62rem;color:var(--muted);margin-bottom:.8rem;">
    Risk: {tc.get('risk_level','Low')} · Score: {tc.get('risk_score',3)}/10 · Area: {tc.get('risk_area','')}
  </div>
  <div class="tc-row">
    <div class="tc-col">
      <div class="tc-lbl">Precondition</div>
      <div class="tc-val">{tc.get('precondition','N/A')}</div>
    </div>
    <div class="tc-col">
      <div class="tc-lbl">Steps</div>
      <div class="tc-val">{steps_html}</div>
    </div>
    <div class="tc-col">
      <div class="tc-lbl">Expected Result</div>
      <div class="tc-val">{tc.get('expected_result','N/A')}</div>
      <div style="margin-top:.6rem;">
        <div class="tc-lbl">Test Data</div>
        <div class="tc-val" style="font-family:var(--mono);font-size:.74rem;color:#0f766e;">{tc.get('test_data','—')}</div>
      </div>
      {eq_html}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — RISK ANALYSIS
# ────────────────────────────────────────────────────────────────────────────
with tab_risk:
    tcs = st.session_state.test_cases
    if not tcs:
        st.info("Generate test cases first to see risk analysis.")
    else:
        st.markdown("### Risk-Based Priority Scoring")
        st.caption("Risk scores are assigned per test technique based on functional impact and defect probability.")

        rc = risk_summary(tcs)
        avg_score = round(sum(tc.get("risk_score",3) for tc in tcs) / len(tcs), 1)

        st.markdown(f"""
<div class="kpi-row">
  <div class="kpi red">    <div class="kpi-val">{rc.get('Critical',0)}</div><div class="kpi-lbl">Critical Risk</div></div>
  <div class="kpi amber">  <div class="kpi-val">{rc.get('High',0)}</div>    <div class="kpi-lbl">High Risk</div></div>
  <div class="kpi blue">   <div class="kpi-val">{rc.get('Medium',0)}</div>  <div class="kpi-lbl">Medium Risk</div></div>
  <div class="kpi">        <div class="kpi-val">{rc.get('Low',0)}</div>     <div class="kpi-lbl">Low Risk</div></div>
  <div class="kpi purple"> <div class="kpi-val">{avg_score}</div>           <div class="kpi-lbl">Avg Score /10</div></div>
</div>
""", unsafe_allow_html=True)

        # Risk scoring reference table
        st.markdown("---")
        st.markdown("#### Technique Risk Reference")
        ref_html = '<table class="matrix-table"><thead><tr><th>Technique</th><th>Risk Level</th><th>Score /10</th><th>Why High Risk?</th></tr></thead><tbody>'
        rationale = {
            "Boundary Value":    "Most defects occur at boundaries — off-by-one errors are common",
            "Equivalence Class":  "Invalid partitions often expose missing validation logic",
            "State Transition":  "Invalid state changes can corrupt data or bypass auth",
            "Negative":          "Unhandled inputs cause crashes, injection vulnerabilities",
            "Positive":          "Baseline happy path — lower defect probability",
            "Error Handling":    "Poor error messages expose system internals",
            "Performance":       "Load edge cases reveal race conditions",
            "Security":          "Critical — auth bypass, injection can be catastrophic",
        }
        for tech, rw in RISK_WEIGHTS.items():
            color = {"Critical":"#dc2626","High":"#d97706","Medium":"#1d4ed8","Low":"#16a34a"}.get(rw["risk"],"#64748b")
            ref_html += f'<tr><td><strong>{tech}</strong></td><td style="color:{color};font-weight:700;">{rw["risk"]}</td><td style="text-align:center;">{rw["score"]}</td><td style="color:#64748b;">{rationale.get(tech,"")}</td></tr>'
        ref_html += "</tbody></table>"
        st.markdown(f'<div class="matrix-wrap">{ref_html}</div>', unsafe_allow_html=True)

        # Sorted TC list by risk score
        st.markdown("---")
        st.markdown("#### All Test Cases — Sorted by Risk Score (High → Low)")
        sorted_tcs = sorted(tcs, key=lambda x: x.get("risk_score",0), reverse=True)

        for tc in sorted_tcs:
            score = tc.get("risk_score", 3)
            lvl   = tc.get("risk_level","Low")
            color = {"Critical":"#dc2626","High":"#d97706","Medium":"#1d4ed8","Low":"#16a34a"}.get(lvl,"#64748b")
            st.markdown(f"""
<div class="card" style="padding:1rem 1.3rem;margin-bottom:.5rem;">
  <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
    <span style="font-family:var(--mono);font-size:.65rem;color:var(--muted);min-width:55px;">{tc.get('id','')}</span>
    <span style="flex:1;font-size:.88rem;font-weight:600;">{tc.get('title','')}</span>
    <span style="font-family:var(--mono);font-size:.7rem;color:{color};font-weight:700;min-width:80px;">{lvl} ({score}/10)</span>
    <span style="font-family:var(--mono);font-size:.65rem;color:var(--muted);">{tc.get('type','')}</span>
  </div>
  {risk_bar_html(score)}
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — COVERAGE MATRIX
# ────────────────────────────────────────────────────────────────────────────
with tab_matrix:
    tcs = st.session_state.test_cases
    st.markdown("### Test Coverage Matrix")
    st.caption("Shows which coverage dimensions are addressed by the generated test cases per technique.")

    if not tcs:
        st.info("Generate test cases first to see the coverage matrix.")
    else:
        matrix = build_coverage_matrix(tcs, st.session_state.last_tc_types or tc_types)
        render_coverage_matrix(matrix)

        st.markdown("---")
        st.markdown("#### Legend")
        st.markdown("""
- **✓** — Covered by at least one generated test case
- **✗** — Not covered — consider adding a test case manually
- **—** — Technique not selected / no test cases of this type generated
        """)

        # Coverage score
        total_cells = sum(len(dims) for dims in matrix.values())
        covered     = sum(1 for dims in matrix.values() for v in dims.values() if v == "✓")
        if total_cells > 0:
            pct = int(covered / total_cells * 100)
            st.markdown(f"**Overall Coverage Score: {covered}/{total_cells} dimensions ({pct}%)**")
            st.progress(pct / 100)


# ────────────────────────────────────────────────────────────────────────────
# TAB 5 — EXPORT
# ────────────────────────────────────────────────────────────────────────────
with tab_export:
    tcs = st.session_state.test_cases
    if not tcs:
        st.info("Generate test cases first.")
    else:
        url = st.session_state.scraped["url"] if st.session_state.scraped else ""
        st.markdown(f"### Export {len(tcs)} Test Cases")
        ts = datetime.now().strftime("%Y%m%d_%H%M")

        e1, e2, e3 = st.columns(3)
        with e1:
            st.markdown("#### 📊 CSV")
            st.caption("JIRA · TestRail · Zephyr · Excel")
            st.download_button("⬇ Download CSV",
                               export_csv(tcs),
                               file_name=f"qa_test_cases_{ts}.csv",
                               mime="text/csv",
                               use_container_width=True)
        with e2:
            st.markdown("#### 📋 JSON")
            st.caption("API · custom tooling · automation")
            st.download_button("⬇ Download JSON",
                               json.dumps(tcs, indent=2),
                               file_name=f"qa_test_cases_{ts}.json",
                               mime="application/json",
                               use_container_width=True)
        with e3:
            st.markdown("#### 📝 Markdown")
            st.caption("Confluence · GitHub · Notion")
            st.download_button("⬇ Download Markdown",
                               export_markdown(tcs, url),
                               file_name=f"qa_test_cases_{ts}.md",
                               mime="text/markdown",
                               use_container_width=True)

        st.markdown("---")
        st.markdown("#### Preview — first 2 records")
        st.code(json.dumps(tcs[:2], indent=2), language="json")
