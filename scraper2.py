import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import sqlite3
import random

url = 'https://lso.ca/public-resources/finding-a-lawyer-or-paralegal/directory-search/member?MemberNumber=P'

def next_page(url, page):
    return url + str(page).zfill(5)

def get_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def extract_name(soup):
    name = soup.find('h2', class_='member-info-title').text.strip()
    return name

def extract_box(soup):
    outermost_div = soup.find('section', class_='tps-content-section')
    return outermost_div

#Function to write the data into the db 
def write_to_db(conn, name, info):
    c = conn.cursor()
    c.execute('INSERT INTO lawyers (name, info) VALUES (?, ?)', (name, str(info)))
    conn.commit()

def main():
    base_url = 'https://lso.ca/public-resources/finding-a-lawyer-or-paralegal/directory-search/member?MemberNumber=P'
    
     # Set the start_page to the page number where the script stopped
    with open('last_page.txt', 'r') as file:
            start_page = int(file.read().strip())

    # Open the database connection
    conn = sqlite3.connect('lso.db')

    for page in range(start_page, 20101):  # Change this to the number of pages you want to scrape
        try:
            url = next_page(base_url, page)
            soup = get_data(url)
            name = extract_name(soup)
            info = extract_box(soup)
            write_to_db(conn, name, info)
            
            # Write the successful page number to a file
            with open('last_page.txt', 'w') as file:
                file.write(str(page))
        except Exception as e:
            #as log file
            with open('log.txt', 'a') as file:
                file.write(f'Error on page {page}: {e}\n')
        time.sleep(0.3)

    # Close the database connection
    conn.close()

if __name__ == '__main__':
    main()