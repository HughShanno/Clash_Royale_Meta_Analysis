# wikiscraper.py
# Author: A.J. Ristino

# This is a scraper that exists in order to scrape card info from the clash royale wiki

import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {'User-Agent' : 
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36' }



# Returns a list of dictionaries containing the title and link suffix to every card's wiki page

def getCards():
    cards = []
    url = 'https://clashroyale.fandom.com/wiki/Card_Overviews'
    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'html.parser')

    collection = soup.find_all('div', {'class':'card-overview'})

    for element in collection:
        element = {
        'title' : element.find('h4').text,
        #'date' : element.find('p', {'class':'home-news-primary-item-date'}).text,
        'link' : element.find('a')['href']
        }
        cards.append(element)

    return(cards)

# returns a few stats on each card formatted as:

# Card name, elixir cost, rarity, Troop/Building/Spell, Arena Unlocked, Release date

'''
def getCardData(title, path):
    statLine = f'{title}'
    url = f'https://clashroyale.fandom.com/{path}'

    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    stats = soup.find_all('div',{'class':['pi-data-value','pi-font']})

    for stat in stats:
        statLine += f', {stat.text}'

    print(statLine)
'''

def getCardData(title, path):
    
    url = f'https://clashroyale.fandom.com/{path}' 
    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    for sibling in soup.find('table', id ='unit-attributes-table').tr.next_siblings:
        child = sibling.text
        statLine = [f'{title}'] + child.split('\n')
        statLine = list(filter(None, statLine))
    
    return(statLine)

def secondaryTroop(title, path,file):
    secondaryStat = [f'{title}']
    url = f'https://clashroyale.fandom.com/{path}' 
    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    result = soup.find("table", id ='unit-attributes-table-secondary')
    print(result)

    if result != None:
        for sibling in soup.find('table', id ='unit-attributes-table-secondary').tr.next_siblings:
            child = sibling.text
            secondaryStat += child.split('\n')
            secondaryStat = list(filter(None, secondaryStat))
        file.write(str(secondaryStat) + '\n')
    else:
        pass


def main():
    cards = getCards()
    file = open('stats.txt','w')
    file2 = open('secondaryStats.txt', 'w')
    for card in cards:
        stats = getCardData(card['title'],card['link'])
        secondaryStats = secondaryTroop(card['title'],card['link'], file2)
        file.write(str(stats) + '\n')
        
        
    file.close()


if __name__ == '__main__':
    main()
