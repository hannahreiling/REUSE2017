from __future__ import division
import dateutil.parser    
from distutils.version import LooseVersion
import semver
import re
import ijson   
import urllib

def error_message(k, e, num, skipped):
	if k not in skipped:
		skipped.add(k) #add key to the set of skipped key names
	print "Skipping ", num, " ", k, "because ", e, ". Number skipped is ", len(skipped) 

def skip_key(row, skipped, k):
	if "time" not in row["doc"] or "versions" not in row["doc"]: #if key doesn't have necessary info
		error_message(k, "N/A", "0", skipped)
		return True

def make_date_version_list(row, skipped, k):
	dv = []
	try:
		for version in row["doc"]["time"]:
			if version != "modified" and version != "created": 
				#append date, version pairs to list dv
				dv.append((dateutil.parser.parse(row["doc"]["time"][version]), version))
		dv.sort()
	except Exception as e:
		error_message(k, e, "1", skipped)
	return dv

def make_list_versions(row):
	versiondep = row["doc"]["versions"].keys()
	versiondep.sort(key=LooseVersion) #sort versions by semver conventions
	return versiondep

def number_dependencies(versiondep, row, skipped, k):
	numDepend = []
	for vers in versiondep:
		try:
			depend = 0
			if "dependencies" in row["doc"]["versions"][vers]:
				depend = len(row["doc"]["versions"][vers]["dependencies"])
			#append number of dependencies for a given version to list depend
			numDepend.append(depend)
		except Exception as e:
			error_message(k, e, "2", skipped)
	return numDepend

def get_num_Users(row):
	if "users" in row["doc"]:
		return len(row["doc"]["users"])
	else:
		return 0

def get_majminpatch(bpversions, skipped, k):
	versionChange = {} 
	versionChange["majorChange"] = 0 #if version num changed in MAJOR.minor.patch
	versionChange["minorChange"] = 0 #if version num changed in major.MINOR.patch
	versionChange["patchChange"] = 0 #if version num changed in major.minor.PATCH
	for i in range(len(bpversions) - 1):
		try:
			version_info0 = semver.parse_version_info(bpversions[i])
			version_info1 = semver.parse_version_info(bpversions[i+1])
			if (version_info1.major != version_info0.major):
				versionChange["majorChange"] += 1
			elif (version_info1.minor != version_info0.minor):
				versionChange["minorChange"] += 1
			elif (version_info1.patch != version_info0.patch):
				versionChange["patchChange"] += 1
		except Exception as e:	
			error_message(k, e, "3", skipped)
	return versionChange

def get_percent(denom, numer):
	if(denom != 0):
		return round((numer/denom), 6) #proportion rounded to 6 decimal places

def make_bp(bpversions, k, skipped):
	bp = {}
	bp["bpCount"] = 0 #num times backporting may have occurred
	bp["majorChange"] = 0 #if backporting occurred, num times it was in a major version number
	bp["minorChange"] = 0 #if backporting occurred, num times it was in a minor version number
	bp["patchChange"] = 0 #if backporting occurred, num times it was in a patch version number
	for i in range(len(bpversions) - 1):
		try:
			if (semver.compare(bpversions[i+1], bpversions[i]) < 0): #if potential backporting occurred
				bp["bpCount"] += 1
				version_info0 = semver.parse_version_info(bpversions[i])
				version_info1 = semver.parse_version_info(bpversions[i+1])
				if (version_info1.major < version_info0.major):
					bp["majorChange"] += 1
				elif (version_info1.minor < version_info0.minor):
					bp["minorChange"] += 1
				elif (version_info1.patch < version_info0.patch):
					bp["patchChange"] += 1
		except Exception as e:	
			error_message(k, e, "4", skipped)
	return bp

def get_avg_time(dates, vcount, skipped, k):
	times = [] #list of times between version releases
	if(vcount > 1): #can't have time between releases if only 1 version
		for i in range(len(dates) - 1):
			try:
				timedif = (dates[i+1] - dates[i])
				hours = timedif.total_seconds()/3600
				times.append(hours)
			except Exception as e:
				error_message(k, e, "5", skipped)
		avgtime = (sum(times) / (vcount - 1))
		return round(((avgtime // 24) + ((avgtime % 24) / 24)), 6) #avg time b/w releases in days
	else:
		return "N/A"

def get_first_dep(dv, versiondep, numDepend): #number dependencies for first version release
	if dv[0][1] == versiondep[0]: #if first version num in "versions" matches first version num in "time"
		return numDepend[0] 
	else:
		return "N/A"



			
			
			

				

			




				
				

		  
	



