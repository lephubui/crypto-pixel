import configparser
import openai

# Read configuration file
config = configparser.ConfigParser()
config.read('config.ini')

OPENAI_API_KEY = config['openai']['api_key']

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

def analyze_with_chatgpt(symbol, latest_data, news_articles):
    prompt = f"Analyze the following data for {symbol}:\n\n{latest_data.to_string(index=False)}\n\n"
    prompt += "Here are the latest news articles:\n"
    for article in news_articles:
        prompt += f"- {article['title']}: {article['description']}\n"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    analysis = response['choices'][0]['message']['content'].strip()
    return analysis