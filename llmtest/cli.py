import argparse, json
from .parser.release_parser import parse_release_notes
from .generator.test_generator import generate_tests
from .runner.sql_runner import run_sql_query, run_sql_query_multi_db
from .evaluator.evaluator import evaluate
from .reporter.reporter import write_reports
from .config import MYSQL
from rich import print

def main():
    ap = argparse.ArgumentParser(description="Release-notes-driven LLM testing tool (MySQL)")
    ap.add_argument("release_file", help="Path to release notes file (md/txt)")
    ap.add_argument("--database", "-d", help="Specific database to test (default: all configured databases)")
    ap.add_argument("--list-databases", action="store_true", help="List all configured databases")
    args = ap.parse_args()
    
    if args.list_databases:
        print(f"[bold]Configured databases:[/bold] {', '.join(MYSQL.databases) if MYSQL.databases else 'None'}")
        return

    with open(args.release_file, encoding="utf-8") as f:
        notes = parse_release_notes(f.read())

    print(f"[bold]Parsed {len(notes)} note(s). Generating tests...[/bold]")
    tests = generate_tests(notes)

    # Determine target databases
    target_databases = [args.database] if args.database else MYSQL.databases
    if not target_databases:
        print("[red]No databases configured. Please set MYSQL_DATABASE in .env[/red]")
        return
    
    print(f"[bold]Testing against databases:[/bold] {', '.join(target_databases)}")
    
    results = []
    for t in tests:
        runner = t.get("runner", "manual")
        expectation = t.get("expectation", "(no expectation)")
        feature = t.get("feature", "(no feature)")
        
        if runner == "sql" and t.get("query") and t["query"].strip().lower().startswith("select"):
            # Run against all target databases
            for db in target_databases:
                try:
                    rows = run_sql_query(t["query"], db)
                    eval_res = evaluate(t, rows)
                    res = {
                        "feature": f"{feature} ({db})", 
                        "expectation": expectation, 
                        "passed": eval_res["passed"], 
                        "message": eval_res["message"], 
                        "runner": runner,
                        "database": db
                    }
                    print(f"• {feature} [{db}]: {'✅' if res['passed'] else '❌'} - {res['message']}")
                    results.append(res)
                except Exception as e:
                    res = {
                        "feature": f"{feature} ({db})", 
                        "expectation": expectation, 
                        "passed": False, 
                        "message": f"Execution error: {e}", 
                        "runner": runner,
                        "database": db
                    }
                    print(f"• {feature} [{db}]: ❌ Execution error: {e}")
                    results.append(res)
        else:
            res = {"feature": feature, "expectation": expectation, "passed": False, "message": "Non-SQL or unsupported step; implement API/UI runner.", "runner": runner, "database": "N/A"}
            print(f"• {feature}: ⚠️ Skipped (non-SQL)")
            results.append(res)

    write_reports(results)
    print("\n[green]Reports written to ./reports[/green]")

if __name__ == "__main__":
    main()
