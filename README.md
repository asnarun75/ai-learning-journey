Welcome to my AI learning journey. As a senior data and risk analytics leader with 20+ years in enterprise financial systems, I’m now diving deeper into applied AI, GenAI platforms, and LLM-based workflows to lead AI-driven transformations at scale.

## 🚀 Focus Areas
- LLMs for Risk & Compliance
- AI-Augmented Reporting & Decisioning
- Cloud-based AI Deployment
- Prompt Engineering for Enterprise

## 📚 Learning Timeline
- Week 1: AI Foundations – [AI for Everyone], [AI for Business]
- Week 2: OpenAI Tools – GPT API, Prompt Design, Function Calling
- Week 3: Strategy – AI in Finance, Responsible AI Use
- Week 4: Projects – Compliance GPT, RAG Pipeline Demo

## 🛠 Projects
- [x] Compliance Doc Summarizer using OpenAI API
- [ ] GPT-powered Regulatory FAQ Assistant
- [ ] Risk Analytics Chatbot (RAG-based)

Stay tuned as I share updates, demos, and practical AI insights.

## 🧘‍♂️ Daily Substack Draft Automation
This repo now includes a daily content automation pipeline tailored for a wholesome, apolitical blog voice.

### Features
- **Topic rotation:** 30-day pool of non-repeating, wholesome themes aligned with a reflective Indian meditator voice.
- **Safety guardrails:** Blocklist for political/controversial terms plus tone smoothing to avoid "AI-sounding" phrasing.
- **Draft outputs:** Title, subtitle, long-form post, and a short teaser (for Substack Notes/Instagram).
- **Assets:** Prompts for cover, background, and thumbnail images with optional OpenAI image generation.
- **Storage:** Saves drafts to dated Markdown files and (optionally) appends rows to a Google Sheet for review and posting.
- **Scheduling:** `APScheduler` helper to run the generation flow at 7 AM EST (configurable via env vars).

### Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Export credentials:
   - `OPENAI_API_KEY` (required for text + image generation)
   - `GOOGLE_SHEET_ID` and `GOOGLE_SERVICE_ACCOUNT_JSON` (optional, enables Sheet logging)
3. Run a single-day generation:
   ```bash
   python scripts/daily_run.py --date 2024-09-01
   ```
   Use `--skip-images` or `--skip-sheets` to disable specific steps.
   For an offline-friendly end-to-end test (stub content and text-based image placeholders), run:
   ```bash
   python scripts/daily_run.py --date 2024-09-01 --stub --skip-sheets
   ```
   This writes a dated Markdown draft plus image prompt text files without calling external APIs.
4. Schedule daily runs (7 AM EST by default):
   ```bash
   python scripts/schedule_runner.py
   ```
   Or wire `scripts/daily_run.py` into cron/GitHub Actions with your preferred schedule.

### Configuration
- `RUN_HOUR`, `RUN_MINUTE`, `RUN_TIMEZONE`: control scheduler timing (defaults: `7`, `0`, `America/New_York`).
- `TEASER_LENGTH`, `MIN_POST_WORDS`: adjust copy length targets.
- `DATA_DIR`, `ASSET_DIR`: override local storage locations.
