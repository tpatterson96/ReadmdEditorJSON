#This script is designed to search and compile data from the Alaska Regional Data Repository (RDR) for each project 
# to track data management progress. Each project should have a data management plan, project metadata, associated data, protocol(s), 
# and associated product metadata. While the scipt cannot assertain the quality of these items, it can identify what is present and who is responsible.
#Returns info: RDR folder, DMP, program; subprogram, record types, title, project status, metadata Status, startDate, endDate, RDR identifier (if present), 
# lastUpdate date, # records publisehd to SB, Point of Contact, owner/trustee, admininstrator, url, if project metadata is Online, Number of products online, 
# # of dictionarys included in metadata, where data is present, how much in raw data and in final data.

#import packages
import os
import pandas as pd
import os
import json
import csv
import collections

def find_program(x):
    if 'mbm' in x:
        y = 'mbm'
    elif 'fes' in x:
        y = 'fes'
    elif 'nwrs' in x:
        y = 'nwrs'
    elif 'sa' in x:
        y = 'sa'
    else:
        y = 'none'
    return y


#define functions
def find_team(x):
    if 'mbmjv' in x:
        y = 'SeaduckJV'
    elif 'mbmlb' in x:
        y = 'Landbirds'
    elif 'mbmra' in x:
        y = 'Raptors'
    elif 'mbmsb' in x:
        y = 'Seabirds'
    elif 'mbmsh' in x:
        y = 'Shorebirds'
    elif 'mbmss' in x:
        y = 'Science Support'
    elif 'mbmwa' in x: 
        y = 'Waterfowl'
    elif 'mbmambcc' in x:
        y = 'AMBCC'
    elif 'fessaf' in x:
        y = 'Southern Alaskan FWCO Fisheries'
    elif 'fessae' in x:
        y = 'Southern Alaskan FWCO Ecological Services'
    elif 'fesnaf' in x:
        y = 'Northern Alaskan FWCO Fisheries'
    elif 'fesnae' in x:
        y = 'Northern Alaskan FWCO Ecological Services'
    elif 'fesmmm' in x:
        y = 'Marine Mammals Management'
    elif 'fesesc' in x: 
        y = 'Regional Ecological Services'
    elif 'fesisp' in x:
        y = 'Invasive Species Program'
    elif 'feshrp' in x:
        y = 'Habitat Restoration and Partnerships'
    else:
        y = 'none'
    return y

def removeComma(string): #define remove comma function
    return string.replace(",","; ")
    
def listToString(s): #define converting list to a string format
    str1 = "; "
    return (str1.join(s))
    
def def_value():
    return "none"

def get_folder_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size
    
