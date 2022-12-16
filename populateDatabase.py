import requests
import json
import psycopg2
import psqlconfig as config
import apikey
from bs4 import BeautifulSoup
import time
import datetime



'''
apikey and psqlconfig are external files that contain secure variable inputs

apikey contains one variable: key
key contains a clash royale api key in string form

psqlconfig contains 3 variables: database, user, and password, which must be set after the user creates themselves a database
'''


class externalDataCollector():
    '''
    This class provides the framework to populate a database with clash royale metadata
    '''


    def __init__(self):
        conn = self.connect()
        self.cur = conn.cursor()
        self.__createTables('createTables.sql')
        print("Created Tables")
        numcards = self.__createCards()
        print("Created Cards")
        self.__createCatchall(numcards)
        print("Created Catchall")
        self.__updateCardStats()
        print("Updated Cards")
        self.populateDatabaseWithBattles()
        print("Populated Database with Battle data")
        conn.commit()
        #need to add functionality for remaining card statistics
    
    def connect(self):
        '''
        Establishes a connection to the database.
        
        Returns: a database connection.

        Note: exits if a connection cannot be established.
        '''
        try:
            connection = psycopg2.connect(database=config.database, user=config.user, password=config.password, host="localhost")
        except Exception as e:
            print("Connection error: ", e)
            exit()
        return connection

    def __createTables(self, filename):
        '''
        runs the createTables script to create all relevant database tables from scratch
        '''
        fd = open(filename, 'r')
        sqlFile = fd.read()
        fd.close()
        sqlCommands = sqlFile.split(';')
        del sqlCommands[-1]

        for command in sqlCommands:
            try:
                self.cur.execute(command)
            except Exception as e:
                print("Command skipped: ", e)

    def __createCards(self):
        '''
        Populates the cards datatable in the database
        '''
        cards = self.__apicall('cards')
        raritydict = {14: "Common", 12: "Rare", 9: "Epic", 6: "Legendary", 4: "Champion"}
        for card in cards:
            data = [card['id'],card['name'],card['iconUrls']['medium'],0,"2000-01-01",0,raritydict[card['maxLevel']],0,0]
            self.__insertCard(data)
        return len(cards)

    def __insertCard(self, data):
        '''
        Given cleaned information about a card, inserts the card into the cards datatable
        '''
        query = "INSERT INTO cards (cardID, cardName, cardImage, elixirCost, releaseDate, minTrophies, rarity, numGames, numWins, cardType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'')"
        try:
            self.cur.execute(query, (data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8]))
        except Exception as e:
            print("Card Insertion Error:",e)
            exit()
        
    
    def __updateCardStats(self):
        arenadict = {'Training Camp': 0, 'Goblin Stadium': 0, 'Bone Pit': 300, 'Barbarian Bowl': 600, 'Spell Valley': 1000, "Builder's Workshop": 1300, "P.E.K.K.A.'s Playhouse": 1600, "P.E.K.K.A's Playhouse": 1600, 'Royal Arena': 2000, 'Frozen Peak': 2300, "Jungle Arena": 2600, "Hog Mountain": 3000, "Electro Valley": 3400, "Spooky Town": 3800, "Rascal's Hideout": 4200, "Serenity Peak": 4600, "Miner's Mine": 5000, "Executioner's Kitchen": 5500, "Royal Crypt": 6000, "Silent Sanctuary": 6500, "Dragon Spa": 7000, "Legendary Arena":7500}
        for card in self.__getUniversalTraits():
            query = "UPDATE cards SET elixirCost = %s, releaseDate = %s, minTrophies = %s, cardType = %s WHERE cardName = %s"
            try:
                newtime = datetime.datetime.strptime(card[-1], r"%d %B %Y")
                newtime = datetime.datetime.strftime(newtime, r"%Y-%m-%d")
            except:
                newtime = datetime.datetime.strptime(card[-1][:-8] + card[-1][-5:], r"%B %d %Y")
                newtime = datetime.datetime.strftime(newtime, r"%Y-%m-%d")
            if card[0] == 'Mirror':
                card[1] = 0
            try:
                self.cur.execute(query, (card[1],newtime,arenadict[card[-2]],card[-3],card[0]))
            except Exception as e:
                print("Card update error:",e)
                exit()
    

    def __getUniversalTraits(self):

        # getUniversalTraits: 

        # returns immutable traits present in all cards as a list of lists, formatted as:

        # Card name, elixir cost, rarity, Troop/Building/Spell, Arena Unlocked, Release date

        cards = self.getCards()
        traitsList = []
        headers = {'User-Agent' : 
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36' }
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
    
    def getCards(self):
        cards = []
        url = 'https://clashroyale.fandom.com/wiki/Card_Overviews'
        headers = {'User-Agent' : 
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36' }

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


    def __createCatchall(self, numcards):
        '''
        Creates the catchall table given the number of cards in order to automaticall populate one column
        '''
        query = "INSERT INTO catchall (id, numMatches, numCards, numDecks) VALUES (0,0,%s,0)"
        try:
            self.cur.execute(query, (numcards,))
        except Exception as e:
            print("Error creating catchall:",e)
            exit()


    def __apicall(self, extension, extraparams={},items=True):
        '''
        Makes a call to the clash royale API based on the given url extension and parameters for the call
        '''
        url = 'https://api.clashroyale.com/v1/'
        key = apikey.key
        params = {'Authorization': 'Bearer ' + key}
        for key, value in extraparams.items():
            params[key] = value
        response = requests.get(url + extension, params=params)
        if items:
            return response.json()['items']
        return response.json()

    def __getTopClanTags(self, rating=73900):
        '''
        Collects the tags for every clan with a rating above the passed in rating, in order to collect the top clans
        '''
        extension = 'clans'
        extraparams = {'minScore': rating}
        clans = self.__apicall(extension, extraparams)
        clantags = []
        for clan in clans:
            tag = clan['tag']
            tag = '%23' + tag[1:] #remove the hashtag and replace it with %23 so the URL accepts it
            clantags.append(tag)
        return clantags

    def __getTopPlayers(self, rating=73900):
        '''
        Collects the tags for each player in each clan with a rating above the input rating.
        '''
        tags = self.__getTopClanTags(rating)
        players = []
        for tag in tags:
            extension = 'clans/' + tag + '/members'
            response = self.__apicall(extension)
            for member in response:
                memtag = member['tag']
                memtag = '%23' + memtag[1:] #remove the hashtag and replace it with %23 so the URL accepts it
                players.append(memtag)
        return players

    def populateDatabaseWithBattles(self):
        '''
        The main function to be called in the class.
        Collects the tags from top players, finds the battle data for each player, and adds the battle data into the database
        '''
        print("Started battle collection")
        players = self.__getTopPlayers()
        print("Finished Collecting Players")
        numMatches = 0
        numplayers = len(players)
        i = 0
        for player in players:
            print("Collecting Battle data for player " + str(i) + "/" + str(numplayers))
            i += 1
            extension = 'players/' + player + '/battlelog'
            battles = self.__apicall(extension,items=False)
            for battle in battles:
                self.__addBattleToDataBase(battle)
                numMatches += 1


    def __updateNumMatches(self):
        '''
        Updates the total number of matches by the passed amount
        '''
        query = "UPDATE catchall SET numMatches = numMatches + 1 WHERE id = 0"
        try:
            self.cur.execute(query)
        except Exception as e:
            print("Data aggregation update error:",e)
            exit()


    def __addBattleToDataBase(self, battle):
        '''
        Given battle data, updates the database to account for the battle
        '''
        if battle['gameMode']['name'] != 'Ladder':
            return
        for team in ['team','opponent']:
            data = self.__getPlayerData(battle,team)
            key = self.__addToDeckTable(data)
            self.__addToDeckStats(data,key)
            self.__addToCards(data)
        self.__updateNumMatches()


    def __getPlayerData(self, battle, team):
        '''
        Strips useful data from battle data such as a player's deck, win, and trophy count
        '''
        data = {}
        deck = []
        for card in battle[team][0]['cards']:
            deck.append(card['id'])
        deck.sort()
        trophycount = battle[team][0]['startingTrophies']
        win = 1
        if team == 'team':
            if battle[team][0]['crowns'] < battle['opponent'][0]['crowns']:
                win = 0
        else:
            if battle[team][0]['crowns'] < battle['team'][0]['crowns']:
                win = 0
        data = {'deck': deck, 'trophyCount': trophycount, 'win': win}
        return data

    def __addToDeckTable(self, data):
        '''
        Checks if a deck has already been recorded, and if not updates the table to insert the deck
        returns the deckID associated with the deck
        '''
        query = "SELECT deckID FROM cardsInDeck WHERE card1 = %s AND card2 = %s AND card3 = %s AND card4 = %s AND card5 = %s AND card6 = %s AND card7 = %s AND card8 = %s"
        deck = data['deck']
        try:
            self.cur.execute(query, (deck[0],deck[1],deck[2],deck[3],deck[4],deck[5],deck[6],deck[7]))
            return self.cur.fetchone()[0]
        except:
            query = "INSERT INTO cardsInDeck (card1, card2, card3, card4, card5, card6, card7, card8) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
            self.cur.execute(query,(deck[0],deck[1],deck[2],deck[3],deck[4],deck[5],deck[6],deck[7]))
        
        query = "SELECT deckID FROM cardsInDeck WHERE card1 = %s AND card2 = %s AND card3 = %s AND card4 = %s AND card5 = %s AND card6 = %s AND card7 = %s AND card8 = %s"
        deck = data['deck']
        self.__updateNumDecks()
        try:
            self.cur.execute(query, (deck[0],deck[1],deck[2],deck[3],deck[4],deck[5],deck[6],deck[7]))
            return self.cur.fetchone()[0]
        except Exception as e:
            print("Insertion Error:",e)
            exit()
    
    def __updateNumDecks(self):
        '''
        Increments the number of decks by one
        '''
        
        query = "UPDATE catchall SET numDecks = numDecks + 1 WHERE id = 0"
        try:
            self.cur.execute(query)
        except Exception as e:
            print("Data aggregation update error:",e)
            exit()


    def __addToDeckStats(self, data, key):
        '''
        Records the stats for each deck
        '''
        query = "SELECT * FROM deckStats WHERE deckID = %s"
        row = []
        try:
            self.cur.execute(query, key)
            row = self.cur.fetchone()[0]
        except:
            row = [key,0,0,0,0]
            query = "INSERT INTO deckStats (deckID, numWins, numGames, totalTrophies, maxTrophies) VALUES (%s,%s,%s,%s,%s)"
            try:
                self.cur.execute(query,(key,0,0,0,0))
            except Exception as e:
                print("Insertion Error:", e)
                exit()
        
        row[1] = row[1] + data['win']
        row[2] = row[2] + 1
        row[3] = row[3] + data['trophyCount']
        row[4] = max(row[4], data['trophyCount'])

        query = "UPDATE deckStats SET numWins = %s, numGames = %s, totalTrophies = %s, maxTrophies = %s WHERE deckID = %s"
        try:
            self.cur.execute(query, (row[1],row[2],row[3],row[4],row[0]))
        except Exception as e:
            print("Updating Error:", e)
            exit()
    
    def __addToCards(self, data):
        '''
        Adds battle data to the cards table, namely for win rate
        '''
        for card in data['deck']:
            query = "UPDATE cards SET numWins = numWins + %s, numGames = numGames + 1 WHERE cardID = %s"
            try:
                self.cur.execute(query, (data['win'],card))
            except Exception as e:
                print("Updating Error:", e)
                exit()
    

        

if __name__ == "__main__":
    start = time.time()
    create = externalDataCollector()
    print("Created Starting Stuff")
    print("Completed Database Setup; total time:", time.time()-start)