import requests
from bs4 import BeautifulSoup
from datetime import datetime
from db_utils import db_manager

def fetch_hexun_articles():
    """获取和讯网外汇策略文章"""
    url = "https://forex.hexun.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    articles = []
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'gbk'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            strategy_section = soup.find_all('div', class_='subItem1 clearfix')

            if strategy_section:
                for section in strategy_section:
                    for article in section.find_all('a'):
                        article_data = {
                            'title': article.get_text(strip=True),
                            'link': article['href'],
                            'type': 'strategy',
                            'site': 'https://forex.hexun.com/',
                            'date': datetime.now().isoformat(),
                            'image_url': 'https://web.hexun.com/pc/img/logo.png'  # 设置默认logo
                        }
                        articles.append(article_data)
                        print(f"Found article: {article_data['title']}")

    except Exception as e:
        print(f"Error fetching Hexun articles: {e}")

    return articles

def main():
    articles = fetch_hexun_articles()
    if articles:
        # 直接保存到数据库
        db_manager.save_to_supabase(articles, 'strategy', 'cn')
    else:
        print("No articles found")

if __name__ == "__main__":
    main()
