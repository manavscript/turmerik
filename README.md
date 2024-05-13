# Clinical Trials Sentiment Analysis

# Files:
1. config.py: It contains all the secrets of the API
2. data.py: This is responsible for scraping and collecting the data into CSV
3. get_info.py: For a specific user you can get the sentiments and what personalized message to send
4. gpt_message.py: This connects to the OpenAI API and gets the personalized message from it
5. sentiment_analysis.py: Based from the data generated we get the sentiments

## Environment

There is a conda environment with all the packages installed. There may be some missing here and there but I have verified it once.

` conda create -f environment.yml `

# Order of the Pipeline and Commands

1. To get data, comments and posts: ` python3.12 data.py --subreddit clinicaltrials `
2. To get sentiments and store: ` python3.12 sentiment_analysis.py --filename combined.csv  `
3. To get the OpenAI personalized messages: `python3.12 gpt_message.py --filename updated_sentiment_data.csv  `
4. To look at a user info `python3.12 get_info.py --filename combined_with_msg.csv  --user_id gtg1j`

There will be intermediate CSV files created which you can use to verify the results


