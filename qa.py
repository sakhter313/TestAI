import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import re
import csv
import io
from datetime import datetime

# ════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Test Case Generator — Learn AI Testing",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════════════
# CSS — Clean, friendly, light theme
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Fira+Code:wght@400;500&display=swap');

html, body, [class*="css"] {
  font-family: 'Nunito', sans-serif;
  background: #f7f9fc;
  color: #1e293b;
}
.stApp { background: #f7f9fc; }

/* HEADER */
.app-header {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 16px;
  padding: 2rem 2.2rem;
  margin-bottom: 1.5rem;
  color: white;
}
.app-header h1 { font-size: 1.8rem; font-weight: 800; margin: 0 0 .3rem; }
.app-header p  { font-size: .9rem; opacity: .85; margin: 0; }

/* STEP BOX */
.step-box {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.4rem 1.6rem;
  margin-bottom: 1.2rem;
  box-shadow: 0 1px 6px rgba(0,0,0,.05);
}
.step-number {
  display: inline-block;
  background: #6366f1;
  color: white;
  font-size: .72rem;
  font-weight: 800;
  padding: .2rem .6rem;
  border-radius: 20px;
  margin-bottom: .6rem;
  letter-spacing: .05em;
}
.step-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: .3rem;
}
.step-desc {
  font-size: .85rem;
  color: #64748b;
  margin-bottom: .9rem;
  line-height: 1.6;
}

/* LEARN BOX */
.learn-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 10px;
  padding: .9rem 1.1rem;
  margin-bottom: .8rem;
  font-size: .82rem;
  color: #1e40af;
  line-height: 1.65;
}
.learn-box strong { color: #1e3a8a; }

/* TIP BOX */
.tip-box {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  padding: .8rem 1rem;
  font-size: .8rem;
  color: #15803d;
  margin-top: .6rem;
}

/* WARN BOX */
.warn-box {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 10px;
  padding: .8rem 1rem;
  font-size: .8rem;
  color: #92400e;
  margin-top: .6rem;
}

/* TEST CASE CARD */
.tc-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.2rem 1.4rem;
  margin-bottom: .9rem;
  border-left: 5px solid #6366f1;
  box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.tc-card.positive    { border-left-color: #16a34a; }
.tc-card.negative    { border-left-color: #dc2626; }
.tc-card.edge        { border-left-color: #d97706; }
.tc-card.security    { border-left-color: #7c3aed; }
.tc-card.performance { border-left-color: #0891b2; }

.tc-id    { font-family: 'Fira Code', monospace; font-size: .65rem; color: #94a3b8; margin-bottom: .3rem; }
.tc-title { font-size: .97rem; font-weight: 800; color: #1e293b; margin-bottom: .5rem; }

.badge {
  display: inline-block;
  font-size: .65rem; font-weight: 700;
  padding: .18rem .55rem; border-radius: 20px;
  margin-right: .3rem; text-transform: uppercase;
}
.b-positive    { background: #dcfce7; color: #15803d; }
.b-negative    { background: #fee2e2; color: #b91c1c; }
.b-edge        { background: #fef3c7; color: #92400e; }
.b-security    { background: #ede9fe; color: #6d28d9; }
.b-performance { background: #cffafe; color: #0e7490; }
.b-high        { background: #fee2e2; color: #b91c1c; }
.b-medium      { background: #fef3c7; color: #92400e; }
.b-low         { background: #dcfce7; color: #15803d; }

.tc-label { font-size: .65rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: .08em; margin-top: .8rem; margin-bottom: .2rem; }
.tc-value { font-size: .85rem; color: #334155; line-height: 1.6; }
.step-line { padding: .1rem 0; }
.step-line::before { content: "→ "; color: #6366f1; font-weight: 700; }

/* STAT ROW */
.stat-row { display: flex; gap: .7rem; margin: .8rem 0; }
.stat {
  flex: 1; background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px; padding: .8rem;
  text-align: center;
}
.stat-num { font-size: 1.5rem; font-weight: 800; color: #6366f1; font-family: 'Fira Code', monospace; }
.stat-lbl { font-size: .65rem; color: #94a3b8; text-transform: uppercase; letter-spacing: .08em; margin-top: .2rem; }

/* AREA TAG */
.area-tag {
  display: inline-block;
  background: #f1f5f9; color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 20px; padding: .2rem .65rem;
  font-size: .75rem; margin: .15rem;
}

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
  background: white !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 10px !important;
  color: #1e293b !important;
  font-family: 'Nunito', sans-serif !important;
  font-size: .88rem !important;
}

/* BUTTON */
.stButton > button {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  color: white !important; border: none !important;
  border-radius: 10px !important;
  font-family: 'Nunito', sans-serif !important;
  font-weight: 800 !important; font-size: .9rem !important;
  padding: .6rem 1.5rem !important; width: 100%;
  transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .88 !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
  background: white; border-radius: 10px;
  padding: .25rem; border: 1px solid #e2e8f0; gap: .2rem;
}
.stTabs [data-baseweb="tab"] {
  background: transparent; border-radius: 8px;
  color: #64748b; font-family: 'Nunito', sans-serif;
  font-weight: 700; font-size: .83rem;
  padding: .4rem 1rem; border: none;
}
.stTabs [aria-selected="true"] {
  background: #6366f1 !important; color: white !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
  background: white !important;
  border-right: 1px solid #e2e8f0 !important;
}
hr { border-color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════════════════

GROQ_MODELS = {
    "LLaMA 3.3 70B — Best quality":  "llama-3.3-70b-versatile",
    "LLaMA 3.1 8B — Fastest":        "llama-3.1-8b-instant",
    "Gemma 2 9B — Google model":      "gemma2-9b-it",
}

HF_MODELS = {
    "Mistral 7B — Good quality":  "mistralai/Mistral-7B-Instruct-v0.3",
    "Zephyr 7B — Balanced":       "HuggingFaceH4/zephyr-7b-beta",
}

TEST_TYPE_EXPLAIN = {
    "Positive": "Tests that the feature works correctly with valid input",
    "Negative": "Tests that the feature handles invalid/wrong input properly",
    "Edge Case": "Tests the boundaries — empty fields, very long text, special characters",
    "Security": "Tests for common vulnerabilities like SQL injection and XSS",
}

AREA_KEYWORDS = {
    "Login / Authentication": ["login","signin","signup","register","password","logout","auth","otp"],
    "Search":                  ["search","filter","query","find","sort","results","autocomplete"],
    "Forms":                   ["form","input","submit","field","validate","required","checkbox"],
    "Navigation":              ["menu","nav","breadcrumb","pagination","tab","link"],
    "User Profile":            ["profile","account","settings","preference","avatar"],
    "E-commerce":              ["cart","checkout","payment","order","price","coupon"],
    "Media":                   ["audio","video","stream","player","upload","download"],
    "Error Pages":             ["error","404","500","exception","fallback","warning"],
}

PRACTICE_SITES = {
    "🔐 Login page (great for beginners)":  "https://the-internet.herokuapp.com/login",
    "📋 Form testing":                       "https://demoqa.com/automation-practice-form",
    "🛒 E-commerce demo":                   "https://opencart.abstracta.us",
    "🔌 API testing site":                  "https://reqres.in",
}


# ════════════════════════════════════════════════════════════════════════════
# SCRAPER — simple, no Selenium needed
# ════════════════════════════════════════════════════════════════════════════

def scrape_website(url: str) -> dict:
    if not url.startswith("http"):
        url = "https://" + url
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36"},
            timeout=12
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        data = {
            "url":    url,
            "title":  (soup.title.string.strip() if soup.title else "Unknown Page"),
            "status": resp.status_code,
            "forms":  [], "inputs": [], "buttons": [],
            "headings": [], "links": [], "page_text": "", "areas": [],
        }

        # Forms
        for form in soup.find_all("form"):
            fields = []
            for inp in form.find_all(["input", "select", "textarea"]):
                fields.append({
                    "type":     inp.get("type", inp.name),
                    "name":     inp.get("name", ""),
                    "label":    inp.get("placeholder", inp.get("aria-label", "")),
                    "required": inp.has_attr("required"),
                })
            if fields:
                data["forms"].append({
                    "method": form.get("method", "GET").upper(),
                    "fields": fields
                })

        # Inputs
        for inp in soup.find_all("input"):
            data["inputs"].append({
                "type":  inp.get("type", "text"),
                "name":  inp.get("name", ""),
                "label": inp.get("placeholder", ""),
            })

        # Buttons
        for btn in soup.find_all(["button", "input"]):
            if btn.name == "input" and btn.get("type") not in ["submit", "button"]:
                continue
            txt = btn.get_text(strip=True) or btn.get("value", "")
            if txt and len(txt) < 50:
                data["buttons"].append(txt)

        # Headings
        for h in soup.find_all(["h1", "h2", "h3"]):
            txt = h.get_text(strip=True)
            if txt:
                data["headings"].append(txt[:80])

        # Links (sample)
        for a in soup.find_all("a", href=True)[:12]:
            txt = a.get_text(strip=True)
            if txt:
                data["links"].append(txt[:40])

        # Page text
        data["page_text"] = " ".join(soup.get_text(separator=" ").split())[:2500]

        # Detect areas
        txt_l = data["page_text"].lower()
        for area, kws in AREA_KEYWORDS.items():
            if any(kw in txt_l for kw in kws):
                data["areas"].append(area)
        if not data["areas"]:
            data["areas"] = ["General"]

        return {"success": True, "data": data}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "The website took too long to respond (12 seconds). Try a different URL."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not reach the website. Check if the URL is correct."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"The website returned an error (HTTP {e.response.status_code})."}
    except Exception as e:
        return {"success": False, "error": f"Something went wrong: {str(e)}"}


# ════════════════════════════════════════════════════════════════════════════
# AI PROMPT — simple, beginner-friendly output
# ════════════════════════════════════════════════════════════════════════════

def build_prompt(scraped: dict, area: str, tc_count: int, tc_types: list) -> str:
    return f"""You are a QA engineer helping a beginner software tester learn.
Generate exactly {tc_count} test cases for the area "{area}" on this website.
Test types to include: {', '.join(tc_types)}.

WEBSITE INFORMATION:
- Page title: {scraped['title']}
- URL: {scraped['url']}
- Forms found: {json.dumps(scraped['forms'][:3])}
- Buttons: {scraped['buttons'][:10]}
- Page headings: {scraped['headings'][:6]}
- Page content snippet: {scraped['page_text'][:1000]}

IMPORTANT RULES:
- Write test steps in plain, simple English — as if explaining to a beginner
- Each step should be one clear action
- Test data must be specific real values (e.g. "enter 'admin@test.com'" not "enter a valid email")
- Expected results must be specific (e.g. "User sees 'Login successful' message" not "it works")

Return ONLY a valid JSON array. No markdown. No explanation.
Each object must have EXACTLY these keys:
- "id": "TC-001" format
- "title": simple, clear test case name
- "type": one of {tc_types}
- "precondition": what the tester must do before starting
- "steps": array of 3-6 simple step strings
- "expected_result": what should happen — be specific
- "priority": "High", "Medium", or "Low"
- "area": "{area}"
- "why_this_test": one sentence explaining WHY this test is important (for learning)
"""


# ════════════════════════════════════════════════════════════════════════════
# AI ENGINES
# ════════════════════════════════════════════════════════════════════════════

def clean_json(raw: str) -> list:
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
                "temperature": 0.4,
                "max_tokens": 3500,
            },
            timeout=40,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return {"success": True, "test_cases": clean_json(content), "model": "Groq"}
    except json.JSONDecodeError:
        return {"success": False, "error": "The AI returned an unexpected format. Try again."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {"success": False, "error": "Your Groq API key is incorrect. Double-check it."}
        if e.response.status_code == 429:
            return {"success": False, "error": "Groq rate limit reached. Wait 30 seconds and try again."}
        return {"success": False, "error": f"Groq error: HTTP {e.response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def call_hf(prompt: str, api_key: str, model_id: str) -> dict:
    try:
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "inputs": f"[INST] {prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": 3000,
                    "temperature": 0.4,
                    "return_full_text": False,
                    "do_sample": True,
                },
            },
            timeout=60,
        )
        if resp.status_code == 503:
            wait = resp.json().get("estimated_time", 20)
            return {"success": False, "error": f"The HuggingFace model is warming up. Wait {int(wait)} seconds and try again. This is normal for free models."}
        resp.raise_for_status()
        data = resp.json()
        raw  = data[0].get("generated_text", "") if isinstance(data, list) else data.get("generated_text", "")
        return {"success": True, "test_cases": clean_json(raw), "model": "HuggingFace"}
    except json.JSONDecodeError:
        return {"success": False, "error": "HuggingFace returned unexpected output. Groq gives more reliable results for beginners."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "HuggingFace took too long. Try Groq instead — it is much faster."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {"success": False, "error": "Your HuggingFace token is incorrect. Double-check it."}
        return {"success": False, "error": f"HuggingFace error: HTTP {e.response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ════════════════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════════════════

def to_csv(tcs: list) -> str:
    buf = io.StringIO()
    w   = csv.writer(buf)
    w.writerow(["ID", "Title", "Type", "Priority", "Area",
                "Precondition", "Steps", "Expected Result", "Why This Test"])
    for tc in tcs:
        w.writerow([
            tc.get("id",""), tc.get("title",""), tc.get("type",""),
            tc.get("priority",""), tc.get("area",""),
            tc.get("precondition",""),
            " | ".join(tc.get("steps",[])),
            tc.get("expected_result",""),
            tc.get("why_this_test",""),
        ])
    return buf.getvalue()


def to_markdown(tcs: list, url: str) -> str:
    lines = [
        "# Test Cases",
        f"**Website:** {url}",
        f"**Date:** {datetime.now().strftime('%d %b %Y %H:%M')}",
        "", "---", ""
    ]
    for tc in tcs:
        lines += [
            f"## {tc.get('id','')} — {tc.get('title','')}",
            f"- **Type:** {tc.get('type','')}",
            f"- **Priority:** {tc.get('priority','')}",
            f"- **Area:** {tc.get('area','')}",
            f"- **Why this test:** {tc.get('why_this_test','')}",
            f"- **Precondition:** {tc.get('precondition','')}",
            "", "**Steps:**",
        ]
        for i, s in enumerate(tc.get("steps",[]), 1):
            lines.append(f"{i}. {s}")
        lines += ["", f"**Expected Result:** {tc.get('expected_result','')}", "", "---", ""]
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════

for k, v in {"scraped": None, "test_cases": []}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — simple, with explanations
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Setup")

    st.markdown("""
<div style="background:#f1f5f9;border-radius:10px;padding:.9rem;font-size:.8rem;color:#475569;margin-bottom:1rem;line-height:1.6;">
<strong>New to AI APIs?</strong><br>
An API key is like a password that lets this app use an AI model. Both Groq and HuggingFace are <strong>free</strong> to sign up.
</div>
""", unsafe_allow_html=True)

    st.markdown("### 🔑 Step 1 — Add API Key")

    # Try loading from secrets (Streamlit Cloud)
    default_groq = ""
    default_hf   = ""
    try:
        default_groq = st.secrets.get("GROQ_API_KEY", "")
        default_hf   = st.secrets.get("HF_API_KEY", "")
    except Exception:
        pass

    provider = st.radio(
        "Choose AI provider",
        ["Groq (Recommended for beginners)", "HuggingFace (Free alternative)"]
    )

    if "Groq" in provider:
        groq_key = st.text_input("Groq API Key", value=default_groq, type="password", placeholder="gsk_...")
        st.markdown("""
<div class="tip-box">
✅ <strong>How to get it free:</strong><br>
1. Go to <strong>console.groq.com</strong><br>
2. Sign up (takes 1 minute)<br>
3. Click "API Keys" → Create key<br>
4. Paste it above
</div>
""", unsafe_allow_html=True)
        hf_key    = default_hf
        use_groq  = True
        groq_model_name = st.selectbox("Choose model", list(GROQ_MODELS.keys()))
        hf_model_name   = list(HF_MODELS.keys())[0]
    else:
        hf_key   = st.text_input("HuggingFace Token", value=default_hf, type="password", placeholder="hf_...")
        st.markdown("""
<div class="warn-box">
⚠️ <strong>HuggingFace tip:</strong><br>
Free models sometimes need 20–30 seconds to warm up when first used. If you get a loading error, just wait and try again. Groq is faster.
</div>
""", unsafe_allow_html=True)
        groq_key        = default_groq
        use_groq        = False
        hf_model_name   = st.selectbox("Choose model", list(HF_MODELS.keys()))
        groq_model_name = list(GROQ_MODELS.keys())[0]

    st.markdown("---")
    st.markdown("### 🧪 Step 2 — Test Settings")
    tc_count = st.slider("How many test cases?", 3, 15, 6,
                          help="Start with 6. You can always generate more.")

    st.markdown("**What types of tests to create?**")
    tc_types = []
    for t, desc in TEST_TYPE_EXPLAIN.items():
        if st.checkbox(t, value=(t in ["Positive", "Negative"]), help=desc):
            tc_types.append(t)

    if not tc_types:
        st.warning("Select at least one test type.")

    st.markdown("---")
    st.markdown("""
<div style="font-size:.72rem;color:#94a3b8;line-height:1.8;">
🤖 AI: Groq / HuggingFace<br>
🕷 Scraper: BeautifulSoup<br>
☁ Deployable on Streamlit Cloud<br>
📚 Built for learning purposes
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header">
  <h1>🤖 AI Test Case Generator</h1>
  <p>Enter any website URL → AI reads the page → Generates test cases for you. Simple as that.</p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs(["🔍 Step 1: Scrape", "⚡ Step 2: Generate", "📥 Step 3: Export"])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — SCRAPE
# ────────────────────────────────────────────────────────────────────────────
with tab1:

    # What is web scraping — explain it
    st.markdown("""
<div class="learn-box">
💡 <strong>What is web scraping?</strong><br>
Web scraping means reading a website's content automatically using code.
This app reads the page to find things like <em>forms, input fields, buttons, and text</em>
— the same things a tester would look at manually. The AI then uses this information
to write relevant test cases for that specific page.
</div>
""", unsafe_allow_html=True)

    # Quick-start sites
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.markdown('<div class="step-number">STEP 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Enter a Website URL</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-desc">Paste any website URL below. Not sure where to start? Pick one of the practice sites made for testers.</div>', unsafe_allow_html=True)

    st.markdown("**🏋️ Practice Sites for Beginners:**")
    for label, site_url in PRACTICE_SITES.items():
        st.markdown(f"- `{site_url}` — {label}")

    url_input = st.text_input(
        "Website URL",
        placeholder="https://the-internet.herokuapp.com/login",
        label_visibility="collapsed"
    )
    scrape_btn = st.button("🔍 Read This Website", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if scrape_btn:
        if not url_input:
            st.error("Please enter a URL first.")
        else:
            with st.spinner("Reading the website... this takes a few seconds"):
                result = scrape_website(url_input)

            if result["success"]:
                st.session_state.scraped    = result["data"]
                st.session_state.test_cases = []
                st.success(f"✅ Done! Read the page: **{result['data']['title']}**")
            else:
                st.error(f"❌ Could not read the website. Reason: {result['error']}")

    # Show what was found
    if st.session_state.scraped:
        d = st.session_state.scraped

        st.markdown(f"""
<div class="stat-row">
  <div class="stat"><div class="stat-num">{len(d['forms'])}</div><div class="stat-lbl">Forms</div></div>
  <div class="stat"><div class="stat-num">{len(d['inputs'])}</div><div class="stat-lbl">Input Fields</div></div>
  <div class="stat"><div class="stat-num">{len(d['buttons'])}</div><div class="stat-lbl">Buttons</div></div>
  <div class="stat"><div class="stat-num">{len(d['areas'])}</div><div class="stat-lbl">Test Areas</div></div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="learn-box">
💡 <strong>What do these numbers mean?</strong><br>
The app found <em>forms</em> (groups of input fields), <em>input fields</em> (text boxes, dropdowns),
and <em>buttons</em> on the page. These are exactly what a tester focuses on —
each form field is something that could have a bug!
</div>
""", unsafe_allow_html=True)

        st.markdown("**Detected testing areas on this page:**")
        st.markdown("".join(f'<span class="area-tag">{a}</span>' for a in d["areas"]), unsafe_allow_html=True)

        with st.expander("👀 See what the app read from the page"):
            st.markdown(f"**Page title:** {d['title']}")
            if d["headings"]:
                st.markdown(f"**Headings found:** {', '.join(d['headings'][:5])}")
            if d["buttons"]:
                st.markdown(f"**Buttons found:** {', '.join(d['buttons'][:8])}")
            if d["forms"]:
                for i, form in enumerate(d["forms"][:2]):
                    st.markdown(f"**Form {i+1}** ({form['method']}) — fields: {[f['name'] or f['type'] for f in form['fields'][:6]]}")

        st.markdown("""
<div class="tip-box">
✅ <strong>Good job!</strong> The website has been read successfully.
Now go to <strong>Step 2: Generate</strong> to create test cases.
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — GENERATE
# ────────────────────────────────────────────────────────────────────────────
with tab2:

    if not st.session_state.scraped:
        st.info("👈 Go to **Step 1: Scrape** first and read a website.")
    else:
        d = st.session_state.scraped

        st.markdown("""
<div class="learn-box">
💡 <strong>How does AI generate test cases?</strong><br>
The app sends the page information (forms, buttons, field names) to an AI model along with
instructions. The AI reads this and writes structured test cases the same way a QA engineer
would — but in seconds. The <strong>quality of test cases depends on what was found on the page.</strong>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="step-box">', unsafe_allow_html=True)
        st.markdown('<div class="step-number">STEP 2</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-title">Generate Test Cases for: {d["title"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="step-desc">Choose the area you want to test, then click Generate.</div>', unsafe_allow_html=True)

        area_opts   = d["areas"] + ["General"]
        chosen_area = st.selectbox("What area do you want to test?", area_opts)
        gen_btn     = st.button("⚡ Generate Test Cases with AI", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if gen_btn:
            if not tc_types:
                st.error("Please select at least one test type in the sidebar.")
            elif "Groq" in provider and not groq_key:
                st.error("Please add your Groq API key in the sidebar.")
            elif "HuggingFace" in provider and not hf_key:
                st.error("Please add your HuggingFace token in the sidebar.")
            else:
                with st.spinner(f"AI is writing {tc_count} test cases... this may take 10–30 seconds"):
                    prompt = build_prompt(d, chosen_area, tc_count, tc_types)

                    if "Groq" in provider:
                        result = call_groq(prompt, groq_key, GROQ_MODELS[groq_model_name])
                    else:
                        result = call_hf(prompt, hf_key, HF_MODELS[hf_model_name])

                if result["success"]:
                    st.session_state.test_cases = result["test_cases"]
                    st.success(f"✅ {len(result['test_cases'])} test cases created by {result['model']}!")
                else:
                    st.error(f"❌ {result['error']}")

        # Show test cases
        if st.session_state.test_cases:
            tcs = st.session_state.test_cases

            st.markdown("---")

            # Count by type
            type_counts = {}
            for tc in tcs:
                t = tc.get("type","?")
                type_counts[t] = type_counts.get(t, 0) + 1

            count_html = "".join(
                f'<span class="badge b-{t.lower().replace(" ","")}">  {t}: {c}</span>'
                for t, c in type_counts.items()
            )
            st.markdown(f"**Generated:** {count_html}", unsafe_allow_html=True)

            st.markdown("""
<div class="learn-box" style="margin-top:.8rem;">
💡 <strong>Reading a test case:</strong><br>
Each card below is one test case. It has: <em>Precondition</em> (what to set up first),
<em>Steps</em> (what to do), <em>Expected Result</em> (what should happen), and
<em>Why This Test</em> (why it matters). This is the standard format used in real QA teams.
</div>
""", unsafe_allow_html=True)

            for tc in tcs:
                tc_type  = tc.get("type","Positive")
                card_cls = tc_type.lower().replace(" ","")
                b_cls    = f"b-{card_cls}"
                pri      = tc.get("priority","Medium")

                steps_html = "".join(f'<div class="step-line">{s}</div>' for s in tc.get("steps",[]))
                why        = tc.get("why_this_test","")

                st.markdown(f"""
<div class="tc-card {card_cls}">
  <div class="tc-id">{tc.get('id','')} · {tc.get('area','')}</div>
  <div class="tc-title">{tc.get('title','')}</div>
  <span class="badge {b_cls}">{tc_type}</span>
  <span class="badge b-{pri.lower()}">{pri} Priority</span>

  <div class="tc-label">Precondition (Setup)</div>
  <div class="tc-value">{tc.get('precondition','N/A')}</div>

  <div class="tc-label">Steps (What to do)</div>
  <div class="tc-value">{steps_html}</div>

  <div class="tc-label">Expected Result (What should happen)</div>
  <div class="tc-value">{tc.get('expected_result','N/A')}</div>

  {f'<div class="tc-label">💡 Why this test matters</div><div class="tc-value" style="color:#6366f1;">{why}</div>' if why else ''}
</div>
""", unsafe_allow_html=True)

            st.markdown("""
<div class="tip-box">
✅ <strong>Next step:</strong> Go to <strong>Step 3: Export</strong> to download these test cases as a CSV or Markdown file.
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — EXPORT
# ────────────────────────────────────────────────────────────────────────────
with tab3:
    tcs = st.session_state.test_cases

    if not tcs:
        st.info("👈 Go to **Step 2: Generate** first to create test cases.")
    else:
        st.markdown("""
<div class="learn-box">
💡 <strong>Why export test cases?</strong><br>
In real QA teams, test cases are stored in tools like <em>JIRA, TestRail, or Excel</em>.
CSV format can be imported into most of these tools. Markdown is useful for documentation
on GitHub or Confluence. Download your test cases and keep them for practice!
</div>
""", unsafe_allow_html=True)

        st.markdown(f"### 📥 Download {len(tcs)} Test Cases")
        url = st.session_state.scraped["url"] if st.session_state.scraped else ""
        ts  = datetime.now().strftime("%Y%m%d_%H%M")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📊 CSV File")
            st.caption("Opens in Excel · importable to JIRA / TestRail")
            st.download_button(
                "⬇ Download CSV",
                data=to_csv(tcs),
                file_name=f"test_cases_{ts}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c2:
            st.markdown("#### 📝 Markdown File")
            st.caption("For GitHub, Notion, or Confluence documentation")
            st.download_button(
                "⬇ Download Markdown",
                data=to_markdown(tcs, url),
                file_name=f"test_cases_{ts}.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("#### 🎓 What you learned by building this app")
        st.markdown("""
- **Web scraping** — how to read a website using Python and BeautifulSoup
- **AI APIs** — how to send data to an AI model and get structured output back
- **Test case structure** — ID, precondition, steps, expected result
- **Streamlit** — how to build a web app in Python without HTML or JavaScript
- **Prompt engineering** — how you write the instructions you send to an AI model matters
        """)

        st.markdown("#### 🚀 What to build next")
        st.markdown("""
- Add a **batch mode** — test multiple URLs at once
- Add **test type filtering** on results
- Add **Selenium scraping** for JavaScript-heavy websites
- Connect to **JIRA API** to create tickets automatically from test cases
        """)
