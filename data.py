# Necessary Import Statements
import praw
import config
import csv
from datetime import datetime
import pandas as pd
import argparse


def create_csv(file_suffix):
    posts_file = open(f'posts{file_suffix}.csv', 'w',
                      newline='', encoding='utf-8')
    authors_file = open(f'authors{file_suffix}.csv',
                        'w', newline='', encoding='utf-8')
    comments_file = open(
        f'comments{file_suffix}.csv', 'w', newline='', encoding='utf-8')

    return posts_file, authors_file, comments_file


def get_writer(posts_file, authors_file, comments_file):
    # Create CSV writers
    posts_writer = csv.writer(posts_file, quoting=csv.QUOTE_ALL)
    authors_writer = csv.writer(authors_file, quoting=csv.QUOTE_ALL)
    comments_writer = csv.writer(comments_file, quoting=csv.QUOTE_ALL)

    # Write headers
    posts_writer.writerow(
        ['post_id', 'title', 'selftext', 'url', 'score', 'created_utc', 'author_id'])
    authors_writer.writerow(
        ['author_id', 'username', 'karma', 'account_created'])
    comments_writer.writerow(['comment_id', 'body', 'post_id', 'author_id'])
    return posts_writer, authors_writer, comments_writer


def scrape_api(diff_categories, posts_writer, authors_writer, comments_writer):
    authors_set = set()

    try:
        for cat in diff_categories:
            for post in cat(limit=None):
                if post.author and post.author.name not in authors_set:
                    # Write author data
                    if getattr(post.author, 'id', None) is None:
                        continue
                    authors_writer.writerow([post.author.id, post.author.name, post.author.comment_karma + post.author.link_karma,
                                             datetime.fromtimestamp(post.author.created_utc).isoformat()])
                    authors_set.add(post.author.name)

                # Write post data
                posts_writer.writerow([
                    post.id, post.title, post.selftext.replace(
                        '\n', ' '), post.url, post.score,
                    datetime.fromtimestamp(post.created_utc).isoformat(
                    ), post.author.id if post.author else None
                ])

                # Process comments
                post.comments.replace_more(limit=None)
                for comment in post.comments.list():
                    if comment.author and comment.author.name not in authors_set:
                        # Write author data
                        if getattr(comment.author, 'id', None) is None:
                            continue
                        authors_writer.writerow([comment.author.id, comment.author.name, comment.author.comment_karma +
                                                comment.author.link_karma, datetime.fromtimestamp(comment.author.created_utc)])
                        authors_set.add(comment.author.name)

                    # Write comment data
                    comments_writer.writerow(
                        [comment.id, comment.body, post.id, comment.author.id if comment.author else None])
    except:
        print("Too many requests sent!")


def merge_database():
    posts_df = pd.read_csv('posts.csv')
    comments_df = pd.read_csv('comments.csv')
    authors_df = pd.read_csv('authors.csv')

    posts_with_authors = pd.merge(
        posts_df, authors_df, on='author_id', how='left', suffixes=('_post', '_author'))
    comments_with_authors = pd.merge(
        comments_df, authors_df, on='author_id', how='left', suffixes=('_comment', '_author'))

    combined_df = pd.concat(
        [posts_with_authors, comments_with_authors], axis=0)

    combined_df['post_text'] = combined_df['title'].fillna(
        '') + " " + combined_df['selftext'].fillna('')
    combined_df['body'] = combined_df['body'].fillna('')
    combined_df.to_csv("combined.csv")

    combined_df.to_csv('combined_database.csv', index=False)

    print("Total Reddit Posts and Comments:", len(combined_df))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='dataScraper',
        description='Scrape Data and store in CSV',
        epilog='Text at the bottom of help')

    parser.add_argument("-r", "--subreddit",
                        default="clinicaltrials", required=False)
    parser.add_argument("-f", "--filename",
                        default="", required=False)

    args = parser.parse_args()

    reddit = praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        user_agent=config.user_agent,
    )

    relevant_subreddits = ["clinicaltrials"]

    for submission in reddit.subreddit("test").hot(limit=5):
        print(submission.title)

    query = "clinical trials"
    subreddit = reddit.subreddit(args.subreddit)
    diff_categories = [subreddit.hot, subreddit.new,
                       subreddit.top, subreddit.rising]

    posts_file, authors_file, comments_file = create_csv(args.filename)
    posts_writer, authors_writer, comments_writer = get_writer(
        posts_file, authors_file, comments_file)

    scrape_api(diff_categories, posts_writer, authors_writer, comments_writer)

    posts_file.close()
    authors_file.close()
    comments_file.close()

    merge_database()
