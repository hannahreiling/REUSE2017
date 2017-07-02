from npmscan4 import error_message, skip_key, make_date_version_list
import csv
from distutils.version import LooseVersion
import ijson
import dateutil.parser 
import urllib
			
url = 'https://replicate.npmjs.com/registry/_all_docs?include_docs=true'
fh = urllib.urlopen(url)
packages = ijson.items(fh, 'rows.item') 
with open("DependencyGraph.csv", "w") as f:
	fwriter = csv.writer(f)
	count = 0
	skipped = set()
	for row in packages:
		count += 1
		k = row["key"]
		key = "'%s'" % k
		if skip_key(row, skipped, k): 
			continue
		try:
			dv = make_date_version_list(row, skipped, k)
			latestVers = dv[-1][1]
		except Exception as e:
			error_message(k, e, "1", skipped)
		try:
			for version in row["doc"]["versions"]:
				if version == latestVers:
					if "dependencies" in row["doc"]["versions"][latestVers]:
						deps = row["doc"]["versions"][version]["dependencies"].keys()
						for dep in deps:
							depQuotes = "'%s'" % dep
							fwriter.writerow([key, depQuotes])
		except Exception as e:
			error_message(k, e, "1", skipped)
		if count%1000 == 0:
			print "It has been 1000 iterations. Count is ", count
	print "The total number of keys analyzed is ", count
	print "The total number of keys skipped is ", len(skipped)

