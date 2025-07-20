# Comprehensive Financial Research Agent

A powerful financial research tool that scrapes vast amounts of content from reliable financial sources, then uses AI for comprehensive analysis and decision making.

## Features

- 🔍 **Comprehensive Article Scraping**: Gathers extensive content from Economic Times, MoneyControl, Business Standard
- 📰 **Vast Content Collection**: Fetches 30-50 detailed articles with full content
- 🤖 **AI Analysis**: Powered by Google Gemini 2.0 Flash for comprehensive investment analysis
- 💹 **Investment Decision Support**: Detailed analysis for buy/sell/hold decisions
- 📊 **Large Data Processing**: Handles massive text datasets for LLM analysis
- 💾 **Structured Output**: Saves comprehensive data in organized text format
- ⚡ **Parallel Processing**: Fast content extraction using multi-threading
- 🎯 **Company-Focused**: Automatically extracts company names and finds relevant content

## Installation

1. Clone or download this directory
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Required API Keys

1. **Gemini API Key** (Required):
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file as `GEMINI_API_KEY`

**Note**: This agent now uses web scraping for search instead of APIs, so you only need the Gemini API key!

## Usage

### Command Line Interface

```bash
# Comprehensive financial research (recommended for vast content)
python cli.py "Can I buy Reliance stock right now?" --comprehensive --max-articles 30

# Financial research with stock data
python cli.py "TCS earnings analysis" --financial --max-articles 15

# Quick analysis mode
python cli.py "HDFC bank analysis" --quick
```

### Python API

```python
from perplexity_agent import PerplexityAgent

# Initialize agent
agent = PerplexityAgent()

# Research a topic
results = agent.research("Can I buy Reliance stock right now?")

# Save report to file
filepath = agent.save_report_to_file(results)

# Quick research (returns just analysis)
analysis = agent.quick_research("Latest market trends")
print(analysis)
```

## Example Output

For the query "Can I buy Reliance stock right now?", the agent will:

1. Generate multiple search queries like:
   - "Reliance Industries stock analysis 2024"
   - "Reliance share price current market conditions"
   - "Should I invest in Reliance stock now"

2. Fetch articles from various sources
3. Analyze content using Gemini AI
4. Generate a comprehensive report including:
   - Executive summary with direct answer
   - Current market sentiment
   - Key findings from multiple sources
   - Expert opinions and analysis
   - Important financial metrics
   - Conclusion with actionable insights

## Project Structure

```
perplexity-agent/
├── perplexity_agent.py    # Main agent class
├── search_engine.py       # Web search functionality
├── article_fetcher.py     # Article content extraction
├── gemini_processor.py    # Gemini AI integration
├── cli.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── reports/              # Generated reports directory
```

## Configuration

The agent can be configured by modifying these parameters in `PerplexityAgent`:

- `max_articles_per_query`: Articles to fetch per search query (default: 5)
- `max_search_queries`: Maximum search queries to generate (default: 4)
- `output_dir`: Directory for saving reports (default: "reports")

## Error Handling

The agent includes robust error handling:

- **API Failures**: Falls back to alternative search engines
- **Article Extraction**: Multiple extraction methods with fallbacks
- **Rate Limiting**: Built-in delays to respect API limits
- **Network Issues**: Retry mechanisms with exponential backoff

## Limitations

- Requires internet connection for web search and article fetching
- Web scraping may occasionally fail if search engines change their HTML structure
- Some websites may block automated content extraction
- Gemini API has rate limits (60 requests per minute)
- Rate limiting is built-in to be respectful to search engines

## Disclaimer

This tool is for informational purposes only. The generated reports should not be considered as professional financial, legal, or medical advice. Always verify information independently and consult with qualified professionals for important decisions.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for educational and research purposes.