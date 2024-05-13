from openai import OpenAI
import config
import argparse
import pandas as pd
import time
from transformers import BartTokenizer, BartForConditionalGeneration

client = OpenAI(api_key=config.api_key)
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')


def advanced_personalization(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    # print(response.choices[0])
    return response.choices[0].message.content.strip()


def summarize(text, max_length=5000):
    # Encode the text input and add the EOS token
    inputs = tokenizer.batch_encode_plus(
        [text], max_length=1024, return_tensors='pt', truncation=True)
    # Generate summary
    summary_ids = model.generate(inputs['input_ids'], max_length=max_length,
                                 min_length=200, length_penalty=2.0, num_beams=4, early_stopping=True)
    # Decode and return the summary
    bart_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return bart_summary


def create_prompt(df, user_id):
    role = "Role: You are a conscientious promoter of clinical trials in Health!"
    task = "The task is to recommend users why to paritcipate in clinical trials, you will be given a user's Reddit activity, write a personalized message for making them participate in clinical trials."
    post_text_df = str(df[df["author_id"] == user_id]["post_text"].values[0])
    comment_df = str(df[df["author_id"] == user_id]["body"].values[0])

    prompt = role + task
    # print("here", len(post_text_df))
    if len(post_text_df) > 1:
        # print(post_text_df)
        post_sentiment = int(
            df[df["author_id"] == user_id]['sentiment'].values[0])
        if len(post_text_df) >= 10000:
            post_text_df = summarize(post_text_df)
        print("post length:", len(post_text_df))

        prompt += f"These are the Reddit posts, the user had made about Clinical Trials: \"{post_text_df}\".\n"
        prompt += f"The sentiment of the posts where 1 being positive and -1 being negative, was: {post_sentiment}\n"

    # print("here")
    if len(comment_df) > 1:
        comment_sentiment = int(
            df[df["author_id"] == user_id]['comment_sentiment'].values[0])

        if len(comment_df) >= 10000:
            post_text_df = summarize(comment_df)
        print("comment length:", len(comment_df))
        prompt += f"These are the Reddit comments to other posts that the user has made about Clinical Trials: {comment_df} \n"
        prompt += f"The sentiment of the posts where 1 being positive and -1 being negative, was: {comment_sentiment}\n"

    prompt += "What should the personalized message to this user be? Act like you are talking to that user or sending them an outreach mesaage."

    return prompt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='dataScraper',
        description='Scrape Data and store in CSV',
        epilog='Text at the bottom of help')

    parser.add_argument("-f", "--filename",
                        default="combined.csv", required=False)

    args = parser.parse_args()

    combined_df = pd.read_csv(args.filename)
    users = set(combined_df["author_id"].values)

    # responses = []
    responses = {}
    content_len = 0
    for user_id in sorted(users):
        p = create_prompt(combined_df, user_id)
        # print(p)
        messages = [{"role": "user", "content": p}]
        print(len(messages[0]["content"]))
        response = advanced_personalization(messages)
        print(len(response))
        content_len += len(messages[0]["content"]) + len(response)
        if content_len >= 30000:
            time.sleep(60)
            content_len = 0
        responses[user_id] = response

    with open('users.txt', 'w') as file:
        for item in sorted(users):
            file.write(f"{item}\n")

    responses_df = pd.DataFrame({
        'author_id': responses.keys(),
        'response': responses.values()
    })

    final_df = pd.merge(combined_df, responses_df, on='author_id', how='left')

    final_df = pd.merge(combined_df, responses_df, on='author_id', how='left')
    final_df.to_csv("combined_with_msg.csv")
