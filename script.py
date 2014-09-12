import netCDF4
import datetime
import numpy
import Queue
import os
import shutil
import sys

inp = sys.argv[1]
out = sys.argv[2]

print "input:", inp
print "output:", out

dataset = netCDF4.MFDataset(inp, "r", aggdim="time")
# print dataset.dimensions

times = dataset.variables["time"][:]
lats = dataset.variables["latitude"][:]
longs = dataset.variables["longitude"][:]
accs = dataset.variables["accumulation"]

nlats = len(lats)
nlongs = len(longs)
ntimes = len(times)

# years = range(startyear, startyear + nyears)
nid = 0
f = open(out, "w")

def writedays(s, f, hasdata = False, curracc = 0):
	if hasdata:
		writeday(curracc)
		s += 1
	for day in range(s, f):
		writeday(-99)

def writeyear(year, newline):
	global nid
	global f
	id = nid
	nid += 1
	name = str(id)
#	print "writing", id, name, year
	if newline:
		f.write("\n")
	f.write("  ")
	f.write(str(id).rjust(4))
	f.write(" ")
	f.write(name.ljust(23))
	f.write(" ")
	f.write(str(year))
	f.write("\n")

def writeday(acc):
	global f
	f.write(str(acc))
	f.write(" ")

for lati in range(nlats):
	lat = lats[lati]
	print "processing", lat, lati, "of", nlats
	for longi in range(nlongs):
		long = longs[longi]
		key = str(lat) + "," + str(long)
		currday = 1
		curryear = 0
		curracc = 0
		hasdata = False
		accs0 = accs[:, lati, longi]
		for timei in range(ntimes):
			time = datetime.datetime.fromtimestamp(times[timei])
			year = time.year
			yday = time.timetuple().tm_yday
			acc = accs0[timei]
			if acc != -99:
#				print "processing", acc, time
				if curryear != year:
					if hasdata:
						writedays(currday, 366, hasdata, curracc)
					writeyear(year, hasdata)
					writedays(1, yday)
					currday = yday
					curryear= year
					curracc = acc
					hasdata = True
				elif currday != yday:
					writedays(currday, yday, hasdata, curracc)
					currday = yday
					curryear= year
					curracc = acc
					hasdata = True
				else:
					curracc += acc
		if hasdata:
			writedays(currday, 366, hasdata, curracc)


f.close()
