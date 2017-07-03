import csv

def make_key2down():
	with open('numDownloads500000.csv', 'r') as f:
		f_reader = csv.reader(f)
		key2down = {} 
		f.next() #skip first row that contains headers
		for row in f_reader:
			key = row[0]
			numDownloads = row[1]
			key2down[key] = numDownloads
		return key2down

def write_num_downloads(row, fw_writer):
	key = row[0]
	if key in key2down: #if key has available data about num downloads
		row.extend([key2down[key]])
		fw_writer.writerow(row)
	else:
		row.extend(["N/A"])
		fw_writer.writerow(row)

key2down = make_key2down() #make dictionary of key : num downloads 
with open('500000data_inclusive.csv', 'r') as fr:
	fr_reader = csv.reader(fr)
	fr_reader.next() #skip first row that contains headers
	with open('npmdata500000wDown.csv', 'w') as fw:
		fw_writer = csv.writer(fw)
		fw_writer.writerow(["Key", "Num Versions", "Num Versions Not Using SemVer", 
			"Proportion Versions Not Using SemVer", "Num Major Version Changes", "Num Minor Version Changes",
			"Num Patch Version Changes", "Num Potential Backporting", "Proportion Potential Backporting", 
			"Num Major Changes - bp", "Num Minor Changes - bp", "Num Patch Changes - bp", 
			"Avg Time Between Releases in Days", "Num Dependencies First Version Release", 
			"Num Dependencies Latest Version Release", "Max Num Dependencies", "Num Users", "Num Downloads"])
		for row in fr_reader:
			write_num_downloads(row, fw_writer)