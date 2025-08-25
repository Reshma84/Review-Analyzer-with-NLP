import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import nltk
from textblob import TextBlob

# Ensure necessary NLTK data is downloaded
nltk.download('stopwords')
nltk.download('punkt')

# Load pre-trained BERT sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# Function to scrape reviews from an e-commerce site
def scrape_reviews(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    if "amazon" in url:
        return scrape_amazon(url, headers)
    elif "flipkart" in url:
        return scrape_flipkart(url, headers)
    else:
        return {"error": "Website not supported"}

def scrape_amazon(url, headers):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        reviews = []
        for review in soup.find_all("span", class_="a-size-base review-text"):
            reviews.append(review.get_text())

        return {"reviews": reviews}
    except Exception as e:
        return {"error": str(e)}

def scrape_flipkart(url, headers):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        reviews = []
        for review in soup.find_all("div", class_="t-ZTKy"):
            reviews.append(review.get_text())

        return {"reviews": reviews}
    except Exception as e:
        return {"error": str(e)}

# Function to analyze sentiment using BERT
def analyze_sentiment(reviews):
    if not reviews:
        return {"error": "No reviews found"}

    try:
        print(f"Reviews being analyzed: {reviews}")  # Debugging line
        sentiments = sentiment_analyzer(reviews)
        print(f"Sentiment analysis results: {sentiments}")  # Debugging line

        positive = sum(1 for s in sentiments if s['label'] == 'POSITIVE')
        negative = sum(1 for s in sentiments if s['label'] == 'NEGATIVE')
        
        total = len(sentiments)
        positive_percentage = (positive / total) * 100 if total > 0 else 0
        negative_percentage = (negative / total) * 100 if total > 0 else 0
        neutral_percentage = 100 - (positive_percentage + negative_percentage)

        return {
            "overall_score": f"{positive_percentage:.2f}% Positive",
            "sentiment_scores": {
                "positive": positive_percentage,
                "negative": negative_percentage,
                "neutral": neutral_percentage,
            }
        }
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")  # Debugging line
        return {"error": str(e)}

# Function to detect spam reviews using TextBlob
def detect_spam(reviews):
    spam_reviews = []
    for review in reviews:
        analysis = TextBlob(review)
        if analysis.sentiment.polarity < -0.5:  # Example threshold for spam detection
            spam_reviews.append(review)
    return spam_reviews

# Tkinter GUI
class ReviewAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Review Analyzer")
        self.root.geometry("1200x800")

        # URL Input
        self.url_label = tk.Label(root, text="Enter Amazon or Flipkart Product URL:")
        self.url_label.pack(pady=10)
        self.url_entry = tk.Entry(root, width=100)
        self.url_entry.pack(pady=10)

        # Analyze Button
        self.analyze_button = tk.Button(root, text="Analyze Reviews", command=self.analyze_reviews)
        self.analyze_button.pack(pady=10)

        # Results Display
        self.results_label = tk.Label(root, text="Analysis Results", font=("Arial", 16))
        self.results_label.pack(pady=10)

        self.results_text = tk.Text(root, height=20, width=140, state='disabled', bg='#dddddd')
        self.results_text.pack(pady=10)

        # Spam Reviews Display
        self.spam_label = tk.Label(root, text="Spam Reviews Detected", font=("Arial", 16))
        self.spam_label.pack(pady=10)

        self.spam_text = tk.Text(root, height=10, width=140, state='disabled', bg='#dddddd')
        self.spam_text.pack(pady=10)

    def analyze_reviews(self):
        product_url = self.url_entry.get().strip()
        if not product_url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            return

        # Scrape reviews
        scraped_data = scrape_reviews(product_url)
        if "error" in scraped_data:
            messagebox.showerror("Error", scraped_data["error"])
            return

        # Analyze sentiment
        analysis_results = analyze_sentiment(scraped_data["reviews"])
        if "error" in analysis_results:
            messagebox.showerror("Error", analysis_results["error"])
            return

        # Detect spam
        spam_reviews = detect_spam(scraped_data["reviews"])

        # Display results
        self.results_text.config(state='normal')
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"Overall Score: {analysis_results['overall_score']}\n")
        self.results_text.insert(tk.END, f"Positive: {analysis_results['sentiment_scores']['positive']:.2f}%\n")
        self.results_text.insert(tk.END, f"Negative: {analysis_results['sentiment_scores']['negative']:.2f}%\n")
        self.results_text.insert(tk.END, f"Neutral: {analysis_results['sentiment_scores']['neutral']:.2f}%\n")
        self.results_text.config(state='disabled')

        # Display spam reviews
        self.spam_text.config(state='normal')
        self.spam_text.delete("1.0", tk.END)
        if spam_reviews:
            for review in spam_reviews:
                self.spam_text.insert(tk.END, f"- {review}\n")
        else:
            self.spam_text.insert(tk.END, "No spam reviews detected.\n")
        self.spam_text.config(state='disabled')

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ReviewAnalyzerApp(root)
    root.mainloop()
