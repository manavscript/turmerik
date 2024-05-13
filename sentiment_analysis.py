import argparse
import re
import pandas as pd
import re
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')


def clean_text(text):
    if type(text) is float or text is None:
        return ""
    text = re.sub(r'https?://\S+|www\.\S+', '', text)  # url removal
    text = re.sub(r'/u/[^\s]+', '', text)  # user mentions
    text = re.sub(r'/r/[^\s]+', '', text)  # subreddit mentions
    text = re.sub(r'[^A-Za-z\s.,!?;:()\'\"/]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def calculate_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)
    # Using the compound score for overall sentiment
    return sentiment_score['compound']


def sentiment_category(sentiment):
    if sentiment > 0.1:
        return 'Positive'
    elif sentiment < -0.1:
        return 'Negative'
    else:
        return 'Neutral'


def get_sentiment(combined_df):
    combined_df['sentiment'] = combined_df['post_text'].apply(
        calculate_sentiment)

    if 'body' in combined_df.columns:
        combined_df['body'] = combined_df['body'].apply(
            clean_text)  # Clean the comments
        combined_df['comment_sentiment'] = combined_df['body'].apply(
            calculate_sentiment)

    combined_df.to_csv('processed_sentiment.csv', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='dataScraper',
        description='Scrape Data and store in CSV',
        epilog='Text at the bottom of help')

    parser.add_argument("-f", "--filename",
                        default="combined.csv", required=False)

    args = parser.parse_args()

    combined_df = pd.read_csv(args.filename)

    get_sentiment(combined_df)

    result_df = combined_df.groupby('author_id').agg({
        'karma': 'first',  # Assuming karma is constant per author_id
        'post_text': ' '.join,  # Concatenate all texts together
        'body': ' '.join,
        'sentiment': 'mean',  # Average post sentiment
        'comment_sentiment': 'mean'  # Average comment sentiment
    }).reset_index()

    result_df['combined_sentiment'] = result_df.apply(lambda row: (row['sentiment'] + row['comment_sentiment']) / 2
                                                      if pd.notnull(row['post_text']) and pd.notnull(row['body'])
                                                      else row['sentiment'] if pd.notnull(row['post_text'])
                                                      else row['comment_sentiment'], axis=1)
    result_df = result_df.sort_values("combined_sentiment")

    result_df['sentiment_category'] = result_df['combined_sentiment'].apply(
        sentiment_category)

    result_df.to_csv('updated_sentiment_data.csv', index=False)
    # result_df.to_csv("results.csv")
