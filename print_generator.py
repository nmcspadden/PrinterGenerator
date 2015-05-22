#!/usr/bin/python
import os
import string
from plistlib import readPlist, writePlist
import csv
import argparse
import sys

def getOptionsString(optionList):
    optionsString = ''
    for option in optionList:
        optionsString += "\"%s\":\"%s\"" % (str(option.split('=')[0]), str(option.split('=')[1])) + ', '
    return optionsString

parser = argparse.ArgumentParser(description='Generate a Munki nopkg-style pkginfo for printer installation.')
parser.add_argument('--printername', help='Name of printer queue. Required.')
parser.add_argument('--driver', help='Name of driver file in /Library/Printers/PPDs/Contents/Resources/. Required.')
parser.add_argument('--address', help='IP or DNS address of printer. Required.')
parser.add_argument('--location', help='Location name for printer. Optional. Defaults to printername.')
parser.add_argument('--displayname', help='Display name for printer (and Munki pkginfo). Optional. Defaults to printername.')
parser.add_argument('--desc', help='Description for Munki pkginfo only. Optional.')
parser.add_argument('--options', nargs='*', dest='options', help='Printer options in form of space-delimited Option1=Key Option2=Key Option3=Key, etc. Optional.')
parser.add_argument('--version', help='Version number of Munki pkginfo. Optional. Defaults to 1.0.', default='1.0')
parser.add_argument('--csv', help='Path to CSV file containing printer info. If CSV is provided, all other options are ignored.')
args = parser.parse_args()


f = open('AddPrinter-Template.plist', 'rb')
templatePlist = readPlist(f)
f.close()

if args.csv:
    # A CSV was found, use that for all data.
    with open(args.csv, mode='r') as infile:
        reader = csv.reader(infile)
        next(reader, None) # skip the header row
        for row in reader:
            newPlist = dict(templatePlist)
            # each row contains 7 elements:
            # Printer name, location, display name, address, driver, description, options
            # options in the form of "Option=Value Option2=Value Option3=Value"
            theOptionString = ''
            if row[6] != "":
                theOptionString = getOptionsString(row[6].split(" "))
            # First, change the plist keys in the pkginfo itself
            newPlist['display_name'] = row[2]
            newPlist['description'] = row[5]
            newPlist['name'] = "AddPrinter-" + str(row[0]) # set to printer name
            # Default choice for versions for CSV is 1.0.
            newPlist['version'] = "1.0"
            # Now change the variables in the installcheck_script
            newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("PRINTERNAME", row[0])
            newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("OPTIONS", theOptionString)
            # Now change the variables in the postinstall_script
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("PRINTERNAME", row[0])
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("LOCATION", row[1].replace('"', ''))
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DISPLAY_NAME", row[2].replace('"', ''))
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("ADDRESS", row[3])
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DRIVER", row[4])
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("OPTIONS", theOptionString)
            # Now change the one variable in the uninstall_script
            newPlist['uninstall_script'] = newPlist['uninstall_script'].replace("PRINTERNAME", row[0])
            # Write out the file
            newFileName = "AddPrinter-" + row[0] + "-1.0.pkginfo"
            f = open(newFileName, 'wb')
            writePlist(newPlist, f)
            f.close()
else:
    if not args.printername:
        print >> sys.stderr, ('ERROR: No printer name given!')
        parser.print_usage()
        sys.exit(1)
    if not args.driver:
        print >> sys.stderr, ('ERROR: No path to driver given!')
        parser.print_usage()
        sys.exit(1)
    if not args.address:
        print >> sys.stderr, ('ERROR: No address given!')
        parser.print_usage()
        sys.exit(1)
        
    if args.desc:
        description = args.desc
    else:
        description = ""

    if args.displayname:
        displayName = args.displayname
    else:
        displayName = args.printername
        
    if args.location:
        location = args.location
    else:
        location = args.printername

    if args.version:
        version = str(args.version)
    else:
        version = "1.0"

    if args.options:
        optionsString = getOptionsString(args.options)
    else:
        optionsString = ''

    newPlist = dict(templatePlist)
   # root pkginfo variable replacement
    newPlist['description'] = description
    newPlist['display_name'] = displayName
    newPlist['name'] = "AddPrinter-" + str(args.printername)
    newPlist['version'] = version
    # installcheck_script variable replacement
    newPlist['installcheck_script'] = templatePlist['installcheck_script'].replace("PRINTERNAME", args.printername)
    newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("LOCATION", location.replace('"', ''))
    newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("DRIVER", args.driver.replace('"', ''))
    newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("OPTIONS", optionsString)            
    # postinstall_script variable replacement
    newPlist['postinstall_script'] = templatePlist['postinstall_script'].replace("PRINTERNAME", args.printername)
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("ADDRESS", args.address)
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DISPLAY_NAME", displayName)
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("LOCATION", location.replace('"', ''))
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DRIVER", args.driver.replace('"', ''))
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("OPTIONS", optionsString)            
    # uninstall_script variable replacement
    newPlist['uninstall_script'] = templatePlist['uninstall_script'].replace("PRINTERNAME", args.printername)

    newFileName = "AddPrinter-" + str(args.printername) + "-%s.pkginfo" % str(version)
    f = open(newFileName, 'wb')
    writePlist(newPlist, f)
    f.close()