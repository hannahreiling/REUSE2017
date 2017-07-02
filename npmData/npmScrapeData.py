from npmscan4 import *
import csv 

url = 'https://replicate.npmjs.com/registry/_all_docs?include_docs=true'
fh = urllib.urlopen(url)
packages = ijson.items(fh, 'rows.item')
with open("500000data_inclusive.csv", "w") as f: 
	writer = csv.writer(f)
	writer.writerow(["Key", "Num Versions", "Num Versions Not Using SemVer", 
		"Proportion Versions Not Using SemVer", "Num Major Version Changes", "Num Minor Version Changes",
		"Num Patch Version Changes", "Num Potential Backporting", "Proportion Potential Backporting", 
		"Num Major Changes - bp", "Num Minor Changes - bp", "Num Patch Changes - bp", 
		"Avg Time Between Releases in Days", "Num Dependencies First Version Release", 
		"Num Dependencies Latest Version Release", "Max Num Dependencies", "Num Users"])
	numkeys = 0 
	skipped = set() #set of all key names that are skipped
	for row in packages:
		numkeys += 1 
		try:
			k = row["key"]
			key = "'%s'" % k 
			if skip_key(row, skipped, k): 
				continue
			dv = make_date_version_list(row, skipped, k) 
			versiondep = make_list_versions(row) #list of versions from "versions" section on file 
			numDepend = number_dependencies(versiondep, row, skipped, k) 
			numUsers = get_num_Users(row) 
			versions = [version[1] for version in dv] #list of versions from "time" section on file
			dates = [date[0] for date in dv] 
			vcount = len(versions)
			#don't include versions that contain alphabet characters or - as potential backporting (bp)
			bpversions = [v for v in versions if (re.search('[a-zA-Z\-]', v) == None)]
			#dictionary of {majorChanges: #, minorChanges: #, patchChanges: #} for each version change from bpversions 
			versionChange = get_majminpatch(bpversions, skipped, k) 
			#num versions that don't follow strict semver major.minor.patch
			numWeirdVersions = len(versions) - len(bpversions) 
			percentWeirdVers = get_percent(len(versions), len(bpversions)) 
			#dictionary of {num potential bp : num, num majorChanges of bp : num, num minorChanges of bp :num, 
				#num patchChanges of bp : num}
			bp = make_bp(bpversions, k, skipped) 
			bpercent = get_percent(vcount, bp["bpCount"]) 
			avgTimeDays = get_avg_time(dates, vcount, skipped, k) 
			firstdep = get_first_dep(dv, versiondep, numDepend) #number dependencies for first version release
			lastdep = numDepend[len(numDepend) - 1] #number dependencies for last version release
			maxdep = max(numDepend) #max number of dependencies for key
			writer.writerow([key, vcount, numWeirdVersions, percentWeirdVers, versionChange["majorChange"], 
				versionChange["minorChange"], versionChange["patchChange"], bp["bpCount"], bpercent, 
				bp["majorChange"], bp["minorChange"], bp["patchChange"], avgTimeDays, firstdep, lastdep, maxdep, numUsers])
		except Exception as e:
			error_message(k, e, "6", skipped)
		if (numkeys % 1000) == 0:
			print "It has been 1000 iterations. Numkeys is: ", numkeys
print "The total number of keys skipped is: ", len(skipped)
print "The total number of keys analyzed is: ", numkeys
