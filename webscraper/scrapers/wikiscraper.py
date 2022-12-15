# wikiscraper.py
# Author: A.J. Ristino

# This is a scraper that exists in order to scrape card info from the clash royale wiki





import requests
from bs4 import BeautifulSoup

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



def getUniversalTraits():

    # getUniversalTraits: 

    # returns immutable traits present in all cards as a list of lists, formatted as:

    # Card name, elixir cost, rarity, Troop/Building/Spell, Arena Unlocked, Release date

    cards = getCards()
    traitsList = []

    for card in cards:
        name = card['title']
        traits = [name]
        url = f'https://clashroyale.fandom.com/{name}'
        r = requests.get(url, headers = headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        for sibling in soup.find_all('div',{'class':['pi-data-value','pi-font']}):
            child = sibling.text
            traits += child.split('\n')
            traits = list(filter(None, traits))
        print(traits)
        
        traitsList.append(traits)
    
    return(traitsList)




def getSpellAttributeTitles():

    # This came up because of complications with recording the attributes of spells

    # The muppets over at the CR wiki didn't standardize how they ordered attributes

    # So my solution was to write the order of the attributes and then the attributes in a matching order 
    # into a document called spellAttributes.txt

    # Ouputs order of attributes and then the corresponding attributes as two lists with matching [0] entries.

    cards = getCards()
    file = open('spellAttributes.txt','w')    
    for card in cards:
        statLine = []
        name = card['title']
        url = f'https://clashroyale.fandom.com/{name}' 
        r = requests.get(url, headers = headers)
        soup = BeautifulSoup(r.text, 'html.parser')


        for sibling in soup.find('table', id ='unit-attributes-table').tr.next_siblings:
            child = sibling.text
            statLine = [card['title']] + child.split('\n')
            statLine = list(filter(None, statLine))
    
        
        if 'Spell' in statLine:
            attributes = [card['title'], 'Cost']
            for sibling in soup.find('table', id ='unit-attributes-table').th.next_siblings:
                child = sibling.text
                attributes += child.split('\n')
                attributes = list(filter(None, attributes))

            file.write(str(attributes) + '\n')
            file.write(str(statLine) + '\n')
            

def getCardData(title, path):

    # This is the function that returns the data (not the titles) found in the attributes table of all cards on the CR Wiki
    
    url = f'https://clashroyale.fandom.com/{path}' 
    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    print(url)
    for sibling in soup.find('table', id ='unit-attributes-table').tr.next_siblings:
        child = sibling.text
        statLine = [f'{title}'] + child.split('\n')
        statLine = list(filter(None, statLine))
    
    if 'Spell' in statLine:
        return('Spell')
    else:
        return(statLine)

def secondaryTroop(title, path):

    # Function used to gather stats of secondary troops, which certain CR cards have as a mechanic

    url = f'https://clashroyale.fandom.com/{path}' 
    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    result = soup.find("table", id ='unit-attributes-table-secondary')
    
    if result is None:
        pass            
    else:
        secondaryStat = [f'{title}']
        for sibling in soup.find('table', id ='unit-attributes-table-secondary').tr.next_siblings:
            child = sibling.text
            secondaryStat += child.split('\n')
            secondaryStat = list(filter(None, secondaryStat))
        
        # This is poor form, I get it, but what are the odds they do the E-golem gimmick again?

        if title == 'Elixir Golem':
                tertiaryStat = [f'{title}']
                for sibling in soup.find('table', id ='unit-attributes-table-tertiary').tr.next_siblings:
                    child = sibling.text
                    tertiaryStat += child.split('\n')
                    tertiaryStat = list(filter(None, tertiaryStat))
                secondaryStat += tertiaryStat
        print(secondaryStat)
        return(secondaryStat)
    

  
    

# Return Primary Attributes as list
def rpaal():

    # Returns all primary attributes of troops + buildings and secondary troops + buildings

    cards = getCards()
    cardAttributes = []
    secondaryCardAttributes = []
    for card in cards:
        
        secondary = secondaryTroop(card['title'],card['link'])

        if secondary is not None:
            secondaryCardAttributes += secondary
        else:
            pass

        stats = getCardData(card['title'],card['link'])
        if stats == 'Spell':
            pass
        else:
            cardAttributes += stats
    
        

    return([cardAttributes, secondaryCardAttributes])

    

def writeStatsToFile():

    # Created for testing purposes, writes all troop/building attributes into a file
    
    cards = getCards()
    file = open('attributes.txt','w')
    file2 = open('secondaryAttributes.txt', 'w')
    for card in cards:

        troop = getCardData(card['title'],card['link'])

        if troop == 'Spell':
            pass
        else:
            file.write(str(troop) + '\n')
        
        secondaryStats = secondaryTroop(card['title'],card['link'])

        if  secondaryStats is not None:
            file2.write(str(secondaryStats) + '\n')
        else:
            pass

        
       
        
        
    file.close()

def main():
    #writeStatsToFile()
    #getSpellAttributeTitles()
    #print(rpaal())
    print(getUniversalTraits())
   



if __name__ == '__main__':
    main()
