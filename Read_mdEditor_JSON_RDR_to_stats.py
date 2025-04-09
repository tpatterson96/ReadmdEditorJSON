#These functions are designed to read metadata files generated from mdEditor and collection fields used 
# to track data management progress. Metadata records MUST meet the Alaska reional metadata standard in order to be successfully read.
# Each project should have a data management plan, project metadata, associated data, protocol(s), and associated product metadata. 
# While the scipt cannot assertain the quality of these items, it can identify what is present and who is responsible.
# Returns info: RDR folder, DMP, program; subprogram, record types, title, project status, metadata Status, startDate, endDate, RDR identifier (if present), 
# lastUpdate date, # records publisehd to SB, Point of Contact, owner/trustee, admininstrator, url, if project metadata is Online, Number of products online, 
# of dictionarys included in metadata, where data is present, how much in raw data and in final data.

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
    elif 'fesecs' in x:
        y = 'Ecological Services Reional Office'
    elif 'fescgl' in x:
        y = 'Conservation Genetics Lab'
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
    
def get_metavalues(m, contact_md):
    import collections
    from collections import defaultdict
    import pandas as pd
    
    def removeComma(string): #define remove comma function
        return string.replace(",","; ")
    
    def listToString(s): #define converting list to a string format
        str1 = "; "
        return (str1.join(s))
    
    #set varibles to defaults 
    records = "no metadata"
    title = "no metadata"
    status = "no metadata"
    metadataStatus = "no metadata"
    startDate = 1900
    endDate = 1900
    DOI = "none"
    RDR = "none"
    dateType = "none"
    lastUpdate = 1900
    SB = 0
    projectOnline = 0
    productsOnline = 0
    dictionary = 0
    PointOC = "none"
    owner = "none"
    admin = "none"
    url = "none"
    typeDic = defaultdict(int)  #empty default dictionary to track metadata record types
    ids = []

    df = pd.read_json(m)  #read JSON metadata files into dataframe
    if len(df.get('data')) == 0 :
        print ("cannot read 'data'")
    else:
        values = df.get('data')  #assigns metadata to values
        for e in range(0, len(values)):  #json file may have multiple metadata records
            element = values[e]  #assign list value e containing the metadata #keys= id, attributes, type
            attribute = element.get('attributes')  #keys= profile, json, data-updated
            typpe = element.get('type')   #get metadata type
            typeDic[typpe] += 1
            if typpe != 'records':  #skip if metadata is not a record and is a data dictionary, setting, schemas, custom-profiles...   
                continue  #go to next record
            jsondata = attribute.get('json')  #create'json' data value
            #convert string to dictionary
            jsondatadict = json.loads(jsondata)  #3 keys = schema, metadata, mdDictionary
            metadata = jsondatadict.get('metadata')  #4 keys = metadataInfo, resourceInfo, associatedResource, resourceDistribution\n",
            mdDictionary = jsondatadict.get('mdDictionary')
            #get metadata key entries
            resourceInfo = metadata.get('resourceInfo')        
            #resourceInfo = 12 keys: 'resourceType', 'citation', 'pointOfContact', 'abstract', 'shortAbstract', 'status', \n",
            #...'defaultResourceLocale', 'extent', 'keyword', 'purpose', 'taxonomy', 'timePeriod'\n",
            resourceType = resourceInfo.get('resourceType')
            #parse resource type info
            typelist = resourceType[0]
            typee = typelist.get('type')
            #print ('typee is ', typee)
            typeDic[typee] += 1 # count resource type ie project, tabular dataset, dictionary, etc.
            typeename = typelist.get('name')
            if typeename != None: 
                typeename = removeComma(typelist.get('name'))  #harvest
            citation = resourceInfo.get('citation')
            pointOfContact = resourceInfo.get('pointOfContact') #harvested
            #gather identifiers to determine repository status
            #pull citation identifiers
            if 'identifier' in citation:
                identify = citation.get('identifier')
                for fier in identify:
                    #print (fier)
                    try:
                        ns = fier.get('namespace')
                        i = fier.get('identifier')
                        nsi = str(ns +': '+i)
                        if ns == 'Alaska Regional Data Repository':
                            RDR = i  #Harvest
                        if ns == 'ServCat':
                            if typee == 'project':
                                url = str('https://iris.fws.gov/APPS/ServCat/Reference/Profile/'+ i) #Harvest
                            projectOnline += 1
                        if ns == 'gov.sciencebase.catalog':
                            if typee == 'project':
                                url = str('https://www.sciencebase.gov/catalog/item/'+ i) #Harvest
                            projectOnline += 1
                        ids.append(nsi)  #Harvest
                    except:
                        continue
            if 'gov.sciencebase.catalog' in listToString(ids):
                SB += 1
            if 'ServCat' in listToString(ids):
                SB += 1
            
            #Pull metadata from project metadata only
            if typee != 'project':
                continue
            #for project metadata, do following:    
            metadataInfo = metadata.get('metadataInfo') #6 Keys = metadataIdentifier, metadataContact, defaultMetadataLocale, metadataDate, parentMetadata, metadataStatus
            metadataDate = metadataInfo.get('metadataDate')
            #parentMetadata = metadataInfo.get('parentMetadata')
            metadataStatus = metadataInfo.get('metadataStatus')  #Harvested
            #abstract = removeComma(resourceInfo.get('abstract'))  #harvested
            title = removeComma(citation.get('title'))  #harvested
            responsibleParty = citation.get('responsibleParty')
            statusList = resourceInfo.get('status')
            status = statusList[0]  #harvest
            #get last update date
            try:
                for d in range(1, len(metadataDate)):
                    metadate = metadataDate[d]
                    if metadate.get('dateType') == "lastUpdate":
                        lastUpdate = (metadate.get('date')).split('T')[0]
                        #dateType = 'last updated'
                    else: 
                        #dateType = metadate.get('dateType')
                        lastUpdate = (metadate.get('date')).split('T')[0]                   
            except:
                lastUpdate = "None"
                #dateType = "None"
            #Get and format startDate and endDate
            timePeriod = resourceInfo.get('timePeriod') 
            try:
                startDate = (timePeriod.get('startDateTime','None')).split('T')[0]
                end = timePeriod.get('endDateTime', 'None')
                if end == None:
                    endDate = 'onGoing'
                else:
                    endDate = end.split('T')[0]
            except:
                startDate = 'None'
                endDate = 'None'


        #POINTS of CONTACT
        #read Master Contact JSON metadata file into dataframe
        contactmetadata = pd.read_json(contact_md)
        contactmd1 = dict(contactmetadata)
        contactmd2 = contactmd1.get('data')
        POC = collections.defaultdict(list) # create empty dictionary for contacts
        POCvalues = []
        count = 0
        #iterate through master contact metadata
        for k in contactmd2:
            contactmd3 = contactmd2[count]
            contactmd4 = contactmd3.get('attributes')
            contactmd5 = contactmd4.get('json')
            if contactmd5 is not None:
                contactmd6 = json.loads(contactmd5)
                contactmd7 = dict(contactmd6)
                contactIDmd = contactmd7.get('contactId') #harvest id#
                count += 1
            else:
                continue
            # iterate through contacts from metadata
            for j in pointOfContact:
                party = j.get('party')
                for p in range(0, len(party)):
                    partyContact = party[p]
                    partyContactID = partyContact.get('contactId') #id to compare in master contact list
                    role = j.get('role')
    
                    #compare master list contact ID with metadata contact ID
                    if contactIDmd == partyContactID:
                        contactName = contactmd7.get('name')
                        POC[role].append(contactName)
                    else:
                        continue
                        
        productsOnline = SB - projectOnline
        owner = listToString(POC['owner'])
        PointOC = listToString(POC['pointOfContact'])
        admin = listToString(POC['administrator'])
        dictionary = typeDic.get('dictionaries', 0)
        records = str(typeDic).removeprefix(str("defaultdict(<class 'int'>, {")).replace("})",'')
    
    return [records, title, status, metadataStatus, startDate, endDate, RDR, lastUpdate, SB, PointOC, owner, admin, url, projectOnline, productsOnline, dictionary]

    