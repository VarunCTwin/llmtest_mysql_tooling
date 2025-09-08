#!/usr/bin/env python3
"""
Script to run queries from release_notes_demo.md using local MySQL database.
This script parses the markdown file and generates relevant SQL queries based on the content.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import re
from pathlib import Path

def load_env_config(env_file='../.env.local'):
    """Load MySQL configuration from environment file."""
    load_dotenv(env_file)
    
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

def execute_queries(connection, queries):
    """Execute the generated queries and display results."""
    cursor = connection.cursor()
    
    for description, query in queries:
        try:
            print(f"\n--- {description} ---")
            print(f"Query: {query}")
            
            cursor.execute(query)
            
            # Handle different types of queries
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                if results:
                    # Print column headers
                    columns = [desc[0] for desc in cursor.description]
                    print(f"Columns: {', '.join(columns)}")
                    
                    # Print results
                    for row in results:
                        print(f"Result: {row}")
                else:
                    print("No results found.")
            else:
                connection.commit()
                print(f"✓ Query executed successfully. Rows affected: {cursor.rowcount}")
                
        except Error as e:
            print(f"✗ Error executing query: {e}")
            continue
    
    cursor.close()

def main():
    """Main function to orchestrate the demo."""
    print("🚀 Starting Release Notes Demo with Local MySQL")
    print("=" * 50)
    
    # Load configuration
    config = load_env_config('../.env.local')
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
    
    # Generate and execute queries
    print(f"\n🔍 Generating demo queries...")
    queries = generate_demo_queries(features)
    
    print(f"\n⚡ Executing {len(queries)} queries...")
    execute_queries(connection, queries)
    
    # Close connection
    connection.close()
    print(f"\n✅ Demo completed successfully!")

if __name__ == "__main__":
    main()
