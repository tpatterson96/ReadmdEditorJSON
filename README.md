# ReadmdEditorJSON
mdEditor (go.mdEditor.org) is a browser-based application for metadata creation.
The exported file type is mdEditor JSON file.  The format is not typical JSON.  It resembles a one element
dict{data: text}. 
This script defines a python function that breaks apart the text portion of the JSON file
to extract metadata entities and values and writes an output.
This repository includes:
Read_mdEdiotr_JSON_to_csv.py writes metadata to csv file
Read_mdEditory_JSON_to_shapefile.py writes the metadata to a shapefile where the extent is the geometry
python_walk_RDR.py is a short script to walk the USFWS Alaska Regional Data Repository (RDR) where metadata is internally stored by program.
Notebooks are applications of these codes and/or testing and development workspaces.

for further information contact:  Tammy Patterson (tamatha_patterson@fws.gov)

