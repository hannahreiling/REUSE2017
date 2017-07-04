import csv
import requests
import urllib2

def print_error_message(key, num, e, skipped):
	print "Skipping ", num, " ", key, " because ", e
	if key not in skipped:
		skipped.add(key)

def write_to_file(writer, key, downloads):
	key2print = "'%s'" % key
	writer.writerow([key2print, downloads])

def get_downloads_one(key, writer, skipped, data): #if only one key in k
	try:
		if "downloads" not in data:
			print_error_message(key, "0", "downloads not in data", skipped)
			return
		downloads = data["downloads"]
		write_to_file(writer, key, downloads)
	except Exception as e:
		print_error_message(key, "1", e, skipped)

def get_downloads_reg(key, writer, skipped, data): #if multiple keys in k
	try:
		if data[key] is None or "downloads" not in data[key]:
			print_error_message(key, "2", "downloads not in data or null", skipped)
			return
		downloads = data[key]["downloads"]
		write_to_file(writer, key, downloads)
	except Exception as e:
		print_error_message(key, "3", e, skipped)

def check_connectivity():
	try:
		urllib2.urlopen('http://216.58.192.142', timeout=1)
		return True
	except urllib2.URLError as e: 
		print "ERROR: There is no internet"
		return False

def get_url(k, writer, skipped):
	url = "http://api.npmjs.org/downloads/point/last-month/"
	url = url + k #append all of the key names to the end of the url to get access to their downloads data
	connection = check_connectivity()
	if connection:
		r = requests.get(url)
		data = r.json() #put data into json format
		if len(k.split(",")) > 1:
			for key in k.split(","):
				get_downloads_reg(key, writer, skipped, data)
		else:
			get_downloads_one(k, writer, skipped, data)
	else:
		go_to_url(k, writer, skipped, row) #call function again and recheck if there is internet connection
	
def print_num_iterations(count):
	if count%1000 == 0:
		print "It has been 1000 iterations. Count is ", count

with open("500000data_inclusive.csv", "r") as fr:
	reader = csv.reader(fr)
	fr.next() #skip the first line with column headers
	count = 0
	skipped = set() #set of all keys skipped 
	keys = ""
	with open("numDownloads500000.csv", "w") as f:
		writer = csv.writer(f)
		writer.writerow(["Key", "Num Downloads"])
		for row in reader:
			count += 1
			key = row[0][1:-1] #get key from data file without the 'quotes'
			if "@" in key:
				get_url(key, writer, skipped) #scoped packages (ex. @angular/router) not included in bulk lookup
				print_num_iterations(count)
				continue 
			keys += (key + ",")
			if(len(keys.split(",")) == 128): #max number of keys in bulk lookup is 128
				get_url(keys[:-1], writer, skipped) #don't include last comma in keys 
				keys = ""
			print_num_iterations(count)
		if(len(keys.split(",")) > 0): #after iterating through all keys, get downloads for keys in the final group (< 128)
			get_url(keys[:-1], writer, skipped)
			keys = ""
		print "The total of number of keys analyzed is ", count, " and the total number skipped is ", len(skipped)
			
