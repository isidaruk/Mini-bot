"""
Task:
Script is used for downloading offices' location: city, address, latitude, longitude, name of office 
from URL https://www.fonbet.ru/ and save the extracted data into an JSON file on the disk.

Description:
Script should generate json file in which an array of objects will be stored.

Format of json file:
[  
    { "adds": "Армавир, улица Воровского 69", "latlon": [44.983268, 41.096873], "name": "Fonbet", "phones": [ "+7 495 544-50-00" ]},
    .....
]
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

import geocoder
import json


driver = webdriver.Firefox()
driver.get('https://www.fonbet.ru/#!/products/addresses') # Go to the specified site.


wait = WebDriverWait(driver, 10) # Explicit waiting for.


iframe_xpath = '''//*[@id="products-page-iframe"]'''
iframe_element = wait.until(EC.presence_of_element_located((By.XPATH, iframe_xpath))) # Find the embeded maps' frame.
driver.switch_to.frame(iframe_element)
      

button_xpath = '''/html/body/f-address/div[1]/div/div[1]/div/div[1]/div[1]/a'''
button_element = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
button_element.click()                                      


cities_element_xpath = '''/html/body/f-address/div[1]/div/div[1]/div/div[1]/div[1]/div/f-city-select/div/div[3]'''  
cities_element = wait.until(EC.presence_of_element_located((By.XPATH, cities_element_xpath)))

cities_str = cities_element.get_attribute("innerText") # Get the text inside of webelement.
# print(cities_str)

cities_names_list = [] # List of names of all cities.

for city in cities_str.split('\n'):
	cities_names_list.append(city)
	# print(city)
# print(cities_names_list)
# print(len(cities_names_list))

cities_addresses_dict = {}

elem = driver.find_element_by_xpath('''/html/body/f-address/div[1]/div/div[1]/div/div[1]/div[1]/div/f-city-select/div/div[2]/input''').clear()

fonbet_list_python = [] # List with all necessary data.

# Find addresses for every city in list.
for city_name in cities_names_list:
	print(city_name)

	elem = driver.find_element_by_xpath('''/html/body/f-address/div[1]/div/div[1]/div/div[1]/div[1]/div/f-city-select/div/div[2]/input''').clear()
	elem = driver.find_element_by_xpath('''/html/body/f-address/div[1]/div/div[1]/div/div[1]/div[1]/div/f-city-select/div/div[2]/input''')
	elem.send_keys(city_name)

	time.sleep(5) # Do nothing for 5 seconds.

	if city_name != 'Ейск': # There is a problem with this city.
		driver.find_element_by_xpath('''/html/body/f-address/div[1]/div/div[1]/div/div[1]/div[1]/div/f-city-select/div/div[3]/div/div[1]/a''').click()
	else:
		driver.find_element_by_xpath('''/html/body/f-address/div[1]/div/div[1]/div/div[1]/div[1]/div/f-city-select/div/div[3]/div/div[2]/a''').click()

	# Get addresses on the right side of the frame for each city.
	addresses_xpath = '''/html/body/f-address/div[1]/div/div[2]/div[3]/div/div[1]'''
	addresses = wait.until(EC.presence_of_element_located((By.XPATH, addresses_xpath)))
	
	# time.sleep(5) # Do nothing for 5 seconds.
	time.sleep(3) # Do nothing for 3 seconds.

	addresses_str = addresses.get_attribute("innerText") # Get the text inside of webelement.
	# print(addresses_str)

	addresses_names_list = [] # List of addresses names of all cities.

	for address in addresses_str.split('\n'):
		addresses_names_list.append(address)
		# print(address)
	# print(addresses_names_list)

	cities_addresses_dict[city_name] = addresses_names_list

	json_dict = {} # Dictionary for each json object.

	# Create a full format city, address, with latitude and longitude.
	for address in addresses_names_list:
		address_str = (city_name + ', ' + address)
		# print(address_str)
		
		json_dict["adds"] = address_str

		g = geocoder.yandex(address_str)
		js = g.json
		# print(js)

		# Take the name of location only, without description: city, village, etc..
		if js is None:
			city_name = city_name.split(',')[0]
			address_str = (city_name + ', ' + address)
			g = geocoder.yandex(address_str)
			js = g.json

		if js is None:
			# print('Missing the data.')

			js = {"lat": 'Not found', "lng": 'Not found'} # Not found.

			with open('failed_addresses.txt', 'a') as data_file: # Write addresses which couldn't be find.
			     data_file.write(address_str)
			     data_file.write('\n')

			
		latlon_list = []
		latlon_list.append(js["lat"])
		latlon_list.append(js["lng"])

		json_dict["latlon"] = latlon_list

		json_dict["name"] = "Fonbet"

		# print(json_dict)
	
		fonbet_list_python.append(json_dict)	

	# print(fonbet_list_python)

	button_element = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
	button_element.click()


# print(fonbet_list_python)

# print(cities_addresses_dict)

# fonbet_json = json.dump(fonbet_list_python) # Convert Python list to JSON.

print('Get all data from the specified url.')

# Write data to json file.
with open('fonbet.json', 'w') as outfile:
    json.dump(fonbet_list_python, outfile)


driver.close() # Close webdriver.