import requests
import json
import psycopg2
import psqlconfig as config
import apikey


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
        numcards = self.__createCards()
        self.__createCatchall(numcards)
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
            data = [card['id'],card['name'],card['iconUrls'],0,"1/1/2000",0,raritydict[card['maxLevel']],0,0]
            self.__insertCard(data)
        return len(cards)

    def __insertCard(self, data):
        '''
        Given cleaned information about a card, inserts the card into the cards datatable
        '''
        query = "INSERT INTO cards (cardID, cardName, cardImage, elixirCost, releaseDate, minTrophies, rarity, numGames, numWins) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            self.cur.execute(query, (data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8]))
        except Exception as e:
            print("Insertion Error:",e)
            exit()
    
    def __createCatchall(self, numcards):
        '''
        Creates the catchall table given the number of cards in order to automaticall populate one column
        '''
        query = "INSERT INTO catchall (id, numMatches, numCards, numPlayers, numDecks) VALUES (0,0,%s,0)"
        try:
            self.cur.execute(query, numcards)
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
            clantags.append[tag]
        return clantags

    def __getTopPlayers(self, rating=73900):
        '''
        Collects the tags for each player in each clan with a rating above the input rating.
        '''
        tags = self.__getTopClanTags(rating)
        players = []
        for tag in tags:
            extension = 'clans/' + tag + '/members'
            response = self.apicall(extension)
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
        players = self.__getTopPlayers()
        numMatches = 0
        for player in players:
            extension = 'players/' + player + '/battlelog'
            battles = self.__apicall(extension,items=False)
            for battle in battles:
                self.__addBattleToDataBase(battle)
                numMatches += 1
        self.__updateNumMatches(numMatches)


    def __updateNumMatches(self,numMatches=1):
        '''
        Updates the total number of matches by the passed amount
        '''
        query = "SELECT numMatches FROM catchall"
        try:
            self.cur.execute(query)
            curmatches = self.cur.fetchone()[0]
        except Exception as e:
            print("Data aggregation access error:", e)
            exit()
        
        query = "UPDATE catchall SET numMatches = %s WHERE id = 0"
        try:
            self.cur.execute(query, numMatches+curmatches)
        except Exception as e:
            print("Data aggregation update error:",e)
            exit()


    def __addBattleToDataBase(self, battle):
        '''
        Given battle data, updates the database to account for the battle
        '''
        for team in ['team','opponent']:
            data = self.__getPlayerData(battle,team)
            key = self.__addToDeckTable(data)
            self.__addToDeckStats(data,key)
            self.__addToCards(data)
        return


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
        if battle[team][0]['trophyChange'] < 0:
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
        query = "SELECT numDecks FROM catchall"
        try:
            self.cur.execute(query)
            numDecks = self.cur.fetchone()[0]
        except Exception as e:
            print("Data aggregation access error:", e)
            exit()
        
        query = "UPDATE catchall SET numDecks = %s WHERE id = 0"
        try:
            self.cur.execute(query, numDecks+1)
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
            query = "SELECT * FROM cards WHERE cardID = %s"
            try:
                self.cur.execute(query, card)
                row = self.cur.fetchone()
            except Exception as e:
                print("Card missing error:", e)
                exit()
            query = "UPDATE cards SET numWins = %s, numGames = %s WHERE cardID = %s"
            try:
                self.cur.execute(query, (row[0]+data['win'],row[1]+1,card))
            except Exception as e:
                print("Updating Error:", e)
                exit()

        

    