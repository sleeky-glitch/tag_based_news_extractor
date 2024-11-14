# News Keyword Search Bot

A Streamlit-based web application that allows users to search for specific keywords across multiple news articles URLs. The application scrapes the articles, searches for specified keywords, and saves the results to a text file.

## Features

- Search multiple news articles simultaneously
- Keyword-based article filtering  
- Article text extraction using Newspaper3k
- Results saved to a text file
- User-friendly web interface built with Streamlit

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sleeky-glitch/newsextractor.git
cd newsextractor
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

- streamlit
- requests 
- beautifulsoup4
- newspaper3k
- Pillow

## Usage

1. Start the Streamlit application:
```bash
streamlit run streamlit.py
```

2. Enter your keywords (comma-separated) in the first text area
3. Enter the news article URLs (one per line) in the second text area
4. Click 'Start Search' to begin the search process
5. Results will be saved in 'article_info.txt'

## Output Format

The application saves the following information for each matching article:
- Article title
- Publication date
- Found keywords
- Full article text

## Error Handling

The application includes error handling for:
- Invalid URLs
- Failed article downloads
- Parsing errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.