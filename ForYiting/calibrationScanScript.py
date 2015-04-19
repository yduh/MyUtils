

# /afs/cern.ch/user/y/yduh/public/txt
# 1_address_ISHA_VFS.txt  2_id_address.txt  3_id_temp.txt  4_temp_ISHA_VFS.txt 

# ======================================================
# 
# ======================================================

import ROOT as r

# ======================================================
# File keys to specify files
# ======================================================
fileKeys = ["ISHA","idAddress","idTemp","mapping"]
baseDir = "/afs/cern.ch/user/y/yduh/public/txt/"
fileNames = {
		"ISHA":"1_address_ISHA_VFS.txt",
		"idAddress":"2_id_address.txt",
		"idTemp":"3_id_temp.txt",
		"mapping":"4_temp_ISHA_VFS.txt"
		}

# ======================================================
# Data format to store information
# ======================================================
allData = {}
ISHAHist = r.TH1D("ISHA"," ; #Delta ISHA ; Entry",201,-100.5,100.5)
VFSHist = r.TH1D("VFS"," ; #Delta VFS ; Entry ",201,-100.5,100.5)

# ======================================================
# Add basedir to fileNames, because I am lazy
# ======================================================
for fileKey in fileKeys:
	fileNames[fileKey] = baseDir+fileNames[fileKey]


# ======================================================
# Read columns from files and store in allData
# ======================================================
mappingList = []
for fileKey in fileKeys:
	allData[fileKey] = {}
	inputLines = open(fileNames[fileKey],"r").readlines()
	for lineNumber,line in enumerate(inputLines):
		if line != "\n":
			if fileKey == "idAddress":
				allData[fileKey][line.split()[1]] = line.split()[0]
			elif fileKey == "idTemp":;d
				allData[fileKey][line.split()[0]] = line.split()[1]
			elif fileKey == "mapping":
				allData[fileKey][line.split()[0]] = line.split()[1:]
				mappingList.append(int(line.split()[0]))
			else:
				allData[fileKey][lineNumber] = line.split()

# ======================================================
# Get the final ISHA and VFS for each column
# ======================================================
for lineNumber,datum in allData["ISHA"].iteritems():
	if datum[0].split(".")[3][0] != "0":
		addressForIDAddress = ".".join(datum[0].split(".")[:-1])
	else:
		tempList = datum[0].split(".")
		addressForIDAddress = ".".join([ tempList[0], tempList[1], tempList[2],tempList[3][1:],tempList[4]  ])
	if addressForIDAddress in allData["idAddress"]:
		addressForIDTemp = allData["idAddress"][addressForIDAddress] 
		if addressForIDTemp in allData["idTemp"]: 
			# print addressForIDAddress,allData["idAddress"][addressForIDAddress],allData["idTemp"][allData["idAddress"][addressForIDAddress]]
			# print min(mappingList, key=lambda x:abs(x-float(allData["idTemp"][allData["idAddress"][addressForIDAddress]])))
			mappingAddress = min(mappingList, key=lambda x:abs(x-float(allData["idTemp"][allData["idAddress"][addressForIDAddress]])))
			finalISHA, finalVFS = allData["mapping"][str(mappingAddress)]
			print finalISHA, finalVFS
