import warnings
            
            return True
    except Exception as e:
        st.error(f"Error downloading NLTK data: {str(e)}")
        return False

def scrape_news(tags, max_articles_per_site=10):
    """
    Scrape news articles based on given tags
    """
    news_sites = [
        'https://www.cnn.com',
        'https://www.bbc.com',
        'https://www.reuters.com',
        'https://www.theguardian.com'
    ]
    
    results = []
    progress_bar = st.progress(0)
    site_count = len(news_sites)
    
    for idx, site in enumerate(news_sites):
        try:
            st.write(f"Scanning {site}...")
            # Configure newspaper with more lenient settings
            paper = newspaper.build(site, 
                                  memoize_articles=False,
                                  fetch_images=False,
                                  request_timeout=10)
            
            article_count = 0
            for article in paper.articles:
                if article_count >= max_articles_per_site:
                    break
                    
                try:
                    article.download()
                    article.parse()
                    
                    # Only perform NLP if parsing was successful
                    if article.text:
                        article.nlp()
                        
                        # Check if any of the tags appear in the article
                        if any(tag.lower() in article.text.lower() or 
                               tag.lower() in ' '.join(article.keywords).lower() 
                               for tag in tags):
                            
                            results.append({
                                'source': site,
                                'title': article.title,
                                'text': article.text[:1000],  # Limit text length
                                'url': article.url,
                                'keywords': ', '.join(article.keywords),
                                'publish_date': article.publish_date
                            })
                            article_count += 1
                        
                except Exception as e:
                    st.warning(f"Error processing article from {site}: {str(e)}")
                    continue
                    
            progress_bar.progress((idx + 1) / site_count)
            
        except Exception as e:
            st.warning(f"Error processing site {site}: {str(e)}")
            continue







