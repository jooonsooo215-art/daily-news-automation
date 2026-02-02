#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_semiconductor_news(self) -> List[Dict]:
        """Fetch semiconductor news from Yonhap news"""
        articles = []
        try:
            # Yonhap news - Semiconductor category
            url = 'https://www.yna.co.kr/search/index?query=semiconductor&date='
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news items
            items = soup.find_all('a', {'class': 'search-news-link'})[:5]
            for item in items:
                title_elem = item.find('strong')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = item.get('href', '')
                    if title and link:
                        articles.append({
                            'title': title[:120],
                            'url': 'https://www.yna.co.kr' + link if not link.startswith('http') else link,
                            'source': 'Yonhap News',
                            'date': self.today,
                            'category': 'Semiconductor'
                        })
        except Exception as e:
            print(f"Error fetching from Yonhap: {e}")
        
        # Fallback: Try Naver news
        if len(articles) < 2:
            try:
                url = 'https://search.naver.com/search.naver?where=news&query=semiconductor&sort=1'
                response = requests.get(url, headers=self.headers, timeout=10)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find news items in Naver
                items = soup.find_all('a', {'class': 'news_tit'})[:3]
                for item in items:
                    title = item.get_text(strip=True)
                    link = item.get('href', '')
                    if title and 'semiconductor' in title.lower():
                        articles.append({
                            'title': title[:120],
                            'url': link,
                            'source': 'Naver News',
                            'date': self.today,
                            'category': 'Semiconductor'
                        })
            except Exception as e:
                print(f"Error fetching from Naver: {e}")
        
        # If still no articles, add placeholder
        if len(articles) == 0:
            articles.append({
                'title': '반도체 산업 최신 뉴스를 준비 중입니다',
                'url': '#',
                'source': 'News Feed',
                'date': self.today,
                'category': 'Semiconductor'
            })
        
        return articles[:5]
    
    def fetch_macro_news(self) -> List[Dict]:
        """Fetch macroeconomy news from Yonhap news"""
        articles = []
        try:
            # Yonhap news - Economy category
            url = 'https://www.yna.co.kr/search/index?query=economy&date='
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news items
            items = soup.find_all('a', {'class': 'search-news-link'})[:5]
            for item in items:
                title_elem = item.find('strong')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = item.get('href', '')
                    if title and link:
                        articles.append({
                            'title': title[:120],
                            'url': 'https://www.yna.co.kr' + link if not link.startswith('http') else link,
                            'source': 'Yonhap News',
                            'date': self.today,
                            'category': 'Macroeconomy'
                        })
        except Exception as e:
            print(f"Error fetching macro news from Yonhap: {e}")
        
        # Fallback: Try Naver news
        if len(articles) < 2:
            try:
                url = 'https://search.naver.com/search.naver?where=news&query=economy&sort=1'
                response = requests.get(url, headers=self.headers, timeout=10)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.content, 'html.parser')
                
                items = soup.find_all('a', {'class': 'news_tit'})[:3]
                for item in items:
                    title = item.get_text(strip=True)
                    link = item.get('href', '')
                    if title:
                        articles.append({
                            'title': title[:120],
                            'url': link,
                            'source': 'Naver News',
                            'date': self.today,
                            'category': 'Macroeconomy'
                        })
            except Exception as e:
                print(f"Error fetching from Naver: {e}")
        
        # If still no articles, add placeholder
        if len(articles) == 0:
            articles.append({
                'title': '경제 뉴스를 준비 중입니다',
                'url': '#',
                'source': 'News Feed',
                'date': self.today,
                'category': 'Macroeconomy'
            })
        
        return articles[:5]
    
    def collect_all_news(self) -> None:
        """Collect news from all sources"""
        print(f"Collecting news for {self.today}...")
        self.semiconductor_news = self.fetch_semiconductor_news()
        time.sleep(1)  # Be polite to servers
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
        html = f"""<html><head><meta charset="UTF-8"></head><body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">📰 일일 뉴스 요약</h1>
            <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">{today}</p>
        </div>
        
        <div style="margin-top: 30px;">
            <h2 style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-bottom: 20px;">🔧 반도체 산업</h2>"""
        
        if semiconductor_news:
            for i, article in enumerate(semiconductor_news, 1):
                html += f"""<div style="margin-bottom: 20px; padding: 15px; background-color: #f8f9ff; border-left: 4px solid #667eea; border-radius: 5px;">
                <p style="margin: 0 0 8px 0; font-weight: bold; font-size: 15px; color: #333;">{i}. {article['title']}</p>
                <p style="margin: 8px 0 10px 0; font-size: 12px; color: #666; line-height: 1.5;">
                    📅 {article['date']} | 📰 {article['source']}
                </p>"""
                if article['url'] != '#':
                    html += f"<p style="margin: 0;"><a href=\"{article['url']}\" style="color: #667eea; text-decoration: none; font-weight: bold;">전체 기사 읽기 →</a></p>"
                html += "</div>"
        
        html += f"""</div>
        
        <div style="margin-top: 30px;">
            <h2 style="color: #ff6b6b; border-bottom: 3px solid #ff6b6b; padding-bottom: 10px; margin-bottom: 20px;">📊 거시 경제</h2>"""
        
        if macro_news:
            for i, article in enumerate(macro_news, 1):
                html += f"""<div style="margin-bottom: 20px; padding: 15px; background-color: #fff8f6; border-left: 4px solid #ff6b6b; border-radius: 5px;">
                <p style="margin: 0 0 8px 0; font-weight: bold; font-size: 15px; color: #333;">{i}. {article['title']}</p>
                <p style="margin: 8px 0 10px 0; font-size: 12px; color: #666; line-height: 1.5;">
                    📅 {article['date']} | 📰 {article['source']}
                </p>"""
                if article['url'] != '#':
                    html += f"<p style="margin: 0;"><a href=\"{article['url']}\" style="color: #ff6b6b; text-decoration: none; font-weight: bold;">전체 기사 읽기 →</a></p>"
                html += "</div>"
        
        html += """</div>
        
        <div style="margin-top: 40px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
            <p style="margin: 0; font-size: 12px; color: #666;">
                ✉️ 이 이메일은 자동으로 생성되었습니다<br>
                🔄 매일 오전 7시 KST에 전송됩니다
            </p>
        </div>
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
                f"📰 일일 뉴스 요약 - {collector.today}",
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
