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

# ── Optional Selenium ────────────────────────────────────────────────────────
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# ────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QA Intelligence — Test Case Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
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

/* ── HERO ── */
.hero {
  position: relative;
  padding: 2.5rem 3rem;
  margin-bottom: 2rem;
  border-radius: 20px;
  background: linear-gradient(135deg, #07080f 0%, #0a0f1e 60%, #07080f 100%);
  border: 1px solid var(--border2);
  overflow: hidden;
}
.hero::before {
  content:'';
  position:absolute; inset:0;
  background:
    radial-gradient(ellipse 60% 80% at 10% 50%, rgba(0,229,255,0.07) 0%, transparent 70%),
    radial-gradient(ellipse 40% 60% at 85% 20%, rgba(124,58,237,0.09) 0%, transparent 70%);
}
.hero-badge {
  display:inline-block;
  font-family:var(--mono);
  font-size:0.65rem;
  color:var(--accent);
  border:1px solid rgba(0,229,255,0.3);
  border-radius:4px;
  padding:0.2rem 0.6rem;
  margin-bottom:0.8rem;
  letter-spacing:0.12em;
  text-transform:uppercase;
}
.hero-title {
  font-size:2.6rem;
  font-weight:900;
  line-height:1.1;
  margin:0 0 0.5rem;
  color: var(--text);
}
.hero-title span {
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-sub {
  font-family:var(--mono);
  font-size:0.8rem;
  color:var(--muted);
  letter-spacing:0.05em;
}
.hero-pills {
  margin-top:1.2rem;
  display:flex; gap:0.5rem; flex-wrap:wrap;
}
.pill {
  font-size:0.72rem;
  font-family:var(--mono);
  padding:0.25rem 0.7rem;
  border-radius:20px;
  border:1px solid var(--border2);
  color:var(--muted);
}
.pill.on { border-color:var(--accent); color:var(--accent); background:rgba(0,229,255,0.07); }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--surface);
  border-radius: 12px;
  padding: 0.3rem;
  border: 1px solid var(--border);
  gap: 0.2rem;
}
.stTabs [data-baseweb="tab"] {
  background: transparent;
  border-radius: 8px;
  color: var(--muted);
  font-family: var(--sans);
  font-weight: 600;
  font-size: 0.85rem;
  padding: 0.5rem 1.2rem;
  border: none;
}
.stTabs [aria-selected="true"] {
  background: var(--surface2) !important;
  color: var(--accent) !important;
}

/* ── METRIC CARDS ── */
.kpi-row { display:flex; gap:0.8rem; margin:1rem 0; }
.kpi {
  flex:1; background:var(--surface);
  border:1px solid var(--border);
  border-radius:12px;
  padding:1rem 1.2rem;
  position:relative; overflow:hidden;
}
.kpi::after {
  content:'';
  position:absolute; top:0; left:0; right:0; height:2px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.kpi-val {
  font-family:var(--mono);
  font-size:1.9rem;
  font-weight:700;
  color:var(--accent);
  line-height:1;
}
.kpi-lbl {
  font-size:0.68rem;
  text-transform:uppercase;
  letter-spacing:0.12em;
  color:var(--muted);
  margin-top:0.3rem;
}

/* ── URL ROW ── */
.url-row {
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:10px;
  padding:0.8rem 1rem;
  margin-bottom:0.5rem;
  display:flex;
  align-items:center;
  gap:0.8rem;
  font-family:var(--mono);
  font-size:0.78rem;
}
.url-status-ok  { color:var(--green); font-weight:700; }
.url-status-err { color:var(--red);   font-weight:700; }
.url-title { color:var(--text); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.url-meta  { color:var(--muted); font-size:0.7rem; }

/* ── TEST CARD ── */
.tc {
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:12px;
  padding:1.3rem 1.5rem;
  margin-bottom:0.9rem;
  position:relative;
  overflow:hidden;
  transition: border-color 0.2s, transform 0.15s;
}
.tc:hover { border-color:var(--border2); transform:translateX(2px); }
.tc::before {
  content:''; position:absolute;
  left:0; top:0; bottom:0; width:3px;
}
.tc.positive::before { background:var(--green); }
.tc.negative::before { background:var(--red); }
.tc.edge::before     { background:var(--accent3); }
.tc.security::before { background:var(--accent2); }
.tc.performance::before { background:var(--accent); }

.tc-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; }
.tc-id { font-family:var(--mono); font-size:0.65rem; color:var(--muted); }
.tc-title { font-size:1rem; font-weight:700; color:var(--text); margin:0.3rem 0; }
.tc-badges { display:flex; gap:0.4rem; flex-wrap:wrap; margin:0.5rem 0; }

.badge {
  font-size:0.62rem; font-family:var(--mono);
  padding:0.18rem 0.55rem; border-radius:4px;
  font-weight:700; text-transform:uppercase; letter-spacing:0.08em;
}
.b-positive    { background:rgba(16,185,129,.15);  color:#10b981; border:1px solid rgba(16,185,129,.3); }
.b-negative    { background:rgba(239,68,68,.15);   color:#ef4444; border:1px solid rgba(239,68,68,.3); }
.b-edge        { background:rgba(245,158,11,.15);  color:#f59e0b; border:1px solid rgba(245,158,11,.3); }
.b-security    { background:rgba(124,58,237,.15);  color:#a78bfa; border:1px solid rgba(124,58,237,.3); }
.b-performance { background:rgba(0,229,255,.1);    color:#00e5ff; border:1px solid rgba(0,229,255,.3); }
.b-high   { background:rgba(239,68,68,.1);   color:#ef4444; }
.b-medium { background:rgba(245,158,11,.1);  color:#f59e0b; }
.b-low    { background:rgba(16,185,129,.1);  color:#10b981; }

.tc-section { margin-top:0.8rem; }
.tc-section-lbl {
  font-size:0.62rem; font-family:var(--mono);
  text-transform:uppercase; letter-spacing:0.12em;
  color:var(--muted); margin-bottom:0.3rem;
}
.tc-section-val { font-size:0.85rem; color:#94a3b8; line-height:1.6; }
.step-item { padding:0.15rem 0; }
.step-item::before { content:"→ "; color:var(--accent); }

/* ── AREA TAGS ── */
.area-tag {
  display:inline-block;
  background:rgba(0,229,255,0.07);
  color:var(--accent);
  border:1px solid rgba(0,229,255,0.2);
  border-radius:6px;
  padding:0.25rem 0.65rem;
  font-size:0.75rem;
  font-family:var(--mono);
  margin:0.2rem;
}

/* ── SCRAPE MODE TOGGLE ── */
.mode-box {
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:10px;
  padding:0.8rem 1rem;
  font-size:0.82rem;
  color:var(--muted);
  margin-bottom:1rem;
}

/* ── PROGRESS ── */
.prog-bar-wrap {
  background:var(--border);
  border-radius:4px; height:4px;
  margin:0.5rem 0;
  overflow:hidden;
}
.prog-bar-fill {
  height:100%;
  background:linear-gradient(90deg, var(--accent), var(--accent2));
  border-radius:4px;
  transition:width 0.3s;
}

/* ── INPUTS ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div,
.stNumberInput>div>div>input {
  background:var(--surface) !important;
  border:1px solid var(--border2) !important;
  color:var(--text) !important;
  border-radius:8px !important;
  font-family:var(--mono) !important;
  font-size:0.82rem !important;
}
.stTextArea>div>div>textarea { font-size:0.8rem !important; }

/* ── BUTTONS ── */
.stButton>button {
  background:linear-gradient(135deg, #0097a7, #6d28d9) !important;
  color:#fff !important; border:none !important;
  border-radius:8px !important;
  font-family:var(--sans) !important;
  font-weight:700 !important;
  font-size:0.88rem !important;
  padding:0.55rem 1.4rem !important;
  transition:opacity .2s, transform .15s !important;
  width:100%;
}
.stButton>button:hover { opacity:0.88 !important; transform:translateY(-1px) !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background:#080c14 !important;
  border-right:1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stMarkdown { color:var(--muted); font-size:0.82rem; }

/* ── EXPANDER ── */
.streamlit-expanderHeader {
  background:var(--surface) !important;
  border:1px solid var(--border) !important;
  border-radius:8px !important;
  color:var(--muted) !important;
  font-size:0.82rem !important;
}

/* ── RADIO ── */
.stRadio>div { gap:0.5rem; }
.stRadio>div>label {
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:8px;
  padding:0.4rem 0.9rem;
  font-size:0.8rem;
  cursor:pointer;
  color:var(--muted);
}

/* ── SUCCESS / ERROR ── */
.stSuccess { background:rgba(16,185,129,.1) !important; border:1px solid rgba(16,185,129,.3) !important; border-radius:8px !important; }
.stError   { background:rgba(239,68,68,.1)  !important; border:1px solid rgba(239,68,68,.3)  !important; border-radius:8px !important; }
.stWarning { background:rgba(245,158,11,.1) !important; border:1px solid rgba(245,158,11,.3) !important; border-radius:8px !important; }

hr { border-color:var(--border) !important; }

/* ── BATCH TABLE ── */
.batch-header {
  font-family:var(--mono);
  font-size:0.65rem;
  text-transform:uppercase;
  letter-spacing:0.12em;
  color:var(--muted);
  padding:0.5rem 1rem;
  border-bottom:1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SCRAPER ENGINES
# ════════════════════════════════════════════════════════════════════════════

AREA_MAP = {
    "Authentication":  ["login","signin","signup","register","password","logout","auth","forgot","reset","otp","2fa","verify"],
    "Search":          ["search","filter","query","find","sort","results","keyword","autocomplete"],
    "Forms & Input":   ["form","input","submit","field","validate","required","placeholder","dropdown","checkbox","radio"],
    "Navigation":      ["menu","nav","breadcrumb","pagination","sidebar","tab","link","redirect","anchor"],
    "API / Data":      ["api","endpoint","json","fetch","response","payload","request","status","schema"],
    "Media / Audio":   ["audio","video","stream","player","upload","download","bitrate","codec","buffer","playback"],
    "E-commerce":      ["cart","checkout","payment","order","price","discount","coupon","invoice","shipping"],
    "User Profile":    ["profile","account","settings","preference","avatar","subscription","plan"],
    "Security":        ["token","csrf","xss","https","cookie","session","cors","header","injection","sql"],
    "Accessibility":   ["aria","alt","role","label","tabindex","screen","wcag","contrast","keyboard","focus"],
    "Performance":     ["load","speed","cache","cdn","timeout","latency","response time","optimize"],
    "Error Handling":  ["error","404","500","exception","retry","fallback","message","alert","warning"],
}

def _parse_html(soup, url: str, status_code: int) -> dict:
    """Extract all QA-relevant signals from a BeautifulSoup object."""
    for tag in soup(["script","style","noscript"]):
        tag.decompose()

    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    data = {
        "url": url,
        "title": (soup.title.string.strip() if soup.title else "Unknown"),
        "status_code": status_code,
        "forms": [], "inputs": [], "buttons": [],
        "links": [], "headings": [], "images": [],
        "tables": [], "page_text": "", "areas": [],
        "meta": {}, "iframes": [], "selects": [],
        "error_messages": [], "api_hints": []
    }

    # Meta tags
    for m in soup.find_all("meta"):
        name = m.get("name") or m.get("property","")
        if name and m.get("content"):
            data["meta"][name[:40]] = m["content"][:100]

    # Forms
    for form in soup.find_all("form"):
        fd = {
            "action": form.get("action",""),
            "method": form.get("method","GET").upper(),
            "fields": [], "has_file_upload": False
        }
        for inp in form.find_all(["input","select","textarea"]):
            inp_type = inp.get("type", inp.name)
            if inp_type == "file":
                fd["has_file_upload"] = True
            fd["fields"].append({
                "type":        inp_type,
                "name":        inp.get("name",""),
                "id":          inp.get("id",""),
                "placeholder": inp.get("placeholder",""),
                "required":    inp.has_attr("required"),
                "pattern":     inp.get("pattern",""),
                "minlength":   inp.get("minlength",""),
                "maxlength":   inp.get("maxlength",""),
            })
        data["forms"].append(fd)

    # Standalone inputs
    for inp in soup.find_all("input"):
        data["inputs"].append({
            "type": inp.get("type","text"),
            "name": inp.get("name",""),
            "placeholder": inp.get("placeholder","")
        })

    # Selects (dropdowns)
    for sel in soup.find_all("select"):
        options = [o.get_text(strip=True) for o in sel.find_all("option")][:6]
        data["selects"].append({"name": sel.get("name",""), "options": options})

    # Buttons
    for btn in soup.find_all(["button","a"]):
        txt = btn.get_text(strip=True)
        if txt and len(txt) < 60:
            data["buttons"].append(txt)

    # Links
    for a in soup.find_all("a", href=True)[:20]:
        href = urljoin(base, a["href"])
        data["links"].append({"text": a.get_text(strip=True)[:40], "href": href})

    # Headings
    for h in soup.find_all(["h1","h2","h3"]):
        txt = h.get_text(strip=True)
        if txt:
            data["headings"].append(txt[:100])

    # Images
    for img in soup.find_all("img")[:12]:
        data["images"].append({"alt": img.get("alt",""), "src": img.get("src","")[:60]})

    # Tables
    for tbl in soup.find_all("table")[:3]:
        headers = [th.get_text(strip=True) for th in tbl.find_all("th")]
        rows    = len(tbl.find_all("tr"))
        if headers:
            data["tables"].append({"headers": headers, "rows": rows})

    # iFrames
    for fr in soup.find_all("iframe"):
        data["iframes"].append(fr.get("src","")[:80])

    # Page text
    data["page_text"] = " ".join(soup.get_text(separator=" ").split())[:3000]

    # Error/alert messages
    for el in soup.find_all(class_=re.compile(r"error|alert|warning|danger|message", re.I)):
        txt = el.get_text(strip=True)
        if txt and len(txt) < 200:
            data["error_messages"].append(txt)

    # API hints (data-* attributes, rel links)
    for el in soup.find_all(attrs={"data-url": True}):
        data["api_hints"].append(el["data-url"][:80])

    # Detect areas
    text_lower = data["page_text"].lower()
    for area, keywords in AREA_MAP.items():
        if any(kw in text_lower for kw in keywords):
            data["areas"].append(area)

    if not data["areas"]:
        data["areas"] = ["General"]

    return data


def scrape_bs4(url: str) -> dict:
    """BeautifulSoup scraper for standard websites."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        data = _parse_html(soup, url, resp.status_code)
        data["scrape_engine"] = "BeautifulSoup4"
        return {"success": True, "data": data}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out (12s). Site may be slow or blocking scrapers."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect. Check the URL and your internet connection."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.response.status_code} error returned by the server."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def scrape_selenium(url: str) -> dict:
    """Selenium scraper for JavaScript-heavy / SPA websites."""
    if not SELENIUM_AVAILABLE:
        return {"success": False, "error": "Selenium not installed. Run: pip install selenium webdriver-manager"}
    driver = None
    try:
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=opts)
        except Exception:
            driver = webdriver.Chrome(options=opts)

        driver.get(url)

        # Wait for body + JS rendering
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2.5)  # allow dynamic content

        # Scroll to trigger lazy loads
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")

        status_code = 200  # Selenium doesn't expose HTTP status directly
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        data = _parse_html(soup, url, status_code)

        # Extra: grab any XHR/fetch network hints via JS
        try:
            perf = driver.execute_script("""
                return window.performance.getEntriesByType('resource')
                    .filter(r => r.initiatorType === 'fetch' || r.initiatorType === 'xmlhttprequest')
                    .slice(0,10)
                    .map(r => r.name);
            """)
            if perf:
                data["api_hints"].extend([p[:80] for p in perf])
        except Exception:
            pass

        data["scrape_engine"] = "Selenium (headless Chrome)"
        data["js_rendered"] = True
        return {"success": True, "data": data}

    except TimeoutException:
        return {"success": False, "error": "Selenium timed out waiting for page to load."}
    except WebDriverException as e:
        return {"success": False, "error": f"WebDriver error: {str(e)[:200]}. Is Chrome installed?"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def scrape_url(url: str, engine: str) -> dict:
    """Route to correct scraper engine."""
    if not url.startswith("http"):
        url = "https://" + url
    if engine == "Selenium (JS-heavy / SPA)":
        return scrape_selenium(url)
    return scrape_bs4(url)


# ════════════════════════════════════════════════════════════════════════════
# AI ENGINES
# ════════════════════════════════════════════════════════════════════════════

def _build_prompt(scraped: dict, area: str, count: int, tc_types: list) -> str:
    return f"""You are a senior QA engineer with 15 years of experience.
Analyze this scraped website and generate exactly {count} test cases for the area: "{area}".
Focus on these types: {', '.join(tc_types)}.

WEBSITE DATA:
- URL: {scraped['url']}
- Title: {scraped['title']}
- Engine: {scraped.get('scrape_engine','Unknown')}
- Forms: {json.dumps(scraped['forms'][:4], indent=2)}
- Buttons found: {scraped['buttons'][:12]}
- Headings: {scraped['headings'][:8]}
- Dropdowns: {json.dumps(scraped['selects'][:4])}
- Tables: {json.dumps(scraped['tables'][:3])}
- API hints: {scraped['api_hints'][:6]}
- Error messages found on page: {scraped['error_messages'][:4]}
- Page text snippet: {scraped['page_text'][:1200]}

Return ONLY a valid JSON array. No markdown fences, no explanation.
Each object must have EXACTLY these keys:
- "id": "TC-001" format
- "title": concise test case title
- "type": one of {tc_types} (or closest match from Positive/Negative/Edge/Security/Performance)
- "precondition": what must be true before execution
- "steps": array of clear step strings (3-6 steps)
- "expected_result": specific expected outcome
- "actual_result": "Not executed"
- "priority": "High", "Medium", or "Low"
- "area": "{area}"
- "test_data": specific test data values to use (empty string if none)

Be specific to the actual page content. Reference real form fields, buttons, URLs found."""


def call_groq(prompt: str, api_key: str) -> dict:
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role":"user","content": prompt}],
                "temperature": 0.35,
                "max_tokens": 4000
            },
            timeout=40
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        content = re.sub(r"^```(?:json)?\s*","",content)
        content = re.sub(r"\s*```$","",content)
        return {"success": True, "test_cases": json.loads(content), "model": "Groq / LLaMA 3.3-70B"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"AI returned malformed JSON: {e}"}
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 401:
            return {"success": False, "error": "Invalid Groq API key (401). Check your key."}
        return {"success": False, "error": f"Groq API HTTP {code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def call_claude(prompt: str, api_key: str) -> dict:
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 4000,
                "messages": [{"role":"user","content": prompt}]
            },
            timeout=40
        )
        resp.raise_for_status()
        content = resp.json()["content"][0]["text"].strip()
        content = re.sub(r"^```(?:json)?\s*","",content)
        content = re.sub(r"\s*```$","",content)
        return {"success": True, "test_cases": json.loads(content), "model": "Claude Haiku 4.5"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"AI returned malformed JSON: {e}"}
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 401:
            return {"success": False, "error": "Invalid Anthropic API key (401). Check your key."}
        return {"success": False, "error": f"Anthropic API HTTP {code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_test_cases(scraped: dict, area: str, count: int,
                        tc_types: list, model: str,
                        groq_key: str, claude_key: str) -> dict:
    prompt = _build_prompt(scraped, area, count, tc_types)
    if model == "Groq (LLaMA 3.3)":
        return call_groq(prompt, groq_key)
    elif model == "Claude (Haiku 4.5)":
        return call_claude(prompt, claude_key)
    else:  # Both — run parallel, merge
        results = {}
        with ThreadPoolExecutor(max_workers=2) as ex:
            futures = {
                ex.submit(call_groq, prompt, groq_key): "groq",
                ex.submit(call_claude, prompt, claude_key): "claude"
            }
            for f in as_completed(futures):
                results[futures[f]] = f.result()

        merged = []
        idx = 1
        for key in ["groq","claude"]:
            if results[key]["success"]:
                for tc in results[key]["test_cases"]:
                    tc["id"] = f"TC-{idx:03d}"
                    tc["source_model"] = results[key]["model"]
                    merged.append(tc)
                    idx += 1

        if merged:
            return {"success": True, "test_cases": merged, "model": "Both Models (merged)"}
        # Both failed — return first error
        return results["groq"] if not results["groq"]["success"] else results["claude"]


# ════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ════════════════════════════════════════════════════════════════════════════

def render_tc(tc: dict, idx: int):
    tc_type  = tc.get("type","Positive").lower()
    card_cls = tc_type if tc_type in ["positive","negative","edge","security","performance"] else "positive"
    b_cls    = f"b-{card_cls}"
    pri      = tc.get("priority","Medium")
    pri_cls  = f"b-{pri.lower()}"

    steps_html = "".join(
        f'<div class="step-item">{s}</div>'
        for s in tc.get("steps", [])
    )
    source = tc.get("source_model","")
    source_html = f'<span class="badge" style="background:rgba(255,255,255,.05);color:#4a5568;border:1px solid #1c2333;">{source}</span>' if source else ""

    td = tc.get("test_data","")
    td_html = f'<div class="tc-section"><div class="tc-section-lbl">Test Data</div><div class="tc-section-val" style="font-family:var(--mono);font-size:0.78rem;color:#64748b;">{td}</div></div>' if td else ""

    st.markdown(f"""
<div class="tc {card_cls}">
  <div class="tc-header">
    <div>
      <div class="tc-id">{tc.get("id", f"TC-{idx+1:03d}")} · {tc.get("area","")}</div>
      <div class="tc-title">{tc.get("title","Untitled")}</div>
      <div class="tc-badges">
        <span class="badge {b_cls}">{tc.get("type","Positive")}</span>
        <span class="badge {pri_cls}">{pri} Priority</span>
        {source_html}
      </div>
    </div>
  </div>
  <div class="tc-section">
    <div class="tc-section-lbl">Precondition</div>
    <div class="tc-section-val">{tc.get("precondition","N/A")}</div>
  </div>
  <div class="tc-section">
    <div class="tc-section-lbl">Steps</div>
    <div class="tc-section-val">{steps_html}</div>
  </div>
  <div class="tc-section">
    <div class="tc-section-lbl">Expected Result</div>
    <div class="tc-section-val">{tc.get("expected_result","N/A")}</div>
  </div>
  {td_html}
</div>
""", unsafe_allow_html=True)


def scraped_metrics(d: dict):
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


def export_csv(test_cases: list) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID","Title","Type","Priority","Area","Precondition","Steps","Expected Result","Test Data","Source Model"])
    for tc in test_cases:
        writer.writerow([
            tc.get("id",""),
            tc.get("title",""),
            tc.get("type",""),
            tc.get("priority",""),
            tc.get("area",""),
            tc.get("precondition",""),
            " | ".join(tc.get("steps",[])),
            tc.get("expected_result",""),
            tc.get("test_data",""),
            tc.get("source_model",""),
        ])
    return buf.getvalue()


def export_markdown(test_cases: list, url: str) -> str:
    lines = [f"# Test Cases — {url}", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    for tc in test_cases:
        lines += [
            f"## {tc.get('id','')} — {tc.get('title','')}",
            f"**Type:** {tc.get('type','')} | **Priority:** {tc.get('priority','')} | **Area:** {tc.get('area','')}",
            f"**Precondition:** {tc.get('precondition','')}",
            "**Steps:**",
        ]
        for i, s in enumerate(tc.get("steps",[]), 1):
            lines.append(f"{i}. {s}")
        lines += [
            f"**Expected Result:** {tc.get('expected_result','')}",
            f"**Test Data:** {tc.get('test_data','')}",
            "---", ""
        ]
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ════════════════════════════════════════════════════════════════════════════

for key, default in {
    "scraped_results": {},   # url -> scraped data dict
    "all_test_cases":  [],   # flat list of all generated TCs
    "batch_urls":      [],   # list of URLs in batch
    "active_tab":      0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — API KEYS & SETTINGS
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
<div style="font-family:var(--mono);font-size:0.65rem;color:#00e5ff;
            text-transform:uppercase;letter-spacing:0.15em;margin-bottom:1rem;">
⚡ QA Intelligence
</div>
""", unsafe_allow_html=True)

    st.markdown("### 🔑 API Keys")
    groq_key   = st.text_input("Groq API Key",       type="password", placeholder="gsk_...")
    claude_key = st.text_input("Anthropic API Key",  type="password", placeholder="sk-ant-...")

    st.markdown("---")
    st.markdown("### 🤖 AI Model")
    ai_model = st.radio(
        "Select model",
        ["Groq (LLaMA 3.3)", "Claude (Haiku 4.5)", "Both (merge results)"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🕷 Scrape Engine")
    scrape_engine = st.radio(
        "Engine",
        ["BeautifulSoup4 (fast)", "Selenium (JS-heavy / SPA)"],
        label_visibility="collapsed"
    )
    if scrape_engine == "Selenium (JS-heavy / SPA)":
        if not SELENIUM_AVAILABLE:
            st.warning("Selenium not installed.\n```\npip install selenium webdriver-manager\n```")
        else:
            st.success("Selenium ready ✓")

    st.markdown("---")
    st.markdown("### ⚙️ Generation Settings")
    tc_count = st.slider("Test cases per area", 3, 20, 8)
    tc_types = st.multiselect(
        "Include test types",
        ["Positive","Negative","Edge","Security","Performance"],
        default=["Positive","Negative","Edge","Security"]
    )

    st.markdown("---")
    st.markdown("""
<div style="font-size:0.7rem;color:#1c2333;line-height:1.8;">
Model: LLaMA 3.3-70B / Claude Haiku 4.5<br>
Scraper: BS4 + Selenium<br>
Built with Streamlit
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════

se_pill  = "on" if SELENIUM_AVAILABLE else ""
model_label = ai_model.split("(")[0].strip()

st.markdown(f"""
<div class="hero">
  <div class="hero-badge">QA Intelligence v2.0</div>
  <div class="hero-title">AI <span>Test Case</span> Generator</div>
  <div class="hero-sub">
    scrape → analyze → generate · batch · dual-model · export
  </div>
  <div class="hero-pills">
    <span class="pill on">🕷 {scrape_engine.split(' ')[0]}</span>
    <span class="pill on">🤖 {model_label}</span>
    <span class="pill on">📋 {tc_count} TCs / area</span>
    <span class="pill {'on' if SELENIUM_AVAILABLE else ''}">
      {'✅ Selenium' if SELENIUM_AVAILABLE else '⚠ Selenium not installed'}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ════════════════════════════════════════════════════════════════════════════

tab_single, tab_batch, tab_results, tab_export = st.tabs([
    "🔍 Single URL", "📦 Batch URLs", "🧪 Test Cases", "📥 Export"
])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — SINGLE URL
# ────────────────────────────────────────────────────────────────────────────
with tab_single:
    st.markdown("### Step 1 — Scrape a Website")

    col1, col2 = st.columns([4,1])
    with col1:
        single_url = st.text_input("URL", placeholder="https://the-internet.herokuapp.com/login", label_visibility="collapsed")
    with col2:
        scrape_btn = st.button("🔍 Scrape", key="btn_scrape_single", use_container_width=True)

    if scrape_btn:
        if not single_url:
            st.error("Enter a URL.")
        else:
            engine_key = scrape_engine
            with st.spinner(f"Scraping with {scrape_engine.split(' ')[0]}..."):
                result = scrape_url(single_url, engine_key)
            if result["success"]:
                d = result["data"]
                st.session_state.scraped_results[d["url"]] = d
                st.success(f"✅ **{d['title']}** · HTTP {d['status_code']} · Engine: {d['scrape_engine']}")
            else:
                st.error(f"❌ {result['error']}")

    # Show scraped data if available
    if st.session_state.scraped_results:
        url_options = list(st.session_state.scraped_results.keys())
        selected_url = st.selectbox("Scraped site", url_options, label_visibility="collapsed") if len(url_options) > 1 else url_options[0]
        d = st.session_state.scraped_results[selected_url]

        scraped_metrics(d)

        # Areas
        st.markdown('<div style="font-family:var(--mono);font-size:0.62rem;text-transform:uppercase;letter-spacing:.12em;color:#4a5568;margin-bottom:.4rem;">Detected Test Areas</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<span class="area-tag">{a}</span>' for a in d["areas"]), unsafe_allow_html=True)

        with st.expander("🔎 Scraped Data Preview"):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown(f"""
**Forms:** {len(d['forms'])}
**Inputs:** {len(d['inputs'])}
**Buttons:** {d['buttons'][:8]}
**Selects:** {[s['name'] for s in d['selects'][:5]]}
""")
            with col_p2:
                st.markdown(f"""
**Headings:** {d['headings'][:5]}
**API Hints:** {d['api_hints'][:4]}
**Errors on page:** {d['error_messages'][:3]}
**Engine:** {d['scrape_engine']}
""")

        st.markdown("---")
        st.markdown("### Step 2 — Generate Test Cases")

        col_a, col_b = st.columns([3,1])
        with col_a:
            area_choices = d["areas"] + ["General","Custom"]
            chosen_area  = st.selectbox("Test Area", area_choices)
            if chosen_area == "Custom":
                chosen_area = st.text_input("Custom area name", placeholder="e.g. Audio Playback")
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            gen_btn = st.button("⚡ Generate", key="btn_gen_single", use_container_width=True)

        if gen_btn:
            if not tc_types:
                st.error("Select at least one test type in the sidebar.")
            elif ai_model != "Claude (Haiku 4.5)" and not groq_key:
                st.error("Add your Groq API key in the sidebar.")
            elif ai_model == "Claude (Haiku 4.5)" and not claude_key:
                st.error("Add your Anthropic API key in the sidebar.")
            else:
                with st.spinner(f"Generating {tc_count} test cases via {ai_model}..."):
                    result = generate_test_cases(
                        d, chosen_area, tc_count, tc_types,
                        ai_model, groq_key, claude_key
                    )
                if result["success"]:
                    new_tcs = result["test_cases"]
                    # Tag with URL
                    for tc in new_tcs:
                        tc["source_url"] = d["url"]
                    st.session_state.all_test_cases.extend(new_tcs)
                    st.success(f"✅ {len(new_tcs)} test cases generated via **{result['model']}** → see **Test Cases** tab")
                else:
                    st.error(f"❌ {result['error']}")
    else:
        st.markdown("""
<div style="text-align:center;padding:3rem 2rem;color:#1c2333;">
  <div style="font-size:3rem;margin-bottom:1rem;">🕷</div>
  <div style="color:#2d3748;font-size:0.95rem;">Enter a URL above and click Scrape</div>
  <div style="color:#1c2333;font-size:0.8rem;margin-top:.4rem;">
    Try: https://the-internet.herokuapp.com · https://demoqa.com · https://reqres.in
  </div>
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — BATCH
# ────────────────────────────────────────────────────────────────────────────
with tab_batch:
    st.markdown("### Batch URL Testing")
    st.markdown("Paste multiple URLs (one per line). All will be scraped and test cases generated per area.")

    batch_input = st.text_area(
        "URLs",
        placeholder="https://example.com\nhttps://demoqa.com\nhttps://the-internet.herokuapp.com",
        height=140,
        label_visibility="collapsed"
    )

    col_b1, col_b2, col_b3 = st.columns([2,2,1])
    with col_b1:
        batch_area = st.text_input("Test area for all URLs", value="Forms & Input", placeholder="e.g. Authentication")
    with col_b2:
        batch_delay = st.slider("Delay between requests (sec)", 0.5, 3.0, 1.0, step=0.5)
    with col_b3:
        st.markdown("<br>", unsafe_allow_html=True)
        batch_btn = st.button("🚀 Run Batch", key="btn_batch", use_container_width=True)

    if batch_btn:
        urls = [u.strip() for u in batch_input.strip().splitlines() if u.strip()]
        if not urls:
            st.error("Enter at least one URL.")
        elif not tc_types:
            st.error("Select test types in the sidebar.")
        elif ai_model != "Claude (Haiku 4.5)" and not groq_key:
            st.error("Add Groq API key in sidebar.")
        elif ai_model == "Claude (Haiku 4.5)" and not claude_key:
            st.error("Add Anthropic API key in sidebar.")
        else:
            progress_bar = st.progress(0)
            status_box   = st.empty()
            total        = len(urls)
            batch_log    = []

            for i, url in enumerate(urls):
                pct = int((i / total) * 100)
                progress_bar.progress(pct)
                status_box.markdown(f'<div class="mode-box">🔄 [{i+1}/{total}] Scraping: <code>{url}</code></div>', unsafe_allow_html=True)

                # Scrape
                s_result = scrape_url(url, scrape_engine)
                log_entry = {"url": url, "scrape": "✅", "generate": "—", "count": 0, "error": ""}

                if s_result["success"]:
                    d = s_result["data"]
                    st.session_state.scraped_results[d["url"]] = d

                    # Generate
                    status_box.markdown(f'<div class="mode-box">⚡ [{i+1}/{total}] Generating TCs: <code>{url}</code></div>', unsafe_allow_html=True)
                    g_result = generate_test_cases(
                        d, batch_area, tc_count, tc_types,
                        ai_model, groq_key, claude_key
                    )
                    if g_result["success"]:
                        new_tcs = g_result["test_cases"]
                        for tc in new_tcs:
                            tc["source_url"] = d["url"]
                        st.session_state.all_test_cases.extend(new_tcs)
                        log_entry["generate"] = "✅"
                        log_entry["count"]    = len(new_tcs)
                    else:
                        log_entry["generate"] = "❌"
                        log_entry["error"]    = g_result["error"]
                else:
                    log_entry["scrape"] = "❌"
                    log_entry["error"]  = s_result["error"]

                batch_log.append(log_entry)
                time.sleep(batch_delay)

            progress_bar.progress(100)
            status_box.empty()

            st.markdown("#### Batch Results")
            for entry in batch_log:
                color = "#10b981" if entry["scrape"]=="✅" and entry["generate"]=="✅" else "#ef4444"
                err   = f' — {entry["error"]}' if entry["error"] else ""
                st.markdown(f"""
<div class="url-row">
  <span style="color:{color};font-weight:700;">{'✅' if entry['generate']=='✅' else '❌'}</span>
  <span class="url-title">{entry['url']}</span>
  <span class="url-meta">{entry['count']} TCs{err}</span>
</div>
""", unsafe_allow_html=True)
            total_gen = sum(e["count"] for e in batch_log)
            st.success(f"✅ Batch complete — {total_gen} total test cases generated → see **Test Cases** tab")


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — TEST CASES
# ────────────────────────────────────────────────────────────────────────────
with tab_results:
    tcs = st.session_state.all_test_cases

    if not tcs:
        st.markdown("""
<div style="text-align:center;padding:3rem;color:#1c2333;">
  <div style="font-size:3rem;margin-bottom:1rem;">🧪</div>
  <div style="color:#2d3748;">No test cases yet. Scrape a URL and generate.</div>
</div>
""", unsafe_allow_html=True)
    else:
        # Summary KPIs
        type_counts = {}
        pri_counts  = {}
        url_counts  = {}
        for tc in tcs:
            t = tc.get("type","?")
            p = tc.get("priority","?")
            u = tc.get("source_url","?")
            type_counts[t] = type_counts.get(t,0)+1
            pri_counts[p]  = pri_counts.get(p,0)+1
            url_counts[u]  = url_counts.get(u,0)+1

        st.markdown(f"""
<div class="kpi-row">
  <div class="kpi"><div class="kpi-val">{len(tcs)}</div><div class="kpi-lbl">Total TCs</div></div>
  <div class="kpi"><div class="kpi-val">{len(url_counts)}</div><div class="kpi-lbl">URLs</div></div>
  <div class="kpi"><div class="kpi-val">{type_counts.get('Negative',0)}</div><div class="kpi-lbl">Negative</div></div>
  <div class="kpi"><div class="kpi-val">{type_counts.get('Security',0)}</div><div class="kpi-lbl">Security</div></div>
  <div class="kpi"><div class="kpi-val">{pri_counts.get('High',0)}</div><div class="kpi-lbl">High Priority</div></div>
</div>
""", unsafe_allow_html=True)

        # Filters
        col_f1, col_f2, col_f3, col_f4 = st.columns([2,2,2,1])
        with col_f1:
            f_type = st.selectbox("Filter: Type", ["All"] + list(type_counts.keys()))
        with col_f2:
            f_pri  = st.selectbox("Filter: Priority", ["All","High","Medium","Low"])
        with col_f3:
            f_url  = st.selectbox("Filter: URL", ["All"] + list(url_counts.keys()))
        with col_f4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑 Clear All", use_container_width=True):
                st.session_state.all_test_cases = []
                st.rerun()

        # Apply filters
        filtered = tcs
        if f_type != "All":
            filtered = [tc for tc in filtered if tc.get("type")==f_type]
        if f_pri != "All":
            filtered = [tc for tc in filtered if tc.get("priority")==f_pri]
        if f_url != "All":
            filtered = [tc for tc in filtered if tc.get("source_url")==f_url]

        st.markdown(f'<div style="font-family:var(--mono);font-size:0.72rem;color:#4a5568;margin:0.5rem 0;">Showing {len(filtered)} of {len(tcs)} test cases</div>', unsafe_allow_html=True)

        for i, tc in enumerate(filtered):
            render_tc(tc, i)


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — EXPORT
# ────────────────────────────────────────────────────────────────────────────
with tab_export:
    tcs = st.session_state.all_test_cases

    if not tcs:
        st.info("Generate test cases first.")
    else:
        st.markdown(f"### Export {len(tcs)} Test Cases")
        st.markdown("---")

        url_str = list(st.session_state.scraped_results.keys())[0] if st.session_state.scraped_results else "batch"

        col_e1, col_e2, col_e3 = st.columns(3)

        with col_e1:
            st.markdown("#### 📊 CSV")
            st.markdown("Best for JIRA, TestRail, Excel import")
            st.download_button(
                "⬇ Download CSV",
                data=export_csv(tcs),
                file_name=f"test_cases_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_e2:
            st.markdown("#### 📋 JSON")
            st.markdown("Best for API integration or custom tools")
            st.download_button(
                "⬇ Download JSON",
                data=json.dumps(tcs, indent=2),
                file_name=f"test_cases_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )

        with col_e3:
            st.markdown("#### 📝 Markdown")
            st.markdown("Best for documentation, Confluence, GitHub")
            st.download_button(
                "⬇ Download Markdown",
                data=export_markdown(tcs, url_str),
                file_name=f"test_cases_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("#### 👁 Preview (first 3)")
        st.code(json.dumps(tcs[:3], indent=2), language="json")
