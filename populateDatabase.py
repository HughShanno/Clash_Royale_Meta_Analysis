import requests
import json
import psycopg2
import psqlconfig as config
import apikey


class externalDataCollection():
    
    def __init__(self):
        conn = self.connect()
        self.cur = conn.cursor()
        return
    
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

    def __apicall(self, extension, extraparams={},items=True):
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
        players = self.__getTopPlayers()
        for player in players:
            extension = 'players/' + player + '/battlelog'
            battles = self.__apicall(extension,items=False)
            for battle in battles:
                self.__addBattleToDataBase(battle)


    def __addBattleToDataBase(self, battle):
        for team in ['team','opponent']:
            data = self.__getPlayerData(battle,team)
            key = self.__addToDeckTable(data)
            self.__addToDeckStats(data,key)
            self.__addToCards(data)
        return

    def __getPlayerData(self, battle, team):
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
        try:
            self.cur.execute(query, (deck[0],deck[1],deck[2],deck[3],deck[4],deck[5],deck[6],deck[7]))
            return self.cur.fetchone()[0]
        except Exception as e:
            return Exception
    
    def __addToDeckStats(self, data, key):
        query = "SELECT * FROM deckStats WHERE deckID = %s"
        row = []
        try:
            self.cur.execute(query, key)
            row = self.cur.fetchone()[0]
        except:
            row = [key,0,0,0,0]
            query = "INSERT INTO deckStats (deckID, numWins, numGames, totalTrophies, maxTrophies), VALUES (%s,%s,%s,%s,%s)"
            try:
                self.cur.execute(query,(key,0,0,0,0))
            except Exception as e:
                return e
        
        row[1] = row[1] + data['win']
        row[2] = row[2] + 1
        row[3] = row[3] + data['trophyCount']
        row[4] = max(row[4], data['trophyCount'])

        query = "UPDATE deckStats SET numWins = %s, numGames = %s, totalTrophies = %s, maxTrophies = %s WHERE deckID = %s"
        try:
            self.cur.execute(query, (row[1],row[2],row[3],row[4],row[0]))
        except Exception as e:
            return e
    
    def __addToCards(self, data):
        for card in data['deck']:
            query = "SELECT * FROM cards WHERE cardID = %s"
            try:
                self.cur.execute(query, card)
                row = self.cur.fetchone()
            except Exception as e:
                return e
            query = "UPDATE cards SET numWins = %s, numGames = %s WHERE cardID = %s"
            try:
                self.cur.execute(query, (row[0]+data['win'],row[1]+1,card))
            except Exception as e:
                return e
        return

        

    