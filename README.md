# 🩻 Arfin Parween — AI in Medical Imaging (Streamlit Demo)

A branded Streamlit application that demonstrates **AI-assisted structured reporting** for medical images (X-ray / CT / MRI / Ultrasound, etc.).
Designed for **presentations and demos** with a reliable **Demo Mode** fallback, optional web context, and **PDF export** of the generated report.

> **Disclaimer:** This project is for **educational/demo purposes only** and is **not medical advice**. It must not be used for real clinical diagnosis or treatment decisions.

---

## ✨ Features

* ✅ **Upload medical images** (jpg / png / bmp)
* ✅ **AI-generated structured report** (radiology-style format)
* ✅ **Patient-friendly summary** section included
* ✅ **Demo Mode (offline fallback)** to avoid quota/network failures during presentations
* ✅ Optional **web context** via DuckDuckGo (for learning references)
* ✅ **Export report** as:

  * Markdown (`.md`)
  * PDF (`.pdf`)
* ✅ **Branding ready**: logo/photo + “About Arfin” card + demo script tab
* ✅ **History tab** to view recent reports in the session

---

## 🧰 Tech Stack

* **Streamlit** — UI framework
* **Gemini API (Google)** — LLM inference
* **Agno** — agent framework to orchestrate model + tools
* **Pillow** — image handling & resizing
* **ReportLab** — PDF generation
* **DDGS / DuckDuckGo** — optional web references

---

## 📂 Project Structure

```
.
├── AI_in_medical_imaging.py   # Main Streamlit app
├── requirements.txt          # Dependencies
├── logo.png                  # (Optional) Place your logo here
└── README.md
```

---

## ✅ Setup (Local)

### 1) Clone repo

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2) Create & activate virtual environment (recommended)

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Mac/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Set your API key

**Windows (PowerShell – current terminal session)**

```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

**Mac/Linux**

```bash
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```



### 5) Run the app

```bash
streamlit run arfin_medimaging_app.py
```

Open:

* [http://localhost:8501](http://localhost:8501)

---

## 🚀 Deploy Free on Streamlit Community Cloud

1. Push your code to a **GitHub repo** (public recommended for free hosting).
2. Go to Streamlit Community Cloud and click **New app**.
3. Select your repo + branch.
4. Main file path:
   `AI_in_medical_imaging.py`

### Add Secrets (important)

In Streamlit Cloud:

* App → **Settings** → **Secrets**
  Paste:

```toml
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
```

Deploy. ✅

---

## 🧪 Demo Mode (Recommended for Presentations)

This app includes **Demo Mode** in the sidebar:

* ✅ Generates a **pre-made report** with no API calls
* ✅ Perfect when network/quota is unstable
* ✅ Lets you demonstrate UI + workflow reliably

For live demo:

* Start with **Demo Mode ON**
* Switch **OFF** for one real run (if quota allows)

---

## 🖼️ Add Your Branding

### Option A — Auto-load logo

Put a `logo.png` file in the project root:

```
logo.png
```

### Option B — Upload logo at runtime

Use the sidebar logo uploader in the app.

---

## 📌 Notes & Best Practices

* Remove all patient identifiers from images (Name / ID / Hospital stamps).
* AI output is probabilistic and can be wrong — use it only for education.
* If you enable web context, responses may take longer and can hit rate limits.

---

## 🩺 Medical Disclaimer

This application is intended for **education and demonstration only**.
It is **not** a medical device and is **not** approved for clinical use.
Always consult qualified medical professionals for diagnosis and treatment.

---

## 👤 Author

**Arfin Parween**
AI / Backend / Data Engineering • Public Speaker • Demo Builder
Topic: **AI in Medical Imaging**

---

## 📄 License

Choose one:

* MIT (recommended for open-source demos)
* Or keep it private if you don’t want reuse

---

If you want, I can also generate:

* an **MIT LICENSE** file,
* a short **project poster text** for your demo slide,
* and a “How to use” section with screenshots placeholders.
