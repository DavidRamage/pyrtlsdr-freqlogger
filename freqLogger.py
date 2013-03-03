#!/usr/bin/python
from __future__ import division
from rtlsdr import *
from pylab import *
from time import time
import sys
import MySQLdb
import argparse
#create connection to mysql server
sqlHost = 'localhost'
sqlUser = 'frequser'
sqlPass = 'datalog'
sqlDb = 'freqlog'
try:
	conn = MySQLdb.connect ( host = sqlHost,
		user = sqlUser,
		passwd = sqlPass,
		db = sqlDb)
	cursor = conn.cursor()
except dbConnFail:
	print "Failed to connect to the database"
#query to be used
sql = "INSERT INTO frequencies (ts,report_id,frequency,decibel) values (FROM_UNIXTIME(%s),%s,%s,%s);"
	
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-s", "--start_frequency", type=float, help="starting frequency for sweep")
	parser.add_argument("-e", "--end_frequency", type=float, help="ending frequency for sweep")
	parser.add_argument("-g", "--gap_start", type=float, help="start of band gap")
	parser.add_argument("-f", "--gap_end", type=float, help="end of band gap")
	parser.add_argument("-i", "--increment",type = float, help="frequency increment for loop")
	parser.add_argument("-d", "--description",type = str,help="Description for report")
	parser.add_argument("-m", "--minutes",type=int,help="Number of minutes to run scan")
	args = parser.parse_args()
	minFreq = float()
	minFreq = 52
	if args.start_frequency:
		minFreq = args.start_frequency
	maxFreq = float()
	maxFreq = 2176
	if args.end_frequency:
		maxFreq = args.end_frequency
	bandGapMin = float()
	bandGapMin = 1089
	if args.gap_start:
		bandGapMin = args.gap_start
	bandGapMax = float()
	bandGapMax = 1252
	if args.gap_end:
		bandGapMax = args.gap_end
	increment = float()
	increment = 1
	if  args.increment:
		increment = args.increment
	description = 'Generic Report'
	if args.description:
		description = args.description	
	freq = minFreq
	try:
		sdr = RtlSdr()
	except sdrFail:
		print "Failed to create object for SDR"
	try:
		sdr.gain = 20
	except sdrGainFail:
		print "Failed to set gain for SDR"
	try:
		cursor.execute("insert into report(min_freq,max_freq,increment,bandgap_min,bandgap_max,description) values(%s,%s,%s,%s,%s,%s)",(minFreq,maxFreq,increment,bandGapMin,bandGapMax,description))
		conn.commit()
		cursor.execute("select id from report order by id desc limit 1")
		reportid = cursor.fetchone()
	except genReportFail:
		print "Failed to create report id"
	starttime = int(time())
	while True:
		while freq <= maxFreq:
			try:
				sdr.fc = (freq * 1000000)
			except setFreqFail:
				print "Failed to set frequency to " + freq + " MHz"
			decibel = 0
			timestamp = int(time())
			samples = sdr.read_samples(256*1024)
			decibel = 10*log10(var(samples))
			try:
				cursor.execute(sql % (timestamp,reportid[0],freq,decibel))
				conn.commit()
			except:
				print "Failed to insert frequency data into database"
			freq += increment
			if freq == bandGapMin:
				freq = bandGapMax + 1
		if args.minutes:
			if int(time()) - starttime >= (args.minutes * 60):
				break
		freq = minFreq
	conn.close()

if __name__ == '__main__':
	main()
