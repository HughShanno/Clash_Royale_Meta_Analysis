DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS cardsInDeck;
DROP TABLE IF EXISTS deckStats;
DROP TABLE IF EXISTS catchall;

CREATE TABLE cards {
    cardID text,
    cardName text,
    cardImage text,
    elixirCost int,
    releaseDate date,
    minTrophies int,
    rarity text,
    numGames int,
    numWins int
};

CREATE TABLE catchall {
    numMatches int,
    numCards int,
    numPlayers int,
    numDecks int
};

CREATE TABLE cardsInDeck {
    deckID serial primary key,
    card1 int,
    card2 int,
    card3 int,
    card4 int,
    card5 int,
    card6 int,
    card7 int,
    card8 int
};

CREATE TABLE deckStats {
    deckID serial foreign key REFERENCES cardsInDeck(deckID),
    numWins int,
    numGames int,
    totalTrophies int,
    maxTrophies int
};