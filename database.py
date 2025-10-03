import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_table():
    "Creates a new table in postgres database"
    
    conn=None
    try:
        db_url=os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("Database URL environment not set")
        
        print("Connecting to Database")
        conn = psycopg2.connect(db_url)
        cur=conn.cursor()
        
        create_table_command = """
        CREATE TABLE IF NOT EXISTS news_articles (
            id SERIAL PRIMARY KEY,
            search_keyword VARCHAR(255) NOT NULL,
            source_name VARCHAR(255),
            title TEXT NOT NULL,
            description TEXT,
            url TEXT NOT NULL UNIQUE,
            published_at TIMESTAMP WITH TIME ZONE,
            fetched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        print("Creating table 'news_articles' if it doesn't exist...")
        cur.execute(create_table_command)
        
        conn.commit()
        print("Table 'news_articles' created successfully or already exists.")
        
        cur.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while creating PostgreSQL table: {error}")
        
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")
            
if __name__ == "__main__":
    create_table()