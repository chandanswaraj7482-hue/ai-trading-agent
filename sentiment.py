import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def fetch_latest_news(ticker: str) -> list:
    """
    Fetch the latest news headlines from Yahoo Finance.
    """
    # Remove '.NS' for Indian stocks for broader news search, or keep it depending on exact ticker structure.
    search_ticker = ticker.replace(".NS", "")
    url = f"https://finance.yahoo.com/quote/{ticker}/news"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        headlines = []
        # Find news links on Yahoo Finance (this selector might need updates if layout changes)
        for item in soup.find_all('h3', class_='clamp'):
            headlines.append(item.get_text())
            
        return headlines[:5] # Return top 5 headlines
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def analyze_sentiment(ticker: str) -> dict:
    """
    Analyze the sentiment of the latest news.
    """
    headlines = fetch_latest_news(ticker)
    
    if not headlines:
        return {"score": 0, "label": "NEUTRAL", "news": "No recent news found."}
        
    analyzer = SentimentIntensityAnalyzer()
    compound_score = 0
    
    for headline in headlines:
        sentiment = analyzer.polarity_scores(headline)
        compound_score += sentiment['compound']
        
    avg_score = compound_score / len(headlines)
    
    if avg_score > 0.15:
        label = "POSITIVE 🟢"
    elif avg_score < -0.15:
        label = "NEGATIVE 🔴"
    else:
        label = "NEUTRAL ⚪"
        
    return {
        "score": round(avg_score, 2),
        "label": label,
        "news": "\n".join([f"- {h}" for h in headlines])
    }

if __name__ == "__main__":
    result = analyze_sentiment("RELIANCE.NS")
    print(result)
