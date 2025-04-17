import streamlit as st
import sys
import io
from contextlib import contextmanager
from reddit_feedback_analyzer import MultiPlatformFeedbackAnalyzer
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import seaborn as sns
import pandas as pd
import praw
from googleapiclient.discovery import build
from openai import OpenAI
import numpy as np


# Load environment variables
load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="Product Feedback Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for the output containers
st.markdown("""
    <style>
    .output-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        height: 300px;
        overflow-y: auto;
        font-family: monospace;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .matrix-box {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 20px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔍 Product Feedback Analyzer")
st.markdown("""
    Analyze user feedback about products from Reddit, YouTube, and Twitter. 
    This tool uses AI to categorize and summarize feedback across different features and sentiment types.
""")

# Sidebar for API keys
with st.sidebar:
    st.header("API Configuration")
    
    # Reddit API credentials
    st.subheader("Reddit API")
    reddit_client_id = st.text_input("Reddit Client ID", value=os.getenv("REDDIT_CLIENT_ID", ""), type="password")
    reddit_client_secret = st.text_input("Reddit Client Secret", value=os.getenv("REDDIT_CLIENT_SECRET", ""), type="password")
    
    # YouTube API key
    st.subheader("YouTube API")
    youtube_api_key = st.text_input("YouTube API Key", value=os.getenv("YOUTUBE_API_KEY", ""), type="password")
    
    # OpenAI API key
    st.subheader("OpenAI API")
    openai_api_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    
    # Twitter API credentials
    st.subheader("Twitter API")
    twitter_api_key = st.text_input("Twitter API Key", value=os.getenv("TWITTER_API_KEY", ""), type="password")
    twitter_api_secret = st.text_input("Twitter API Secret", value=os.getenv("TWITTER_API_SECRET", ""), type="password")
    twitter_access_token = st.text_input("Twitter Access Token", value=os.getenv("TWITTER_ACCESS_TOKEN", ""), type="password")
    twitter_access_token_secret = st.text_input("Twitter Access Token Secret", value=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""), type="password")

# Input section
st.subheader("Analysis Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    product_name = st.text_input("Product Name", placeholder="e.g., Nothing Phone 3a")

with col2:
    analyze_reddit = st.checkbox("Reddit", value=True)
    analyze_youtube = st.checkbox("YouTube", value=True)
    analyze_twitter = st.checkbox("Twitter", value=True)

with col3:
    num_posts = st.slider("Number of posts to analyze per platform:", min_value=1, max_value=20, value=5)

# Create containers for output and matrix
output_container = st.empty()
matrix_container = st.empty()

# Run analysis button
if st.button("Run Analysis"):
    if not product_name:
        st.error("Please enter a product name")
    elif not any([analyze_reddit, analyze_youtube, analyze_twitter]):
        st.error("Please select at least one platform to analyze")
    else:
        with st.spinner("Analyzing feedback..."):
            # Create a string buffer to collect all output
            output_buffer = io.StringIO()
            
            # Initialize analyzer with output buffer
            analyzer = MultiPlatformFeedbackAnalyzer(product_name, output_buffer=output_buffer)
            
            # Set API credentials if provided
            if reddit_client_id and reddit_client_secret:
                analyzer.reddit = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    user_agent='FeedbackAnalyzer/1.0'
                )
            
            if youtube_api_key:
                analyzer.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
            
            if openai_api_key:
                analyzer.openai_client = OpenAI(api_key=openai_api_key)
            
            # Collect data from platforms
            all_posts_data = []
            
            if analyze_reddit:
                with st.spinner("Fetching Reddit posts..."):
                    reddit_posts = analyzer.fetch_reddit_posts(num_posts)
                    all_posts_data.extend(reddit_posts)
                    output_buffer.write(f"Found {len(reddit_posts)} Reddit posts\n")
                    output_container.markdown(
                        f'<div class="output-box">{output_buffer.getvalue().replace(chr(10), "<br>")}</div>',
                        unsafe_allow_html=True
                    )
            
            if analyze_youtube:
                with st.spinner("Fetching YouTube comments..."):
                    youtube_posts = analyzer.fetch_youtube_comments(num_posts)
                    all_posts_data.extend(youtube_posts)
                    output_buffer.write(f"Found {len(youtube_posts)} YouTube comments\n")
                    output_container.markdown(
                        f'<div class="output-box">{output_buffer.getvalue().replace(chr(10), "<br>")}</div>',
                        unsafe_allow_html=True
                    )
            
            if analyze_twitter:
                with st.spinner("Fetching Twitter posts..."):
                    twitter_posts = analyzer.fetch_twitter_posts(num_posts)
                    all_posts_data.extend(twitter_posts)
                    output_buffer.write(f"Found {len(twitter_posts)} Twitter posts\n")
                    output_container.markdown(
                        f'<div class="output-box">{output_buffer.getvalue().replace(chr(10), "<br>")}</div>',
                        unsafe_allow_html=True
                    )
            
            output_buffer.write(f"\nTotal posts to analyze: {len(all_posts_data)}\n")
            output_container.markdown(
                f'<div class="output-box">{output_buffer.getvalue().replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True
            )
            
            analyzer.analyze_feedback(all_posts_data)
            st.session_state.analyzer = analyzer
            st.session_state.feature_categories = analyzer.feature_categories
            st.session_state.feedback_types = analyzer.feedback_types

            # Display feedback visualizations
            st.header("Feedback Visualizations")
            col1, col2, col3 = st.columns(3)
            # 1) Heatmap of feedback matrix
            fig1, ax1 = plt.subplots(figsize=(15, 10))
            matrix_data = np.array([
                [analyzer.feedback_matrix[feat][ft] for ft in analyzer.feedback_types]
                for feat in analyzer.feature_categories
            ])
            sns.heatmap(
                matrix_data,
                annot=True,
                fmt=".0f",
                cmap="YlOrRd",
                xticklabels=analyzer.feedback_types,
                yticklabels=analyzer.feature_categories,
                cbar_kws={"label": "Number of feedback items"},
                ax=ax1
            )
            ax1.set_title(f"Feedback Matrix for {product_name}", pad=20, fontsize=14)
            ax1.set_xlabel("Feedback Type")
            ax1.set_ylabel("Feature Category")
            col1.pyplot(fig1)

            # 2) Bar chart of feedback by feature
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            totals = np.array([
                sum(analyzer.feedback_matrix[feat].values())
                for feat in analyzer.feature_categories
            ])
            percentages = (totals / totals.sum() * 100) if totals.sum() > 0 else np.zeros_like(totals)
            ax2.bar(analyzer.feature_categories, percentages)
            ax2.set_title(f"Feedback Distribution by Feature for {product_name}", pad=20, fontsize=14)
            ax2.set_ylabel("Percentage of total feedback")
            ax2.set_xticklabels(analyzer.feature_categories, rotation=45, ha="right")
            col2.pyplot(fig2)

            # 3) Pie chart of feedback by source
            fig3, ax3 = plt.subplots(figsize=(8, 8))
            source_totals = {s: c for s, c in analyzer.feedback_by_source.items() if c > 0}
            if source_totals:
                ax3.pie(
                    source_totals.values(),
                    labels=source_totals.keys(),
                    autopct="%1.1f%%",
                    startangle=90
                )
                ax3.set_title(f"Feedback Distribution by Source for {product_name}", pad=20, fontsize=14)
                ax3.axis("equal")
            else:
                ax3.text(0.5, 0.5, "No feedback by source", ha="center", va="center", fontsize=14)
                ax3.axis("off")
            col3.pyplot(fig3)

            # Finally, offer the CSV download as you already do:
            with open("complaints.csv", "rb") as file:
                st.download_button(
                    label="Download Detailed Results (CSV)",
                    data=file,
                    file_name=f"{product_name.replace(' ', '_')}_feedback.csv",
                    mime="text/csv"
                )

if 'analyzer' in st.session_state:
    st.header("Detailed Feedback Filter")
    st.session_state.setdefault("selected_feature", None)
    st.session_state.setdefault("selected_feedback_type", None)
    st.session_state.setdefault("summaries_text", "")

    def update_summaries():
        try:
            df = pd.read_csv("complaints.csv")
            f = st.session_state.selected_feature
            t = st.session_state.selected_feedback_type
            if f and t:
                filtered_df = df[(df["feature"] == f) & (df["feedback_type"] == t)]
                summaries = filtered_df["summary"].tolist()
                display_text = "\n".join([f"- {summary}" for summary in summaries]) if summaries else "No matching summaries found."
            else:
                display_text = ""
        except FileNotFoundError:
            display_text = "Error: complaints.csv not found. Please run the analysis first."
        except pd.errors.EmptyDataError:
            display_text = "Error: complaints.csv is empty."
        except Exception as e:
            display_text = f"An error occurred: {e}"

        st.session_state.summaries_text = display_text

    st.selectbox(
        "Feature Category",
        options=st.session_state.feature_categories,
        key="selected_feature",
        on_change=update_summaries,
    )

    st.selectbox(
        "Feedback Type",
        options=st.session_state.feedback_types,
        key="selected_feedback_type",
        on_change=update_summaries,
    )

    st.text_area("Matching Summaries", value=st.session_state.summaries_text, height=200)

# Add footer with instructions
st.markdown("---")
st.markdown("""
    ### How to Use
    1. Enter the product name you want to analyze
    2. Select the platforms to analyze
    3. Set the number of posts to analyze for each platform
    4. Click "Run Analysis" to start
    5. View the results and download the detailed CSV report
    
    Note: The analysis time depends on the number of posts selected.
""") 