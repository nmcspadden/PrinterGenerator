#!/usr/bin/python
#PPRINTERNAME = fqdn
#LOCATION = human readable name
#DRIVER = actual driver file
#DESCRIPTION = description for Munki
#DISPLAY_NAME = Cosmetic name for Munki

import os
import string
from plistlib import readPlist, writePlist
import csv
import argparse

parser = argparse.ArgumentParser(description='Generate installcheck_script and postinstall_script for Munki nopkg printer pkginfos.')
parser.add_argument('printername', help='full IP or simple domain of the printer')
parser.add_argument('location', help='human readable name of printer')
parser.add_argument('driver', help='name of driver file in /Library/Printers/PPDs/Contents/Resources/')
parser.add_argument('--address', help='address of printer')
parser.add_argument('--displayname', help='cosmetic name for Munki')
parser.add_argument('--desc', help='cosmetic description for Munki')
parser.add_argument('--csv', help='path to CSV file containing printer info')
args = parser.parse_args()
vars(args)

f = open('AddPrinter-Template.plist', 'rb')
templatePlist = readPlist(f)
f.close()
newPlist = templatePlist
newPlist['name'] = "AddPrinter-" + args.printername

if args.csv:
	# A CSV was found, use that for all data.
	with open(args.csv, mode='r') as infile:
		reader = csv.reader(infile)
		for row in reader:
			# each row contains 6 elements
			# First, change the plist keys in the pkginfo itself
			newPlist['display_name'] = row[2]
			newPlist['description'] = row[5]
			# Now change the variables in the installcheck_script
			newPlist['installcheck_script'] = templatePlist['installcheck_script'].replace("PRINTERNAME", row[0])
			newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("LOCATION", row[1].replace('"', ''))
			newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("DISPLAY_NAME", row[2].replace('"', ''))
			newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("ADDRESS", row[3])
			newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("DRIVER", row[4])
			# Now change the variables in the postinstall_script
			newPlist['postinstall_script'] = templatePlist['postinstall_script'].replace("PRINTERNAME", row[0])
			newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("LOCATION", row[1].replace('"', ''))
			newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DISPLAY_NAME", row[2].replace('"', ''))
			newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("ADDRESS", row[3])
			newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DRIVER", row[4])
			# Now change the one variable in the uninstall_script
			newPlist['uninstall_script'] = templatePlist['uninstall_script'].replace("PRINTERNAME", row[0])
			# Write out the file
			newFileName = "AddPrinter-" + args.printername + "-1.0.pkginfo"
			f = open(newFileName, 'wb')
			writePlist(newPlist, f)
			f.close()
else:
	if(args.desc):
		newPlist['description'] = args.desc
	else:
		newPlist['description'] = ""

	if(args.displayname):
		newPlist['display_name'] = args.displayname
	else:
		newPlist['display_name'] = newPlist['name']

	newPlist['installcheck_script'] = templatePlist['installcheck_script'].replace("PRINTERNAME", args.printername)
	newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("LOCATION", args.location.replace('"', ''))
	newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("DRIVER", args.driver.replace('"', ''))

	newPlist['postinstall_script'] = templatePlist['postinstall_script'].replace("PRINTERNAME", args.printername)
	newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("LOCATION", args.location.replace('"', ''))
	newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DRIVER", args.driver.replace('"', ''))

	newPlist['uninstall_script'] = templatePlist['uninstall_script'].replace("PRINTERNAME", args.printername)

	newFileName = "AddPrinter-" + args.printername + "-1.0.plist"
	f = open(newFileName, 'wb')
	writePlist(newPlist, f)
	f.close()