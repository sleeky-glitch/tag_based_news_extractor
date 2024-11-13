import streamlit as st
import newspaper
from newspaper import Article
import pandas as pd
from datetime import datetime

def scrape_news(tags):
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
                    
        except Exception as e:
            st.warning(f"Error processing site {site}: {str(e)}")
            continue
    
    return results

def save_results(results):
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'articles_{timestamp}.csv'
    
    # Convert DataFrame to CSV
    csv = df.to_csv(index=False)
    
    # Create download button
    st.download_button(
        label="Download results as CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )
    return filename

# Streamlit UI
st.title('News Article Tag Scraper')

# Input for tags
st.subheader('Enter Tags')
tags_input = st.text_input('Enter tags separated by commas')

if st.button('Scrape Articles'):
    if tags_input:
        tags = [tag.strip() for tag in tags_input.split(',')]
        
        with st.spinner('Scraping articles...'):
            # Perform scraping
            results = scrape_news(tags)
            
            if results:
                st.success(f'Found {len(results)} articles matching your tags!')
                
                # Save results
                filename = save_results(results)
                
                # Display results
                for idx, article in enumerate(results):
                    with st.expander(f"Article {idx + 1}: {article['title']}"):
                        st.write(f"Source: {article['source']}")
                        st.write(f"URL: {article['url']}")
                        st.write(f"Keywords: {article['keywords']}")
                        st.write("Text preview:")
                        st.write(article['text'][:500] + "...")
            else:
                st.warning('No articles found matching your tags.')
    else:
        st.error('Please enter at least one tag.')

