import csv

def make_id2key(id2key):
	with open("npmTop20000.csv", "rU") as f:
		freader = csv.reader(f)
		f.next()
		idNum = 1
		for row in freader:
			try:
				key = row[0]
				id2key[idNum] = key
				idNum += 1
			except Exception as e:
				print "Skipping1 because ", e

def make_graph(key2id, pairs, id2key):
	with open("DependencyGraph.txt", "rU") as fd:
		for line in fd:
			try:
				currentLine = line.split(",")
				fromKey = currentLine[0]
				toKey = currentLine[1][:-1]
				if fromKey in key2id:
					fromID = key2id[fromKey]
					if toKey in key2id:
						toID = key2id[toKey]
						pairs.append((fromID, toID, 1))
			except Exception as e:
				print "Skipping2 because ", e

def write_graph(id2key, pairs):
	with open("DependencyGraphFiltered2.txt", "w") as fw:
		fw.write("*Vertices %d\n" % len(id2key))
		for idNum in id2key:
			try:
				fw.write("%s %s\n" % (idNum, id2key[idNum]))
			except Exception as e:
				print "Skipping3 because ", e
		fw.write("*arcs\n")
		for i in range(len(pairs)):
			try:
				fw.write("%s %s %s\n" % ((pairs[i][0]), (pairs[i][1]), (pairs[i][2])))
			except Exception as e:
				print "Skipping4 because ", e

id2key = {}
pairs = []
try:
	make_id2key(id2key)
	key2id = {key: idNum for idNum, key in id2key.iteritems()}
	make_graph(key2id, pairs, id2key)
	write_graph(id2key, pairs)
except Exception as e:
	print "Skipping because ", e

	
