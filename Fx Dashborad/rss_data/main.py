import time
from rss_parser import RSSParser
from hexun import fetch_hexun_articles
from db_utils import db_manager

def run_rss_parser():
    """运行RSS解析器"""
    try:
        print("\n=== Starting RSS Parser ===")
        parser = RSSParser()
        
        # 分别处理新闻和策略
        for content_type in ['news', 'strategy']:
            print(f"\nProcessing {content_type}...")
            articles_by_lang = parser.parse_all_feeds(content_type)
            
            # 检查是否成功获取到文章
            total_articles = sum(len(articles) for articles in articles_by_lang.values())
            print(f"Total {content_type} articles found: {total_articles}")
            
    except Exception as e:
        print(f"Error in RSS Parser: {str(e)}")

def run_hexun_crawler():
    """运行和讯网爬虫"""
    try:
        print("\n=== Starting Hexun Crawler ===")
        articles = fetch_hexun_articles()
        if articles:
            db_manager.save_to_supabase(articles, 'strategy', 'cn')
            print(f"Total Hexun articles found: {len(articles)}")
        else:
            print("No articles found from Hexun")
            
    except Exception as e:
        print(f"Error in Hexun Crawler: {str(e)}")

def main():
    print("=== Starting RSS and News Crawlers ===")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 运行RSS解析器
        run_rss_parser()
        
        # 运行和讯网爬虫
        run_hexun_crawler()
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")
    
    print(f"\nEnd time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=== Crawling Complete ===")

if __name__ == "__main__":
    main() 