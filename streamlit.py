import streamlit as st
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






