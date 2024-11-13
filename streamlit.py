import streamlit as st
import nltk
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import warnings
import time
from urllib.parse import urljoin

# Suppress warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(page_title="News Article Tag Scraper", page_icon="📰", layout="wide")

# Initialize NLTK
@st.cache_resource
def download_nltk_data():
  try:
      nltk.download('punkt')
      nltk.download('stopwords')
      return True
  except Exception as e:
      st.error(f"Error downloading NLTK data: {str(e)}")
      return False

# Download NLTK data
download_nltk_data()

def clean_text(text):
  """Clean and normalize text content."""
  if not text:
      return ""
  # Remove extra whitespace
  text = ' '.join(text.split())
  # Remove special characters
  text = ''.join(char for char in text if char.isprintable())
  return text

def extract_article_content(url, headers):
  """Extract content from a single article URL."""
  try:
      response = requests.get(url, headers=headers, timeout=10)
      soup = BeautifulSoup(response.text, 'html.parser')
      
      # Try different methods to find the article content
      article_text = ""
      
      # Method 1: Look for article tags
      article = soup.find('article')
      if article:
          paragraphs = article.find_all('p')
      else:
          # Method 2: Look for main content area
          main_content = soup.find(['main', 'div[role="main"]', '#main-content'])
          if main_content:
              paragraphs = main_content.find_all('p')
          else:
              # Method 3: Get all paragraphs
              paragraphs = soup.find_all('p')
      
      # Extract text from paragraphs
      article_text = ' '.join([p.get_text() for p in paragraphs])
      
      # Clean the text
      article_text = clean_text(article_text)
      
      # Get title
      title = soup.find('title')
      title = title.get_text() if title else "No title found"
      
      return {
          'title': clean_text(title),
          'text': article_text
      }
  except Exception as e:
      st.warning(f"Error extracting content from {url}: {str(e)}")
      return None

def scrape_news(tags, max_articles_per_site=10):
  news_sites = {
      'CNN': 'https://www.cnn.com',
      'BBC': 'https://www.bbc.com',
      'Reuters': 'https://www.reuters.com',
      'The Guardian': 'https://www.theguardian.com/international'
  }
  
  results = []
  progress_bar = st.progress(0)
  
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  }
  
  for idx, (site_name, site_url) in enumerate(news_sites.items()):
      try:
          st.write(f"Scanning {site_name}...")
          response = requests.get(site_url, headers=headers, timeout=10)
          soup = BeautifulSoup(response.text, 'html.parser')
          
          # Find all links
          links = soup.find_all('a', href=True)
          article_count = 0
          processed_urls = set()
          
          for link in links:
              if article_count >= max_articles_per_site:
                  break
              
              try:
                  url = link['href']
                  # Make URL absolute if it's relative
                  if not url.startswith('http'):
                      url = urljoin(site_url, url)
                  
                  # Skip if already processed or non-article URLs
                  if (url in processed_urls or
                      any(ext in url for ext in ['.jpg', '.png', '.pdf', '.zip']) or
                      any(path in url for path in ['/video/', '/audio/', '/images/', '/tags/', '/category/'])):
                      continue
                  
                  processed_urls.add(url)
                  
                  # Extract article content
                  article_data = extract_article_content(url, headers)
                  if not article_data:
                      continue
                  
                  # Check if article contains any of the tags
                  text_content = f"{article_data['title']} {article_data['text']}".lower()
                  if any(tag.lower() in text_content for tag in tags):
                      results.append({
                          'source': site_name,
                          'title': article_data['title'],
                          'text': article_data['text'][:1000] + "...",
                          'url': url,
                          'keywords': ', '.join(tags),
                          'publish_date': datetime.now().strftime("%Y-%m-%d")
                      })
                      article_count += 1
                      
                      # Show progress
                      st.write(f"Found article: {article_data['title']}")
                  
                  # Add a small delay to be respectful to the servers
                  time.sleep(0.5)
                  
              except Exception as e:
                  continue
                  
          progress_bar.progress((idx + 1) / len(news_sites))
          
      except Exception as e:
          st.warning(f"Error processing site {site_name}: {str(e)}")
          continue
          
  progress_bar.empty()
  return results

def save_results(results):
  """Save results to CSV and provide download button."""
  if not results:
      return None
      
  df = pd.DataFrame(results)
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = f'articles_{timestamp}.csv'
  
  csv = df.to_csv(index=False).encode('utf-8')
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
  
  st.markdown("""
  ### About
  This app searches for articles across major news sites:
  - CNN
  - BBC
  - Reuters
  - The Guardian
  
  ### Tips
  - Use specific tags for better results
  - Multiple tags increase chances of finding relevant articles
  - Be patient as scanning takes time
  """)

# Main interface
tags_input = st.text_input(
  '🏷️ Enter Tags',
  placeholder='Enter tags separated by commas (e.g., climate, technology, health)'
)

if st.button('🔍 Start Scraping', type='primary'):
  if tags_input:
      tags = [tag.strip() for tag in tags_input.split(',')]
      
      with st.spinner('🔍 Scraping articles... This may take a few minutes.'):
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
                      st.markdown(f"**Date:** {article['publish_date']}")
                      st.markdown("**Preview:**")
                      st.markdown(article['text'])
          else:
              st.warning('⚠️ No articles found matching your tags.')
  else:
      st.error('⚠️ Please enter at least one tag.')

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
  <p>Built with Streamlit and BeautifulSoup4</p>
</div>
""", unsafe_allow_html=True)








