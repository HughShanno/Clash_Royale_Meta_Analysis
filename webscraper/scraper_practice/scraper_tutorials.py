import requests
from bs4 import BeautifulSoup


url="https://oxylabs.io/"
response = requests.get(url)

# Below code returns all .html info  from the target page, but in an unreadable, non-parsed format
'''
import requests
response = requests.get("https://clashroyale.com/blog/news/balance-changes-october-2022.html”)
print(response.text)
'''

# Below code returns the .html title of the target page
'''
url = 'https://clashroyale.com/blog/news/balance-changes-october-2022.html'
response = requests.get(url)

from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')
print(soup.title)
'''
# Below code pulls from the tutorial blogpost I'm using to write the scrapers using soup
'''
soup = BeautifulSoup(response.text, 'html.parser')

blog_titles = soup.select('h2.blog-card__content-title')
for title in blog_titles:
    print(title.text)
'''
# Output:
# Prints all blog tiles on the page
# except no it doesn't because there's no 'h2' in the returned text
# This example just didn't work

# Below code pulls from clash royale blog using lxml:

# After response = requests.get() 
'''
from lxml import html
tree = html.fromstring(response.text)

#lxml uses Xpath to query the tree object built above

blog_titles = tree.xpath('//h2[@class="blog-card__content-title"]/text()')
for title in blog_titles:
    print(title)
'''
# The objective with this lxml example is to create an HTML
'''
tree = etree.parse('input.html')
elem = tree.getroot()
''' # Prints out contents of input.html

'''
xml = '<html><body>Hello</body></html>'
root = etree.fromstring(xml)
etree.dump(root) #prints file contents to console
'''
'''
tree = etree.parse('input.html')
elem = tree.getroot()
para = elem.find('body/p')
etree.dump(para)
 
# Output:
# <p id="firstPara">This HTML is XML Compliant!</p>
''' # Opens up input.html as reference, gets root of etree, finds the first pargraph then prints it

'''
tree = etree.parse('input.html')
elem = tree.getroot()
para = elem.findall('body/p')
for e in para:
    etree.dump(e)

# Outputs
# <p id="firstPara">This HTML is XML Compliant!</p>
# <p id="secondPara">This is the second paragraph.</p>
''' # This one is the same as the code above, except it returns the contents of ALL 
    # paragraph objects in the html file, this is because of the .findall('body/p) method

# This next one is the use of XPath, which is very common with professional developers
# It does return outputs in XPath syntax though, which I don't know much about

'''
tree = etree.parse('input.html')
elem = tree.getroot()

para = elem.xpath('//p/text()')
for e in para:
    print(e)
 
# Output
# This HTML is XML Compliant!
# This is the second paragraph
'''

# This code takes in an input html, then uses the xpath syntax to specify information from
# paragraph elements, formatting them to text(), then adding that syntax into an iterable object
# The final thing this code does is iterate through para and print out all elements specified

# Note: HTML processing via lxml.html does not support direct-file-reading, 
# so I have to parse every file to a string if I want to process it using lxml
# For example:
'''
from lxml import html
with open('input.html') as f:
    html_string = f.read()
tree = html.fromstring(html_string)
para = tree.xpath('//p/text()')
for e in para:
    print(e)

# Output
# This HTML is XML Compliant!
# This is the second paragraph
'''

# Actual web-scraping tutorial ahead:

'''
import requests
 
response = requests.get('http://books.toscrape.com/')
print(response.text)
# prints source HTML
'''

# The above is just an introduction into using requests to request a webpage

# This technique can be combined with lxml to retrieve any target data:

# final attempt to print out all of the blog section titlesl, this time using selenium

from selenium.webdriver import Chrome
driver = Chrome(executable_path='chromedriver')

driver.get('https://oxylabs.io/blog/python-web-scraping')

# This scraper doesn't work super well, the below method "find_element_by_css_selector" 
# apparently doesn't exist.

blog_titles = driver.find_element_by_css_selector(' h2.blog-card__content-title')
for title in blog_titles:
    print(title.text)
driver.quit() # closing the browser