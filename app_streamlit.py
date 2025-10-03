import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        st.error(f"Database connection error: {error}")
        return None

st.title("News Articles Dashboard")

conn = get_db_connection()
if conn:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM news_articles ORDER BY published_at DESC;")
    articles = cur.fetchall()
    cur.close()
    conn.close()

    if articles:
        for article in articles:
            # Display each column dynamically
            st.subheader(article.get('title', 'No Title'))
            
            # Loop through all columns except 'title'
            for key, value in article.items():
                if key != 'title':
                    st.write(f"**{key}:** {value}")
            
            st.markdown("---")
    else:
        st.info("No articles found.")