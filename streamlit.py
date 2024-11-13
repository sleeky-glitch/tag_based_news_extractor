import streamlit as st
import nltk
import newspaper
from newspaper import Article
import pandas as pd
from datetime import datetime
import os

# Set page configuration
st.set_page_config(
    page_title="News Article Tag Scraper",
    page_icon="📰",
    layout="wide"
)

# Create a directory for NLTK data if it doesn't exist
NLTK_DATA_DIR = os.path.join(os.getcwd(), "nltk_data")
if not os.path.exists(NLTK_DATA_DIR):
    os.makedirs(NLTK_DATA_DIR)

# Configure NLTK to use the local directory
nltk.data.path.insert(0, NLTK_DATA_DIR)

# Download required NLTK data
@st.cache_resource
def download_nltk_data():
    try:
        with st.spinner('Downloading required NLTK data...'):
            # Download all required NLTK data
            required_packages = [
                'punkt',
                'punkt_tab',
                'averaged_perceptron_tagger',
                'maxent_ne_chunker',
                'words'
            ]
            
            for package in required_packages:
                try:
                    nltk.download(package, download_dir=NLTK_DATA_DIR, quiet=True)
                    st.write(f"Successfully downloaded {package}")
                except Exception as e:
                    st.warning(f"Error downloading {package}: {str(e)}")
                    
            # Verify downloads
            nltk.data.find('tokenizers/punkt')
            return True
    except Exception as e:
        st.error(f"Error downloading NLTK data: {str(e)}")
        return False

# Initialize NLTK data
if download_nltk_data():
    st.success("NLTK data downloaded successfully!")
else:
    st.error("Failed to download NLTK data. Some features may not work correctly.")

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
            paper = newspaper.build(site, memoize_articles=False)
            
            article_count = 0
            for article in paper.articles:
                if article_count >= max_articles_per_site:
                    break
                    
                try:
                    article.download()
                    article.parse()
                    article.nlp()
                    
                    # Check if any of the tags appear in the article
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
                        article_count += 1
                        
                except Exception as e:
                    st.warning(f"Error processing article from {site}: {str(e)}")
                    continue
                    
            progress_bar.progress((idx + 1) / site_count)
            
        except Exception as e:
            st.warning(f"Error processing site {site}: {str(e)}")
            continue
            
    progress_bar.empty()
    return results

def save_results(results):
    """
    Convert results to DataFrame and create download button
    """
    if not results:
        return None
        
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'articles_{timestamp}.csv'
    
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )
    return filename

# UI Layout
st.title('📰 News Article Tag Scraper')
st.markdown("""
This app scrapes major news websites for articles containing your specified tags.
Enter multiple tags separated by commas to begin searching.
""")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    max_articles = st.slider(
        "Maximum articles per site",
        min_value=5,
        max_value=50,
        value=10,
        help="Limit the number of articles to scan per news site"
    )

# Main interface
tags_input = st.text_input('🏷️ Enter Tags', 
                          placeholder='Enter tags separated by commas (e.g., climate, technology, health)')

if st.button('🔍 Start Scraping', type='primary'):
    if tags_input:
        tags = [tag.strip() for tag in tags_input.split(',')]
        
        with st.spinner('🔍 Scraping articles...'):
            results = scrape_news(tags, max_articles)
            
            if results:
                st.success(f'✅ Found {len(results)} articles matching your tags!')
                
                # Save results
                filename = save_results(results)
                
                # Display results in tabs
                st.subheader("📑 Results")
                for idx, article in enumerate(results, 1):
                    with st.expander(f"📄 Article {idx}: {article['title']}"):
                        st.markdown(f"**Source:** {article['source']}")
                        st.markdown(f"**URL:** [{article['url']}]({article['url']})")
                        st.markdown(f"**Keywords:** {article['keywords']}")
                        st.markdown("**Preview:**")
                        st.markdown(article['text'][:500] + "...")
            else:
                st.warning('⚠️ No articles found matching your tags.')
    else:
        st.error('⚠️ Please enter at least one tag.')

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with Streamlit and Newspaper3k</p>
</div>
""", unsafe_allow_html=True)





