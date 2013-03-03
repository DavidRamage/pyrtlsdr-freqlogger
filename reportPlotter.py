#!/usr/bin/python
import MySQLdb
import matplotlib.pyplot as plt
import matplotlib.dates 
import argparse
import string
import sys
import datetime
import time
sqlHost = 'localhost'
sqlUser = 'frequser'
sqlPass = 'datalog'
sqlDb = 'freqlog'
try:
	conn = MySQLdb.connect ( host = sqlHost,
		user = sqlUser,
		passwd = sqlPass,
		db = sqlDb)
except dbFail:
	print "Failed to connect to mysql"
cursor = conn.cursor()
save = False
savefile = str()
def main():
	global save
	global savefile
	#pull in command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-r", "--report_id", type=int, help="report id to plot")
	parser.add_argument("-l", "--list_reports", action='store_true', default=False, help="list reports")
	parser.add_argument("-t", "--time_plot", action='store_true', default = False, help = "plot signal strength vs time")
	parser.add_argument("-m", "--min_freq", type=float, help="minimum frequency for graph")
	parser.add_argument("-n", "--max_freq", type=float, help="maximum frequency for graph")
	parser.add_argument("-s", "--save", type = str, help="save graph to file (png)")
	args = parser.parse_args()
	if args.save:
		save = True
		savefile = args.save
	if args.list_reports:
		listReports()
		sys.exit(0)
	if args.report_id:
		if args.time_plot:
			if args.min_freq and args.max_freq:
				timeStrengthReport(args.report_id,args.min_freq,args.max_freq)
			else:
				timeStrengthReport(args.report_id)
		else:
			freqStrengthPlot(args.report_id)
	conn.close()
	sys.exit(0)

def listReports():
	try:
		cursor.execute("select id, min_freq, max_freq, increment, bandgap_min, bandgap_max, description from report order by id desc")
		rows = cursor.fetchall()
	except reportSelectFail:
		print "Failed to list reports"
	print "Report Id   Minimum Frequency   Maximum Frequency  Increment   Bandgap Minimum   Bandgap Maximum Description"
	for row in rows:
		print '{0:9d} {1:19f} {2:19f} {3:10f} {4:17f}  {5:16f} {6:<20s}'.format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) 

def freqStrengthPlot(report):
	frequencies = list()
	avgDb = list()
	maxDb = list()
	stdDev=list()
	try:
		cursor.execute("select frequency,avg(decibel) as avg_strength, max(decibel) as max_strength,std(decibel) as std_dev from frequencies where report_id = '%s' group by frequency order by frequency",(report))
		rows=cursor.fetchall()
	except strengthSelectFail:
		print "Failed to get frequency vs signal strength"
	for row in rows:
		frequencies.append(row[0])
		avgDb.append(row[1])
		maxDb.append(row[2])
		stdDev.append(row[3])
	try:
		plt.plot(frequencies,avgDb,label="Average dB",color='b')
		plt.plot(frequencies,maxDb,label="Max dB",color='r')
		plt.plot(frequencies,stdDev,label="Standard Deviation",color='g')
		plt.xlabel('MHz')
		plt.ylabel('dB')
		plt.title('Signal Strength vs. Frequency')
		plt.legend()
	except plotBuildFail:
		print "Failed to build data plot"
	if save:
		try:
			plt.draw()
			plt.savefig(savefile,dpi=400,bbox_inches=0)
		except saveFigFail:
			print "Failed to save figure"
	else:
		try:
			plt.show()
		except showPlotFail:
			print "Failed to show plot"	

def timeStrengthReport(report,min_freq=None,max_freq=None):
	times = list()
	avgDb = list()
	maxDb = list()
	stdDev=list()
	if min_freq == None and max_freq == None:
		try:
			cursor.execute("select unix_timestamp(ts),avg(decibel) as avg_db, max(decibel) as maxdb, std(decibel) as stdev from frequencies where report_id = '%s' group by ts order by ts",(report))
		except selectTimeStrengthFail:
			print "Failed to execute sql query"
	elif min_freq != None and max_freq != None:
		try:
			cursor.execute("select unix_timestamp(ts),avg(decibel) as avg_db, max(decibel) as maxdb, std(decibel) as stdev from frequencies where report_id = '%s' and frequency between %s and %s group by ts order by ts",(report,min_freq,max_freq))
		except selectTimeStrengthFail:
			print "Failed to execute sql query"
	else:
		sys.exit(1)
	rows=cursor.fetchall()
	for row in rows:
		#times.append(row[0])
		times.append(datetime.datetime.fromtimestamp(row[0]))
		avgDb.append(row[1])
		maxDb.append(row[2])
		stdDev.append(row[3])
	try:
		plt.plot_date(times,avgDb,label="Average dB",color='b',linestyle='solid',fmt="r-")
		plt.plot_date(times,maxDb,label="Max dB",color='r', linestyle = 'solid',fmt="r-")
		plt.plot_date(times,stdDev,label="Standard Deviation",color='g', linestyle = 'solid',fmt="r-")
		plt.xlabel('Time')
		plt.ylabel('dB')
		plt.title('Signal Strength vs. Time')
		plt.legend()
	except buildPlotFail:
		print "Failed to build plot"
	if save:
		try:
			plt.draw()
			plt.savefig(savefile,dpi=400,bbox_inches=0)
		except saveFigFail:
			print "Failed to save figure"
	else:
		try:
			plt.show()
		except showPlotFail:
			print "Failed to show plot"


if __name__ == '__main__':
	main()
