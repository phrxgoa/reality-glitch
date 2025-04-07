import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def wait_for_postgres():
    """Wait for PostgreSQL to be ready."""
    print("Waiting for PostgreSQL to be ready...")
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "db"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                database=os.getenv("POSTGRES_DB", "reality_glitch")
            )
            conn.close()
            print("PostgreSQL is ready!")
            return True
        except psycopg2.OperationalError:
            retry_count += 1
            print(f"PostgreSQL is not ready yet. Retrying... ({retry_count}/{max_retries})")
            time.sleep(1)
    
    print("Could not connect to PostgreSQL after maximum retries.")
    return False

def init_database():
    """Initialize the database and create tables if they don't exist."""
    if not wait_for_postgres():
        print("Failed to connect to PostgreSQL. Exiting.")
        return False
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "db"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            database=os.getenv("POSTGRES_DB", "reality_glitch")
        )
        
        # Set isolation level to autocommit
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Define possible locations for the SQL file
        sql_file_paths = [
            "init_db.sql",
            "/app/init_db.sql",
            "../init_db.sql"
        ]
        
        # Try to find and read the SQL initialization script
        sql_script = None
        for file_path in sql_file_paths:
            try:
                print(f"Trying to open SQL file at {file_path}...")
                with open(file_path, "r") as sql_file:
                    sql_script = sql_file.read()
                print(f"Successfully read SQL file from {file_path}")
                break
            except FileNotFoundError:
                print(f"SQL file not found at {file_path}")
        
        if sql_script:
            cursor.execute(sql_script)
            print("Successfully executed SQL initialization script")
        else:
            print("Could not find init_db.sql file")
            return False
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("Database initialization completed successfully.")
        return True
    
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    init_database() 