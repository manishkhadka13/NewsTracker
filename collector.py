import os
import requests
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY=os.getenv("NEWS_API_KEY")
DATABASE_URL=os.getenv("DATABASE_URL")
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"


print(f"DATABASE_URL: {DATABASE_URL}")

def fetch_news(keywords):
    all_articles=[]
    print(f"Fetching news for keywords: {keywords}")
    for keyword in keywords:
        params = {
            'q': keyword,
            'apiKey': NEWS_API_KEY,
            'language': 'en',
            'sortBy': 'publishedAt', # Get the most recent articles
            'pageSize': 20 # Limit to 20 articles per keyword to be respectful of API limits
        }
        
        try:
            response = requests.get(NEWS_API_ENDPOINT, params=params)
            response.raise_for_status()
            data=response.json()
            articles=data.get("articles",[])
            
            for article in articles:
                article['search_keyword']=keyword
            all_articles.extend(articles)
            print(f"Found {len(articles)} articles for '{keyword}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for '{keyword}':{e}")
    return all_articles

def store_articles(articles):
    if not articles:
        print("No new articles to store.")
        return
    
    conn=None
    try:
        conn=psycopg2.connect(DATABASE_URL)
        cur=conn.cursor()
        
        insert_query="""
        INSERT INTO news_articles (search_keyword, source_name, title, description, url, published_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        """
        articles_to_insert=[]
        for article in articles:
            article_data = (
                article.get('search_keyword', 'N/A'),
                article.get('source', {}).get('name'),
                article.get('title'),
                article.get('description'),
                article.get('url'),
                article.get('publishedAt')
            )
            articles_to_insert.append(article_data)
            
        psycopg2.extras.execute_batch(cur, insert_query, articles_to_insert)
        conn.commit()
        
        inserted_count = cur.rowcount
        print(f"Successfully stored {inserted_count} new articles in the database.")
        cur.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while connecting to or writing to PostgreSQL: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    
    KEYWORDS_TO_TRACK = [
        '"Microsoft Maia"',
        '"Project Maia" AND Microsoft' 
    ]
    
    fetched_articles = fetch_news(KEYWORDS_TO_TRACK)
    store_articles(fetched_articles)
    print("\nCollection process finished.")