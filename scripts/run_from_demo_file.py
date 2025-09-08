#!/usr/bin/env python3
"""
Script to run queries from release_notes_demo.md using local MySQL database.
This script parses the markdown file and generates relevant SQL queries based on the content.
Provides comprehensive results including instructions, queries, results, and validation.
"""

import os
import sys
import argparse
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import re
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

def load_env_config(env_type='local'):
    """Load MySQL configuration from environment file based on environment type."""
    env_file = f'../.env.{env_type}'
    load_dotenv(env_file)
    print(f"Loading configuration from: {env_file}")
    
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'test_db')
    }
    
    return config

def connect_to_mysql(config):
    """Establish connection to MySQL database."""
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print(f"✓ Connected to MySQL database: {config['database']} at {config['host']}:{config['port']}")
            return connection
    except Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        return None

def parse_release_notes(file_path):
    """Parse the release notes markdown file and extract features."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract bullet points (features/changes)
        lines = content.split('\n')
        features = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                feature = line[2:].strip()  # Remove '- ' prefix
                features.append(feature)
        
        return features
    except FileNotFoundError:
        print(f"✗ Release notes file not found: {file_path}")
        return []
    except Exception as e:
        print(f"✗ Error reading release notes: {e}")
        return []

def generate_demo_queries(features):
    """Generate SQL queries based on the release notes features."""
    queries = []
    
    # Create a demo table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS release_features (
        id INT AUTO_INCREMENT PRIMARY KEY,
        feature_description TEXT NOT NULL,
        category VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    queries.append(("Create demo table", create_table_query))
    
    # Clear existing data for fresh demo
    clear_query = "DELETE FROM release_features;"
    queries.append(("Clear existing data", clear_query))
    
    # Insert each feature as a record
    for i, feature in enumerate(features, 1):
        # Categorize features based on keywords
        category = categorize_feature(feature)
        
        insert_query = f"""
        INSERT INTO release_features (feature_description, category) 
        VALUES ('{mysql.connector.conversion.MySQLConverter().escape(feature)}', '{category}');
        """
        queries.append((f"Insert feature {i}", insert_query))
    
    # Demo analysis queries
    analysis_queries = [
        ("Count total features", "SELECT COUNT(*) as total_features FROM release_features;"),
        ("Features by category", "SELECT category, COUNT(*) as count FROM release_features GROUP BY category ORDER BY count DESC;"),
        ("Recent features", "SELECT feature_description, category, created_at FROM release_features ORDER BY created_at DESC;"),
        ("Security-related features", "SELECT feature_description FROM release_features WHERE category = 'Security' OR feature_description LIKE '%security%' OR feature_description LIKE '%authentication%';"),
        ("Performance improvements", "SELECT feature_description FROM release_features WHERE category = 'Performance' OR feature_description LIKE '%performance%' OR feature_description LIKE '%optimization%';")
    ]
    
    queries.extend(analysis_queries)
    return queries

def categorize_feature(feature_text):
    """Categorize a feature based on keywords in the description."""
    feature_lower = feature_text.lower()
    
    if any(keyword in feature_lower for keyword in ['security', 'authentication', 'password', 'login', 'session']):
        return 'Security'
    elif any(keyword in feature_lower for keyword in ['performance', 'optimization', 'speed', 'index', 'cache']):
        return 'Performance'
    elif any(keyword in feature_lower for keyword in ['bug', 'fix', 'issue', 'error']):
        return 'Bug Fix'
    elif any(keyword in feature_lower for keyword in ['add', 'new', 'support', 'feature']):
        return 'New Feature'
    elif any(keyword in feature_lower for keyword in ['improve', 'enhance', 'better', 'update']):
        return 'Enhancement'
    else:
        return 'Other'

def execute_queries_with_validation(connection, queries, features):
    """Execute queries with comprehensive result display and validation."""
    console = Console()
    cursor = connection.cursor()
    
    # Display header
    console.print("\n" + "="*80, style="bold blue")
    console.print("📊 COMPREHENSIVE QUERY RESULTS & VALIDATION", style="bold blue", justify="center")
    console.print("="*80 + "\n", style="bold blue")
    
    # Display original instructions
    console.print(Panel.fit(
        "\n".join([f"• {feature}" for feature in features]),
        title="📋 Original Instructions from Release Notes",
        border_style="green"
    ))
    
    query_results = []
    setup_queries = []
    analysis_queries = []
    
    # Separate setup and analysis queries
    for desc, query in queries:
        if any(keyword in desc.lower() for keyword in ['create', 'clear', 'insert']):
            setup_queries.append((desc, query))
        else:
            analysis_queries.append((desc, query))
    
    # Execute setup queries quietly
    console.print("\n🔧 Setting up demo environment...", style="yellow")
    for description, query in setup_queries:
        try:
            cursor.execute(query)
            if not query.strip().upper().startswith('SELECT'):
                connection.commit()
        except Error as e:
            console.print(f"❌ Setup error in {description}: {e}", style="red")
    
    # Execute and display analysis queries with full details
    console.print("\n🔍 Executing Analysis Queries:\n", style="bold cyan")
    
    for i, (description, query) in enumerate(analysis_queries, 1):
        try:
            # Create result panel
            result_data = {
                'instruction': description,
                'query': query.strip(),
                'results': [],
                'status': 'UNKNOWN',
                'is_bug': False,
                'validation_message': ''
            }
            
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                result_data['results'] = results
                result_data['columns'] = columns
                
                # Validate results and determine status
                validation = validate_query_results(description, results, features)
                result_data['status'] = validation['status']
                result_data['is_bug'] = validation['is_bug']
                result_data['validation_message'] = validation['message']
                
                # Display comprehensive result
                display_query_result(console, i, result_data)
                
            query_results.append(result_data)
                
        except Error as e:
            result_data = {
                'instruction': description,
                'query': query.strip(),
                'results': [],
                'status': 'FAILED',
                'is_bug': True,
                'validation_message': f'Query execution error: {str(e)}'
            }
            display_query_result(console, i, result_data)
            query_results.append(result_data)
    
    cursor.close()
    
    # Display summary
    display_summary(console, query_results)
    
    return query_results

def validate_query_results(description, results, features):
    """Validate query results and determine if there are any issues."""
    validation = {
        'status': 'PASSED',
        'is_bug': False,
        'message': 'Query executed successfully with expected results'
    }
    
    # Check for empty results where we expect data
    if not results:
        if 'count' in description.lower() or 'features' in description.lower():
            validation['status'] = 'WARNING'
            validation['message'] = 'No results returned - this might indicate missing data'
        else:
            validation['status'] = 'PASSED'
            validation['message'] = 'No results found (may be expected)'
        return validation
    
    # Validate specific query types
    if 'count total features' in description.lower():
        total_count = results[0][0] if results else 0
        expected_count = len(features)
        if total_count != expected_count:
            validation['status'] = 'FAILED'
            validation['is_bug'] = True
            validation['message'] = f'Expected {expected_count} features, got {total_count}'
        else:
            validation['message'] = f'Correct count: {total_count} features'
    
    elif 'security' in description.lower():
        security_features = [f for f in features if any(keyword in f.lower() for keyword in ['security', 'authentication', 'password', 'login'])]
        if len(security_features) > 0 and not results:
            validation['status'] = 'FAILED'
            validation['is_bug'] = True
            validation['message'] = 'Expected security features but none found in results'
        elif results:
            validation['message'] = f'Found {len(results)} security-related features'
    
    elif 'performance' in description.lower():
        perf_features = [f for f in features if any(keyword in f.lower() for keyword in ['performance', 'optimization', 'speed', 'index'])]
        if len(perf_features) > 0 and not results:
            validation['status'] = 'FAILED'
            validation['is_bug'] = True
            validation['message'] = 'Expected performance features but none found in results'
        elif results:
            validation['message'] = f'Found {len(results)} performance-related features'
    
    return validation

def display_query_result(console, query_num, result_data):
    """Display a single query result with comprehensive formatting."""
    # Status styling
    status_style = {
        'PASSED': 'green',
        'FAILED': 'red', 
        'WARNING': 'yellow',
        'UNKNOWN': 'blue'
    }[result_data['status']]
    
    # Status icon
    status_icon = {
        'PASSED': '✅',
        'FAILED': '❌',
        'WARNING': '⚠️',
        'UNKNOWN': '❓'
    }[result_data['status']]
    
    bug_indicator = " 🐛 BUG DETECTED" if result_data['is_bug'] else ""
    
    # Create panel content
    panel_content = []
    panel_content.append(f"[bold]Query:[/bold] {result_data['query']}")
    panel_content.append("")
    
    if result_data['results']:
        panel_content.append("[bold]Results:[/bold]")
        if 'columns' in result_data and result_data['columns']:
            # Create table for results
            table = Table(show_header=True, header_style="bold magenta")
            for col in result_data['columns']:
                table.add_column(str(col))
            
            for row in result_data['results'][:10]:  # Limit to first 10 rows
                table.add_row(*[str(cell) for cell in row])
            
            console.print(table)
            
            if len(result_data['results']) > 10:
                panel_content.append(f"... and {len(result_data['results']) - 10} more rows")
        else:
            for row in result_data['results'][:5]:
                panel_content.append(f"  {row}")
    else:
        panel_content.append("[dim]No results returned[/dim]")
    
    panel_content.append("")
    panel_content.append(f"[bold]Validation:[/bold] {result_data['validation_message']}")
    
    # Display panel
    console.print(Panel(
        "\n".join(panel_content),
        title=f"Query {query_num}: {result_data['instruction']} {status_icon}{bug_indicator}",
        border_style=status_style,
        title_align="left"
    ))
    console.print("")

def display_summary(console, query_results):
    """Display execution summary."""
    total_queries = len(query_results)
    passed = sum(1 for r in query_results if r['status'] == 'PASSED')
    failed = sum(1 for r in query_results if r['status'] == 'FAILED')
    warnings = sum(1 for r in query_results if r['status'] == 'WARNING')
    bugs_detected = sum(1 for r in query_results if r['is_bug'])
    
    # Create summary table
    summary_table = Table(title="📈 Execution Summary", show_header=True, header_style="bold blue")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Count", justify="right")
    summary_table.add_column("Status", justify="center")
    
    summary_table.add_row("Total Queries", str(total_queries), "ℹ️")
    summary_table.add_row("Passed", str(passed), "✅" if passed > 0 else "➖")
    summary_table.add_row("Failed", str(failed), "❌" if failed > 0 else "✅")
    summary_table.add_row("Warnings", str(warnings), "⚠️" if warnings > 0 else "✅")
    summary_table.add_row("Bugs Detected", str(bugs_detected), "🐛" if bugs_detected > 0 else "✅")
    
    console.print("\n")
    console.print(summary_table)
    
    # Overall status
    if bugs_detected > 0 or failed > 0:
        overall_status = "❌ ISSUES DETECTED"
        status_style = "red"
    elif warnings > 0:
        overall_status = "⚠️ WARNINGS PRESENT"
        status_style = "yellow"
    else:
        overall_status = "✅ ALL TESTS PASSED"
        status_style = "green"
    
    console.print(f"\n[{status_style}][bold]Overall Status: {overall_status}[/bold][/{status_style}]")
    console.print(f"\n[dim]Execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

def main():
    """Main function to orchestrate the demo."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run release notes demo with MySQL database')
    parser.add_argument('-env', '--environment', 
                       choices=['local', 'remote'], 
                       default='local',
                       help='Environment to use: local or remote (default: local)')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Release Notes Demo with {args.environment.upper()} MySQL")
    print("=" * 50)
    
    # Load configuration
    config = load_env_config(args.environment)
    print(f"Database config: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
    
    # Connect to database
    connection = connect_to_mysql(config)
    if not connection:
        print("Failed to connect to database. Exiting.")
        sys.exit(1)
    
    # Parse release notes
    demo_file = Path(__file__).parent.parent / 'data' / 'release_notes_demo.md'
    print(f"\n📖 Parsing release notes from: {demo_file}")
    
    features = parse_release_notes(demo_file)
    if not features:
        print("No features found in release notes. Exiting.")
        connection.close()
        sys.exit(1)
    
    print(f"Found {len(features)} features:")
    for i, feature in enumerate(features, 1):
        print(f"  {i}. {feature}")
    
    # Generate and execute queries with comprehensive results
    print(f"\n🔍 Generating demo queries...")
    queries = generate_demo_queries(features)
    
    print(f"\n⚡ Executing {len(queries)} queries with validation...")
    results = execute_queries_with_validation(connection, queries, features)
    
    # Close connection
    connection.close()
    print(f"\n✅ Demo completed successfully!")

if __name__ == "__main__":
    main()
