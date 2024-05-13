import pandas as pd
import argparse


def print_user_data(df, user_id):
    # Filter the DataFrame for the given user_id
    user_data = df[df['author_id'] == user_id]

    if user_data.empty:
        print(f"No data available for user ID: {user_id}")
        return

    # Display posts and their sentiments
    if user_data['post_text'].notna().any():
        print("Posts by the user:")
        for _, row in user_data.dropna(subset=['post_text']).iterrows():
            print(f" - {row['post_text']} (Sentiment: {row['sentiment']})")

    # Display comments and their sentiments
    if user_data['body'].notna().any():
        print("\nComments by the user:")
        for _, row in user_data.dropna(subset=['body']).iterrows():
            print(
                f" - {row['body']} (Comment Sentiment: {row['comment_sentiment']})")

    print("\nPersonalized Message:")
    # Assuming the same message is relevant for all entries
    print(user_data['personalized_message'].iloc[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='dataScraper',
        description='Scrape Data and store in CSV',
        epilog='Text at the bottom of help')

    parser.add_argument("-f", "--filename",
                        default="combined.csv", required=False)
    parser.add_argument("-u", "--user_id",
                        default="", required=False)

    args = parser.parse_args()

    df = pd.read_csv(args.filename)
    print_user_data(df, args.user_id)
