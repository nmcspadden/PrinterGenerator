#!/usr/bin/python
import os
from plistlib import readPlist, writePlist
import csv
import argparse
import sys
import re

def getOptionsString(optionList):
    # optionList should be a list item
    optionsString = ''
    for option in optionList:
        if option == optionList[-1]:
            optionsString += "\"%s\":\"%s\"" % (str(option.split('=')[0]), str(option.split('=')[1]))
        else:
            optionsString += "\"%s\":\"%s\"" % (str(option.split('=')[0]), str(option.split('=')[1])) + ', '
    return optionsString

parser = argparse.ArgumentParser(description='Generate a Munki nopkg-style pkginfo for printer installation.')
parser.add_argument('--printername', help='Name of printer queue. May not contain spaces, tabs, # or /. Required.')
parser.add_argument('--driver', help='Name of driver file in /Library/Printers/PPDs/Contents/Resources/. Can be relative or full path. Required.')
parser.add_argument('--address', help='IP or DNS address of printer. If no protocol is specified, defaults to lpd://. Required.')
parser.add_argument('--location', help='Location name for printer. Optional. Defaults to printername.')
parser.add_argument('--displayname', help='Display name for printer (and Munki pkginfo). Optional. Defaults to printername.')
parser.add_argument('--desc', help='Description for Munki pkginfo only. Optional.')
parser.add_argument('--requires', help='Required packages in form of space-delimited \'CanonDriver1 CanonDriver2\'. Optional.')
parser.add_argument('--options', nargs='*', dest='options', help='Printer options in form of space-delimited \'Option1=Key Option2=Key Option3=Key\', etc. Optional.')
parser.add_argument('--version', help='Version number of Munki pkginfo. Optional. Defaults to 1.0.', default='1.0')
parser.add_argument('--icon', help='Specifies an existing icon in the Munki repo to display for the printer in Managed Software Center. Optional.')
parser.add_argument('--csv', help='Path to CSV file containing printer info. If CSV is provided, all other options are ignored.')
args = parser.parse_args()


pwd = os.path.dirname(os.path.realpath(__file__))
f = open(os.path.join(pwd, 'AddPrinter-Template.plist'), 'rb')
templatePlist = readPlist(f)
f.close()

if args.csv:
    # A CSV was found, use that for all data.
    with open(args.csv, mode='r') as infile:
        reader = csv.reader(infile)
        next(reader, None) # skip the header row
        for row in reader:
            newPlist = dict(templatePlist)
            # each row contains 10 elements:
            # Printer name, location, display name, address, driver, description, options, version, requires, icon
            # options in the form of "Option=Value Option2=Value Option3=Value"
            # requires in the form of "package1 package2" Note: the space seperator
            theOptionString = ''
            if row[6] != "":
                theOptionString = getOptionsString(row[6].split(" "))
            # First, change the plist keys in the pkginfo itself
            newPlist['display_name'] = row[2]
            newPlist['description'] = row[5]
            newPlist['name'] = "AddPrinter_" + str(row[0]) # set to printer name
            # Check for an icon
            if row[9] != "":
                newPlist['icon_name'] = row[9]
            # Check for a version number
            if row[7] != "":
                # Assume the user specified a version number
                version = row[7]
            else:
                # Use the default version of 1.0
                version = "1.0"
            newPlist['version'] = version
            # Check for a protocol listed in the address
            if '://' in row[3]:
                # Assume the user passed in a full address and protocol
                address = row[3]
            else:
                # Assume the user wants to use the default, lpd://
                address = 'lpd://' + row[3]
            # Append the driver path to the driver file specified in the csv
            driver = '/Library/Printers/PPDs/Contents/Resources/%s' % row[4]
            base_driver = row[4]
            if row[4].endswith('.gz'):
                base_driver = row[4].replace('.gz', '')
            if base_driver.endswith('.ppd'):
                base_driver = base_driver.replace('.ppd', '')
            # Now change the variables in the installcheck_script
            newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("PRINTERNAME", row[0])
            newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("OPTIONS", theOptionString)
            newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("LOCATION", row[1].replace('"', ''))
            newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("DISPLAY_NAME", row[2].replace('"', ''))
            newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("ADDRESS", address)
            newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("DRIVER", base_driver)
            # Now change the variables in the postinstall_script
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("PRINTERNAME", row[0])
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("LOCATION", row[1].replace('"', ''))
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DISPLAY_NAME", row[2].replace('"', ''))
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("ADDRESS", address)
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DRIVER", driver)
            newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("OPTIONS", theOptionString)
            # Now change the one variable in the uninstall_script
            newPlist['uninstall_script'] = newPlist['uninstall_script'].replace("PRINTERNAME", row[0])
            # Add required packages if passed in the csv
            if row[8] != "":
                newPlist['requires'] = row[8].split(' ')
            # Write out the file
            newFileName = "AddPrinter-" + row[0] + "-" + version + ".pkginfo"
            f = open(newFileName, 'wb')
            writePlist(newPlist, f)
            f.close()
else:
    if not args.printername:
        print >> sys.stderr, (os.path.basename(sys.argv[0]) + ': error: argument --printername is required')
        parser.print_usage()
        sys.exit(1)
    if not args.driver:
        print >> sys.stderr, (os.path.basename(sys.argv[0]) + ': error: argument --driver is required')
        parser.print_usage()
        sys.exit(1)
    if not args.address:
        print >> sys.stderr, (os.path.basename(sys.argv[0]) + ': error: argument --address is required')
        parser.print_usage()
        sys.exit(1)

    if re.search(r"[\s#/]", args.printername):
        # printernames can't contain spaces, tabs, # or /.  See lpadmin manpage for details.
        print >> sys.stderr, ("ERROR: Printernames can't contain spaces, tabs, # or /.")
        sys.exit(1)

    if args.desc:
        description = args.desc
    else:
        description = ""

    if args.displayname:
        displayName = args.displayname
    else:
        displayName = str(args.printername)

    if args.location:
        location = args.location
    else:
        location = args.printername

    if args.version:
        version = str(args.version)
    else:
        version = "1.0"

    if args.requires:
        requires = args.requires
    else:
        requires = ""

    if args.icon:
        icon = args.icon
    else:
        icon = ""

    if args.options:
        optionsString = str(args.options[0]).split(' ')
        optionsString = getOptionsString(optionsString)
    else:
        optionsString = ''

    if args.driver.startswith('/Library'):
        # Assume the user passed in a full path rather than a relative filename
        driver = args.driver
    else:
        # Assume only a relative filename
        driver = os.path.join('/Library/Printers/PPDs/Contents/Resources', args.driver)

    if '://' in args.address:
        # Assume the user passed in a full address and protocol
        address = args.address
    else:
        # Assume the user wants to use the default, lpd://
        address = 'lpd://' + args.address

    newPlist = dict(templatePlist)
   # root pkginfo variable replacement
    newPlist['description'] = description
    newPlist['display_name'] = displayName
    newPlist['name'] = "AddPrinter_" + displayName.replace(" ", "")
    newPlist['version'] = version
    newPlist['icon_name'] = icon
    # installcheck_script variable replacement
    newPlist['installcheck_script'] = templatePlist['installcheck_script'].replace("PRINTERNAME", args.printername)
    newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("ADDRESS", address)
    newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("DISPLAY_NAME", displayName)
    newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("LOCATION", location.replace('"', ''))
    newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("DRIVER", os.path.splitext(os.path.basename(driver))[0].replace('"', ''))
    newPlist['installcheck_script'] = newPlist['installcheck_script'].replace("OPTIONS", optionsString)
    # postinstall_script variable replacement
    newPlist['postinstall_script'] = templatePlist['postinstall_script'].replace("PRINTERNAME", args.printername)
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("ADDRESS", address)
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DISPLAY_NAME", displayName)
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("LOCATION", location.replace('"', ''))
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("DRIVER", driver.replace('"', ''))
    newPlist['postinstall_script'] = newPlist['postinstall_script'].replace("OPTIONS", optionsString)
    # uninstall_script variable replacement
    newPlist['uninstall_script'] = templatePlist['uninstall_script'].replace("PRINTERNAME", args.printername)
    # required packages
    if requires != "":
        newPlist['requires'] = [r.replace('\\', '') for r in re.split(r"(?<!\\)\s", requires)]

    newFileName = "AddPrinter-" + str(args.printername) + "-%s.pkginfo" % str(version)
    f = open(newFileName, 'wb')
    writePlist(newPlist, f)
    f.close()
