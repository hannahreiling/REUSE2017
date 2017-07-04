import csv
import requests
import urllib2

def print_error_message(key, num, e, skipped):
	print "Skipping ", num, " ", key, " because ", e
	if key not in skipped:
		skipped.add(key)

def write_to_file(writer, key, stats, row):
	row.extend([stats["readmeSize"], stats["testsSize"], stats["hasChangelog"], stats["outdatedDependencies"], stats["carefulness"], stats["tests"],
		stats["health"], stats["branding"], stats["communityInterest"], stats["downloadsCount"], 
		stats["downloadsAcceleration"], stats["dependentsCount"], stats["releasesFrequency"], 
		stats["commitsFrequency"], stats["openIssues"], stats["issuesDistribution"], stats["finalScore"], 
		stats["qualityScore"], stats["popularityScore"], stats["maintenanceScore"]])
	writer.writerow(row)

def get_stats(key, writer, skipped, data, row):
	stats = {"readmeSize" : "N/A", "testsSize" : "N/A", "hasChangelog" : "N/A", "outdatedDependencies" : "N/A", 
		"carefulness" : "N/A", "tests" : "N/A", "health" : "N/A", "branding" : "N/A", "communityInterest" : "N/A", 
		"downloadsCount" : "N/A", "downloadsAcceleration" : "N/A", "dependentsCount" : "N/A", 
		"releasesFrequency" : "N/A", "commitsFrequency" : "N/A", "openIssues" : "N/A", "issuesDistribution" : "N/A",
		"finalScore" : "N/A", "qualityScore" : "N/A", "popularityScore" : "N/A", "maintenanceScore" : "N/A"}
	try:
		if "code" in data and "code" == "NOT_FOUND":
			write_to_file(writer, key, stats, row)
			return
		if "collected" in data and "file" in data["collected"] and "source" in data["collected"]["file"]:
			stats["readmeSize"] = data["collected"]["source"]["files"]["readmeSize"]
			stats["testsSize"] = data["collected"]["source"]["files"]["testsSize"]
			#check hasChangelog specifically bc multiple packages don't have this stat
			if "hasChangelog" in data["collected"]["source"]:
				if data["collected"]["source"]["hasChangelog"] == true:
					stats["hasChangelog"] = True
				else:
					stats["hasChangelog"] = False
			#check outdatedDependencies specifically bc multiple packages don't have this stat
			if "outdatedDependencies" in data["collected"]["source"]:
				stats["outdatedDependencies"] = len(data["collected"]["source"]["outdatedDependences"])
		if "evaluation" in data: 
			if "quality" in data["evaluation"]:
				stats["carefulness"] = data["evaluation"]["quality"]["carefulness"]
				stats["tests"] = data["evaluation"]["quality"]["tests"]
				stats["health"] = data["evaluation"]["quality"]["health"]
				stats["branding"] = data["evaluation"]["quality"]["branding"]
			if "popularity" in data["evaluation"]:
				stats["communityInterest"] = data["evaluation"]["popularity"]["communityInterest"]
				stats["downloadsCount"] = data["evaluation"]["popularity"]["downloadsCount"]
				stats["downloadsAcceleration"] = data["evaluation"]["popularity"]["downloadsAcceleration"]
				stats["dependentsCount"] = data["evaluation"]["popularity"]["dependentsCount"]
			if "maintenance" in data["evaluation"]:
				stats["releasesFrequency"] = data["evaluation"]["maintenance"]["releasesFrequency"]
				stats["commitsFrequency"] = data["evaluation"]["maintenance"]["commitsFrequency"]
				stats["openIssues"] = data["evaluation"]["maintenance"]["openIssues"]
				stats["issuesDistribution"] = data["evaluation"]["maintenance"]["issuesDistribution"]
		if "score" in data:
			stats["finalScore"] = data["score"]["final"]
			stats["qualityScore"] = data["score"]["detail"]["quality"]
			stats["popularityScore"] = data["score"]["detail"]["popularity"]
			stats["maintenanceScore"] = data["score"]["detail"]["maintenance"]
		write_to_file(writer, key, stats, row)
	except Exception as e:
		print_error_message(key, "0", e, skipped)

def check_connectivity():
	try:
		urllib2.urlopen('http://216.58.192.142', timeout=1)
		return True
	except urllib2.URLError as e: 
		print "ERROR: There is no internet"
		return False

def go_to_url(k, writer, skipped, row):
	url = "https://api.npms.io/v2/package/"
	url = url + k #append key name to the end of the url to get access to its aggregated statistics
	connection = check_connectivity()
	if connection:
		r = requests.get(url)
		data = r.json() #put data into json format
		get_stats(key, writer, skipped, data, row)
	else:
		get_url(k, writer, skipped) #call function again and recheck if there is internet connection
	
def print_num_iterations(count):
	if count%1000 == 0:
		print "It has been 1000 iterations. Count is ", count

count = 0
skipped = set() #set of all keys skipped 
with open("npmTop25000.csv", "r") as fr:
	reader = csv.reader(fr)
	fr.next() #skip the first line with column headers
	with open("npmTop25000Complete.csv", "w") as f:
		writer = csv.writer(f)
		writer.writerow(["Key", "Num Versions", "Num Versions Not Using SemVer", 
			"Proportion Versions Not Using SemVer", "Num Major Version Changes", "Num Minor Version Changes",
			"Num Patch Version Changes", "Num Potential Backporting", "Proportion Potential Backporting", 
			"Num Major Changes - bp", "Num Minor Changes - bp", "Num Patch Changes - bp", 
			"Avg Time Between Releases in Days", "Num Dependencies First Version Release", 
			"Num Dependencies Latest Version Release", "Max Num Dependencies", "Num Users", "Num Downloads",
			"readme Size", "Tests Size", "Has Change Log", "Num Outdated Dependencies", "Carefulness", "Tests", 
			"Health", "Branding", "Community Interest", "Downloads Count", "Downloads Acceleration", 
			"Releases Frequency", "Commits Frequency", "Open Issues", "Issues Distribution", "Final Score", 
			"Quality Score", "Popularity Score", "Maintenance Score"])
		for row in reader:
			count += 1
			try:
				key = row[0][1:-1] #get key from data file without the 'quotes'
				go_to_url(key, writer, skipped, row)
				print_num_iterations(count)
			except Exception as e:
				print_error_message(key, "1", e, skipped)
	print "The total of number of keys analyzed is ", count, " and the total number skipped is ", len(skipped)
			
