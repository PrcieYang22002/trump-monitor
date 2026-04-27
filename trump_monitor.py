import os
import json
import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitor.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Load environment variables
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

# Keywords configuration based on the user's document
PROFANE_KEYWORDS = ["vulgar", "expletive", "cursed", "swore", "profanity"]
OUTRAGEOUS_KEYWORDS = ["outrageous", "shocking claim", "bizarre", "unhinged", "meltdown", "rant", "explosive"]
INSULT_KEYWORDS = ["insulted", "slammed", "bashed", "mocked", "slams"]
POLICY_KEYWORDS = ["executive order"]
ACTION_KEYWORDS = ["threatens"]

ALL_KEYWORDS = PROFANE_KEYWORDS + OUTRAGEOUS_KEYWORDS + INSULT_KEYWORDS + POLICY_KEYWORDS + ACTION_KEYWORDS

def load_json(filepath, default_val):
    if not os.path.exists(filepath):
        return default_val
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {filepath}. Using default.")
        return default_val

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def fetch_news(api_key):
    """Fetch recent news articles about Donald Trump using NewsAPI."""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "Trump",
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": api_key,
        "pageSize": 50
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        else:
            logging.error(f"NewsAPI returned an error: {data.get('message')}")
            return []
    except Exception as e:
        logging.error(f"Failed to fetch news: {e}")
        return []

def analyze_articles(articles, sent_articles_urls):
    """Filter articles based on keywords, relevance, and if they've been sent already."""
    matching_articles = []
    trump_names = ["trump", "donald"]
    
    for article in articles:
        url = article.get("url")
        if not url or url in sent_articles_urls:
            continue
            
        title = (article.get("title") or "").lower()
        description = (article.get("description") or "").lower()
        
        # 1. Relevance check: Trump must be mentioned in the headline (main subject)
        if not any(name in title for name in trump_names):
            continue
            
        # 2. Proximity check: Keyword and Trump must appear together in the same field
        has_match = False
        for keyword in ALL_KEYWORDS:
            # Check title
            if keyword in title and any(name in title for name in trump_names):
                has_match = True
                break
            # Check description
            if keyword in description and any(name in description for name in trump_names):
                has_match = True
                break
                
        if has_match:
            matching_articles.append(article)
            
    return matching_articles

def send_email_alert(article, config):
    """Send an email notification for the controversial article."""
    sender = os.getenv("GMAIL_SENDER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    recipients = config.get("recipient_emails", [])
    
    if not sender or not password or not recipients:
        logging.error("Email credentials or recipients are missing in config.")
        return False

    headline = article.get("title", "No Title")
    summary = article.get("description", "No Summary")
    source = article.get("source", {}).get("name", "Unknown Source")
    link = article.get("url", "#")
    timestamp = article.get("publishedAt", datetime.now().isoformat())
    
    subject = f"🚨 Trump Alert: {headline[:50]}..."
    
    # Constructing HTML email body
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #d9534f;">🚨 Trump Controversial Statement Alert</h2>
        <p><strong>Headline:</strong> {headline}</p>
        <p><strong>Summary:</strong> {summary}</p>
        <p><strong>Source:</strong> {source}</p>
        <p><strong>Published At:</strong> {timestamp}</p>
        <br>
        <a href="{link}" style="background-color: #0275d8; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">Read Full Article</a>
      </body>
    </html>
    """
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    
    msg.attach(MIMEText(html_body, "html"))
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        logging.info(f"Successfully sent email alert for: {headline}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    sent_articles_path = os.path.join(base_dir, "sent_articles.json")
    
    logging.info("Starting Trump Monitor (Single Execution)")
    
    config = load_json(config_path, None)
    if not config:
        logging.error(f"Configuration file not found at {config_path}. Exiting.")
        return
        
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key or api_key == "YOUR_NEWSAPI_KEY_HERE":
        logging.error("Please set a valid NewsAPI key in .env file.")
        return

    sent_urls = load_json(sent_articles_path, [])
    
    logging.info("Fetching latest news...")
    articles = fetch_news(api_key)
    logging.info(f"Fetched {len(articles)} articles.")
    
    controversial_articles = analyze_articles(articles, set(sent_urls))
    logging.info(f"Found {len(controversial_articles)} new controversial articles.")
    
    for article in controversial_articles:
        success = send_email_alert(article, config)
        if success:
            url = article.get("url")
            if url:
                sent_urls.append(url)
                
    # Save the updated list of sent articles
    save_json(sent_articles_path, sent_urls)
    logging.info("Finished execution.")

if __name__ == "__main__":
    main()
