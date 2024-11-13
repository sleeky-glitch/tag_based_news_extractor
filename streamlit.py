import streamlit as st
import nltk
import newspaper
from newspaper import Article
import pandas as pd
from datetime import datetime
import os
import warnings
import ssl

# SSL Certificate handling
try:
  _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
  pass
else:
  ssl._create_default_https_context = _create_unverified_https_context

# Suppress warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(page_title="News Article Tag Scraper", page_icon="📰", layout="wide")

# Download NLTK data at startup
@st.cache_resource
def download_nltk_data():
  try:
      nltk.download('punkt')
      nltk.download('averaged_perceptron_tagger')
      nltk.download('maxent_ne_chunker')
      nltk.download('words')
      nltk.download('stopwords')
      return True
  except Exception as e:
      st.error(f"Error downloading NLTK data: {str(e)}")
      return False

# Initialize NLTK
download_nltk_data()

def process_article(article):
  try:
      article.download()
      article.parse()
      
      if article.text:
          # Simple keyword extraction without using article.nlp()
          words = article.text.lower().split()
          # Remove common words and short words
          keywords = list(set([word for word in words if len(word) > 3]))[:10]
          article.keywords = keywords
          return True
      return False
  except Exception as e:
      st.warning(f"Article processing failed: {str(e)}")
      return False

def scrape_news(tags, max_articles_per_site=10):
  news_sites = [
      'https://www.cnn.com',
      'https://www.bbc.com',
      'https://www.reuters.com',
      'https://www.theguardian.com'
  ]
  
  results = []
  progress_bar = st.progress(0)
  
  for idx, site in enumerate(news_sites):
      try:
          st.write(f"Scanning {site}...")
          paper = newspaper.build(site, 
                                memoize_articles=False,
                                fetch_images=False,
                                request_timeout=10)
          
          article_count = 0
          for article in paper.articles:
              if article_count >= max_articles_per_site:
                  break
                  
              if process_article(article):
                  if any(tag.lower() in article.text.lower() or 
                        tag.lower() in ' '.join(article.keywords).lower() 
                        for tag in tags):
                      
                      results.append({
                          'source': site,
                          'title': article.title,
                          'text': article.text[:1000],
                          'url': article.url,
                          'keywords': ', '.join(article.keywords),
                          'publish_date': article.publish_date
                      })
                      article_count += 1
                  
          progress_bar.progress((idx + 1) / len(news_sites))
          
      except Exception as e:
          st.warning(f"Error processing site {site}: {str(e)}")
          continue
          
  progress_bar.empty()
  return results

def save_results(results):
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
tags_input = st.text_input(
  '🏷️ Enter Tags',
  placeholder='Enter tags separated by commas (e.g., climate, technology, health)'
)

if st.button('🔍 Start Scraping', type='primary'):
  if tags_input:
      tags = [tag.strip() for tag in tags_input.split(',')]
      
      with st.spinner('🔍 Scraping articles...'):
          results = scrape_news(tags, max_articles)
          
          if results:
              st.success(f'✅ Found {len(results)} articles matching your tags!')
              filename = save_results(results)
              
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

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
  <p>Built with Streamlit and Newspaper3k</p>
</div>
""", unsafe_allow_html=True)








