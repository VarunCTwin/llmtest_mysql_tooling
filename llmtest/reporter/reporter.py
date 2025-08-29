from typing import List, Dict, Any
import os, json
from datetime import datetime

def write_reports(results: List[Dict[str, Any]], out_dir: str = "reports") -> None:
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Group results by database
    db_groups = {}
    for r in results:
        db = r.get("database", "default")
        if db not in db_groups:
            db_groups[db] = []
        db_groups[db].append(r)

    # Markdown
    md_path = os.path.join(out_dir, "report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# LLM Test Report\n\nGenerated: {ts}\n\n")
        
        for db, db_results in db_groups.items():
            if db != "N/A":
                f.write(f"## Database: {db}\n\n")
            
            for r in db_results:
                status = "✅" if r["passed"] else "❌"
                feature_name = r['feature'].replace(f" ({db})", "") if db != "N/A" else r['feature']
                f.write(f"{status} **{feature_name}** → {r['expectation']}\n\n")
                f.write(f"- Runner: {r['runner']}\n")
                f.write(f"- Message: {r['message']}\n\n")

    # JSON
    json_path = os.path.join(out_dir, "results.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump({"generated": ts, "results": results, "databases": list(db_groups.keys())}, jf, indent=2)

