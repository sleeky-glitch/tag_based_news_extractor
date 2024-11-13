import streamlit as st
import newspaper
from newspaper import Article
import pandas as pd
from datetime import datetime
import nltk

# Download required NLTK data
@st.cache_resource
def download_nltk_data():
    try:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('maxent_ne_chunker')
        nltk.download('words')
        return True
    except Exception as e:
        st.error(f"Error downloading NLTK data: {str(e)}")
        return False

# Initialize NLTK data
download_nltk_data()

def scrape_news(tags):
    # List of popular news sites
    news_sites = [
        'https://www.cnn.com',
        'https://www.bbc.com',
        'https://www.reuters.com',
        'https://www.theguardian.com'


