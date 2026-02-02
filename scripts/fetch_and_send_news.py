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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def fetch_semiconductor_news(self) -> List[Dict]:
        """Fetch semiconductor industry news from multiple sources"""
        articles = []
        
        # Source 1: RSS feed from tech news
        try:
            response = requests.get(
                'https://feeds.bloomberg.com/markets/news.rss',
                headers=self.headers,
                timeout=10
            )
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item', limit=5)
            
            for item in items:
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                # Filter for semiconductor-related content
                if title and ('chip' in title.text.lower() or 'semiconductor' in title.text.lower() or 
                             'tsmc' in title.text.lower() or 'samsung' in title.text.lower() or
                             'intel' in title.text.lower()):
                    articles.append({
                        'title': title.text[:100] if title else 'N/A',
                        'url': link.text if link else '#',
                        'source': 'Bloomberg',
                        'date': self.today,
                        'category': 'Semiconductor',
                        'description': description.text[:200] if description else ''
                    })
        except Exception as e:
            print(f"Error fetching from Bloomberg: {e}")
        
        # Source 2: Tech Crunch-like content
        try:
            response = requests.get(
                'https://feeds.engadget.com/webfeeds/rss2/gadgets/',
                headers=self.headers,
                timeout=10
            )
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item', limit=5)
            
            for item in items:
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                
                if title and ('chip' in title.text.lower() or 'semiconductor' in title.text.lower()):
                    articles.append({
                        'title': title.text[:100] if title else 'N/A',
                        'url': link.text if link else '#',
                        'source': 'Engadget',
                        'date': self.today,
                        'category': 'Semiconductor',
                        'description': description.text[:200] if description else ''
                    })
        except Exception as e:
            print(f"Error fetching from Engadget: {e}")
        
        # If we don't have enough articles from feeds, add placeholder
        if len(articles) == 0:
            articles = [{
                'title': '[업데이트 대기 중] 반도체 산업 뉴스',
                'url': '#',
                'source': 'News Feed',
                'date': self.today,
                'category': 'Semiconductor',
                'description': '현재 피드에서 반도체 관련 뉴스를 수집 중입니다.'
            }]
        
        return articles[:5]
    
    def fetch_macro_news(self) -> List[Dict]:
        """Fetch macroeconomy news from multiple sources"""
        articles = []
        
        # Source 1: Bloomberg Economics
        try:
            response = requests.get(
                'https://feeds.bloomberg.com/markets/news.rss',
                headers=self.headers,
                timeout=10
            )
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item', limit=5)
            
            for item in items:
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                
                if title and any(keyword in title.text.lower() for keyword in 
                               ['economy', 'interest rate', 'inflation', 'market', 'fed', 'gdp', '금리', '경제']):
                    articles.append({
                        'title': title.text[:100] if title else 'N/A',
                        'url': link.text if link else '#',
                        'source': 'Bloomberg',
                        'date': self.today,
                        'category': 'Macroeconomy',
                        'description': description.text[:200] if description else ''
                    })
        except Exception as e:
            print(f"Error fetching macroeconomy news: {e}")
        
        # Source 2: Reuters
        try:
            response = requests.get(
                'https://feeds.reuters.com/finance/markets',
                headers=self.headers,
                timeout=10
            )
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item', limit=5)
            
            for item in items:
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                
                articles.append({
                    'title': title.text[:100] if title else 'N/A',
                    'url': link.text if link else '#',
                    'source': 'Reuters',
                    'date': self.today,
                    'category': 'Macroeconomy',
                    'description': description.text[:200] if description else ''
                })
        except Exception as e:
            print(f"Error fetching from Reuters: {e}")
        
        # If we don't have enough articles, add placeholder
        if len(articles) == 0:
            articles = [{
                'title': '[업데이트 대기 중] 거시 경제 뉴스',
                'url': '#',
                'source': 'News Feed',
                'date': self.today,
                'category': 'Macroeconomy',
                'description': '현재 피드에서 거시 경제 관련 뉴스를 수집 중입니다.'
            }]
        
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
        html = f"""<html><head><meta charset="UTF-8"></head><body style="font-family: Arial, sans-serif;">
        <h1 style="color: #1e88e5;">📰 Daily News Summary - {today}</h1>
        <h2 style="color: #0d47a1; border-bottom: 3px solid #1e88e5; padding-bottom: 10px;">🔧 Semiconductor Sector</h2>"""
        
        for i, article in enumerate(semiconductor_news, 1):
            html += f"""<div style="margin: 15px 0; padding: 12px; background-color: #f5f5f5; border-left: 4px solid #1e88e5; border-radius: 4px;">
            <p style="margin: 5px 0;"><strong style="font-size: 14px;">{i}. {article['title']}</strong></p>
            <p style="font-size: 12px; color: #666; margin: 5px 0;">
                📅 {article['date']} | 📌 {article['source']}
            </p>"""
            if article.get('description'):
                html += f"<p style="font-size: 13px; color: #333; margin: 8px 0;">{article['description']}</p>"
            if article['url'] != '#':
                html += f"<p style="margin: 8px 0;"><a href=\"{article['url']}\" style="color: #1e88e5; text-decoration: none;">➡️ Read full article</a></p>"
            html += "</div>"
        
        html += """<h2 style="color: #0d47a1; border-bottom: 3px solid #1e88e5; padding-bottom: 10px; margin-top: 30px;">📊 Macroeconomy</h2>"""
        
        for i, article in enumerate(macro_news, 1):
            html += f"""<div style="margin: 15px 0; padding: 12px; background-color: #f5f5f5; border-left: 4px solid #ffa726; border-radius: 4px;">
            <p style="margin: 5px 0;"><strong style="font-size: 14px;">{i}. {article['title']}</strong></p>
            <p style="font-size: 12px; color: #666; margin: 5px 0;">
                📅 {article['date']} | 📌 {article['source']}
            </p>"""
            if article.get('description'):
                html += f"<p style="font-size: 13px; color: #333; margin: 8px 0;">{article['description']}</p>"
            if article['url'] != '#':
                html += f"<p style="margin: 8px 0;"><a href=\"{article['url']}\" style="color: #ffa726; text-decoration: none;">➡️ Read full article</a></p>"
            html += "</div>"
        
        html += """<hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
        <p style="font-size: 11px; color: #999; text-align: center; margin-top: 20px;">
            ✉️ This email was automatically generated by Daily News Automation System<br>
            🔄 Sent daily at 7 AM KST
        </p>
        </body></html>"""
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
