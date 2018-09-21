PrinterGenerator
================

This script will generate a ["nopkg"](https://groups.google.com/d/msg/munki-dev/hmfPZ7sgW6k/q6vIkPIPepoJ) style pkginfo file for [Munki](https://github.com/munki/munki/wiki) to install a printer.

See [Managing Printers with Munki](https://github.com/munki/munki/wiki/Managing-Printers-With-Munki) for more details.

## Usage

The script can either take arguments on the command line, or a CSV file containing a list of printers with all the necessary information.  

The script will generate a pkginfo file.  This pkginfo file is a "nopkg" style, and thus has three separate scripts:  

* installcheck_script
* postinstall_script
* uninstall_script

The installcheck_script looks for an existing print queue named PRINTERNAME.  If it does not find one, it will exit 0 and trigger an installation request.  If it does find one, it will compare all of the options provided (DRIVER, ADDRESS, DISPLAYNAME, LOCATION, and OPTIONS) for differences.  If there are any differences, it will trigger an installation request.

The postinstall_script will attempt to delete the existing print queue named PRINTERNAME first, and then will reinstall the queue with the specified options.  
*Note that it does not check to see if the printer queue is in use at the time, so it is possible that existing print jobs will be cancelled if a user is printing when a Munki reinstall occurs.*

The uninstall_script will delete the printer queue named PRINTERNAME if uninstallation is triggered.

### Using a CSV file:

A template CSV file is provided to make it easy to generate multiple pkginfos in one run.  Pass the path to the csv file with `--csv`:

```
./print_generator.py --csv /path/to/printers.csv
```
*Note: if a CSV file is provided, all other command line arguments are ignored.*

The CSV file's columns should be pretty self-explanatory:

* Printer name: Name of the print queue
* Location: The "location" of the printer
* Display name: The visual name that shows up in the Printers & Scanners pane of the System Preferences, and in the print dialogue boxes.  Also used in the Munki pkginfo.
* Address: The IP or DNS address of the printer. The template uses the form: `lpr://ADDRESS`.  Change to another protocol in the template if necessary.
* Driver: Name of the driver file in /Library/Printers/PPDs/Contents/Resources/.
* Description: Used only in the Munki pkginfo.
* Options: Any printer options that should be specified. These **must** be space-delimited key=value pairs, such as "HPOptionDuplexer=True OutputMode=normal".  **Do not use commas to separate the options, because this is a comma-separated values file.**
* Version: Used only in the Munki pkginfo.
* Requires: Required packages for Munki pkginfo. These **must** be space-delimited, such as "CanonDriver1 CanonDriver2".
* Icon: Optionally specify an existing icon in the Munki repo to display for the printer in Managed Software Center.

The CSV file is not sanity-checked for invalid entries or blank fields, so double check your file and test your pkginfos thoroughly.

### Command-line options:

A full description of usage is available with:

```
./print_generator.py -h
usage: print_generator.py [-h] [--printername PRINTERNAME] [--driver DRIVER]
                          [--address ADDRESS] [--location LOCATION]
                          [--displayname DISPLAYNAME] [--desc DESC]
                          [--requires REQUIRES]
                          [--options [OPTIONS [OPTIONS ...]]]
                          [--version VERSION] [--icon ICON] [--csv CSV]

Generate a Munki nopkg-style pkginfo for printer installation.

optional arguments:
  -h, --help            show this help message and exit
  --printername PRINTERNAME
                        Name of printer queue. May not contain spaces, tabs, #
                        or /. Required.
  --driver DRIVER       Name of driver file in
                        /Library/Printers/PPDs/Contents/Resources/. Can be
                        relative or full path. Required.
  --address ADDRESS     IP or DNS address of printer. If no protocol is
                        specified, defaults to lpd://. Required.
  --location LOCATION   Location name for printer. Optional. Defaults to
                        printername.
  --displayname DISPLAYNAME
                        Display name for printer (and Munki pkginfo).
                        Optional. Defaults to printername.
  --desc DESC           Description for Munki pkginfo only. Optional.
  --requires REQUIRES   Required packages in form of space-delimited
                        'CanonDriver1 CanonDriver2'. Optional.
  --options [OPTIONS [OPTIONS ...]]
                        Printer options in form of space-delimited
                        'Option1=Key Option2=Key Option3=Key', etc. Optional.
  --version VERSION     Version number of Munki pkginfo. Optional. Defaults to
                        1.0.
  --icon ICON           Name of exisiting icon in Munki repo. Optional.
  --csv CSV             Path to CSV file containing printer info. If CSV is
                        provided, all other options are ignored.
```

As in the above CSV section, the arguments are all the same:

* `--printername`: Name of the print queue. May not contain spaces, tabs, "#" or "/" characters. **Required.**
* `--driver`: Name of the driver file in /Library/Printers/PPDs/Contents/Resources/. This can be either a relative path (i.e. the filename in the path above), or a full path (starting with "/Library"). **Required.**
* `--address`: The IP or DNS address of the printer. If no protocol is specified, `lpd://ADDRESS` will be used.  **Required.**
* `--location`: The "location" of the printer. If not provided, this will default to the value of `--printername`.
* `--displayname`: The visual name that shows up in the Printers & Scanners pane of the System Preferences, and in the print dialogue boxes.  Also used in the Munki pkginfo.  If not provided, this will default to the value of `--printername`.
* `--desc`: Used only in the Munki pkginfo. If not provided, will default to an empty string ("").
* `--requires`: Add required packages in the Munki pkginfo. If not provided, no packages will be required.
* `--options`: Any number of printer options that should be specified. These should be space-delimited key=value pairs, such as "HPOptionDuplexer=True OutputMode=normal".
* `--version`: The version number of the Munki pkginfo. Defaults to "1.0".
* `--icon`: Used only in the Munki pkginfo. If not provided, will default to an empty string ("").

### Figuring out options:

Printer options can be determined by using `lpoptions` on an existing printer queue:  
`/usr/bin/lpoptions -p YourPrinterQueueName -l`  

Here's a snip of output:

```
OutputMode/Quality: high-speed-draft fast-normal *normal best highest
HPColorMode/Color: *colorsmart colorsync grayscale
ColorModel/Color Model: *RGB RGBW
HPPaperSource/Source: *Tray1
Resolution/Resolution: *300x300dpi 600x600dpi 1200x1200dpi
```

Options typically have the actual PPD option name on the left side of the /, and a display name (which is likely to show up in the printer settings dialogue boxes) on the right of the /.  The possible values for the printer are listed after the colon.  The current option is marked with an "*".  

Despite `lpoptions` using a "Name/Nice Name: Value *Value Value" format, the option must be specified more strictly:  
"HPColorMode=grayscale"

This is the format you must use when passing options to `--options`, or specifying them in the CSV file.  

*Note that `/usr/bin/lpoptions -l` without specifying a printer will list options for the default printer.*


### Example:
```
./print_generator.py --printername="MyPrinterQueue" \
		--driver="HP officejet 5500 series.ppd.gz" \
		--address="10.0.0.1" \
		--location="Tech Office" \
		--displayname="My Printer Queue" \
		--desc="Black and white printer in Tech Office" \
		--requires="CanonPrinterDriver" \
		--options="HPOptionDuplexer=True OutputMode=normal" \
		--icon="HP LaserJet 4250.icns" \
		--version=1.5
```

The output pkginfo file generated:

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>autoremove</key>
	<false/>
	<key>catalogs</key>
	<array>
		<string>testing</string>
	</array>
	<key>description</key>
	<string>Black and white printer in Tech Office</string>
	<key>display_name</key>
	<string>My Printer Queue</string>
	<key>icon_name</key>
	<string>HP LaserJet 4250.icns</string>
	<key>installcheck_script</key>
	<string>#!/usr/bin/python
import subprocess
import sys
import shlex

printerOptions = { "HPOptionDuplexer":"True", "OutputMode":"normal" }

cmd = ['/usr/bin/lpoptions', '-p', 'MyPrinterQueue', '-l']
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(lpoptLongOut, lpoptErr) = proc.communicate()

# lpoptions -p printername -l will still exit 0 even if printername does not exist
# but it will print to stderr
if lpoptErr:
    print lpoptErr
    sys.exit(0)

cmd = ['/usr/bin/lpoptions', '-p', 'MyPrinterQueue']
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(lpoptOut, lpoptErr) = proc.communicate()

#Note: lpoptions -p printername will never fail. If MyPrinterQueue does not exist, it 
#will still exit 0, but just produce no output.  
#Thanks, cups, I was having a good day until now.

for option in lpoptLongOut.splitlines():
    for myOption in printerOptions.keys():
        optionName = option.split("/", 1)[0]
        optionValues = option.split("/",1)[1].split(":")[1].strip().split(" ")
        for opt in optionValues:
            if "*" in opt:
                actualOptionValue = opt.replace('*', '')
                break
        if optionName == myOption:
            if not printerOptions[myOption].lower() == actualOptionValue.lower():
                print "Found mismatch: %s is '%s', should be '%s'" % (myOption, printerOptions[myOption], actualOptionValue)
                sys.exit(0)

optionDict = {}                
for builtOption in shlex.split(lpoptOut):
    try:
        optionDict[builtOption.split("=")[0]] = builtOption.split("=")[1]
    except:
        optionDict[builtOption.split("=")[0]] = None
    
comparisonDict = { "device-uri":"lpd://10.0.0.1", "printer-info":"My Printer Queue", "printer-location":"Tech Office" }
for keyName in comparisonDict.keys():
    if not comparisonDict[keyName] == optionDict[keyName]:
        print "Settings mismatch: %s is '%s', should be '%s'" % (keyName, optionDict[keyName], comparisonDict[keyName])
        sys.exit(0)

sys.exit(1)</string>
	<key>installer_type</key>
	<string>nopkg</string>
	<key>minimum_os_version</key>
	<string>10.7.0</string>
	<key>name</key>
	<string>AddPrinter_MyPrinterQueue</string>
	<key>postinstall_script</key>
	<string>#!/usr/bin/python
import subprocess
import sys

# Populate these options if you want to set specific options for the printer. E.g. duplexing installed, etc.
printerOptions = { "HPOptionDuplexer":"True", "OutputMode":"normal" }

cmd = [ '/usr/sbin/lpadmin', '-x', 'MyPrinterQueue' ]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(lpadminxOut, lpadminxErr) = proc.communicate()

# Install the printer
cmd = [ '/usr/sbin/lpadmin',
        '-p', 'MyPrinterQueue',
        '-L', 'Tech Office',
        '-D', 'My Printer Queue',
        '-v', 'lpd://10.0.0.1',
        '-P', "/Library/Printers/PPDs/Contents/Resources/HP officejet 5500 series.ppd.gz",
        '-E',
        '-o', 'printer-is-shared=false',
        '-o', 'printer-error-policy=abort-job' ]

for option in printerOptions.keys():
    cmd.append("-o")
    cmd.append(str(option) + "=" +  str(printerOptions[option]))

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(lpadminOut, lpadminErr) = proc.communicate()

if lpadminErr:
    print "Error: %s" % lpadminErr
    sys.exit(1)
print "Results: %s" % lpadminOut    
sys.exit(0)</string>
	<key>requires</key>
	<array>
		<string>CanonPrinterDriver</string>
	</array>
	<key>unattended_install</key>
	<true/>
	<key>uninstall_method</key>
	<string>uninstall_script</string>
	<key>uninstall_script</key>
	<string>#!/bin/bash
/usr/sbin/lpadmin -x MyPrinterQueue</string>
	<key>uninstallable</key>
	<true/>
	<key>version</key>
	<string>1.5</string>
</dict>
</plist>
```
