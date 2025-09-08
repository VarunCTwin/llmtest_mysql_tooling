# LLM Test Tool (MySQL) — Enhanced

This is a **VS Code–ready** tool that converts **release notes → test cases → SQL execution → evaluation → report**. Now includes both remote and local MySQL database support with organized script structure.

## Features

- 🔄 **Dual Database Support**: Connect to remote production databases or local development databases
- 📝 **Release Notes Processing**: Parse markdown release notes and generate SQL test cases
- 🏗️ **Organized Structure**: Scripts organized in dedicated folders for better maintainability
- 🔒 **Security**: Environment files excluded from version control
- 📊 **Comprehensive Reporting**: Generate detailed markdown and JSON reports

## Quickstart

1. **Open in VS Code** (recommended)
   - Extract this project and open the folder in VS Code.

2. **Python env**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Database Connection**
   
   **For Local MySQL:**
   - Use `.env.local` for local development database
   - Example configuration:
     ```
     MYSQL_HOST=localhost
     MYSQL_PORT=3306
     MYSQL_USER=root
     MYSQL_PASSWORD=
     MYSQL_DATABASE=test_db
     ```

   **For Remote MySQL:**
   - Use `.env.remote` for production database (requires VPN/network access)
   - Copy `.env.example` → `.env` and fill in values (MySQL + optional OpenAI key)

4. **Run the Demo**

   **Local MySQL Demo (Recommended):**
   ```bash
   python scripts/run_from_demo_file.py
   ```

   **CLI Tool (for remote databases):**
   ```bash
   python -m llmtest.cli data/release_notes_demo.md
   ```

5. **See output**
   - `reports/report.md`
   - `reports/results.json`

## Project Structure

```
llmtest_mysql_tooling/
├── scripts/                    # Organized scripts
│   └── run_from_demo_file.py  # Local MySQL demo script
├── data/                      # Demo data files
│   └── release_notes_demo.md  # Sample release notes
├── llmtest/                   # Core modules
│   ├── parser/               # Release notes parsing
│   ├── generator/            # Test case generation
│   ├── runner/               # SQL execution
│   ├── evaluator/            # Result evaluation
│   └── reporter/             # Report generation
├── reports/                  # Generated reports (gitignored)
├── .env.local               # Local database config (gitignored)
├── .env.remote              # Remote database config (gitignored)
└── requirements.txt         # Python dependencies
```

## Local MySQL Demo Features

The `scripts/run_from_demo_file.py` script provides:

- 🔍 **Automatic Feature Parsing**: Extracts features from markdown bullet points
- 🏷️ **Smart Categorization**: Automatically categorizes features (Security, Performance, Bug Fix, etc.)
- 📊 **Demo Database**: Creates and populates a demo table with release features
- 📈 **Analytics Queries**: Runs comprehensive analysis on the parsed features
- ✅ **Local Development**: Works with local MySQL without network dependencies

## Architecture Notes

- The tool is modular:
  - **parser**: splits notes into actionable lines
  - **generator**: uses LLM (or simple heuristic) to produce test cases
  - **runner**: executes SQL in MySQL
  - **evaluator**: checks results against expectations
  - **reporter**: writes markdown + json report
- You can disable LLM generation (and use the heuristic generator) by setting `USE_LLM=false` in `.env`
- Environment files are excluded from version control for security
- Reports folder is gitignored to keep repository clean

## Troubleshooting

**Remote Database Connection Issues:**
- Ensure VPN connection is active for production database access
- Check network connectivity and firewall settings
- Use local MySQL demo for development and testing

**Local MySQL Setup:**
- Ensure MySQL server is running locally
- Update `.env.local` with correct credentials
- Create the target database if it doesn't exist

