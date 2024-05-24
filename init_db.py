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

    # conn.execute('''DROP TABLE IF EXISTS skill_sharing;''')

    # Create the Skill sharing table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS skill_sharing (
            ss_id INTEGER PRIMARY KEY,
            citizen_id TEXT,
            description TEXT ,
            phone INTEGER NOT NULL,
            email TEXT NOT NULL,
            type TEXT NOT NULL,
            img_name TEXT NOT NULL,
            date_added date NOT NULL,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id)
        )
    ''')

     # Create the Skill sharing table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS news (
            news_id INTEGER PRIMARY KEY,
            body TEXT NOT NULL,
            title TEXT NOT NULL,
            date_added date NOT NULL
        )
    ''')

    # Create the blog table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS blog (
            blog_id INTEGER PRIMARY KEY,
            name_blog TEXT NOT NULL,
            description TEXT NOT NULL,
            date_added date NOT NULL
        )
    ''')
    # Create the reply blog table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reply_blog (
            reply_id INTEGER PRIMARY KEY,
            blog_id INTEGER,
            name_reply TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY(blog_id) REFERENCES blog(blog_id)
        )
    ''')
    
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully.")
