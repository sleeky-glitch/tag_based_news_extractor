import streamlit as st
import newspaper
from newspaper import Article
import pandas as pd
from datetime import datetime
import os

def scrape_news(tags):
    # Create a directory for storing results if it doesn't exist
    if not os.path.exists('scraped_articles'):
        os.makedirs('scraped_articles')
    
    # List of popular news sites
    news_sites = [
        'https://www.cnn.com',
        'https://www.bbc.com',
        'https://www.reuters.com',
        'https://www.theguardian.com'
    ]
    
    results = []
    
    for site in news_sites:
        try:
            # Build newspaper site
            paper = newspaper.build(site, memoize_articles=False)
            
            # Search through articles
            for article in paper.articles[:10]:  # Limiting to 10 articles per site for demo
                try:
                    article.download()
                    article.parse()
                    article.nlp()
                    
                    # Check if any of the tags appear in the article text or keywords
                    if any(tag.lower() in article.text.lower() or 
                           tag.lower() in ' '.join(article.keywords).lower() 
                           for tag in tags):
                        
                        results.append({
                            'source': site,
                            'title': article.title,
                            'text': article.text,
                            'url': article.url,
                            'keywords': ', '.join(article.keywords),
                            'publish_date': article.publish_date
                        })
                        
                except Exception as e:
                    st.warning(f"Error processing article: {str(e)}")
                    continue
                    
