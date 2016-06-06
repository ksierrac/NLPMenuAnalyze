__author__ = 'Sierra'

from urllib import request
from bs4 import *
import nltk
from nltk.corpus import stopwords
import re

#strip HTML tags and return remaining text as a string
def removeHTML(webpage):
    raw = BeautifulSoup(webpage, "html.parser").get_text()
    sents = nltk.sent_tokenize(raw)
    astring = ''
    for s in range(len(sents)):
        astring += sents[s]
    return astring

#Takes a link to a city's main TripAdvisor restaurant page
#Parses full html source page to find and return a link for each restaurant on the page
def getRestLinks(startPage):
    page = request.urlopen(startPage).read().decode('utf8')
    restLinks = []
    count = 0
    for i in range(300):
        try:
            findLinks = re.findall(r'href=.*html\" class=\"property_title\"', page)
            for l in findLinks:
                link = 'https://www.tripadvisor.com'+l[6:-24]
                restLinks.append(link)
                count += 1
                print('link '+str(count))
            findNextLink = re.findall(r'rel=\"next\" href=.*html\"/>',page)
            nextLink = 'https://www.tripadvisor.com'+findNextLink[0][17:-3]
            page = request.urlopen(nextLink).read().decode('utf8')
        except:
            continue
    return restLinks

def getMenuTokensString(restPage):
    page = request.urlopen(restPage).read().decode('utf8')  #open page and define stopwords
    page = removeHTML(page)
    ignore = list(stopwords.words('english'))+['Dinner','Menu','Brunch','Tasting','Lunch','Breakfast','Dessert','Main','Appetizer','Appetizers']
    returnmenu = []
    if page.find('Restaurant Menu') > -1 and page.find('Sorry') == -1:  #if the menu exists and can be accessed
        startIndex = page.index('Restaurant Menu')+15                   #locate menu
        endIndex = page.index('Questions & Answers')
        menu = page[startIndex:endIndex]
        menu = menu.replace('\n',' ')           #throw out \n and split into words
        menu = menu.replace(',','')
        menu = menu.split(' ')
        returnmenu = [x for x in menu if x != '' and re.match('\w',x) and not re.match('\$?\d+\.?\d+?',x) and x not in ignore]
        menu = ' '.join(returnmenu)
        return menu
    else:
        return 'not found'

def getCuisine(restPage):
    page = request.urlopen(restPage).read().decode('utf8')      #open page, define category names
    page = removeHTML(page)
    tags = []
    tagSection = ''

    block = re.findall(r'Cuisine[\w\s,]*Dining options',page)   #locate and isolate category section in source page
    if block != []:
        startIndex = page.index(block[0])
        endIndex = startIndex+(len(block[0])-14)
        tagSection = page[startIndex:endIndex]
        start2 = tagSection.index('Cuisine')+7    #identify start/end indices of tag values
        cuisines = tagSection[start2:endIndex].strip()
        cuisines = cuisines.split(',')
        for c in cuisines:
            c = c.strip()
            c = c.replace(' ','-')
            tags.append(c)
        return tags
    else:
        return 'not found'

testlink = 'https://www.tripadvisor.com/Restaurants-g60763-New_York_City_New_York.html'

# Code to call getRestLinks and write links to a file
# restaurantlinks = getRestLinks(testlink)
# f = open('links.txt', 'w')
# for l in range(len(restaurantlinks)):
#     f.write(restaurantlinks[l]+'\n')
# f.close()

# Opens each link in a list, gets menu and category, generates a file ID and writes file ID and categories to cats.txt
count = 0
corp = open('cats.txt', 'w', encoding='utf-8')
links = open('links.txt', 'r')
linklist = list(links)
for line in linklist:
    tokens = getMenuTokensString(line)
    cuisines = getCuisine(line)
    if tokens != 'not found' and cuisines != 'not found':
        count += 1
        print("cuisines = "+str(count),cuisines, '\n'+tokens)
        fileID = 'menu'+str(count)+'.txt'
        file = open(fileID, 'w', encoding='utf-8')
        file.write(tokens)
        file.close()
        corp.write(fileID+' '+' '.join(cuisines)+'\n')
corp.close()
links.close()