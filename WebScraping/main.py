import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv

url = "https://wowpedia.fandom.com/wiki/"

# Get quests starting with letter d from Level 60 quests page
page = requests.get(url + "Category:Quests_at_60?pagefrom=D")
soup = BeautifulSoup(page.content, 'html.parser')
#print(soup.prettify())

section_d = soup.find('div', class_='mw-category-group')

quest_titles = []

print("Parsing leve 60 quests")

for quest in section_d.find_all('a', href=True):

    # Get link of sub page for each quest after the /wiki/ prefix
    quest_name = quest['href'][6:]
    quest_link = url + quest_name
    print(quest_link)

    # Get page from each quest and grab description
    sub_page = requests.get(quest_link)
    sub_soup = BeautifulSoup(sub_page.content, 'html.parser')

    quest_description = ""

    for index, text in enumerate(sub_soup.find_all('p')):

        # Skip initial quest overview text
        if index == 0:
            continue

        # Stop iterating through paragraph tags when quest rewards data is reached
        if "You will receive:" in text.text:
            break

        quest_description += text.text[:-1]
        quest_description += " "

    if quest_description:
        quest_titles.append([quest_name, quest_description])


# Get remaining quests to make 100 fron
page = requests.get(url + "Category:Quests_at_40?pagefrom=D")
soup = BeautifulSoup(page.content, 'html.parser')

section_d = soup.find('div', class_='mw-category-group')

print("Parsing level 40 quests")
for quest in section_d.find_all('a', href=True):

    # Get link of sub page for each quest after the /wiki/ prefix
    quest_name = quest['href'][6:]
    quest_link = url + quest_name
    print(quest_link)

    # Get page from each quest and grab description
    sub_page = requests.get(quest_link)
    sub_soup = BeautifulSoup(sub_page.content, 'html.parser')

    quest_description = ""

    for index, text in enumerate(sub_soup.find_all('p')):

        # Skip initial quest overview text
        if index == 0:
            continue

        # Stop iterating through paragraph tags when quest rewards data is reached
        if "You will receive:" in text.text:
            break

        quest_description += text.text[:-1]
        quest_description += " "

    # Replace instances of new lines with spaces for clarity in csv file
    if quest_description:
        quest_titles.append([quest_name, quest_description])

print("Final Quest list!")
print(quest_titles)
print(len(quest_titles))


header = ['name', 'description']

print("Writing Quest data to csv file")
with open('wowquests_d.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    writer.writerow(header)
    for index, row in enumerate(quest_titles):
        writer.writerow(row)
