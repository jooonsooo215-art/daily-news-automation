#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Environment variables
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

class NewsCollector:
    def __init__(self):
        self.semiconductor_news = []
        self.macro_news = []
        self.today = datetime.now().strftime('%Y-%m-%d')
    
    def fetch_semiconductor_news(self) -> List[Dict]:
        """Fetch semiconductor industry news"""
        articles = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            # Search for semiconductor news
            urls = [
                'https://search.naver.com/search.naver?query=semiconductor&nso=so:r,p:1d',
                'https://search.naver.com/search.naver?query=TSMC&nso=so:r,p:1d',
                'https://search.naver.com/search.naver?query=Samsung&nso=so:r,p:1d',
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.content, 'html.parser')
                    news_items = soup.find_all('a', {'class': 'news_tit'})
                    for item in news_items[:3]:
                        title = item.get_text(strip=True)
                        link = item.get('href', '')
                        if title and link:
                            articles.append({
                                'title': title,
                                'url': link,
                                'source': 'Naver News',
                                'date': self.today,
                                'category': 'Semiconductor'
                            })
                except Exception as e:
                    print(f"Error fetching from {url}: {e}")
        except Exception as e:
            print(f"Error in fetch_semiconductor_news: {e}")
        
        return articles[:5]
    
    def fetch_macro_news(self) -> List[Dict]:
        """Fetch macroeconomy news"""
        articles = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            urls = [
                'https://search.naver.com/search.naver?query=macroeconomy&nso=so:r,p:1d',
                'https://search.naver.com/search.naver?query=interest rate&nso=so:r,p:1d',
                'https://search.naver.com/search.naver?query=stock market&nso=so:r,p:1d',
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.content, 'html.parser')
                    news_items = soup.find_all('a', {'class': 'news_tit'})
                    for item in news_items[:3]:
                        title = item.get_text(strip=True)
                        link = item.get('href', '')
                        if title and link:
                            articles.append({
                                'title': title,
                                'url': link,
                                'source': 'Naver News',
                                'date': self.today,
                                'category': 'Macroeconomy'
                            })
                except Exception as e:
                    print(f"Error fetching from {url}: {e}")
        except Exception as e:
            print(f"Error in fetch_macro_news: {e}")
        
        return articles[:5]
    
    def collect_all_news(self) -> None:
        """Collect news from all sources"""
        print(f"Collecting news for {self.today}...")
        self.semiconductor_news = self.fetch_semiconductor_news()
        self.macro_news = self.fetch_macro_news()
        print(f"Collected {len(self.semiconductor_news)} semiconductor articles")
        print(f"Collected {len(self.macro_news)} macroeconomy articles")

class EmailSender:
    def __init__(self):
        self.sender = GMAIL_USER
        self.password = GMAIL_APP_PASSWORD
    
    def send_email(self, recipient: str, subject: str, body_html: str) -> bool:
        """Send email with HTML content"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = recipient
            msg.attach(MIMEText(body_html, 'html', 'utf-8'))
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender, self.password)
                server.sendmail(self.sender, recipient, msg.as_string())
            
            print(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def create_email_body(self, semiconductor_news: List[Dict], macro_news: List[Dict], today: str) -> str:
        """Create HTML email body with news articles"""
        html = f"""<html><head><meta charset=\"UTF-8\"></head><body>
        <h1 style=\"color: #1e88e5;\">Daily News Summary - {today}</h1>
        <h2 style=\"color: #0d47a1;\">Semiconductor Sector</h2>"""
        
        for i, article in enumerate(semiconductor_news, 1):
            html += f"""<div style=\"margin: 10px 0; padding: 10px; background-color: #f5f5f5;\">
            <p><strong>{i}. {article['title']}</strong></p>
            <p style=\"font-size: 12px; color: #666;\">Date: {article['date']} | Source: {article['source']}</p>
            <p><a href=\"{article['url']}\">Read full article</a></p>
            </div>"""
        
        html += "<h2 style=\"color: #0d47a1;\">Macroeconomy</h2>"
        
        for i, article in enumerate(macro_news, 1):
            html += f"""<div style=\"margin: 10px 0; padding: 10px; background-color: #f5f5f5;\">
            <p><strong>{i}. {article['title']}</strong></p>
            <p style=\"font-size: 12px; color: #666;\">Date: {article['date']} | Source: {article['source']}</p>
            <p><a href=\"{article['url']}\">Read full article</a></p>
            </div>"""
        
        html += "<hr/><p style=\"font-size: 12px; color: #999;\">This email was automatically generated.</p></body></html>"
        return html

def main():
    """Main execution function"""
    print("Starting daily news automation...")
    try:
        # Collect news
        collector = NewsCollector()
        collector.collect_all_news()
        
        # Send email
        if GMAIL_USER and GMAIL_APP_PASSWORD and RECIPIENT_EMAIL:
            sender = EmailSender()
            email_body = sender.create_email_body(
                collector.semiconductor_news,
                collector.macro_news,
                collector.today
            )
            sender.send_email(
                RECIPIENT_EMAIL,
                f"Daily News Summary - {collector.today}",
                email_body
            )
        else:
            print("Warning: Email credentials not configured")
        
        print("Daily news automation completed successfully")
    except Exception as e:
        print(f"Error in main execution: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
