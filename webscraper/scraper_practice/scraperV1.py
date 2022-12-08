# scraperlxml.py 
# Author: A.J. Ristino

# Very rudimentary scraper and .txt processing function to scrape and format press release data for readers

import requests
from lxml import html
 
response = requests.get('https://clashroyale.com/blog/news/end-of-support-below-ios-11.html')

# Establish that tree root is the response from inserted URL
tree = html.fromstring(response.text)

# Add all instances of div class that contains press release info to a list
paragraphs = tree.xpath('//div[@class="textBlock__wrapper"]')

# Create a .txt file
file = open("text.txt", "w") 

# Using first item in div instance list, add all text within divs
text = str(paragraphs[0].xpath("//div[@class='textBlock__wrapper']//text()"))

file.write(text)

file.close()

with open('text.txt', 'r+') as f:
    lines = f.readlines()
    new_lines = [line.replace('\\n', '\n').replace('\\t','\t').replace("', '",'') for line in lines]
    f.seek(0)
    f.writelines(new_lines)
    f.truncate()



