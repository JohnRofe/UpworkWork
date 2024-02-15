'''adress is a dificult string so I need regex and a algorithm
In pseducode:
    1. Extracts the postal code from the address the last 7 characters and updates businessAddress
    2. Checks if the businessAddress contains only one ',' if yes
        1. splits the string the second part is the city province and the first part is the street+city
        2. with regex finds an instance when there are 2 capital letters without space between them and splits at the second one
        3. updates the businessAddress with the first part and concatenates the second part with the city and province as city, province
    3. If the businessAddress contains more than one ','
        1. splits the string at the last ',' and updates the businessAddress with the first part 
        2. follows the same steps as in the previous case'''

import re

# read the file and create a list of addresses

def extract_postal_code(address):
    # Extract the last 7 characters from the address
    postal_code = address[-7:]
    # Update the address to exclude the postal code
    address = address[:-7]
    return postal_code, address

import re

def process_address(address):
    postal_code, address = extract_postal_code(address)
    # Check if the address contains a comma
    if ',' in address:
        # Split the address at the last comma and keep both parts
        address, city_data = address.rsplit(',', 1)
    else:
        # If there is no comma, set city_data to an empty string
        city_data = ''
    return postal_code, address, city_data.strip()

import re

# read the file and create a list of addresses

def extract_postal_code(address):
    # Extract the last 7 characters from the address
    postal_code = address[-7:]
    # Update the address to exclude the postal code
    address = address[:-7]
    return postal_code, address

import re

def split_address(address):
    # Remove all periods from the address
    address = address.replace('.', '')
    address = address.replace('PO B', 'po b')

    # Define the patterns
    patterns = [
        r'([A-Z])[A-Z]',  # Capital letter followed by another capital letter (not 'PO'), followed by a lowercase letter
        r'(?<!o)[0-9a-z][A-Z]',  # Number or lowercase letter (not 'o') followed by a capital letter
        r'([\w])[A-Z]',  # Word character followed by a capital letter
    ]
    # Iterate over the patterns
    for pattern in patterns:
        # Find all occurrences of the pattern
        matches = list(re.finditer(pattern, address))
        if matches:
            # If any matches are found, take the last one
            match = matches[-1]
            # Split the address at this position and return
            split_position = match.start() + 1
            return address[:split_position], address[split_position:]
    # If no match is found, return the whole address as the first part and an empty string as the second part
    return address, ''

def process_address(address):
    postal_code, address = extract_postal_code(address)
    # Check if the address contains a comma
    if ',' in address:
        # Split the address at the last comma and keep both parts
        address, city_data = address.rsplit(',', 1)
    else:
        # If there is no comma, set city_data to an empty string
        city_data = ''
    return postal_code, address, city_data.strip()

def process_addresses(addresses):
    result = []
    for address in addresses:
        # Process the address
        postal_code, address, city_data = process_address(address)
        # Split the address
        address_part1, address_part2 = split_address(address)
        # Concatenate address_part2 and city_data
        city = f'{address_part2}, {city_data}'
        # Add the postal code, the first part of the address, and the city data to the result list
        result.append((postal_code, address_part1, city))
    return result

def process_addresses_dict(address):
    # Process the address
    postal_code, address, city_data = process_address(address)
    # Split the address
    address_part1, address_part2 = split_address(address)
    # Concatenate address_part2 and city_data
    city = f'{address_part2}, {city_data}'
    # Return the postal code, the first part of the address, and the city data
    return postal_code, address_part1, city

def main():
    with open('addresses.txt', 'r') as file:
        addresses = file.read().splitlines()
    # Filter out blank lines and lines with less than 10 characters
    addresses = [address for address in addresses if address.strip() and len(address) >= 10]
    # Process all addresses
    processed_addresses = process_addresses(addresses)
    for postal_code, address, city in processed_addresses:
        print(f'Postal code: {postal_code}')
        print(f'Address: {address}')
        print(f'City: {city}')

if __name__ == "__main__":
    main()

    
    