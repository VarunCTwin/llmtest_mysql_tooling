# LLM Test Tool (MySQL) — Starter

This is a **VS Code–ready** starter that converts **release notes → test cases → SQL execution → evaluation → report**.

## Quickstart

1. **Open in VS Code** (recommended)
   - Extract this project and open the folder in VS Code.

2. **Python env**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure .env**
   - Copy `.env.example` → `.env` and fill in values (MySQL + optional OpenAI key).

4. **Run the demo (Integrated Terminal or Run/Debug ▶)**  
   ```bash
   python -m llmtest.cli data/release_notes_demo.md
   ```

5. **See output**
   - `reports/report.md`
   - `reports/results.json`

## Notes
- The tool is modular:
  - **parser**: splits notes into actionable lines
  - **generator**: uses LLM (or simple heuristic) to produce test cases
  - **runner**: executes SQL in MySQL
  - **evaluator**: checks results against expectations
  - **reporter**: writes markdown + json report
- You can disable LLM generation (and use the heuristic generator) by setting `USE_LLM=false` in `.env`.

