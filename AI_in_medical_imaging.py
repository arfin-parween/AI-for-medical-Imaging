import os
import time
import uuid
from datetime import datetime
from io import BytesIO

import streamlit as st
from PIL import Image as PILImage

from agno.agent import Agent
from agno.models.google import Gemini
from agno.media import Image as AgnoImage
from agno.tools.duckduckgo import DuckDuckGoTools

# PDF export
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


# -----------------------------
# Branding
# -----------------------------
APP_TITLE = "Arfin Parween • AI in Medical Imaging"
APP_SUBTITLE = "An app for medical image understanding (educational only)"
BRAND_TAGLINE = "Structured radiology-style notes • explainable • demo-friendly"


st.set_page_config(page_title=APP_TITLE, page_icon="🩻", layout="wide")

st.markdown(
    """
    <style>
      .ap-hero {
        padding: 18px 22px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(14,165,233,0.18), rgba(99,102,241,0.18));
        border: 1px solid rgba(148,163,184,0.35);
      }
      .ap-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(15,23,42,0.08);
        border: 1px solid rgba(148,163,184,0.35);
        font-size: 12px;
      }
      .ap-card {
        padding: 14px 16px;
        border-radius: 14px;
        border: 1px solid rgba(148,163,184,0.35);
        background: rgba(255,255,255,0.02);
      }
      .small-note { color: rgba(100,116,139,1); font-size: 12px; }
      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
    </style>
    """,
    unsafe_allow_html=True
)

DISCLAIMER = """
**Important:** This is an **educational demo** — **not medical advice**.  
It does not replace a licensed radiologist/doctor. Please consult a clinician for diagnosis/treatment.
"""

# -----------------------------
# API Key
# -----------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY environment variable is not set. Set it and re-run.")
    st.stop()
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


# -----------------------------
# Sidebar: Branding + About + Controls
# -----------------------------
st.sidebar.markdown(f"## 🩻 {APP_TITLE}")
st.sidebar.caption(APP_SUBTITLE)
st.sidebar.markdown("---")

# Logo: either upload OR auto-load logo.png if exists
st.sidebar.markdown("### 🖼️ Upload Image")
logo_file = st.sidebar.file_uploader("Upload logo/photo (png/jpg)", type=["png", "jpg", "jpeg"])
auto_logo_path = "logo.png"  # optional: drop a logo.png in same folder

logo_image = None
if logo_file is not None:
    logo_image = PILImage.open(logo_file)
elif os.path.exists(auto_logo_path):
    logo_image = PILImage.open(auto_logo_path)

if logo_image is not None:
    st.sidebar.image(logo_image, use_container_width=True)

st.sidebar.markdown("---")

demo_mode = st.sidebar.toggle("🧪 Demo Mode (no API call)", value=False)
enable_web = st.sidebar.toggle("🌐 Enable web context (DuckDuckGo)", value=False)
model_id = st.sidebar.selectbox(
    "🧠 Gemini model",
    options=[
        "gemini-flash-latest",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash-exp",
    ],
    index=0,
)
max_retries = st.sidebar.slider("🔁 Retry on rate-limit", 0, 5, 3)
resize_width = st.sidebar.slider("🖼️ Resize width", 320, 900, 640, 10)

st.sidebar.markdown("---")

# About Arfin card (MBRDI/ADAS + NVIDIA context)
st.sidebar.markdown("### 👤 About Arfin")
st.sidebar.markdown(
    """
<div class="ap-card">
<b>Arfin Parween</b><br/>
<span class="small-note">Backend & Data Engineer • AI Speaker • Content Creator</span><br/><br/>
<b>Context (for talk):</b><br/>
• Work exposure to automotive/ADAS-style pipelines (data + perception workflows)<br/>
• Cloud-native microservices (FastAPI, Kubernetes), data tooling & observability<br/>
• Interest in GPU-accelerated AI stacks (e.g., NVIDIA ecosystem concepts)<br/><br/>
<span class="small-note">This app focuses on safe, structured AI outputs for medical imaging education.</span>
</div>
""",
    unsafe_allow_html=True
)

st.sidebar.info(DISCLAIMER)


# -----------------------------
# Agent (cached)
# -----------------------------
@st.cache_resource
def get_agent(selected_model: str, use_web: bool) -> Agent:
    tools = [DuckDuckGoTools()] if use_web else []
    return Agent(
        model=Gemini(id=selected_model),
        tools=tools,
        markdown=True
    )


def build_prompt(web_enabled: bool) -> str:
    return f"""
You are an AI assistant for an **educational demo** on **AI in Medical Imaging**.
Be cautious, avoid definitive diagnosis, and use safe language like "may suggest" or "could be consistent with".

Return Markdown with:

## 1) Modality & Anatomy
- Likely modality and view/region
- Image quality/limitations

## 2) Key Visual Observations
- Bullet observations (describe what you see)

## 3) Differential & Next Steps (Educational)
- 2–4 differentials with low/medium/high confidence
- What additional info/imaging helps
- Mention urgent red flags if relevant (without alarmist tone)

## 4) Patient-friendly summary
Explain simply.

## 5) Safety Note
Short disclaimer: not medical advice.

{"## 6) References (web)\nIf web is enabled, include 2–3 brief references/titles.\n" if web_enabled else ""}

---
**Demo Branding:** {APP_TITLE} • {BRAND_TAGLINE}
"""


# -----------------------------
# PDF Export (Markdown -> simple PDF)
# -----------------------------
def markdown_to_text(md: str) -> str:
    # very light cleanup for PDF readability
    lines = []
    for line in md.splitlines():
        line = line.replace("**", "").replace("__", "")
        line = line.replace("### ", "").replace("## ", "").replace("# ", "")
        lines.append(line)
    return "\n".join(lines).strip()


def make_pdf_bytes(title: str, md_report: str) -> bytes:
    text = markdown_to_text(md_report)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, height - 2 * cm, title)

    c.setFont("Helvetica", 10)
    y = height - 3 * cm

    # wrap manually
    max_chars = 110  # simple wrap, good enough for demo
    for raw_line in text.splitlines():
        if not raw_line.strip():
            y -= 10
            continue

        line = raw_line
        while len(line) > max_chars:
            chunk = line[:max_chars]
            c.drawString(2 * cm, y, chunk)
            y -= 12
            line = line[max_chars:]

            if y < 2 * cm:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 2 * cm

        c.drawString(2 * cm, y, line)
        y -= 12

        if y < 2 * cm:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 2 * cm

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# -----------------------------
# Helpers
# -----------------------------
def resize_and_save(image_path: str, target_width: int) -> str:
    img = PILImage.open(image_path)
    w, h = img.size
    aspect = (w / h) if h else 1.0
    new_w = target_width
    new_h = int(new_w / aspect)
    resized = img.resize((new_w, new_h))
    temp_name = f"temp_{uuid.uuid4().hex}.png"
    resized.save(temp_name)
    return temp_name


def run_analysis_with_retry(agent: Agent, prompt: str, agno_image: AgnoImage, retries: int) -> str:
    last_err = None
    for i in range(retries + 1):
        try:
            resp = agent.run(prompt, images=[agno_image])
            return resp.content
        except Exception as e:
            last_err = e
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "RATE_LIMIT" in msg:
                time.sleep(2 ** i)
                continue
            break
    return f"⚠️ Analysis error: {last_err}"


def demo_report_template() -> str:
    return f"""
## 1) Modality & Anatomy
- Likely modality: X-ray (educational guess)
- Region: Chest (projection uncertain)
- Quality: Mild rotation; exposure acceptable for a basic educational interpretation.

## 2) Key Visual Observations
- No obvious large focal consolidation on this preview.
- Cardiomediastinal silhouette appears within expected range (projection-dependent).
- No clear large pleural effusion; subtle findings may require additional views.

## 3) Differential & Next Steps (Educational)
- Low confidence: mild atelectasis vs under-inflation (shallow inspiration).
- Consider additional view (lateral) or repeat if clinically indicated.
- Correlate with symptoms, exam, oxygen saturation, and clinician assessment.

## 4) Patient-friendly summary
At a quick glance, nothing big stands out, but subtle issues can be missed. A doctor uses symptoms + more views/tests to confirm.

## 5) Safety Note
Educational demo only. Not medical advice. Consult a clinician for diagnosis/treatment.

---
**Demo Branding:** {APP_TITLE} • {BRAND_TAGLINE}
"""


# -----------------------------
# Session state
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# -----------------------------
# Main UI
# -----------------------------
# Top hero with logo (if available)
hero_left, hero_right = st.columns([0.18, 0.82], vertical_alignment="center")

with hero_left:
    if logo_image is not None:
        st.image(logo_image, use_container_width=True)
    else:
        st.markdown("<div class='ap-badge'>🩻 Demo</div>", unsafe_allow_html=True)

with hero_right:
    st.markdown(
        f"""
        <div class="ap-hero">
          <div class="ap-badge">AI • Medical Imaging • Streamlit</div>
          <h2 style="margin: 10px 0 6px 0;">{APP_TITLE}</h2>
          <div class="small-note">{APP_SUBTITLE} — {BRAND_TAGLINE}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.caption(DISCLAIMER)

tab1, tab2, tab3 = st.tabs(["🧪 Analyze", "🗂️ History", "🎤 Script"])

with tab1:
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown("### Upload medical image")
        uploaded = st.file_uploader("Upload", type=["jpg", "jpeg", "png", "bmp"], label_visibility="collapsed")

        st.markdown('<div class="ap-card">', unsafe_allow_html=True)
        st.markdown("**Tips:**")
        st.markdown("- Use a **public / non-sensitive** sample image.")
        st.markdown("- Avoid patient identifiers (name/ID/hospital labels).")
        st.markdown("- If quota/network is unstable, enable **Demo Mode**.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("### Run settings")
        st.write(f"**Model:** `{model_id}`")
        st.write(f"**Demo mode:** `{demo_mode}`")
        st.write(f"**Resize width:** `{resize_width}px`")
        st.write(f"**Retries:** `{max_retries}`")

    st.write("")
    if uploaded is not None:
        st.image(uploaded, caption="Uploaded image (preview)", use_container_width=True)

        if st.button("🚀 Generate structured report", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                ext = uploaded.type.split("/")[-1]
                raw_path = f"upload_{uuid.uuid4().hex}.{ext}"
                with open(raw_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                try:
                    if demo_mode:
                        report = demo_report_template()
                    else:
                        agent = get_agent(model_id, enable_web)
                        prompt = build_prompt(enable_web)
                        resized_path = resize_and_save(raw_path, resize_width)
                        try:
                            ag_img = AgnoImage(filepath=resized_path)
                            report = run_analysis_with_retry(agent, prompt, ag_img, max_retries)
                        finally:
                            if os.path.exists(resized_path):
                                os.remove(resized_path)

                    st.session_state.history.insert(
                        0,
                        {
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "model": model_id,
                            "web": enable_web,
                            "demo": demo_mode,
                            "report": report,
                        },
                    )

                    st.success("Report generated ✅")
                    st.markdown("### 📋 Report")
                    st.markdown(report, unsafe_allow_html=True)

                    # Download buttons
                    st.download_button(
                        "⬇️ Download report (.md)",
                        data=report.encode("utf-8"),
                        file_name=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )

                    pdf_bytes = make_pdf_bytes(APP_TITLE, report)
                    st.download_button(
                        "⬇️ Download report (PDF)",
                        data=pdf_bytes,
                        file_name=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                finally:
                    if os.path.exists(raw_path):
                        os.remove(raw_path)
    else:
        st.warning("Upload an image to start.")


with tab2:
    st.markdown("### 🗂️ Analysis history")
    if not st.session_state.history:
        st.info("No reports yet. Generate one from the Analyze tab.")
    else:
        for idx, item in enumerate(st.session_state.history[:10], start=1):
            with st.expander(f"#{idx} • {item['time']} • model={item['model']} • demo={item['demo']}"):
                st.caption(f"web={item['web']}")
                st.markdown(item["report"], unsafe_allow_html=True)

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("🧹 Clear history"):
                st.session_state.history = []
                st.success("History cleared.")
        with c2:
            st.download_button(
                "⬇️ Download all history (.txt)",
                data="\n\n---\n\n".join([h["report"] for h in st.session_state.history]).encode("utf-8"),
                file_name="all_reports.txt",
                use_container_width=True,
            )


with tab3:
    st.markdown("### A script")
    st.markdown(
        """
1) “This is an educational tool—**not diagnosis**—to show how AI can structure imaging observations.”  
2) “We upload an image, preprocess/resize it for consistent inference, then prompt a Gemini model.”  
3) “Output is organized like a mini radiology note: modality/anatomy, key observations, differentials, next steps, and a patient-friendly summary.”  
4) “Optionally we can add learning references via web context.”  
5) “And for reliability, there’s a **Demo Mode** fallback so the demo never fails due to quota/network.”
        """
    )
