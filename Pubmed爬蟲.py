import time
import requests
from bs4 import BeautifulSoup

def fetch_pubmed_articles(query, max_articles=10000):
    articles_fetched = 0
    start_index = 0
    articles_per_request = 10
    wait_time = 1

    with open('articles.txt', 'w', encoding='utf-8') as article_file:
        while articles_fetched < max_articles:
            url = f'https://pubmed.ncbi.nlm.nih.gov/?term={query}&start={start_index}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            articles = soup.find_all('article', class_='full-docsum')

            if not articles:
                break

            for article in articles:
                title = article.find('a', class_='docsum-title').get_text(strip=True)
                article_link = article.find('a', class_='docsum-title')['href']
                article_response = requests.get(f'https://pubmed.ncbi.nlm.nih.gov{article_link}')
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                abstract = article_soup.find('div', class_='abstract-content')
                abstract_text = abstract.get_text(strip=True) if abstract else 'No abstract available.'

                article_file.write(f'{title}\n')
                article_file.write(f'{abstract_text}\n')
                article_file.write('-' * 80 + '\n')

                articles_fetched += 1
                if articles_fetched >= max_articles:
                    break

            start_index += len(articles)
            time.sleep(wait_time)

            remaining_articles = max_articles - articles_fetched
            requests_needed = remaining_articles / articles_per_request
            total_time = requests_needed * wait_time
            print(f'已獲取 {articles_fetched} 篇文章，預計還需 {total_time:.2f} 秒')

if __name__ == '__main__':
    query = 'fibrosis'
    fetch_pubmed_articles(query, max_articles=10000)
