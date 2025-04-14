# Reddit Nothing Phone Complaint Scraper

This program scrapes Reddit for complaints about the Nothing Phone 3a and 3a Pro, analyzes the complaints using OpenAI's language model, and stores them in a CSV file.

## Features

- Scrapes Reddit posts and comments about Nothing Phone 3a and 3a Pro
- Uses OpenAI's language model to identify and group similar complaints
- Automatically detects semantic similarity between complaints
- Generates a CSV file with complaint summaries and their frequencies

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your API credentials:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
OPENAI_API_KEY=your_openai_api_key
```

3. Run the program:
```bash
python main.py
```

## Output

The program will create a CSV file named `nothing_phone_complaints.csv` with two columns:
- Complaint Summary: A summary of the complaint
- Count: Number of times this complaint was mentioned

## How it Works

1. The program scrapes Reddit posts and comments about Nothing Phone 3a and 3a Pro
2. Each piece of text is processed using OpenAI's language model to generate embeddings
3. New complaints are compared with existing ones using cosine similarity
4. Similar complaints are grouped together and their counts are updated
5. Results are saved to a CSV file, sorted by frequency

## Note

Make sure to follow Reddit's API guidelines and rate limits when using this scraper.
The program uses OpenAI's API for language model processing, which may incur costs based on your usage. 