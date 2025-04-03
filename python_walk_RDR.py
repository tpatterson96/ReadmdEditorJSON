#Search Migratory Birds Management RDR folder for mdeditor files to extract metadata
#Count number of preserved mdEditor records
import os
RDR = '\\\\ifw7ro-file.fws.doi.net\\datamgt\\mbm'
MBMmetadataNo = 0
program = "Migratory Bird Manangement"

# Pathway to the contacts file you want to use to check against existing vs. new contacts; i.e., master AK contacts file\n",
contact_md = 'C:\\Users\\tpatterson\\OneDrive - DOI\\Documents\\DM_Metadatafiles\\AKContactsmdeditor-20211228-101265.json'

# Pathway to csv file where to write metaata
csvname = 'C:\\Users\\\\tpatterson\\OneDrive - DOI\\Documents\\DM_Metadatafiles\\CatalogCSV\\catalogCSVPhase2v1.csv'

workspace = 'C:\\Users\\tpatterson\\OneDrive - DOI\\Documents\\DM_Metadatafiles\\CatalogCSV\\MBMExtentTest'

#loop through RDR folder structure and find mdeditor json files that is NOT in incoming folder
for root, dirs, files in os.walk(RDR,topdown=True):
    #print ("root=", root, "  dirs=", dirs, "  file=", files)
    for name in files:
        if 'incoming' not in root and 'mdeditor' in name and name.endswith('.json'):
            jfile = os.path.join(root,name)
            mdEditor_read(jfile, contact_md, csvname, workspace)
            MBMmetadataNo += 1
            print (jfile)
print ("Number of MBM completed mdeditor records in RDR = ",MBMmetadataNo) 