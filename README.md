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

   **Local MySQL Demo:**
   ```bash
   python scripts/run_from_demo_file.py -env local
   # or simply (local is default):
   python scripts/run_from_demo_file.py
   ```

   **Remote MySQL Demo:**
   ```bash
   python scripts/run_from_demo_file.py -env remote
   ```

   **CLI Tool (alternative method):**
   ```bash
   python -m llmtest.cli data/release_notes_demo.md -env=local
   python -m llmtest.cli data/release_notes_demo.md -env=remote
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

## Enhanced Demo Script Features

The `scripts/run_from_demo_file.py` script now supports **dual environment execution** with the following features:

### Core Functionality
- 🔍 **Automatic Feature Parsing**: Extracts features from markdown bullet points
- 🏷️ **Smart Categorization**: Automatically categorizes features (Security, Performance, Bug Fix, etc.)
- 📊 **Demo Database**: Creates and populates a demo table with release features
- 📈 **Analytics Queries**: Runs comprehensive analysis on the parsed features

### New: Dual Environment Support
- 🌐 **Environment Selection**: Choose between local and remote databases with `-env` parameter
- 🔧 **Dynamic Configuration**: Automatically loads `.env.local` or `.env.remote` based on selection
- 🎯 **Single Entry Point**: One script works with both environments seamlessly
- 📋 **Command Line Interface**: Built-in argument parsing with help documentation

### Usage Examples
```bash
# Local development (default)
python scripts/run_from_demo_file.py
python scripts/run_from_demo_file.py -env local

# Remote production database
python scripts/run_from_demo_file.py -env remote

# Get help
python scripts/run_from_demo_file.py --help
```

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

## Recent Updates (v2.0)

### Dual Environment Support Enhancement
**Date**: September 2025  
**Changes Made**:

1. **Enhanced `run_from_demo_file.py` Script**:
   - Added `argparse` support for command-line argument parsing
   - Implemented `-env`/`--environment` parameter with choices: `local`, `remote`
   - Modified `load_env_config()` function to dynamically load environment files
   - Added environment-specific feedback and logging

2. **Technical Implementation**:
   ```python
   # Before: Fixed to local environment
   config = load_env_config('../.env.local')
   
   # After: Dynamic environment selection
   parser = argparse.ArgumentParser(description='Run release notes demo with MySQL database')
   parser.add_argument('-env', '--environment', choices=['local', 'remote'], default='local')
   config = load_env_config(args.environment)
   ```

3. **Benefits**:
   - Single script handles both local development and remote production databases
   - Maintains backward compatibility (local is default)
   - Clear command-line interface with help documentation
   - Environment-specific configuration loading and validation

4. **Usage**:
   - Local: `python scripts/run_from_demo_file.py` or `python scripts/run_from_demo_file.py -env local`
   - Remote: `python scripts/run_from_demo_file.py -env remote`

## Troubleshooting

**Remote Database Connection Issues:**
- Ensure VPN connection is active for production database access
- Check network connectivity and firewall settings
- Verify `.env.remote` file exists with correct credentials
- Use local MySQL demo for development and testing

**Local MySQL Setup:**
- Ensure MySQL server is running locally
- Update `.env.local` with correct credentials
- Create the target database if it doesn't exist

**Environment Configuration:**
- Ensure `.env.local` and `.env.remote` files are properly configured
- Check that environment files are not tracked in git (they should be gitignored)
- Verify database credentials and network access for remote connections

