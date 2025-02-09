import os
import json
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse

class DBManager:
    def __init__(self):
        # 设置默认的 Supabase 配置
        self.supabase_url = 'https://jfhncvkdqrhasbffxeub.supabase.co'
        self.supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpmaG5jdmtkcXJoYXNiZmZ4ZXViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzg4NTIyNiwiZXhwIjoyMDUzNDYxMjI2fQ.mezMLhqmDWy3oUTS8y9aqFDXgtol7L8ULUvoFUAN3-Y'
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates'
        }

    def delete_old_data(self):
        """删除7天前的数据"""
        try:
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            response = requests.delete(
                f'{self.supabase_url}/rest/v1/rss',
                headers=self.headers,
                params={
                    'update_date': f'lt.{seven_days_ago}'
                }
            )
            if response.status_code == 200:
                print(f"Successfully deleted articles older than {seven_days_ago}")
            else:
                print(f"Error deleting old articles: {response.status_code}")
        except Exception as e:
            print(f"Error deleting old data: {str(e)}")

    def get_existing_links(self, link=None):
        """获取数据库中已存在的链接"""
        try:
            if link:
                # 查询特定链接
                response = requests.get(
                    f'{self.supabase_url}/rest/v1/rss',
                    headers=self.headers,
                    params={
                        'select': 'link',
                        'link': f'eq.{link}'  # 精确匹配链接
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    exists = len(data) > 0
                    print(f"Link {link} exists: {exists}")
                    return exists
                
                print(f"Error checking link: {response.status_code}")
                return False
                
            else:
                # 获取所有链接
                response = requests.get(
                    f'{self.supabase_url}/rest/v1/rss',
                    headers=self.headers,
                    params={
                        'select': 'link',
                        'link': 'neq.null'
                    }
                )
                
                if response.status_code == 200:
                    existing_links = {item['link'] for item in response.json() if item.get('link')}
                    print(f"Found {len(existing_links)} existing links")
                    return existing_links
                
                print(f"Error getting links: {response.status_code}")
                return set()
                
        except Exception as e:
            print(f"Error in get_existing_links: {str(e)}")
            return set() if link is None else False

    def save_to_supabase(self, articles, content_type, nation='cn'):
        """保存文章到 Supabase 数据库"""
        try:
            # 首先删除旧数据
            self.delete_old_data()

            # 准备数据
            data_to_insert = []
            for article in articles:
                # 跳过没有链接的文章
                if not article.get('link'):
                    continue

                # 检查链接是否存在
                if self.get_existing_links(article['link']):
                    print(f"Skipping duplicate article: {article['title']}")
                    continue

                # 从链接中提取网站域名
                site = article.get('site', '')
                if not site and article.get('link'):
                    site = urlparse(article['link']).netloc

                # 确保日期格式正确
                try:
                    date = datetime.fromisoformat(article.get('date', '')).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                article_data = {
                    'title': article.get('title', ''),
                    'link': article['link'],
                    'update_date': date,
                    'image_url': article.get('image_url', ''),
                    'site': site,
                    'nation': nation
                }

                # 根据内容类型设置标志
                if content_type == 'news':
                    article_data['newsFlag'] = 'news'
                elif content_type == 'strategy':
                    article_data['strategyFlag'] = 'strategy'

                data_to_insert.append(article_data)

            if data_to_insert:
                # 插入数据
                response = requests.post(
                    f'{self.supabase_url}/rest/v1/rss',
                    headers=self.headers,
                    json=data_to_insert
                )
                
                if response.status_code in [200, 201]:
                    print(f"Successfully inserted {len(data_to_insert)} articles to Supabase")
                    return response.json()
                else:
                    print(f"Error inserting data: {response.status_code}")
                    print(f"Response content: {response.text}")
                    return None
            
        except Exception as e:
            print(f"Error saving to Supabase: {str(e)}")
            return None

# 创建单例实例
db_manager = DBManager() 