# Reddit Complaint Analyzer

A command-line tool that analyzes Reddit comments about a product and extracts the most common complaints, categorizing them into different aspects like camera, performance, battery, etc.

## Features

- Searches Reddit for product reviews and discussions
- Analyzes comments to identify common complaints
- Categorizes complaints into different aspects (camera, performance, battery, etc.)
- Generates concise summaries of each complaint
- Exports results to CSV and displays them in the terminal

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/redditScraper.git
cd redditScraper
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API credentials:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
OPENAI_API_KEY=your_openai_api_key
```

### Getting API Keys:

#### Reddit API:
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Select "script"
4. Fill in the required information
5. Copy the client ID and client secret to your .env file

#### OpenAI API (Optional - for enhanced analysis):
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key to your .env file as OPENAI_API_KEY
4. Note: If you don't provide an OpenAI API key, the tool will use a simpler analysis method

## Usage

Run the script from the command line with the following syntax:

```bash
python export_top_complaints.py "Product Name" [--posts NUMBER] [--output FILENAME]
```

### Arguments:

- `Product Name`: The name of the product to analyze (required)
- `--posts`: Number of Reddit posts to analyze (optional, default: 10)
- `--output`: Output CSV file name (optional, default: top_10_complaints.csv)

### Examples:

Analyze the latest 10 posts about iPhone 15:
```bash
python export_top_complaints.py "iPhone 15"
```

Analyze 20 posts about Samsung S24 and save to a custom file:
```bash
python export_top_complaints.py "Samsung S24" --posts 20 --output s24_complaints.csv
```

## Output

The tool will:
1. Display progress as it fetches and analyzes Reddit posts
2. Show the top 10 most frequent complaints in the terminal
3. Export the results to a CSV file

The complaints are categorized into:
- Camera
- Performance
- Battery
- Storage
- Display
- Design
- Price
- Software
- Hardware

## Analysis Modes

The tool has two analysis modes:

1. **Simple Mode** (Default): Uses keyword-based analysis to identify and categorize complaints. No API key required.

2. **Enhanced Mode** (With OpenAI API): Uses OpenAI's language models for more accurate complaint analysis and summarization. Requires an OpenAI API key in the .env file.

## Requirements

- Python 3.6+
- praw
- python-dotenv
- openai (optional)

## License

MIT License 