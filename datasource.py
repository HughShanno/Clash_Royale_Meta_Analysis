import psycopg2
import psqlconfig as config

class Datasource():


    def __init__(self):
        conn = self.connect()
        self.cur = conn.cursor()

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

    def sqlCommandRunner(self,query):
        try:
            self.cur.execute(query)
            return self.cur.fetchone()
        except Exception as e:
            print(e)
            exit()

    def getTopWinRates(self, number=5):
        '''
        Returns the [passed number] top win rate decks
        '''
        query = "SELECT numWins/numGames, deckID FROM deckStats ORDER BY numWins/numGames LIMIT %s"
        try:
            self.cur.execute(query, (number,))
            info = self.cur.fetchone()
        except Exception as e:
            print("Deck Collection Error:",e)
            exit()
        
        data = []
        for line in info:
            data.append({'win rate': line[0], 'cards': self.getCardsInDeck(line[1])})
        return data

    def getTopCardWinRates(self,card):
        '''
        Returns the 3 top win rate decks that contain the passed card
        '''
        query = "SELECT numWins/numGames, deckID FROM deckStats LEFT JOIN (SELECT deckID FROM cardsInDeck WHERE card1 = %s OR card2 = %s OR card3 = %s OR card4 = %s OR card5 = %s OR card6 = %s OR card7 = %s OR card8 = %s) AS p ON deckStats.deckID = p.deckID ORDER BY numWins/numGames LIMIT 3"
        try:
            self.cur.execute(query, (card,card,card,card,card,card,card,card))
        except Exception as e:
            return "Card is not used in any decks"
        return

    def getCardsInDeck(self,deckID):
        '''
        Returns the card IDs that make up the deck with the given ID
        '''
        query = "SELECT card1,card2,card3,card4,card5,card6,card7,card8 FROM cardsInDeck WHERE deckID = %s"
        try:
            self.cur.execute(query, (deckID,))
            return self.cur.fetchone()
        except Exception as e:
            print("Incorrect Deck Error:", e)
            exit()


    def getGeneralCardInfo(self,cardID):
        '''
        Returns all of the information for a card with the given ID
        '''
        query = "SELECT * FROM cards WHERE cardID = %s"
        return self.getCardInfo(query, cardID)


    def getCardElixirCost(self,cardID):
        '''
        Returns the elixir cost for a card with the given ID
        '''
        query = "SELECT elixirCost FROM cards WHERE cardID = %s"
        return self.getCardInfo(query, cardID)


    def getCardDisplayInfo(self, cardID):
        '''
        Returns the necessary information (card name and link to image) in order to display the card with the given ID
        '''
        query = "SELECT cardName, cardImage FROM cards WHERE cardID = %s"
        return self.getCardInfo(query,cardID)


    def getCardInfo(self, query, cardID):
        '''
        Runs the given query on the given cardID and returns whatever the query returns
        '''
        try:
            self.cur.execute(query, (cardID,))
            return self.cur.fetchone()
        except Exception as e:
            print("Card not found error:",e)
            exit()


    def getTotalNumGames(self):
        '''
        Returns the total number of games that have been played
        '''
        query = "SELECT numMatches FROM catchall"
        try:
            self.cur.execute(query)
            return self.cur.fetchone()[0]
        except Exception as e:
            print("Error collecting matches:",e)
            exit()
    

    def getDeckStats(self,deckID):
        '''
        Returns the raw database entries for a deck with a given ID
        '''
        query = "SELECT numWins, numGames, totalTrophies, maxTrophies FROM deckStats WHERE deckID = %s"
        try:
            self.cur.execute(query, (deckID,))
            return self.cur.fetchone()
        except:
            return None

    def getDeckID(self, cardIDs):
        '''
        Returns the deckID for a deck with the given cards, or None if the deck does not exist
        '''
        cardIDs.sort()
        query = "SELECT deckID from cardsInDeck WHERE card1 = %s AND card2 = %s AND card3 = %s AND card4 = %s AND card5 = %s AND card6 = %s AND card7 = %s AND card8 = %s"
        try:
            self.cur.execute(query, (cardIDs[0],cardIDs[1],cardIDs[2],cardIDs[3],cardIDs[4],cardIDs[5],cardIDs[6],cardIDs[7]))
            id = self.cur.fetchone()
        except:
            return None

    def deckLookup(self, cardIDs):
        '''
        Takes in a list of card IDs and returns the win rate, usage rate, elixir cost, and user trophies stats for the deck consisting of those cards, or if the deck does not exist
        '''
        id = self.getDeckID(cardIDs)

        if not id:
            return "Deck does not exist"
        
        info = self.getDeckStats(id)
        if not info:
            return "Deck does not exist"

        numGames = self.getTotalNumGames()

        elixirCost = 0
        for card in cardIDs:
            elixirCost += self.getCardElixirCost(card)
        elixirCost = elixirCost/8

        return {'win rate': info[0]/info[1], 'usage rate': info[1]/numGames, 'elixir cost': elixirCost, 'average trophies': info[2]/numGames, 'max trophies': info[3]}

    
    def getMostRecentCards(self, date):
        '''
        Gets a list of cards that were released after a date (ideally the date the user last played)
        '''
        query = "SELECT cardID FROM cards WHERE releaseDate > %s"
        try:
            self.cur.execute(query, (date,))
            return self.cur.fetchone()
        except Exception as e:
            return None

    def getLowestArena(self,deck):
        '''
        Takes in a deck and returns the lowest trophy count that a user can unlock the deck at
        '''
        lowest = 0
        for card in deck:
            query = "SELECT minTrophies FROM cards WHERE cardID = %s"
            try:
                self.cur.execute(query, (card,))
                lowest = max(lowest, self.cur.fetchone())
            except Exception as e:
                print("Card Lookup Error:", e)
                exit()
        return lowest

if __name__ == "__main__":
    datasource = Datasource()
    print(datasource.sqlCommandRunner("SELECT * FROM information_schema.tables;"))
    print(datasource.getCardsInDeck(0))