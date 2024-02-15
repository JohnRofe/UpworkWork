'''This will parse the info column from the database'''

import sqlite3
from bs4 import BeautifulSoup
import address_algo
import csv
import os
import pandas as pd

def get_data():
    conn = sqlite3.connect('lso.db')
    c = conn.cursor()
    c.execute('SELECT * FROM lawyers')
    data = c.fetchall()
    conn.close()
    return data

def from_string_to_soup(soup_string):
    return BeautifulSoup(soup_string, 'html.parser')

def extract_languages(soup):
    languages_element = soup.find('div', class_='member-info-label', string='Additional Languages')
    if languages_element:
        languages = languages_element.next_sibling.get_text(strip=True)
        languages = {'Additional Languages': languages}
        return languages
    else:
        return {}

def extract_values_from_wrapper(wrapper):
    label_element = wrapper.find(class_='member-info-label')
    value_element = wrapper.find(class_='member-info-value')
    if label_element and value_element:
        label = label_element.text.strip()
        value = value_element.text.strip()
        return label, value
    else:
        return None, None

def extract_values_from_soup(soup):
    values = {}
    info_wrappers = soup.find_all('div', class_='member-info-wrapper')
    info_wrappers.pop(0)
    for wrapper in info_wrappers:
        label, value = extract_values_from_wrapper(wrapper)
        if label:
            values[label] = value

    special_cases = soup.find_all('div', class_='member-special-cases')
    for case in special_cases:
        label, value = extract_values_from_wrapper(case)
        if label:
            values[label] = value

    return values

def add_languages_and_name(values, languages, name):
    values.update(languages)
    values['name'] = name
    return values

def get_name_map():
    return {
        'MailingName': 'mailingName',
        'Mailing Name': 'mailingName',
        'LawSocietyNumber': 'lsoNumber',
        'Law Society Number': 'lsoNumber',
        'ClassofLicence Definitions': 'classOfLicence',
        'ClassofLicenceDefinitions': 'classOfLicence',
        'Class of Licence  Definitions': 'classOfLicence',
        'Status Definitions': 'status',
        'StatusDefinitions': 'status',
        'AreasofLaw/LegalServices': 'areasOfLaw',
        'areasOfLaw': 'areasOfLaw',
        'Area(s) of Law/Legal Services': 'areasOfLaw',
        'Areas Of law': 'areasOfLaw',
        'Areas of law': 'areasOfLaw',
        'BusinessName': 'businessName',
        'Business Name': 'businessName',
        'BusinessAddress': 'businessAddress',
        'Business Address': 'businessAddress',
        'Phone': 'phone',
        'EmailAddress': 'emailAddress',
        'Email Address': 'emailAddress',
        'Fax': 'fax',
        'Trusteeships': 'trusteeship',
        'CurrentPracticeRestrictions': 'currentPracticeRestrictions',
        'Current Practice Restrictions': 'currentPracticeRestrictions',
        'CurrentRegulatoryProceedings': 'currentRegulatoryProceedings',
        'Current Regulatory Proceedings': 'currentRegulatoryProceedings',
        'RegulatoryHistory': 'regulatoryHistory',
        'Regulatory History': 'regulatoryHistory',
        'LimitedScopeRetainers': 'limitedScopeRetainer',
        'Limited Scope Retainers': 'limitedScopeRetainer',
        'Additional Languages' : 'languages',
        'name': 'name'
    }

def name_mapping(values):
    name_map = get_name_map()
    renamed_values = {name_map.get(key, key): value for key, value in values.items()}
    return renamed_values

#Area of law

def area_of_law_integration(renamed_values):
    if 'areasOfLaw' in renamed_values: 
        areasOfLaw_dict = areas_of_law_to_dict(renamed_values['areasOfLaw'])
        renamed_values.update(areasOfLaw_dict)
    
    renamed_values.pop('areasOfLaw', None)  
    return renamed_values

def areas_of_law_to_dict(areasOfLaw):
    if not areasOfLaw:
        return {}
    else:
        areas = areasOfLaw.split('|')
        areasOfLaw = {f'areaOfLaw{str(i+1).zfill(2)}': area.strip() for i, area in enumerate(areas) if area}
        return areasOfLaw

def areas_of_law_updater(renamed_values):
    renamed_values = area_of_law_integration(renamed_values)
    return renamed_values


#FRENCH AND LANGUAGES

def languages_integration(renamed_values):
    renamed_values = french_updater(renamed_values)
    renamed_values = languages_updater(renamed_values)
    return renamed_values

def french_updater(renamed_values):
    '''adds '|French' to the languages column if the lawyer offers services in French and language does not have french already'''
    if 'Offers Services in French?' in renamed_values:
        if renamed_values['Offers Services in French?'] == 'Yes':
            if 'languages' in renamed_values:
                if 'French' not in renamed_values['languages']:
                    renamed_values['languages'] += '|French'
            else:
                renamed_values['languages'] = 'French'

    renamed_values.pop('Offers Services in French?', None)  # Remove 'Offers Services in French?' key if it exists
    return renamed_values

def languages_to_dict(languages):
    if not languages:
        return {}
    else:
        languages = languages.split('|')
        languages = {f'language{str(i+1).zfill(2)}': language.strip() for i, language in enumerate(languages) if language}
        return languages

def languages_updater(renamed_values):
    if 'languages' in renamed_values: 
        languages_dict = languages_to_dict(renamed_values['languages'])
        renamed_values.update(languages_dict)
    if 'languages' in renamed_values:
        del renamed_values['languages']  
    return renamed_values

# From address algo

def business_adress_to_components(businessAddress):
    if not businessAddress:
        return None, None, None
    else:
        components = address_algo.process_addresses_dict(businessAddress)
        businessPostalCode, businessAddress, businessCity = components
        return businessAddress, businessCity, businessPostalCode
    
def business_address_integration(renamed_values):
    if 'businessAddress' in renamed_values:
        renamed_values['businessAddress'], renamed_values['businessCity'], renamed_values['businessPostalCode'] = business_adress_to_components(renamed_values['businessAddress'])
    elif 'City' in renamed_values:
        renamed_values['businessCity'] = renamed_values['City']
        del renamed_values['City']
    else:
        renamed_values['businessAddress'] = None
        renamed_values['businessCity'] = None
        renamed_values['businessPostalCode'] = None
    
    return renamed_values

def write_to_csv(renamed_values, output_file):
    # Specify the order of the columns
    fieldnames = ['name', 'mailingName', 'lsoNumber',
                   'status', 'areaOfLaw01','areaOfLaw02','areaOfLaw03','areaOfLaw04','areaOfLaw05',
                    'areaOfLaw06', 'areaOfLaw07', 'areaOfLaw08', 'areaOfLaw09',
                    'language01','language02', 'language03', 'language04','language05', 'language06',
                    'language07','language08', 'language09', 'businessName', 'businessAddress', 'businessCity',
                    'businessPostalCode', 'phone', 'fax', 'emailAddress', 'trusteeship',
                    'currentPracticeRestrictions', 'currentRegulatoryProceedings',
                    'regulatoryHistory', 'limitedScopeRetainer']

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame([renamed_values])

    # Reorder the columns
    df = df.reindex(columns=fieldnames)

    # If the file exists, append without writing the header
    if os.path.isfile(output_file):
        df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        df.to_csv(output_file, mode='w', header=True, index=False)
        
def main():
    records = get_data()
    for record in records:
        name, soup_string = record[0], record[1]
        soup = from_string_to_soup(soup_string)
        languages = extract_languages(soup)
        values = extract_values_from_soup(soup)
        values = add_languages_and_name(values, languages, name)
        renamed_values = name_mapping(values)
        renamed_values = areas_of_law_updater(renamed_values)  
        renamed_values = languages_integration(renamed_values)
        renamed_values = business_address_integration(renamed_values)
        renamed_values.pop('classOfLicence', None)
        write_to_csv(renamed_values, 'output2.csv')

if __name__ == "__main__":
    main()



