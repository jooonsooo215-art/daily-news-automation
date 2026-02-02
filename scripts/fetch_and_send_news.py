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
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def fetch_semiconductor_news(self) -> List[Dict]:
        """Fetch semiconductor news from multiple sources with fallbacks"""
        articles = []
        
        # Try multiple search terms for semiconductor news
        search_terms = ['반도체', 'semiconductor', '삼성전자 반도체', 'SK하이닉스']
        
        for term in search_terms:
            if len(articles) >= 3:
                break
                
            print(f"Searching for: {term}")
            
            # Method 1: Try Naver News with improved parsing
            try:
                url = f'https://search.naver.com/search.naver?where=news&query={term}&sort=1&ds=&de=&nso=so:dd,p:1d'
                print(f"Fetching from Naver: {url[:80]}...")
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                print(f"Response status: {response.status_code}, length: {len(response.content)}")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors
                selectors = [
                    {'class': 'news_tit'},
                    {'class': 'api_txt_lines'},
                    {'class': 'news_area'}
                ]
                
                for selector in selectors:
                    items = soup.find_all('a', selector)[:5]
                    print(f"Found {len(items)} items with selector {selector}")
                    
                    for item in items:
                        if len(articles) >= 3:
                            break
                        try:
                            title = item.get_text(strip=True)
                            link = item.get('href', '')
                            
                            if title and link and len(title) > 5:
                                articles.append({
                                    'title': title[:120],
                                    'url': link if link.startswith('http') else f'https://naver.com{link}',
                                    'source': 'Naver News',
                                    'date': self.today,
                                    'category': 'Semiconductor'
                                })
                                print(f"Added article: {title[:50]}...")
                        except Exception as e:
                            print(f"Error processing item: {e}")
                    
                    if len(articles) >= 3:
                        break
                        
            except Exception as e:
                print(f"Error fetching from Naver: {type(e).__name__}: {e}")
            
            # Add small delay
            if len(articles) < 3:
                time.sleep(2)
        
        # Fallback: Add placeholder if no articles found
        if len(articles) == 0:
            print("No articles found, adding placeholder")
            articles.append({
                'title': '반도체 산업 최신 뉴스를 업데이트 중입니다',
                'url': '#',
                'source': 'News Feed',
                'date': self.today,
                'category': 'Semiconductor'
            })
        
        return articles[:5]
    
    def fetch_macro_news(self) -> List[Dict]:
        """Fetch macroeconomy news from multiple sources with fallbacks"""
        articles = []
        
        # Try multiple search terms for macro news
        search_terms = ['경제', 'economy', '금리율', '인플레이션']
        
        for term in search_terms:
            if len(articles) >= 3:
                break
                
            print(f"Searching for macro news: {term}")
            
            try:
                url = f'https://search.naver.com/search.naver?where=news&query={term}&sort=1&ds=&de=&nso=so:dd,p:1d'
                print(f"Fetching from Naver: {url[:80]}...")
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                print(f"Response status: {response.status_code}, length: {len(response.content)}")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                selectors = [
                    {'class': 'news_tit'},
                    {'class': 'api_txt_lines'},
                    {'class': 'news_area'}
                ]
                
                for selector in selectors:
                    items = soup.find_all('a', selector)[:5]
                    print(f"Found {len(items)} items with selector {selector}")
                    
                    for item in items:
                        if len(articles) >= 3:
                            break
                        try:
                            title = item.get_text(strip=True)
                            link = item.get('href', '')
                            
                            if title and link and len(title) > 5:
                                articles.append({
                                    'title': title[:120],
                                    'url': link if link.startswith('http') else f'https://naver.com{link}',
                                    'source': 'Naver News',
                                    'date': self.today,
                                    'category': 'Macroeconomy'
                                })
                                print(f"Added macro article: {title[:50]}...")
                        except Exception as e:
                            print(f"Error processing item: {e}")
                    
                    if len(articles) >= 3:
                        break
                        
            except Exception as e:
                print(f"Error fetching macro news: {type(e).__name__}: {e}")
            
            if len(articles) < 3:
                time.sleep(2)
        
        if len(articles) == 0:
            print("No macro articles found, adding placeholder")
            articles.append({
                'title': '경제 뉴스를 업데이트 중입니다',
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
        time.sleep(1)
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
        <h1 style="margin: 0; font-size: 28px;">🗠️ 일일 뉴스 요약</h1>
        <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">{today}</p>
    </div>
    
    <div style="margin-top: 30px;">
        <h2 style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-bottom: 20px;">🔧 반도체 산업</h2>"""
        
        if semiconductor_news:
            for i, article in enumerate(semiconductor_news, 1):
                html += f"""<div style="margin-bottom: 20px; padding: 15px; background-color: #f8f9ff; border-left: 4px solid #667eea; border-radius: 5px;">
            <p style="margin: 0 0 8px 0; font-weight: bold; font-size: 15px; color: #333;">{i}. {article['title']}</p>
            <p style="margin: 8px 0 10px 0; font-size: 12px; color: #666; line-height: 1.5;">
                📅 {article['date']} | 🗠️ {article['source']}
            </p>"""
                if article['url'] != '#':
                    html += f"<p style=\"margin: 0;\"><a href=\"{article['url']}\" style=\"color: #667eea; text-decoration: none; font-weight: bold;\">전체 기사 읽기 →</a></p>"
                html += "</div>"
        
        html += f"""</div>
    
    <div style="margin-top: 30px;">
        <h2 style="color: #ff6b6b; border-bottom: 3px solid #ff6b6b; padding-bottom: 10px; margin-bottom: 20px;">📈 챰시 경제</h2>"""
        
        if macro_news:
            for i, article in enumerate(macro_news, 1):
                html += f"""<div style="margin-bottom: 20px; padding: 15px; background-color: #fff8f6; border-left: 4px solid #ff6b6b; border-radius: 5px;">
            <p style="margin: 0 0 8px 0; font-weight: bold; font-size: 15px; color: #333;">{i}. {article['title']}</p>
            <p style="margin: 8px 0 10px 0; font-size: 12px; color: #666; line-height: 1.5;">
                📅 {article['date']} | 🗠️ {article['source']}
            </p>"""
                if article['url'] != '#':
                    html += f"<p style=\"margin: 0;\"><a href=\"{article['url']}\" style=\"color: #ff6b6b; text-decoration: none; font-weight: bold;\">전체 기사 읽기 →</a></p>"
                html += "</div>"
        
        html += """</div>
    
    <div style="margin-top: 40px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
        <p style="margin: 0; font-size: 12px; color: #666;">
            ✉️ 이 이메일은 자동으로 생성되었습니다
            <br>
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
                f"🗠️ 일일 뉴스 요약 - {collector.today}",
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
