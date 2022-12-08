# scraperV2.py
# Author: A.J. Ristino
# Special thanks to John Watson Rooney

# Second version of the scraper build in V1, this version is an attempt to scrape from the https://clashroyale.com/blog/news/ page

import requests
from bs4 import BeautifulSoup
from lxml import html

headers = {'User-Agent' : 
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36' }

articleList = [] 

def getArticles():
    url = 'https://clashroyale.com/blog/news/'
    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'html.parser')

    articles = soup.find_all('div', {'class':'home-news-primary-item'})

    for article in articles:
        article = {
        'title' : article.find('h3').text,
        'date' : article.find('p', {'class':'home-news-primary-item-date'}).text,
        'link' : article.find('a', {'class':'js-click'})['href']
        }
        articleList.append(article)

def getInfo(articleList):
    file = open("text.txt", "w") 

    for article in articleList:
        response = requests.get(article['link'])
        # Establish that tree root is the response from inserted URL
        tree = html.fromstring(response.text)

        # Add all instances of div class that contains press release info to a list
        paragraphs = tree.xpath('//div[@class="textBlock__wrapper"]')

        # Create a .txt file
        

        # Using first item in div instance list, add all text within divs
        text = str(paragraphs[0].xpath("//div[@class='textBlock__wrapper']//text()"))

        file.write(text)
    
    file.close()

def processTxt():
    with open('text.txt', 'r+') as f:
        lines = f.readlines()
        new_lines = [line.replace('\\n', '\n').replace('\\t','\t').replace("', '",'') for line in lines]
        f.seek(0)
        f.writelines(new_lines)
        f.truncate()

def main():    
    getArticles()
    getInfo(articleList)
    processTxt()


if __name__ == '__main__':
    main()


