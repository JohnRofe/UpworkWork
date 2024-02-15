This is a github repository portfolio. 

The objective is to scrap over 20000 pages in the website lso.ca, where there is information about layers to create 
a lead list. 

create the database with db_creation.py
Run scraper2.py 
    * This scraper creates a consectuvie list from 0 to 20000 and scrapes the website. 
    It connects to the database and stores the information in the database with name and info. 
    It produces a log.txt file with the information of the scraping process. 

Parser 
    db_html_parser.py

This document pulls the information from the database and creates a csv file with the information.

For the businessAdress section it refers to functions in the address_algo. (This algorithm managed to separate correctly  97 % of the addresses)

The csv is created as output.csv

Then the csv is cleaned and validated with the clean_csv.py 

The final csv is output_clean.csv

Addresses.txt is a print of the addresses to be separated by the address_algo.


