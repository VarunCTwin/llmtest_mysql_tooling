from typing import List, Dict, Any
import json
from ..config import LLM
from rich import print

PROMPT_TMPL = """You are a QA assistant. Convert each release note into a structured test case.
For SQL-related notes, generate a MySQL query.
For workflow notes, describe the action and expectation.
Return strict JSON list where each item has:
  - feature: short name
  - query: a SQL string OR an empty string if not SQL
  - expectation: textual expectation (e.g., 'should not appear', 'only include')
  - runner: 'sql' or 'manual'

Example output:
[{{"feature":"activationDate filter","query":"SELECT * FROM clients WHERE activationDate >= '2025-01-01';","expectation":"Only include clients with activationDate >= 2025-01-01","runner":"sql"}}]

Release notes:
{notes}
"""

def _heuristic_generate(notes: List[str]) -> List[Dict[str, Any]]:
    """Fallback simple generator (no LLM)."""
    tests = []
    for n in notes:
        low = n.lower()
        item = {"feature": n[:60], "query": "", "expectation": "", "runner": "manual"}
        if "activationdate" in low or "activation date" in low:
            item["feature"] = "activationDate filter"
            item["query"] = "SELECT id, activationDate FROM clients WHERE activationDate >= '2025-01-01';"
            item["expectation"] = "Only include clients with activationDate >= 2025-01-01"
            item["runner"] = "sql"
        elif "disenrollment" in low:
            item["feature"] = "pending disenrollment visibility"
            item["query"] = "SELECT id FROM members WHERE status != 'PENDING_DISENROLLMENT';"
            item["expectation"] = "Only active members should appear in search results"
            item["runner"] = "sql"
        elif "authentication" in low or "login" in low or "password" in low:
            item["feature"] = "user authentication"
            item["query"] = "SELECT id, username FROM users WHERE status = 'ACTIVE' AND last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY);"
            item["expectation"] = "Only recently active users should be able to authenticate"
            item["runner"] = "sql"
        elif "performance" in low and "search" in low:
            item["feature"] = "search performance optimization"
            item["query"] = "SELECT COUNT(*) as total_records FROM search_index WHERE indexed_at >= CURDATE();"
            item["expectation"] = "Search index should be updated daily"
            item["runner"] = "sql"
        else:
            item["expectation"] = "Produce correct behavior per release note"
        tests.append(item)
    return tests

def generate_tests(notes: List[str]) -> List[Dict[str, Any]]:
    if not LLM.use_llm:
        return _heuristic_generate(notes)

    # Use OpenAI if configured
    try:
        from openai import OpenAI
        if not LLM.openai_api_key:
            print("[yellow]OPENAI_API_KEY not set — falling back to heuristic generator[/yellow]")
            return _heuristic_generate(notes)
        client = OpenAI(api_key=LLM.openai_api_key)
        prompt = PROMPT_TMPL.format(notes='\n'.join(f"- {n}" for n in notes))
        resp = client.chat.completions.create(
            model=LLM.openai_model,
            messages=[
                {"role": "system", "content": "You write strict, valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        content = resp.choices[0].message.content.strip()
        tests = json.loads(content)
        # basic normalization
        norm = []
        for t in tests:
            norm.append({
                "feature": t.get("feature", "Unnamed feature"),
                "query": t.get("query", ""),
                "expectation": t.get("expectation", ""),
                "runner": t.get("runner", "sql" if t.get("query") else "manual"),
            })
        return norm
    except Exception as e:
        print(f"[yellow]LLM generation failed: {e}. Falling back to heuristic.[/yellow]")
        return _heuristic_generate(notes)
