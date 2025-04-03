#define function to read mdEditor files, and write out as shapefile
#and shapefile with geography, if applicable
#by Tamatha A. Patterson; verson 5; December 2022
#distribution section updated.
#extent merged with metadata and written to shapefile. #FeatureCollection type handled.
#associations section updated.

def mdEditor_read(metadataToRead, contact_md, csvname, workspace, recordtype = 'all'):
    #recordtype used to write chosen resource types  \"all\", \"project\", etc.in future versions
    #extent/geography read when is True, skipped when False.
    import os
    import json
    import csv
    import pandas as pd
    import geopandas as gpd
    import collections
    import fiona
    from shapely.geometry import Point, LineString, Polygon, MultiPolygon
    from datetime import date
    
    def removeComma(string): #define remove comma function
        return string.replace(",","; ")
    
    def listToString(s): #define converting list to a string format
        str1 = "; "
        return (str1.join(s))
    
    def def_value():
        return "none"
    
    os.chdir(workspace) # assign working directory
    today = date.today()
    
    df = pd.read_json(metadataToRead)#read JSON metadata files into dataframe
    values = df.get('data') #assigns metadata to values
    for e in range(0, len(values)): #json file may have multiple metadata records
        element = values[e] #assign list value e containing the metadata #keys= id, attributes, type
        ID = element.get('id') #get metadata id
        attribute = element.get('attributes') # keys= profile, json, data-updated
        typpe = element.get('type') #get metadata type
        if typpe != 'records':  
            # skip if metadata is not a record and is a data dictionary, setting, schemas, custom-profiles...
            continue  #go to next record

        #parse 'attribute' to create profile, json, and date-updated\n",
        dateUpdate = attribute.get('date-updated') #create dateUpdate value--where does this date come from???
        jsondata = attribute.get('json') #create'json' data value
        profile = attribute.get('profile') #create 'profile' value
        
        #convert string to dictionary
        jsondatadict = json.loads(jsondata)  #3 keys = schema, metadata, mdDictionary
        schema = jsondatadict.get('schema')
        metadata = jsondatadict.get('metadata') #4 keys = metadataInfo, resourceInfo, associatedResource, resourceDistribution\n",
        mdDictionary = jsondatadict.get('mdDictionary')
        #get metadata key entries
        metadataInfo = metadata.get('metadataInfo') #6 Keys = metadataIdentifier, metadataContact, defaultMetadataLocale, metadataDate, parentMetadata, metadataStatus
        resourceInfo = metadata.get('resourceInfo') #12 keys = resourceType, citation, pointOfContact, abstract, shortAbstract, status, defaultResourceLocale, extent, keyword, purpose, taxonomy, timePeriod
        associatedResource = metadata.get('associatedResource') #is list
        resourceDistribution = metadata.get('resourceDistribution') #keys = n

        #parse metadataInfo dictionary 6 keys
        metadataIdentifier = metadataInfo.get('metadataIdentifier') #Harvest as ID to fields
        metadataContact = metadataInfo.get('metadataContact')
        defaultMetadataLocale = metadataInfo.get('defaultMetadataLocale')
        metadataDate = metadataInfo.get('metadataDate')
        parentMetadata = metadataInfo.get('parentMetadata')
        metadataStatus = metadataInfo.get('metadataStatus') #Harvest as status to fields

        #get metadata uuid identifier; autocreated in mdEditor\n",
        if metadataIdentifier['namespace'] == 'urn:uuid':
                metaIdentifier = metadataIdentifier.get('identifier')

        #parse resourceInfo 12 keys: 'resourceType', 'citation', 'pointOfContact', 'abstract', 'shortAbstract', 'status', \n",
        #...'defaultResourceLocale', 'extent', 'keyword', 'purpose', 'taxonomy', 'timePeriod'\n",
        resourceType = resourceInfo.get('resourceType')
        citation = resourceInfo.get('citation')
        pointOfContact = resourceInfo.get('pointOfContact')
        abstract = removeComma(resourceInfo.get('abstract')) #harvested to fields
        if resourceInfo.get('shortAbstract') == None:
            shortAbstract = " "
        else:
            shortAbstract = removeComma(resourceInfo.get('shortAbstract'))#harvested as shortAbstract to fields
        statusList = resourceInfo.get('status')
        status = statusList[0]#harvest as status to fields
        defaultResourceLocale = resourceInfo.get('defaultResourceLocale')
        extent = resourceInfo.get('extent')
        keyword = resourceInfo.get('keyword')
        if resourceInfo.get('purpose') == None:
            purpose = " "
        else:
            purpose = removeComma(resourceInfo.get('purpose')) #harvested to fields
        taxonomy = resourceInfo.get('taxonomy')
        timePeriod = resourceInfo.get('timePeriod')

        #find last update date from metadataDate
        #Consider comparing this to last run date and only reading metadata updated after????
        if len(metadataDate) == 1:
            lastUpdate = metadataDate[0].get('date') 
            dateType = metadataDate[0].get('dateType')
        else:
            if len(metadataDate) > 1:
                for i in metadataDate:
                    if i.get('dateType') == "lastUpdate":
                        lastUpdate = (i.get('date')).split('T')[0]
                        dateType = 'last updated'
                    else: 
                        dateType = i.get('dateType')
                        lastUpdate = (i.get('date')).split('T')[0]                   

        #parse resource Type info
        typelist = resourceType[0]
        typee = typelist.get('type')
        typeename = typelist.get('name')
        if typeename != None: 
            typeename = removeComma(typelist.get('name'))

        #parse citation info
        title = removeComma(citation.get('title')) #harvested as title to fields
        dates = citation.get('date')
        responsibleParty = citation.get('responsibleParty')
        altTitle = citation.get('alternateTitle')
        if altTitle != None:
            altTitle = listToString(altTitle)#Harvested as altTitle to fields
            altTitle = removeComma(altTitle)
        
        #Get and format startDate and endDate
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
            
            
        #['EARTH SCIENCE > BIOLOGICAL CLASSIFICATION > ANIMALS/VERTEBRATES > BIRDS > SANDPIPERS', 
        #'biota', 'intelligenceMilitary', 'environment', 'yellowlegs', 'shorebird', 'migration', 'life cycle']
        
        #create empty list for keywords
        klist =[]
        #loop through keyword thesaurus and add keywords to keyword list
        try:
             #loop through keyword thesaurus and add keywords to keyword list
            for g in range(0, len(keyword)):
                word = keyword[g]
                #print(word.keys())
                word1 = word.get('keyword') #list of variable length
                #print(word1)
                for h in range(0, len(word1)):
                    word2 = word1[h]
                    word3 = word2.get('keyword')#string
                    word4 = word.get('keywordType')
                    word5 = word.get('thesaurus')#dict_keys(['date', 'title', 'edition', 'onlineResource', 'identifier'])
                    ktype = word5.get('title') 
                    if ktype == 'Global Change Master Directory (GCMD) Science Keywords':
                        parseword = word3.split('>')
                        klist.append(parsedword.lower())
                    else:
                        klist.append(word3)

            keywords = listToString(klist)
            
        except:
            keywords = 'None'
            
        #parse species names from taxonomy; may need to loop if more than one species.
        try: # check for taxonomy entry
            taxdic = taxonomy[0]
            taxClass = taxdic.get('taxonomicClassification')
            taxSys = taxdic.get('taxonomicSystem')
            taxvoucher = taxdic.get('voucher')
            taxClass1 = taxClass[0]
            taxClass1.keys()
            taxSysID = taxClass1.get('taxonoicSystemID')
            taxLevel = taxClass1.get('taxonomicLevel')
            taxName = taxClass1.get('taxonomicName')
            taxSubClass = taxClass1.get('subClassification')
            taxIs = taxClass1.get('isITIS')
            taxSub0 = taxSubClass[0]
            taxSysID0 = taxSub0.get('taxonoicSystemID')
            taxLevel0 = taxSub0.get('taxonomicLevel')
            taxName0 = taxSub0.get('taxonomicName')
            taxSubClass0 = taxSub0.get('subClassification')
            taxIs0 = taxSub0.get('isITIS')
            subKingdom =taxSubClass0[0]
            infraKingdomL = subKingdom.get('subClassification')
            infraKingdom = infraKingdomL[0]
            phylumL = infraKingdom.get('subClassification')
            phylum = phylumL[0]
            subphylumL = phylum.get('subClassification')
            subphylum = subphylumL[0]
            infraphylumL = subphylum.get('subClassification')
            infraphylum = infraphylumL[0]
            superclassL = infraphylum.get('subClassification')
            superclass = superclassL[0]
            classL = superclass.get('subClassification')
            classD = classL[0]
            orderL = classD.get('subClassification')
            order = orderL[0]
            familyL = order.get('subClassification')
            family = familyL[0]
            genusL = family.get('subClassification')
            genus = genusL[0]
            taxname = genus.get('taxonomicName') #harvested to fields
            t =[taxname]
            comname = genus.get('commonName') #harvested to fields
            t.append(comname)
            comname = listToString(comname)
            comname = removeComma(comname)
        except:  # if no taxomony, then assign 'none'
            taxname = "none"
            comname = "none"  
    
    #Get Associated Resource Info
    #if assocated resources are selected from metadata records.... then:
        try:
            assoclist = []  # create empty list of assocated resource
            assocdic = associatedResource[0] #dict_keys(['resourceType', 'resourceCitation', 'associationType', 'initiativeType'])
            aresourceType = assocdic.get('resourceType')
            aresourceCitation = assocdic.get('resourceCitation')
            aassociationType = assocdic.get('associationType')#harvest as associationType ie parentProject
            ainitiativeType = assocdic.get('initiativeType') #initiativeType ie project
            if aassociationType == 'parentProject' and aresourceType != None:  #this is product metadata record
                aresourceType1 = aresourceType[0] #i.e.{'type': 'project', 'name': 'Lesser Yellowlegs Ecology'}
                atype = aresourceType1.get('type') #get first entry to remove brackets
                aname = aresourceType1.get('name')
                addassoc = "parentProject: " + aname
                assoclist.append(addassoc)
            elif aassociationType == 'product': #this is project metadata record
                for a in range (0, len(associatedResource)):
                    l = associatedResource[a]
                    k = l.get('mdRecordId')
                    assoclist.append(k)
            else:
                assoclist = 'no assocated records'
        except:
            assoclist = 'no assocated records present'
        
        assoclistString = '; '.join(assoclist)
        
    
    #get resourceDistribution metada
        resourceDistribution = metadata.get('resourceDistribution')
        distlist = {} #create empty distribution list
        try:
            for d in range(0, len(resourceDistribution)): #iterate through resourceDistribution info list
                distributor = resourceDistribution[d]
                dist = dict(distributor)
                dist0 = dist.get("distributor")
                dist1 = dist0[0] #dictionary keys = 'contact', 'transferOption'
                contact = dist1.get('contact')
                order = dist1.get('orderProcess')
                transopt = dist1.get('transferOption')
                distrole =contact.get('role') #harvested as distributor role to distlist
                distparty = contact.get('party') #distrbutor contact identifiers
                #if len(distparty) > 1:
                    #for org in range(0,len(distparty)): 
                        #distID = distparty[0]
                        #distributorID = distID.get('contactId') #harvest distributor ID & compare with contact master list be
                #else:
                distID = distparty[0]
                distributorID = distID.get('contactId') #harvest distributor ID & compare with contact master list be
                transopt1 = transopt[0]
                transopt2 = transopt1.get('onlineOption')
                transopt3 = transopt2[0]
                onlineName = transopt3.get('name') #harvested to distlist
                onlineUri = transopt3.get('uri') #harvested to distlist
                distInfo =[distrole, distributorID, onlineName, onlineUri]
                distlist[d] = distInfo
                #print ("distlist = ", distlist)
                distInfoString = '; '.join(distInfo)
            
        except:
            print(title, ' has NO distribution metadata')
            distInfoString = ' '
      
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
            contactmd6 = json.loads(contactmd5)
            contactmd7 = dict(contactmd6)
            contactIDmd = contactmd7.get('contactId') #harvest id#
            count += 1

            for id in distlist:
                if distlist[id][1] == contactIDmd:
                    contactisOrganizationmd = contactmd7.get('isOrganization')
                    contactName = contactmd7.get('name') #havest as distributor name to fields
                    contactMemberOf = contactmd7.get('memberOfOrganization')
                    contactemail = contactmd7.get('electronicMailAdddress')
                    contactType = contactmd7.get('contactType')
                    distlist[id][1] = contactName 

            # iterate through contacts from metadata
            for j in pointOfContact:
                party = j.get('party')
                for p in range(0, len(party)):
                    partyContact = party[p]
                    partyContactID = partyContact.get('contactId') #id to compare in master contact list
                    role = j.get('role')

                    #compare master list contact ID with metadata contact ID
                    if contactIDmd == partyContactID:
                        contactisOrganizationmd = contactmd7.get('isOrganization')
                        contactName = contactmd7.get('name')
                        contactMemberOf = contactmd7.get('memberOfOrganization')
                        contactemail = contactmd7.get('electronicMailAdddress')
                        contactType = contactmd7.get('contactType')
                        POC[role].append(contactName)
                    #else:
                        continue

        owner = listToString(POC['owner'])
        PointOC = listToString(POC['pointOfContact'])
        princ = listToString(POC['principalInvestigator'])
        custodian = listToString(POC['custodian'])
        admin = listToString(POC['administrator'])
        originator = listToString(POC['originator'])
        contributor = listToString(POC['contributor'])
        #distlistString = '; '.join(distInfo) 

   #Write vales to CSV
        #fields = [ID, typee, title, altTitle, typeename, purpose, abstract, shortAbstract, 
                 # PointOC, owner, princ, custodian, admin, originator, contributor, startDate, endDate, lastUpdate, status, 
                  #metaIdentifier, metadataStatus, keywords, taxname, comname, distInfoString, assoclistString] #gEid?
       
        #write files to csv.
        #with open (csvname, 'a', newline = '') as csvfile:
         #   csvwriter = csv.writer(csvfile)
          #  csvwriter.writerow(fields)     
   
        #Extent to geodataframe
        if typee == 'project':  #only gather extents from projects?
            extenlist = (extent[0])
            try:
                extenDisc = extenlist['description'] #harvest as Extent Description?
            except:
                extenDisc = 'noExtentDiscription'
            extenGeo = extenlist['geographicExtent']
            extenGeo1 = extenGeo[0]
            #extenBox = extenGeo1['boundingBox']
            extenGeoElement = extenGeo1['geographicElement'] #type = list

            geoInput =[] #empty list for geoinput to geodataframe
            poly = gpd.GeoDataFrame(columns = ['id', 'name','geometry', 'type', 'title', 'altTitle', 'typename', 
                                               'purpose', 'abstract', 'shortAb', 'PointOC', 'trustee', 'PI', 
                                               'custodian', 'admin', 'origin', 'contrib', 'startDate', 'endDate', 'lastUpdat',
                                               'status', 'metaIdent', 'metaStatus', 'keywords', 'taxname', 'comname',
                                               'distib', 'assoc']) #gEid?
            for ex in range(0, len(extenGeoElement)): #need id, name, descripiton, geometry
                gElement = extenGeoElement[ex]  #=dict_keys(['type', 'id', 'geometry', 'properties']) or ['type', 'features']
                if gElement.get('type') == "FeatureCollection":
                    extrastep = gElement.get('features')
                    nextstep = extrastep[0] #=dict_keys(['type', 'id', 'geometry', 'properties'])
                    gtype = nextstep.get('type') #Feature
                    gEid = nextstep.get('id') #harvest as GeoID to fields
                    gEgeometry = nextstep.get('geometry') #type=dict_keys(['type', 'coordinates'])
                    ggtype = gEgeometry.get('type')
                    gcoordinates = gEgeometry.get('coordinates')#list
                    gEcoordinates = gcoordinates[0] #list length = 1
                    if len(gEcoordinates) == 1:
                        gEcoordinates = gEcoordinates[0]
                
                    #poly_coord = Polygon(gEcoordinates)
                    gEproperties = nextstep.get('properties')
                    gname = gEproperties.get ('name', 'NotNamed') #harvested to geodataframe
                    propertyDesc = gEproperties.get('description', 'NotDescribed')
                    print(propertyDesc)
                    
                    if ggtype == 'Polygon':
                        #gcoordinates = gEgeometry.get('coordinates')#list
                        #gEcoordinates = gcoordinates[0] #list
                        print ('this is polygon')
                        poly_coord = Polygon(gEcoordinates)
                        geoattributes = {'id':gEid, 'name':gname, 'geometry':poly_coord, 'type':typee, 'title':title, 
                            'altTitle':altTitle, 'typename':typeename, 'purpose':purpose, 'abstract':abstract, 'shortAb':shortAbstract, 
                            'PointOC':PointOC, 'trustee':owner, 'PI':princ, 'custodian':custodian, 'admin':admin,
                            'origin':originator, 'contrib':contributor, 'startDate':startDate, 
                            'endDate':endDate, 'lastUpdat':lastUpdate, 'status':status, 
                            'metaIdent':metaIdentifier, 'metaStatus':metadataStatus, 'keywords':keywords, 'taxname':taxname,
                            'comname':comname, 'distrib':distInfoString, 'assoc':assoclistString} #gEid?} #creating dict of geoattrit of geoattribute
                        geoInput.append(geoattributes)
                    elif ggtype == 'Point':
                        #ptcoordinates = gEgeometry.get('coordinates')
                        pt_coord = Point(gcoordinates)
                        #geoattributes = {'id':gEid, 'name':gname, 'geometry':pt_coord} #creating dict of geoattributes
                        continue
                    elif ggtype == 'MultiPolygon':
                        print ('this is multipolygon')
                        mpoly_coord = MultiPolygon(gEcoordinates)
                        geoattributes = {'id':gEid, 'name':gname, 'geometry':mpoly_coord, 'type':typee, 'title':title, 
                            'altTitle':altTitle, 'typename':typeename, 'purpose':purpose, 'abstract':abstract, 'shortAb':shortAbstract, 
                            'PointOC':PointOC, 'trustee':owner, 'PI':princ, 'custodian':custodian, 'admin':admin,
                            'origin':originator, 'contrib':contributor, 'startDate':startDate, 
                            'endDate':endDate, 'lastUpdat':lastUpdate, 'status':status, 
                            'metaIdent':metaIdentifier, 'metaStatus':metadataStatus, 'keywords':keywords, 'taxname':taxname,
                            'comname':comname, 'distrib':distInfoString, 'assoc':assoclistString} #gEid?} #creating dict of geoatttribut                        
                        geoInput.append(geoattributes)
                    else:
                        continue
                        
                elif gElement.get('type') == "Feature":
                    gEtype = gElement.get('type') #dict_keys(['type', 'id', 'geometry', 'properties'])
                    gEid = gElement.get('id') #harvest as GeoID to fields
                    gEgeometry = gElement.get('geometry') #type=dict_keys(['type', 'coordinates'])
                    try:
                        gEproperties = gElement.get('properties')
                        gname = gEproperties.get ('name', 'NotNamed') #harvested to geodataframe
                        #propertyDesc = gEproperties.get('description')
                    except: 
                        gname = 'NotDefined'
                    gtype = gEgeometry.get('type') #indicates geometry type: Polygon, Point, line
                    if gtype == 'Polygon':
                        gcoordinates = gEgeometry.get('coordinates')#list
                        gEcoordinates = gcoordinates[0] #list
                        poly_coord = Polygon(gEcoordinates)
                        geoattributes = {'id':gEid, 'name':gname, 'geometry':poly_coord, 'type':typee, 'title':title, 
                           'altTitle':altTitle, 'typename':typeename, 'purpose':purpose, 'abstract':abstract, 'shortAb':shortAbstract, 
                            'PointOC':PointOC, 'trustee':owner, 'PI':princ, 'custodian':custodian, 'admin':admin,
                            'origin':originator, 'contrib':contributor, 'startDate':startDate, 
                            'endDate':endDate, 'lastUpdat':lastUpdate, 'status':status, 
                            'metaIdent':metaIdentifier, 'metaStatus':metadataStatus, 'keywords':keywords, 'taxname':taxname,
                            'comname':comname, 'distrib':distInfoString, 'assoc':assoclistString} #gEid?} #creating dict of geoattributes
                        geoInput.append(geoattributes)
                    elif gtype == 'Point':
                        ptcoordinates = gEgeometry.get('coordinates')
                        pt_coord = Point(ptcoordinates)
                        #geoattributes = {'id':gEid, 'name':gname, 'geometry':pt_coord} #creating dict of geoattributes
                        continue
                    elif gtype == 'MultiPolygon':
                        gcoordinates = gEgeometry.get('coordinates')#list
                        gEcoordinates = gcoordinates[0] #list
                        mpoly_coord = MultiPolygon(gEcoordinates)
                        geoattributes = {'id':gEid, 'name':gname, 'geometry':mpoly_coord, 'type':typee, 'title':title, 
                            'altTitle':altTitle, 'typename':typeename, 'purpose':purpose, 'abstract':abstract, 'shortAb':shortAbstract, 
                            'PointOC':PointOC, 'trustee':owner, 'PI':princ, 'custodian':custodian, 'admin':admin,
                            'origin':originator, 'contrib':contributor, 'startDate':startDate, 
                            'endDate':endDate, 'lastUpdat':lastUpdate, 'status':status, 
                            'metaIdent':metaIdentifier, 'metaStatus':metadataStatus, 'keywords':keywords, 'taxname':taxname,
                            'comname':comname, 'distrib':distInfoString, 'assoc':assoclistString} #gEid?} #creating dict of geoattributes
                        geoInput.append(geoattributes)
                    else:
                        continue    
            
            poly = gpd.GeoDataFrame(geoInput, geometry = 'geometry', crs = "EPSG:4326")  #crs = lat, long designation 
            polyname = str(workspace + title[0:12] +'.shp') #generate name for shapefile 

                #if geography is desired, then merge metadata with extent and output shapefile
                #if outShape == True:
                #Create shapefile from csv with geographic info
                #metadf = pd.read_csv(csvname, encoding = 'cp1252') #read completed csv into dataframe

                #Subset for projects only
                #projectOnly = pd.DataFrame(metadf.loc[metadf['typee'] == 'project'])

                #merge geodataframe with metadata dataframe
                #dfmerge = pd.merge(poly, projectOnly, how='cross')#,left_on='id',right_on='GeoID')

            #write shapefile
            poly.to_file(polyname, encoding = 'utf-8')#, driver = 'ESRI Shapefile', schema = {"geometry": "Polygon", "properties":{"id":"int"}})
            print(gElement, ' ', gtype, ggtype," shapefile created.", "Number of contacts in master list = ", len(contactmd2))
    return
    