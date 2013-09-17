#!/usr/bin/python

import os
import tarfile
import datetime
import shutil
import syslog
import re
import socket

#Get hostname of server
getHostname = socket.gethostname()

#To configure, set the following variables
pathtofiles = '/opt/splunk/etc/' #Set the path to the directory you would like to archive. Note that this utility will recurse through nested directories.
backupLabel = 'splunk' #Optional, if set will be added to the archive filename
pathtoserver = '/mnt/oc03/archive/' #This is the path to the fileserver, default to /mnt/oc03/archive/

#Used to extract the hostname if set to hostname.domainname
if re.search(r"\.", getHostname):
    hostre = re.compile(r"[a-zA-Z0-9]+")
    result = hostre.match(getHostname)
    getHostname = result.group()
else:
    pass

#Create the path to the archive directory, check if exists and create if not exist
makepathtoserver = pathtoserver + '%s/' % getHostname
if os.path.exists(makepathtoserver):
    pass
else:
    os.mkdir(makepathtoserver)

#Establish the location of the script and therefore the output file
pathtoscript  = os.getcwd()

#Create variable with current date and time and creates a string from datatime
now = datetime.datetime.now()
ct_now = now.strftime("%Y%m%d-%H%M%S")

#Create a list of the filenames in the directory and sets the working directory
files = os.listdir(pathtofiles)
os.chdir(pathtofiles)

#Create a variable for the name of the tarfile that includes hostname, timestamp and the actual tar file as a compressed tar
if backupLabel:
    tarfilename =  getHostname + '-' + backupLabel + '_archive' + ct_now + '.tar.gz'
else:
    tarfilename =  getHostname +'_archive' + ct_now + '.tar.gz'
tar = tarfile.open(tarfilename, "w:gz")

#Loop to add files to the tar file
for file in files:
    tar.add(file)
tar.close()

#Copy the archive to the fileserver, do error checking and write appropriate logs to syslogd
tarfilepath = pathtofiles + tarfilename
archivepath = (makepathtoserver + tarfilename)
try:
    shutil.copy(tarfilepath, archivepath)
    syslog.syslog('Completed copy of ' + tarfilepath + ' to ' + archivepath)
except:
    if os.path.exists(pathtoserver):
        syslog.syslog('Failed copy of ' + tarfilepath + ' to ' + archivepath + ' Reason: Unknown exception')
    else:
        syslog.syslog('Failed copy of ' + tarfilepath + ' to ' + archivepath + ' Reason: Path does not exist')

#Remove file from working directory
os.remove(pathtofiles + tarfilename)

#Remove backups older than 7 days and logging result
for dirpath, dirnames, filenames in os.walk(makepathtoserver):
    for file in filenames:
        if re.search(r"archive", file): #Skip files not created by this backup utility
            dt = re.search(r"\d+\-\d+", file).group()
            dtObj = datetime.datetime.strptime(dt, "%Y%m%d-%H%M%S")
            if datetime.datetime.now() - datetime.timedelta(days=7) > dtObj:
                pathtofile = os.path.join(makepathtoserver, file)
                os.remove(pathtofile)
                syslog.syslog("Removed stale backup file: %s" % file)
            else:
                syslog.syslog("No stale bakup files found")
        else:
            pass
        


