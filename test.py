import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import csv
import io
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="QA Intelligence — Test Case Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@300;400;600;800;900&display=swap');

:root {
  --bg:       #07080f;
  --surface:  #0d1017;
  --surface2: #131820;
  --border:   #1c2333;
  --border2:  #243044;
  --accent:   #00e5ff;
  --accent2:  #7c3aed;
  --accent3:  #f59e0b;
  --green:    #10b981;
  --red:      #ef4444;
  --text:     #e2eaf6;
  --muted:    #4a5568;
  --mono:     'Space Mono', monospace;
  --sans:     'Outfit', sans-serif;
}

html, body, [class*="css"] { font-family: var(--sans); background: var(--bg); color: var(--text); }
.stApp { background: var(--bg); }

/* HERO */
.hero {
  position:relative; padding:2.5rem 3rem; margin-bottom:2rem;
  border-radius:20px;
  background:linear-gradient(135deg,#07080f 0%,#0a0f1e 60%,#07080f 100%);
  border:1px solid var(--border2); overflow:hidden;
}
.hero::before {
  content:''; position:absolute; inset:0;
  background:
    radial-gradient(ellipse 60% 80% at 10% 50%,rgba(0,229,255,.07) 0%,transparent 70%),
    radial-gradient(ellipse 40% 60% at 85% 20%,rgba(124,58,237,.09) 0%,transparent 70%);
}
.hero-badge {
  display:inline-block; font-family:var(--mono); font-size:0.65rem;
  color:var(--accent); border:1px solid rgba(0,229,255,.3); border-radius:4px;
  padding:.2rem .6rem; margin-bottom:.8rem; letter-spacing:.12em; text-transform:uppercase;
}
.hero-title { font-size:2.6rem; font-weight:900; line-height:1.1; margin:0 0 .5rem; color:var(--text); }
.hero-title span { background:linear-gradient(90deg,var(--accent),var(--accent2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero-sub { font-family:var(--mono); font-size:.8rem; color:var(--muted); letter-spacing:.05em; }
.hero-pills { margin-top:1.2rem; display:flex; gap:.5rem; flex-wrap:wrap; }
.pill { font-size:.72rem; font-family:var(--mono); padding:.25rem .7rem; border-radius:20px; border:1px solid var(--border2); color:var(--muted); }
.pill.on { border-color:var(--accent); color:var(--accent); background:rgba(0,229,255,.07); }

/* TABS */
.stTabs [data-baseweb="tab-list"] { background:var(--surface); border-radius:12px; padding:.3rem; border:1px solid var(--border); gap:.2rem; }
.stTabs [data-baseweb="tab"] { background:transparent; border-radius:8px; color:var(--muted); font-family:var(--sans); font-weight:600; font-size:.85rem; padding:.5rem 1.2rem; border:none; }
.stTabs [aria-selected="true"] { background:var(--surface2) !important; color:var(--accent) !important; }

/* KPI */
.kpi-row { display:flex; gap:.8rem; margin:1rem 0; }
.kpi { flex:1; background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:1rem 1.2rem; position:relative; overflow:hidden; }
.kpi::after { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,var(--accent),var(--accent2)); }
.kpi-val { font-family:var(--mono); font-size:1.9rem; font-weight:700; color:var(--accent); line-height:1; }
.kpi-lbl { font-size:.68rem; text-transform:uppercase; letter-spacing:.12em; color:var(--muted); margin-top:.3rem; }

/* URL ROW */
.url-row { background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:.8rem 1rem; margin-bottom:.5rem; display:flex; align-items:center; gap:.8rem; font-family:var(--mono); font-size:.78rem; }
.url-title { color:var(--text); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.url-meta  { color:var(--muted); font-size:.7rem; }

/* TEST CARD */
.tc { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:1.3rem 1.5rem; margin-bottom:.9rem; position:relative; overflow:hidden; transition:border-color .2s,transform .15s; }
.tc:hover { border-color:var(--border2); transform:translateX(2px); }
.tc::before { content:''; position:absolute; left:0; top:0; bottom:0; width:3px; }
.tc.positive::before    { background:var(--green); }
.tc.negative::before    { background:var(--red); }
.tc.edge::before        { background:var(--accent3); }
.tc.security::before    { background:var(--accent2); }
.tc.performance::before { background:var(--accent); }

.tc-id    { font-family:var(--mono); font-size:.65rem; color:var(--muted); }
.tc-title { font-size:1rem; font-weight:700; color:var(--text); margin:.3rem 0; }
.tc-badges { display:flex; gap:.4rem; flex-wrap:wrap; margin:.5rem 0; }

.badge { font-size:.62rem; font-family:var(--mono); padding:.18rem .55rem; border-radius:4px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
.b-positive    { background:rgba(16,185,129,.15);  color:#10b981; border:1px solid rgba(16,185,129,.3); }
.b-negative    { background:rgba(239,68,68,.15);   color:#ef4444; border:1px solid rgba(239,68,68,.3); }
.b-edge        { background:rgba(245,158,11,.15);  color:#f59e0b; border:1px solid rgba(245,158,11,.3); }
.b-security    { background:rgba(124,58,237,.15);  color:#a78bfa; border:1px solid rgba(124,58,237,.3); }
.b-performance { background:rgba(0,229,255,.1);    color:#00e5ff; border:1px solid rgba(0,229,255,.3); }
.b-high   { background:rgba(239,68,68,.1);  color:#ef4444; }
.b-medium { background:rgba(245,158,11,.1); color:#f59e0b; }
.b-low    { background:rgba(16,185,129,.1); color:#10b981; }
.b-model  { background:rgba(255,255,255,.04); color:#4a5568; border:1px solid #1c2333; }

.tc-section     { margin-top:.8rem; }
.tc-section-lbl { font-size:.62rem; font-family:var(--mono); text-transform:uppercase; letter-spacing:.12em; color:var(--muted); margin-bottom:.3rem; }
.tc-section-val { font-size:.85rem; color:#94a3b8; line-height:1.6; }
.step-item::before { content:"→ "; color:var(--accent); }

/* AREA TAG */
.area-tag { display:inline-block; background:rgba(0,229,255,.07); color:var(--accent); border:1px solid rgba(0,229,255,.2); border-radius:6px; padding:.25rem .65rem; font-size:.75rem; font-family:var(--mono); margin:.2rem; }

/* MODEL BADGE */
.model-info { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:.6rem 1rem; font-family:var(--mono); font-size:.75rem; color:var(--muted); margin-bottom:1rem; }
.model-info span { color:var(--accent); font-weight:700; }

/* INPUTS */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div,
.stNumberInput>div>div>input {
  background:var(--surface) !important; border:1px solid var(--border2) !important;
  color:var(--text) !important; border-radius:8px !important;
  font-family:var(--mono) !important; font-size:.82rem !important;
}

/* BUTTONS */
.stButton>button {
  background:linear-gradient(135deg,#0097a7,#6d28d9) !important;
  color:#fff !important; border:none !important; border-radius:8px !important;
  font-family:var(--sans) !important; font-weight:700 !important;
  font-size:.88rem !important; padding:.55rem 1.4rem !important;
  transition:opacity .2s,transform .15s !important; width:100%;
}
.stButton>button:hover { opacity:.88 !important; transform:translateY(-1px) !important; }

/* SIDEBAR */
[data-testid="stSidebar"] { background:#080c14 !important; border-right:1px solid var(--border) !important; }

hr { border-color:var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════════════════

AREA_MAP = {
    "Authentication":  ["login","signin","signup","register","password","logout","auth","forgot","reset","otp","2fa","verify"],
    "Search":          ["search","filter","query","find","sort","results","keyword","autocomplete"],
    "Forms & Input":   ["form","input","submit","field","validate","required","placeholder","dropdown","checkbox","radio"],
    "Navigation":      ["menu","nav","breadcrumb","pagination","sidebar","tab","link","redirect"],
    "API / Data":      ["api","endpoint","json","fetch","response","payload","request","status","schema"],
    "Media / Audio":   ["audio","video","stream","player","upload","download","bitrate","codec","buffer","playback"],
    "E-commerce":      ["cart","checkout","payment","order","price","discount","coupon","invoice","shipping"],
    "User Profile":    ["profile","account","settings","preference","avatar","subscription","plan"],
    "Security":        ["token","csrf","xss","https","cookie","session","cors","header","injection","sql"],
    "Accessibility":   ["aria","alt","role","label","tabindex","screen","wcag","contrast","keyboard","focus"],
    "Performance":     ["load","speed","cache","cdn","timeout","latency","optimize"],
    "Error Handling":  ["error","404","500","exception","retry","fallback","message","alert","warning"],
}

# Hugging Face free inference models that support text generation
HF_MODELS = {
    "Mistral 7B Instruct":     "mistralai/Mistral-7B-Instruct-v0.3",
    "Zephyr 7B Beta":          "HuggingFaceH4/zephyr-7b-beta",
    "Falcon 7B Instruct":      "tiiuae/falcon-7b-instruct",
}

GROQ_MODELS = {
    "LLaMA 3.3 70B (Best)":   "llama-3.3-70b-versatile",
    "LLaMA 3.1 8B (Fast)":    "llama-3.1-8b-instant",
    "Gemma 2 9B":              "gemma2-9b-it",
    "Mixtral 8x7B":            "mixtral-8x7b-32768",
}


# ════════════════════════════════════════════════════════════════════════════
# SCRAPER
# ════════════════════════════════════════════════════════════════════════════

def _parse_html(soup: BeautifulSoup, url: str, status_code: int) -> dict:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    data = {
        "url": url,
        "title": (soup.title.string.strip() if soup.title else "Unknown"),
        "status_code": status_code,
        "forms": [], "inputs": [], "buttons": [], "links": [],
        "headings": [], "images": [], "tables": [], "selects": [],
        "error_messages": [], "api_hints": [], "page_text": "", "areas": [],
    }

    # Forms
    for form in soup.find_all("form"):
        fd = {
            "action": form.get("action", ""),
            "method": form.get("method", "GET").upper(),
            "fields": [], "has_file_upload": False,
        }
        for inp in form.find_all(["input", "select", "textarea"]):
            t = inp.get("type", inp.name)
            if t == "file":
                fd["has_file_upload"] = True
            fd["fields"].append({
                "type":        t,
                "name":        inp.get("name", ""),
                "placeholder": inp.get("placeholder", ""),
                "required":    inp.has_attr("required"),
                "maxlength":   inp.get("maxlength", ""),
            })
        data["forms"].append(fd)

    # Inputs
    for inp in soup.find_all("input"):
        data["inputs"].append({
            "type":        inp.get("type", "text"),
            "name":        inp.get("name", ""),
            "placeholder": inp.get("placeholder", ""),
        })

    # Selects
    for sel in soup.find_all("select"):
        opts = [o.get_text(strip=True) for o in sel.find_all("option")][:6]
        data["selects"].append({"name": sel.get("name", ""), "options": opts})

    # Buttons
    for btn in soup.find_all(["button", "a"]):
        txt = btn.get_text(strip=True)
        if txt and len(txt) < 60:
            data["buttons"].append(txt)

    # Links
    for a in soup.find_all("a", href=True)[:20]:
        href = urljoin(base, a["href"])
        data["links"].append({"text": a.get_text(strip=True)[:40], "href": href})

    # Headings
    for h in soup.find_all(["h1", "h2", "h3"]):
        txt = h.get_text(strip=True)
        if txt:
            data["headings"].append(txt[:100])

    # Images
    for img in soup.find_all("img")[:12]:
        data["images"].append({"alt": img.get("alt", ""), "src": img.get("src", "")[:60]})

    # Tables
    for tbl in soup.find_all("table")[:3]:
        headers = [th.get_text(strip=True) for th in tbl.find_all("th")]
        if headers:
            data["tables"].append({"headers": headers, "rows": len(tbl.find_all("tr"))})

    # Error messages
    for el in soup.find_all(class_=re.compile(r"error|alert|warning|danger", re.I)):
        txt = el.get_text(strip=True)
        if txt and len(txt) < 200:
            data["error_messages"].append(txt)

    # Page text
    data["page_text"] = " ".join(soup.get_text(separator=" ").split())[:3000]

    # Detect test areas
    text_lower = data["page_text"].lower()
    for area, keywords in AREA_MAP.items():
        if any(kw in text_lower for kw in keywords):
            data["areas"].append(area)
    if not data["areas"]:
        data["areas"] = ["General"]

    return data


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
        data = _parse_html(soup, url, resp.status_code)
        return {"success": True, "data": data}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out (12s). Site may be slow or blocking scrapers."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect. Check the URL."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.response.status_code} returned by server."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ════════════════════════════════════════════════════════════════════════════
# AI PROMPT BUILDER
# ════════════════════════════════════════════════════════════════════════════

def _build_prompt(scraped: dict, area: str, count: int, tc_types: list) -> str:
    return f"""You are a senior QA engineer with 15 years of experience.
Analyze this scraped website data and generate exactly {count} test cases for the area: "{area}".
Focus on these test types: {', '.join(tc_types)}.

WEBSITE DATA:
- URL: {scraped['url']}
- Title: {scraped['title']}
- Forms: {json.dumps(scraped['forms'][:4], indent=2)}
- Buttons: {scraped['buttons'][:12]}
- Headings: {scraped['headings'][:8]}
- Dropdowns: {json.dumps(scraped['selects'][:4])}
- Tables: {json.dumps(scraped['tables'][:3])}
- Error messages on page: {scraped['error_messages'][:4]}
- Page text snippet: {scraped['page_text'][:1200]}

Return ONLY a valid JSON array. No markdown fences, no explanation, no preamble.
Each object must have EXACTLY these keys:
- "id": "TC-001" format
- "title": concise test case title
- "type": one of Positive / Negative / Edge / Security / Performance
- "precondition": what must be true before execution
- "steps": array of 3-6 clear step strings
- "expected_result": specific expected outcome
- "priority": "High", "Medium", or "Low"
- "area": "{area}"
- "test_data": specific test data values (empty string if none)

Be specific to the actual page — reference real field names, button text, URLs found.
Generate a good mix of the requested types."""


def _clean_json(raw: str) -> list:
    """Strip markdown fences and parse JSON."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    # Sometimes models wrap in extra text — find the JSON array
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        raw = match.group(0)
    return json.loads(raw)


# ════════════════════════════════════════════════════════════════════════════
# AI ENGINES
# ════════════════════════════════════════════════════════════════════════════

def call_groq(prompt: str, api_key: str, model_id: str) -> dict:
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.35,
                "max_tokens": 4000,
            },
            timeout=45,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return {"success": True, "test_cases": _clean_json(content), "model": f"Groq / {model_id}"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"AI returned malformed JSON: {e}"}
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        msg  = {401: "Invalid Groq API key.", 429: "Groq rate limit hit. Wait a moment.", 503: "Groq service unavailable."}.get(code, f"Groq API HTTP {code}")
        return {"success": False, "error": msg}
    except Exception as e:
        return {"success": False, "error": str(e)}


def call_huggingface(prompt: str, api_key: str, model_id: str) -> dict:
    """
    Uses Hugging Face Inference API (free tier).
    Free tier has rate limits — suitable for learning/demo use.
    """
    hf_prompt = f"[INST] {prompt} [/INST]"   # Instruct format for most HF models
    try:
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "inputs": hf_prompt,
                "parameters": {
                    "max_new_tokens": 3000,
                    "temperature": 0.35,
                    "return_full_text": False,
                    "do_sample": True,
                },
            },
            timeout=60,
        )

        # HF returns 503 when model is loading
        if resp.status_code == 503:
            try:
                wait_time = resp.json().get("estimated_time", 20)
            except Exception:
                wait_time = 20
            return {"success": False, "error": f"Model is loading on HF servers. Wait ~{int(wait_time)}s and retry."}

        resp.raise_for_status()
        data = resp.json()

        # HF returns list of generated text objects
        if isinstance(data, list) and data:
            raw = data[0].get("generated_text", "")
        elif isinstance(data, dict):
            raw = data.get("generated_text", "")
        else:
            return {"success": False, "error": "Unexpected HF response format."}

        return {"success": True, "test_cases": _clean_json(raw), "model": f"HuggingFace / {model_id}"}

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"HF model returned malformed JSON: {e}. Try a Groq model for more reliable JSON output."}
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        msg  = {401: "Invalid HF API token.", 429: "HF rate limit hit.", 404: "Model not found on HF."}.get(code, f"HF API HTTP {code}")
        return {"success": False, "error": msg}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "HF request timed out (60s). Model may be cold-starting. Try again."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def call_both(prompt: str, groq_key: str, groq_model_id: str,
              hf_key: str, hf_model_id: str) -> dict:
    """Run Groq + HF in parallel, merge results."""
    results = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {
            ex.submit(call_groq, prompt, groq_key, groq_model_id): "groq",
            ex.submit(call_huggingface, prompt, hf_key, hf_model_id): "hf",
        }
        for f in as_completed(futures):
            results[futures[f]] = f.result()

    merged = []
    idx = 1
    for key in ["groq", "hf"]:
        if results[key]["success"]:
            for tc in results[key]["test_cases"]:
                tc["id"] = f"TC-{idx:03d}"
                tc["source_model"] = results[key]["model"]
                merged.append(tc)
                idx += 1

    if merged:
        return {"success": True, "test_cases": merged, "model": "Both (Groq + HuggingFace merged)"}

    # Both failed — return most informative error
    err = results["groq"]["error"] if not results["groq"]["success"] else results["hf"]["error"]
    return {"success": False, "error": err}


def generate_test_cases(scraped: dict, area: str, count: int, tc_types: list,
                        provider: str, groq_key: str, groq_model: str,
                        hf_key: str, hf_model: str) -> dict:
    prompt = _build_prompt(scraped, area, count, tc_types)

    if provider == "Groq":
        result = call_groq(prompt, groq_key, GROQ_MODELS[groq_model])
    elif provider == "Hugging Face":
        result = call_huggingface(prompt, hf_key, HF_MODELS[hf_model])
    else:  # Both
        result = call_both(prompt, groq_key, GROQ_MODELS[groq_model], hf_key, HF_MODELS[hf_model])

    # Tag with sequential IDs if not "both" (both already does it)
    if result["success"] and provider != "Both":
        for i, tc in enumerate(result["test_cases"]):
            tc["id"] = f"TC-{i+1:03d}"
            tc.setdefault("source_model", result["model"])

    return result


# ════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ════════════════════════════════════════════════════════════════════════════

def render_tc(tc: dict, idx: int):
    tc_type  = tc.get("type", "Positive").lower()
    card_cls = tc_type if tc_type in ["positive","negative","edge","security","performance"] else "positive"
    b_cls    = f"b-{card_cls}"
    pri      = tc.get("priority", "Medium")
    pri_cls  = f"b-{pri.lower()}"
    source   = tc.get("source_model", "")
    src_html = f'<span class="badge b-model">{source}</span>' if source else ""
    td       = tc.get("test_data", "")
    td_html  = f'<div class="tc-section"><div class="tc-section-lbl">Test Data</div><div class="tc-section-val" style="font-family:var(--mono);font-size:.78rem;color:#64748b;">{td}</div></div>' if td else ""
    steps_html = "".join(f'<div class="step-item">{s}</div>' for s in tc.get("steps", []))

    st.markdown(f"""
<div class="tc {card_cls}">
  <div class="tc-id">{tc.get('id', f'TC-{idx+1:03d}')} · {tc.get('area','')}</div>
  <div class="tc-title">{tc.get('title','Untitled')}</div>
  <div class="tc-badges">
    <span class="badge {b_cls}">{tc.get('type','Positive')}</span>
    <span class="badge {pri_cls}">{pri} Priority</span>
    {src_html}
  </div>
  <div class="tc-section">
    <div class="tc-section-lbl">Precondition</div>
    <div class="tc-section-val">{tc.get('precondition','N/A')}</div>
  </div>
  <div class="tc-section">
    <div class="tc-section-lbl">Steps</div>
    <div class="tc-section-val">{steps_html}</div>
  </div>
  <div class="tc-section">
    <div class="tc-section-lbl">Expected Result</div>
    <div class="tc-section-val">{tc.get('expected_result','N/A')}</div>
  </div>
  {td_html}
</div>
""", unsafe_allow_html=True)


def render_metrics(d: dict):
    st.markdown(f"""
<div class="kpi-row">
  <div class="kpi"><div class="kpi-val">{len(d['forms'])}</div><div class="kpi-lbl">Forms</div></div>
  <div class="kpi"><div class="kpi-val">{len(d['inputs'])}</div><div class="kpi-lbl">Inputs</div></div>
  <div class="kpi"><div class="kpi-val">{len(d['buttons'])}</div><div class="kpi-lbl">Buttons</div></div>
  <div class="kpi"><div class="kpi-val">{len(d['links'])}</div><div class="kpi-lbl">Links</div></div>
  <div class="kpi"><div class="kpi-val">{len(d['tables'])}</div><div class="kpi-lbl">Tables</div></div>
  <div class="kpi"><div class="kpi-val">{len(d['areas'])}</div><div class="kpi-lbl">Test Areas</div></div>
</div>
""", unsafe_allow_html=True)


def export_csv(tcs: list) -> str:
    buf = io.StringIO()
    w   = csv.writer(buf)
    w.writerow(["ID","Title","Type","Priority","Area","Precondition","Steps","Expected Result","Test Data","Model","Source URL"])
    for tc in tcs:
        w.writerow([
            tc.get("id",""), tc.get("title",""), tc.get("type",""),
            tc.get("priority",""), tc.get("area",""), tc.get("precondition",""),
            " | ".join(tc.get("steps",[])), tc.get("expected_result",""),
            tc.get("test_data",""), tc.get("source_model",""), tc.get("source_url",""),
        ])
    return buf.getvalue()


def export_markdown(tcs: list) -> str:
    lines = ["# AI Generated Test Cases", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    for tc in tcs:
        lines += [
            f"## {tc.get('id','')} — {tc.get('title','')}",
            f"**Type:** {tc.get('type','')} | **Priority:** {tc.get('priority','')} | **Area:** {tc.get('area','')}",
            f"**Precondition:** {tc.get('precondition','')}",
            "**Steps:**",
        ]
        for i, s in enumerate(tc.get("steps",[]), 1):
            lines.append(f"{i}. {s}")
        lines += [f"**Expected Result:** {tc.get('expected_result','')}", "---", ""]
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════

for k, v in {
    "scraped_results": {},
    "all_test_cases":  [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
<div style="font-family:var(--mono);font-size:.65rem;color:#00e5ff;
            text-transform:uppercase;letter-spacing:.15em;margin-bottom:1.2rem;">
⚡ QA Intelligence v2
</div>
""", unsafe_allow_html=True)

    # ── API Keys (from secrets or manual input) ──
    st.markdown("### 🔑 API Keys")

    # Try secrets first (Streamlit Cloud), fall back to manual input
    default_groq = ""
    default_hf   = ""
    try:
        default_groq = st.secrets.get("GROQ_API_KEY", "")
        default_hf   = st.secrets.get("HF_API_KEY", "")
    except Exception:
        pass

    groq_key = st.text_input(
        "Groq API Key",
        value=default_groq,
        type="password",
        placeholder="gsk_...",
        help="Free at console.groq.com"
    )
    hf_key = st.text_input(
        "Hugging Face Token",
        value=default_hf,
        type="password",
        placeholder="hf_...",
        help="Free at huggingface.co/settings/tokens"
    )

    st.markdown("---")

    # ── Provider ──
    st.markdown("### 🤖 AI Provider")
    provider = st.radio(
        "Provider",
        ["Groq", "Hugging Face", "Both (merge)"],
        label_visibility="collapsed"
    )

    # ── Model selection per provider ──
    groq_model = "LLaMA 3.3 70B (Best)"
    hf_model   = "Mistral 7B Instruct"

    if provider in ["Groq", "Both (merge)"]:
        st.markdown("**Groq Model**")
        groq_model = st.selectbox("Groq Model", list(GROQ_MODELS.keys()), label_visibility="collapsed")

    if provider in ["Hugging Face", "Both (merge)"]:
        st.markdown("**HuggingFace Model**")
        hf_model = st.selectbox("HF Model", list(HF_MODELS.keys()), label_visibility="collapsed")
        st.caption("⚠ HF free tier may be slow or require model warm-up. Groq is faster for demos.")

    st.markdown("---")

    # ── Generation Settings ──
    st.markdown("### ⚙️ Settings")
    tc_count = st.slider("Test cases per run", 3, 20, 8)
    tc_types = st.multiselect(
        "Test types to include",
        ["Positive", "Negative", "Edge", "Security", "Performance"],
        default=["Positive", "Negative", "Edge", "Security"]
    )

    st.markdown("---")
    st.markdown("""
<div style="font-size:.7rem;color:#1c2333;line-height:1.9;">
Groq: free · fast · reliable JSON<br>
HuggingFace: free · slower · may need warm-up<br>
Scraper: BeautifulSoup4<br>
Deploy: Streamlit Cloud ready
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════

provider_label = provider.split(" ")[0]
st.markdown(f"""
<div class="hero">
  <div class="hero-badge">QA Intelligence v2 — Free AI Edition</div>
  <div class="hero-title">AI <span>Test Case</span> Generator</div>
  <div class="hero-sub">scrape · analyze · generate · batch · export — 100% free APIs</div>
  <div class="hero-pills">
    <span class="pill on">🤖 {provider_label}</span>
    <span class="pill on">📋 {tc_count} TCs / run</span>
    <span class="pill on">🕷 BeautifulSoup4</span>
    <span class="pill on">☁ Streamlit Cloud Ready</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════

tab_single, tab_batch, tab_results, tab_export = st.tabs([
    "🔍  Single URL", "📦  Batch URLs", "🧪  Test Cases", "📥  Export"
])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — SINGLE URL
# ────────────────────────────────────────────────────────────────────────────
with tab_single:
    st.markdown("### Step 1 — Scrape a Website")

    col1, col2 = st.columns([4, 1])
    with col1:
        single_url = st.text_input(
            "URL", placeholder="https://the-internet.herokuapp.com/login",
            label_visibility="collapsed"
        )
    with col2:
        scrape_btn = st.button("🔍 Scrape", key="scrape_single", use_container_width=True)

    if scrape_btn:
        if not single_url:
            st.error("Enter a URL first.")
        else:
            with st.spinner("Scraping..."):
                result = scrape_url(single_url)
            if result["success"]:
                d = result["data"]
                st.session_state.scraped_results[d["url"]] = d
                st.success(f"✅ **{d['title']}** · HTTP {d['status_code']}")
            else:
                st.error(f"❌ {result['error']}")

    if st.session_state.scraped_results:
        urls     = list(st.session_state.scraped_results.keys())
        sel_url  = st.selectbox("Active site", urls, label_visibility="collapsed") if len(urls) > 1 else urls[0]
        d        = st.session_state.scraped_results[sel_url]

        render_metrics(d)

        # Areas
        st.markdown('<div style="font-family:var(--mono);font-size:.62rem;text-transform:uppercase;letter-spacing:.12em;color:#4a5568;margin-bottom:.4rem;">Detected Test Areas</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<span class="area-tag">{a}</span>' for a in d["areas"]), unsafe_allow_html=True)

        with st.expander("🔎 Scraped Data Preview"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Forms:** {len(d['forms'])}\n\n**Inputs:** {len(d['inputs'])}\n\n**Buttons:** {d['buttons'][:8]}\n\n**Dropdowns:** {[s['name'] for s in d['selects'][:5]]}")
            with c2:
                st.markdown(f"**Headings:** {d['headings'][:5]}\n\n**Errors on page:** {d['error_messages'][:3]}\n\n**Tables:** {[t['headers'] for t in d['tables'][:3]]}")

        st.markdown("---")
        st.markdown("### Step 2 — Generate Test Cases")

        ca, cb = st.columns([3, 1])
        with ca:
            area_choices = d["areas"] + ["General", "Custom"]
            chosen_area  = st.selectbox("Test Area", area_choices)
            if chosen_area == "Custom":
                chosen_area = st.text_input("Custom area", placeholder="e.g. Audio Playback")
        with cb:
            st.markdown("<br>", unsafe_allow_html=True)
            gen_btn = st.button("⚡ Generate", key="gen_single", use_container_width=True)

        if gen_btn:
            # Validation
            if not tc_types:
                st.error("Select at least one test type in the sidebar.")
            elif provider in ["Groq", "Both (merge)"] and not groq_key:
                st.error("Add your Groq API key in the sidebar.")
            elif provider in ["Hugging Face", "Both (merge)"] and not hf_key:
                st.error("Add your HuggingFace API token in the sidebar.")
            else:
                with st.spinner(f"Generating {tc_count} test cases via {provider}..."):
                    result = generate_test_cases(
                        d, chosen_area, tc_count, tc_types,
                        provider, groq_key, groq_model, hf_key, hf_model
                    )
                if result["success"]:
                    new_tcs = result["test_cases"]
                    for tc in new_tcs:
                        tc["source_url"] = d["url"]
                    st.session_state.all_test_cases.extend(new_tcs)
                    st.success(f"✅ {len(new_tcs)} test cases via **{result['model']}** → see **Test Cases** tab")
                else:
                    st.error(f"❌ {result['error']}")
    else:
        st.markdown("""
<div style="text-align:center;padding:3rem;color:#1c2333;">
  <div style="font-size:3rem;margin-bottom:1rem;">🕷</div>
  <div style="color:#2d3748;font-size:.95rem;">Enter a URL above and click Scrape</div>
  <div style="color:#1c2333;font-size:.8rem;margin-top:.4rem;">
    Try: https://the-internet.herokuapp.com · https://demoqa.com · https://reqres.in
  </div>
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — BATCH
# ────────────────────────────────────────────────────────────────────────────
with tab_batch:
    st.markdown("### Batch URL Testing")
    st.caption("Paste multiple URLs (one per line). Each will be scraped and test cases generated.")

    batch_input = st.text_area(
        "URLs",
        placeholder="https://example.com\nhttps://demoqa.com\nhttps://the-internet.herokuapp.com",
        height=130,
        label_visibility="collapsed"
    )

    bc1, bc2, bc3 = st.columns([2, 2, 1])
    with bc1:
        batch_area = st.text_input("Test area for all URLs", value="Forms & Input")
    with bc2:
        batch_delay = st.slider("Delay between requests (sec)", 0.5, 3.0, 1.0, step=0.5)
    with bc3:
        st.markdown("<br>", unsafe_allow_html=True)
        batch_btn = st.button("🚀 Run Batch", key="run_batch", use_container_width=True)

    if batch_btn:
        urls = [u.strip() for u in batch_input.strip().splitlines() if u.strip()]
        errors = []
        if not urls:
            errors.append("Enter at least one URL.")
        if not tc_types:
            errors.append("Select test types in the sidebar.")
        if provider in ["Groq", "Both (merge)"] and not groq_key:
            errors.append("Add Groq API key in sidebar.")
        if provider in ["Hugging Face", "Both (merge)"] and not hf_key:
            errors.append("Add HuggingFace token in sidebar.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            progress  = st.progress(0)
            status    = st.empty()
            total     = len(urls)
            batch_log = []

            for i, url in enumerate(urls):
                progress.progress(int(i / total * 100))
                status.info(f"[{i+1}/{total}] Scraping: `{url}`")

                s = scrape_url(url)
                entry = {"url": url, "count": 0, "ok": False, "error": ""}

                if s["success"]:
                    d = s["data"]
                    st.session_state.scraped_results[d["url"]] = d
                    status.info(f"[{i+1}/{total}] Generating TCs: `{url}`")
                    g = generate_test_cases(
                        d, batch_area, tc_count, tc_types,
                        provider, groq_key, groq_model, hf_key, hf_model
                    )
                    if g["success"]:
                        for tc in g["test_cases"]:
                            tc["source_url"] = d["url"]
                        st.session_state.all_test_cases.extend(g["test_cases"])
                        entry["count"] = len(g["test_cases"])
                        entry["ok"]    = True
                    else:
                        entry["error"] = g["error"]
                else:
                    entry["error"] = s["error"]

                batch_log.append(entry)
                time.sleep(batch_delay)

            progress.progress(100)
            status.empty()

            st.markdown("#### Results")
            for e in batch_log:
                color = "#10b981" if e["ok"] else "#ef4444"
                icon  = "✅" if e["ok"] else "❌"
                err   = f' — {e["error"]}' if e["error"] else ""
                st.markdown(f"""
<div class="url-row">
  <span style="color:{color};font-weight:700;">{icon}</span>
  <span class="url-title">{e['url']}</span>
  <span class="url-meta">{e['count']} TCs{err}</span>
</div>
""", unsafe_allow_html=True)

            total_gen = sum(e["count"] for e in batch_log)
            st.success(f"✅ Done — {total_gen} test cases generated → see **Test Cases** tab")


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — TEST CASES
# ────────────────────────────────────────────────────────────────────────────
with tab_results:
    tcs = st.session_state.all_test_cases

    if not tcs:
        st.markdown("""
<div style="text-align:center;padding:3rem;color:#1c2333;">
  <div style="font-size:3rem;margin-bottom:1rem;">🧪</div>
  <div style="color:#2d3748;">No test cases yet. Use Single URL or Batch tab to generate.</div>
</div>
""", unsafe_allow_html=True)
    else:
        type_counts = {}
        pri_counts  = {}
        url_counts  = {}
        for tc in tcs:
            type_counts[tc.get("type","?")] = type_counts.get(tc.get("type","?"), 0) + 1
            pri_counts[tc.get("priority","?")] = pri_counts.get(tc.get("priority","?"), 0) + 1
            url_counts[tc.get("source_url","?")] = url_counts.get(tc.get("source_url","?"), 0) + 1

        st.markdown(f"""
<div class="kpi-row">
  <div class="kpi"><div class="kpi-val">{len(tcs)}</div><div class="kpi-lbl">Total TCs</div></div>
  <div class="kpi"><div class="kpi-val">{len(url_counts)}</div><div class="kpi-lbl">URLs Tested</div></div>
  <div class="kpi"><div class="kpi-val">{type_counts.get('Negative',0)}</div><div class="kpi-lbl">Negative</div></div>
  <div class="kpi"><div class="kpi-val">{type_counts.get('Security',0)}</div><div class="kpi-lbl">Security</div></div>
  <div class="kpi"><div class="kpi-val">{pri_counts.get('High',0)}</div><div class="kpi-lbl">High Priority</div></div>
</div>
""", unsafe_allow_html=True)

        f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
        with f1:
            f_type = st.selectbox("Type", ["All"] + list(type_counts.keys()))
        with f2:
            f_pri  = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
        with f3:
            f_url  = st.selectbox("URL", ["All"] + list(url_counts.keys()))
        with f4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑 Clear", use_container_width=True):
                st.session_state.all_test_cases = []
                st.rerun()

        filtered = [
            tc for tc in tcs
            if (f_type == "All" or tc.get("type") == f_type)
            and (f_pri  == "All" or tc.get("priority") == f_pri)
            and (f_url  == "All" or tc.get("source_url") == f_url)
        ]

        st.markdown(f'<div style="font-family:var(--mono);font-size:.72rem;color:#4a5568;margin:.5rem 0;">Showing {len(filtered)} of {len(tcs)}</div>', unsafe_allow_html=True)

        for i, tc in enumerate(filtered):
            render_tc(tc, i)


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — EXPORT
# ────────────────────────────────────────────────────────────────────────────
with tab_export:
    tcs = st.session_state.all_test_cases
    if not tcs:
        st.info("Generate test cases first — then export here.")
    else:
        st.markdown(f"### Export {len(tcs)} Test Cases")
        ts = datetime.now().strftime("%Y%m%d_%H%M")

        e1, e2, e3 = st.columns(3)
        with e1:
            st.markdown("#### 📊 CSV")
            st.caption("JIRA · TestRail · Excel import")
            st.download_button("⬇ Download CSV", export_csv(tcs),
                               file_name=f"test_cases_{ts}.csv", mime="text/csv", use_container_width=True)
        with e2:
            st.markdown("#### 📋 JSON")
            st.caption("API integration · custom tooling")
            st.download_button("⬇ Download JSON", json.dumps(tcs, indent=2),
                               file_name=f"test_cases_{ts}.json", mime="application/json", use_container_width=True)
        with e3:
            st.markdown("#### 📝 Markdown")
            st.caption("Confluence · GitHub · Docs")
            st.download_button("⬇ Download MD", export_markdown(tcs),
                               file_name=f"test_cases_{ts}.md", mime="text/markdown", use_container_width=True)

        st.markdown("---")
        st.markdown("#### 👁 JSON Preview (first 2 records)")
        st.code(json.dumps(tcs[:2], indent=2), language="json")
