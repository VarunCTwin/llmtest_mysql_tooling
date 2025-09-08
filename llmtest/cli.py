import argparse, json, os
from .parser.release_parser import parse_release_notes
from .generator.test_generator import generate_tests
from .runner.sql_runner import run_sql_query, run_sql_query_multi_db
from .evaluator.evaluator import evaluate
from .reporter.reporter import write_reports
from .config import MYSQL
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

def main():
    ap = argparse.ArgumentParser(description="Release-notes-driven LLM testing tool (MySQL)")
    ap.add_argument("release_file", help="Path to release notes file (md/txt)")
    ap.add_argument("--database", "-d", help="Specific database to test (default: all configured databases)")
    ap.add_argument("--list-databases", action="store_true", help="List all configured databases")
    ap.add_argument("-env", "--environment", choices=['local', 'remote'], help="Environment configuration to use")
    args = ap.parse_args()
    
    console = Console()
    
    # Handle environment configuration
    if args.environment:
        env_file = f'.env.{args.environment}'
        if os.path.exists(env_file):
            os.environ['LLMTEST_ENV_FILE'] = env_file
            console.print(f"[green]Using environment: {args.environment} ({env_file})[/green]")
        else:
            console.print(f"[red]Environment file not found: {env_file}[/red]")
            return
    
    if args.list_databases:
        console.print(f"[bold]Configured databases:[/bold] {', '.join(MYSQL.databases) if MYSQL.databases else 'None'}")
        return

    # Read and parse release notes
    with open(args.release_file, encoding="utf-8") as f:
        content = f.read()
        notes = parse_release_notes(content)
        
    # Extract original features from markdown for display
    original_features = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('- '):
            original_features.append(line[2:].strip())
    
    # Display comprehensive header
    console.print("\n" + "="*80, style="bold blue")
    console.print("📊 COMPREHENSIVE LLM TEST RESULTS & VALIDATION", style="bold blue", justify="center")
    console.print("="*80 + "\n", style="bold blue")
    
    # Display original instructions
    console.print(Panel.fit(
        "\n".join([f"• {feature}" for feature in original_features]),
        title="📋 Original Instructions from Release Notes",
        border_style="green"
    ))

    console.print(f"\n[bold]Parsed {len(notes)} note(s). Generating tests...[/bold]")
    tests = generate_tests(notes)

    # Determine target databases
    target_databases = [args.database] if args.database else MYSQL.databases
    if not target_databases:
        console.print("[red]No databases configured. Please set MYSQL_DATABASE in .env[/red]")
        return
    
    console.print(f"[bold]Testing against databases:[/bold] {', '.join(target_databases)}")
    console.print("\n🔍 Executing Generated Tests:\n", style="bold cyan")
    
    results = []
    test_counter = 1
    
    for t in tests:
        runner = t.get("runner", "manual")
        expectation = t.get("expectation", "(no expectation)")
        feature = t.get("feature", "(no feature)")
        query = t.get("query", "")
        
        if runner == "sql" and query and query.strip().lower().startswith("select"):
            # Run against all target databases
            for db in target_databases:
                try:
                    rows = run_sql_query(query, db)
                    eval_res = evaluate(t, rows)
                    
                    # Display comprehensive result
                    display_test_result(console, test_counter, {
                        "instruction": f"{feature} (Database: {db})",
                        "expectation": expectation,
                        "query": query.strip(),
                        "results": rows,
                        "status": "PASSED" if eval_res["passed"] else "FAILED",
                        "is_bug": not eval_res["passed"] and "error" not in eval_res["message"].lower(),
                        "validation_message": eval_res["message"]
                    })
                    
                    res = {
                        "feature": f"{feature} ({db})", 
                        "expectation": expectation, 
                        "passed": eval_res["passed"], 
                        "message": eval_res["message"], 
                        "runner": runner,
                        "database": db
                    }
                    results.append(res)
                    test_counter += 1
                    
                except Exception as e:
                    # Display error result
                    display_test_result(console, test_counter, {
                        "instruction": f"{feature} (Database: {db})",
                        "expectation": expectation,
                        "query": query.strip(),
                        "results": [],
                        "status": "FAILED",
                        "is_bug": True,
                        "validation_message": f"Execution error: {str(e)}"
                    })
                    
                    res = {
                        "feature": f"{feature} ({db})", 
                        "expectation": expectation, 
                        "passed": False, 
                        "message": f"Execution error: {e}", 
                        "runner": runner,
                        "database": db
                    }
                    results.append(res)
                    test_counter += 1
        else:
            # Display skipped result
            display_test_result(console, test_counter, {
                "instruction": feature,
                "expectation": expectation,
                "query": query or "N/A - Non-SQL test",
                "results": [],
                "status": "SKIPPED",
                "is_bug": False,
                "validation_message": "Non-SQL or unsupported step; implement API/UI runner."
            })
            
            res = {"feature": feature, "expectation": expectation, "passed": False, "message": "Non-SQL or unsupported step; implement API/UI runner.", "runner": runner, "database": "N/A"}
            results.append(res)
            test_counter += 1

    # Display summary
    display_cli_summary(console, results)
    
    write_reports(results)
    console.print("\n[green]Reports written to ./reports[/green]")

def display_test_result(console, test_num, result_data):
    """Display a single test result with comprehensive formatting."""
    status_style = {
        'PASSED': 'green',
        'FAILED': 'red', 
        'WARNING': 'yellow',
        'SKIPPED': 'blue'
    }.get(result_data['status'], 'blue')
    
    status_icon = {
        'PASSED': '✅',
        'FAILED': '❌',
        'WARNING': '⚠️',
        'SKIPPED': '⏭️'
    }.get(result_data['status'], '❓')
    
    bug_indicator = " 🐛 BUG DETECTED" if result_data['is_bug'] else ""
    
    # Create panel content
    panel_content = []
    panel_content.append(f"[bold]Expected:[/bold] {result_data['expectation']}")
    panel_content.append(f"[bold]Query:[/bold] {result_data['query']}")
    panel_content.append("")
    
    if result_data['results']:
        panel_content.append("[bold]Results:[/bold]")
        if isinstance(result_data['results'], list) and result_data['results']:
            table = Table(show_header=True, header_style="bold magenta")
            
            if isinstance(result_data['results'][0], (list, tuple)):
                for i, col in enumerate(result_data['results'][0]):
                    table.add_column(f"Column {i+1}")
                for row in result_data['results'][:10]:
                    table.add_row(*[str(cell) for cell in row])
            else:
                table.add_column("Result")
                for row in result_data['results'][:10]:
                    table.add_row(str(row))
            
            console.print(table)
            
            if len(result_data['results']) > 10:
                panel_content.append(f"... and {len(result_data['results']) - 10} more rows")
    else:
        panel_content.append("[dim]No results returned[/dim]")
    
    panel_content.append("")
    panel_content.append(f"[bold]Validation:[/bold] {result_data['validation_message']}")
    
    console.print(Panel(
        "\n".join(panel_content),
        title=f"Test {test_num}: {result_data['instruction']} {status_icon}{bug_indicator}",
        border_style=status_style,
        title_align="left"
    ))
    console.print("")

def display_cli_summary(console, results):
    """Display execution summary for CLI."""
    total_tests = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = sum(1 for r in results if not r['passed'] and 'error' in r['message'].lower())
    skipped = sum(1 for r in results if 'skipped' in r['message'].lower() or 'non-sql' in r['message'].lower())
    bugs_detected = sum(1 for r in results if not r['passed'] and 'error' not in r['message'].lower() and 'skipped' not in r['message'].lower())
    
    summary_table = Table(title="📈 Test Execution Summary", show_header=True, header_style="bold blue")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Count", justify="right")
    summary_table.add_column("Status", justify="center")
    
    summary_table.add_row("Total Tests", str(total_tests), "ℹ️")
    summary_table.add_row("Passed", str(passed), "✅" if passed > 0 else "➖")
    summary_table.add_row("Failed", str(failed), "❌" if failed > 0 else "✅")
    summary_table.add_row("Skipped", str(skipped), "⏭️" if skipped > 0 else "✅")
    summary_table.add_row("Bugs Detected", str(bugs_detected), "🐛" if bugs_detected > 0 else "✅")
    
    console.print("\n")
    console.print(summary_table)
    
    if bugs_detected > 0 or failed > 0:
        overall_status = "❌ ISSUES DETECTED"
        status_style = "red"
    elif skipped > 0:
        overall_status = "⚠️ SOME TESTS SKIPPED"
        status_style = "yellow"
    else:
        overall_status = "✅ ALL TESTS PASSED"
        status_style = "green"
    
    console.print(f"\n[{status_style}][bold]Overall Status: {overall_status}[/bold][/{status_style}]")
    console.print(f"\n[dim]Execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

if __name__ == "__main__":
    main()
