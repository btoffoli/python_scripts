# -*- coding: utf-8 -*-

import csv
from datetime import datetime

input_date_mask 				= "%d %b %Y %H:%M:%S"
output_date_mask_date 			= "%Y%m%d-%H-%M"
output_date_mask_sample_ref 	= "%Y%m%d-%H-%M"
prefix 							= "CTD"
separator 						= ","


def extract_p(line):
	line_array					= line.split(separator)
	depth   					= float(line_array[0])
	return "P1" if depth else "P3" if depth > 32 else "P2"

def extract_csv_info(line, line_number, p):
	resp_map = {}

	line_array = line.split(separator)

	depth 						= float(line_array[0])
	resp_map["Depth[m]"] 		= depth
	resp_map["Sal[PSU]"] 		= float(line_array[1])
	resp_map["Temp[C]"]  		= float(line_array[2])
	resp_map["Cond[mS/cm]"]  	= float(line_array[3])
	resp_map["Dens[kg/m3]"] 		= float(line_array[4])
	resp_map["SigmaT[kg/m3]"]		= float(line_array[5])
	resp_map["Chl_a[mg/m3]"]		= float(line_array[6])
	resp_map["Turb[NTU]"]		= float(line_array[7])
	resp_map["DO[%]"]			= float(line_array[8])
	resp_map["DO[mg/l]"]		= float(line_array[9])
	
	resp_map["Site"]			= "Estações Oceanográficas"	
	resp_map["Sample Point"]	= "Estacao %s" % p
	resp_map["Datasource"]		= prefix
	reading_date				= datetime.strptime(line_array[11], input_date_mask)
	resp_map["Date"] 			= reading_date.strftime(output_date_mask_date)
	resp_map["Sample Ref"]		= "%s%s_%.2d" %(prefix, reading_date.strftime(output_date_mask_sample_ref), line_number)

	return resp_map




csvFile = open("/tmp/%s%s.csv" %(prefix, datetime.now().isoformat()), mode="w")
array_header = ["Depth[m]", "Sal[PSU]", "Temp[C]", "Cond[mS/cm]", "Dens[kg/m3]",
"SigmaT[kg/m3]", "Chl_a[mg/m3]", "Turb[NTU]", "DO[%]", "DO[mg/l]", "Site",
"Sample Point", "Datasource", "Date", "Sample Ref"]

writer = csv.DictWriter(csvFile,  fieldnames=array_header)
# writer.writerow(array_header)
writer.writeheader()

with open("/home/btoffoli/Downloads/SBE19plus_01906864_2016_11_24_0440rel_5binasc.asc", mode="r") as asc_file:	
	p = extract_p(asc_file.readline())
	asc_file.seek(0, 0)
	i = 1	
	for line in asc_file.readlines():
		map_info = extract_csv_info(line, i, p)
		writer.writerow(map_info)
		i += 1

csvFile.close()

		