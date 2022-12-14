# FORMATTING FOR DATA SCRAPED FROM THE CLASH WIKI

## NORMAL TROOPS: 

### [Name, Cost, Hit Speed, Speed, Deploy Time, Range, Target, Count, Transport, Type, Rarity]

Most cards fall under the 'Normal Troop' categorization, the only ones that don't are the spirits, wallbreakers and Battle Ram

## CHARGING TROOPS:

### [Name, Cost, Hit Speed, Speed, ***Charging Speed, Deploy Time, Range, Target, Count, Transport, Type, Rarity]

Cards with a charging ability fall under this category, they have a second Speed field with their charge speed

## SUICIDE TROOPS: 

### [Name, Cost, Speed, Deploy Time, Range, Target, **Gimmick, Transport, Type, Rarity]

Any card that has a gimmick in its stats will have that gimmick appear in its attributes between the Target and Transport fields.
This stays consistent across all cards, BUT SOME GIMMICKS THEMSELVES OCCUPY MULTIPLE FIELDS. 
This means, consider all fields between Target and Transport to be gimmick fields when dealing with troop cards.

## SECONDARY TROOPS (Spawned or Spawned On Death)

All secondary troops included are Normal Troops except for:

Furnace — The entry corresponds to the Fire Spirit entry

Ram Rider — The rider is listed as a separate unit with the following attributes:

[Name, Hit Speed, Range, Target, Count, Snare duration]

Lumberjack — The entry is the only one corresponding to a spell, that being Rage

Elixir golem — the list is copied onto itself twice, since the only differences between blob stages are DPS and movement speed

## SPAWNERS: 

### [Cost, Spawn on Death, ***Spawn Speed, ***Deploy Time, Lifetime, Type, Rarity]

NOTE: Elixir pump is technically a spawner, it just replaces 'Spawn Speed' with 'Production Speed'

This is standard across all spawners except Goblin Cage

Goblin Cage: [Cost, Spawn on Death, Lifetime, Type, Rarity]

## DEFENSES: 

### [Cost, Hit Speed, Deploy Time, Lifetime, Range, Target, Type, Rarity]

## SPELLS:

Spells are where everything falls apart, not only are they the most dynamic card type in the game,
but the muppets who wrote the wiki mixed up the order on certain repeating attributes, such as duration.
My recomendation for Spells is to just not use an SQL table and instead use a script that has uses a dictionary to map
the correct headers to corresponding stats. I used the scraper to make a txt file (spellAttributes.txt) where I scraped 
the labels so that they match the displayed attributes on the following line.



