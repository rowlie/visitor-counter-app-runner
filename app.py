import os
from flask import Flask
import psycopg2
from psycopg2 import sql

# App setup
app = Flask(__name__)

def get_db_connection():
    """Establishes and returns a database connection."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("Error: DATABASE_URL not set in environment variables.")
    return psycopg2.connect(db_url)

@app.route('/')
def index():
    """
    Handles a visitor request, increments the counter in the database,
    and returns the current count.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Ensure the counter table exists.
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS counter (
                        id INT PRIMARY KEY,
                        count INT NOT NULL DEFAULT 0
                    );
                """)

                # Atomically insert or update the counter row.
                # This prevents race conditions if multiple users visit at the same time.
                cursor.execute("""
                    INSERT INTO counter (id, count) VALUES (1, 1)
                    ON CONFLICT (id) DO UPDATE
                    SET count = counter.count + 1
                    RETURNING count;
                """)
                
                # Fetch the new count returned by the query.
                current_count = cursor.fetchone()[0]
                
                conn.commit()

        return f"<h1>HellGoodbye from the Visitor Counter!</h1><p>You are visitor number <b>{current_count}</b>.</p>"

    except Exception as e:
        # In a real app, you would log this error instead of showing it to the user.
        error_message = str(e).replace('<', '&lt;').replace('>', '&gt;')
        return f"<h1>Database Connection Error!</h1><p>Could not connect to the database and update the counter.</p><p><b>Error:</b> {error_message}</p>", 500

if __name__ == '__main__':
    # Load environment variables from .env file for local development
    from dotenv import load_dotenv
    load_dotenv()
    
    # Gunicorn will handle this in production.this is an edit dfdf ff
    # The default port for App Runner is 8080, but 5000 is fine for local testing.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
