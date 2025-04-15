# Reddit Feedback Analyzer

A Python tool that analyzes Reddit discussions about products to extract and categorize user feedback. The tool uses OpenAI's GPT-4 to analyze posts and comments, generating a comprehensive feedback matrix and detailed summaries.

## Features

- **Reddit Data Collection**: Fetches posts and comments from relevant subreddits
- **AI-Powered Analysis**: Uses OpenAI's GPT-4 to analyze and categorize feedback
- **Feedback Categorization**: 
  - Features: design, camera, performance, battery, software, display, price, audio
  - Feedback Types: missing_feature, unuseful_feature, worse_than_competitor, very_good_feature, better_than_competitor, neutral
- **Visualizations**:
  - Feedback Matrix Heatmap: Shows distribution of feedback types across features
  - Feature Distribution Chart: Displays percentage of feedback for each feature
- **Detailed Export**: Generates a CSV file with comprehensive feedback summaries

## Requirements

- Python 3.8+
- Reddit API credentials
- OpenAI API key
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lighteningAB/redditScraper.git
cd redditScraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with your API credentials:
```
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_user_agent
OPENAI_API_KEY=your_openai_api_key
```

## Usage

Run the analyzer with a product name:

```bash
python reddit_feedback_analyzer.py "Product Name" --posts 10
```

Arguments:
- `product`: Name of the product to analyze (required)
- `--posts`: Number of posts to analyze (default: 10)

## Output

The tool generates:

1. **Feedback Matrix Visualization** (`product_name_feedback_matrix.png`):
   - Heatmap showing distribution of feedback types
   - Features on Y-axis, feedback types on X-axis
   - Color intensity indicates frequency of feedback

2. **Feature Distribution Chart** (`product_name_feedback_distribution.png`):
   - Bar chart showing percentage of total feedback per feature
   - Helps identify most discussed aspects of the product

3. **Detailed Feedback CSV** (`complaints.csv`):
   - Contains detailed feedback for each feature
   - Columns: title, feature, feedback_type, summary, url
   - Provides context and specific details for each piece of feedback

## Example

```bash
python reddit_feedback_analyzer.py "Nothing Phone 3a" --posts 5
```

This will:
1. Fetch 5 posts about the Nothing Phone 3a
2. Analyze feedback using GPT-4
3. Generate visualizations
4. Export detailed feedback to complaints.csv

## Contributing

Feel free to submit issues and enhancement requests! 
