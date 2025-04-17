# Multi-Platform Feedback Analyzer

A powerful tool for analyzing user feedback about products across multiple platforms: Reddit, YouTube, and X (Twitter).

## Features

- **Multi-Platform Analysis**: Collects and analyzes feedback from Reddit, YouTube, and X (Twitter)
- **Comprehensive Feedback Categorization**: Automatically categorizes feedback into specific features (design, camera, performance, etc.)
- **Sentiment Analysis**: Identifies whether features are praised, criticized, or compared to competitors
- **Visual Analytics**: Generates heatmaps and distribution charts to visualize feedback patterns
- **Detailed Export**: Exports all feedback with summaries to CSV for further analysis
- **Source Distribution**: Shows the distribution of feedback across different platforms
- **Web Interface**: User-friendly Streamlit web app for easy interaction

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/multi-platform-feedback-analyzer.git
cd multi-platform-feedback-analyzer
```

2. Create a virtual environment and activate it:
```bash
conda create -n scraper python=3.9
conda activate scraper
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up API keys in a `.env` file:
```
# Reddit API credentials
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name/1.0

# OpenAI API key
OPENAI_API_KEY=your_openai_api_key

# YouTube API key (optional)
YOUTUBE_API_KEY=your_youtube_api_key

# Twitter/X API credentials (optional)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
```

## Usage

### Web App (Recommended)

The easiest way to use this tool is through the Streamlit web interface:

1. Make sure your conda environment is activated:
```bash
conda activate scraper
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

4. Using the web interface:
   - Enter the product name you want to analyze
   - Select which platforms to analyze (Reddit, YouTube, Twitter)
   - Set the number of posts to analyze per platform using the slider
   - Click "Run Analysis" to start
   - View real-time progress in the output box
   - See the final results in the matrix box below
   - Download the detailed CSV report using the download button

### Command Line Interface

You can also run the script directly from the command line:

```bash
python reddit_feedback_analyzer.py "Product Name" --posts 10 --platforms reddit youtube twitter
```

### Arguments

- `product`: The name of the product to analyze (required)
- `--posts`: Number of posts to analyze per platform (default: 10)
- `--platforms`: Platforms to analyze (default: reddit youtube twitter)

### Output

The script generates:

1. **Feedback Matrix Visualization**: A heatmap showing the distribution of feedback types across features
2. **Feature Distribution Chart**: A bar chart showing the percentage of total feedback for each feature
3. **Source Distribution Chart**: A pie chart showing the distribution of feedback across platforms
4. **CSV Export**: A detailed CSV file with all feedback, including summaries

## API Setup Instructions

### Reddit API

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create another app..."
3. Select "script" as the type
4. Fill in the name and description
5. For "redirect uri" use http://localhost:8080
6. Note the client ID (under the app name) and client secret

### YouTube API

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable the YouTube Data API v3
4. Create credentials (API key)
5. Copy the API key to your .env file

### Twitter/X API

1. Go to https://developer.twitter.com/
2. Create a new project and app
3. Generate API key and secret
4. Generate access token and secret
5. Add these to your .env file

## Example

```bash
python reddit_feedback_analyzer.py "Nothing Phone 3a" --posts 5 --platforms reddit youtube
```

This will analyze 5 posts from Reddit and 5 videos from YouTube about the Nothing Phone 3a, generating visualizations and a CSV export.

## License

MIT 
