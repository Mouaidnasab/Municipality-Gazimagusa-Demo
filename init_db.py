import sqlite3

def initialize_db():
    conn = sqlite3.connect('database.db')
    
    # Create the citizens table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS citizens (
            citizen_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')
    
    # Create the votes table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            vote_id INTEGER,
            citizen_id TEXT,
            date TEXT NOT NULL,
            vote_count INTEGER DEFAULT 0,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id)
        )
    ''')
    
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully.")
