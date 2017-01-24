# -*- coding: utf-8 -*-

import csv
from sys import argv
from datetime import datetime
from glob import glob

input_date_mask 				= "%d %b %Y %H:%M:%S"
output_date_mask_date 			= "%d/%m/%Y %H:%M:%S"
output_date_mask_sample_ref 	= "%Y%m%d-%H-%M"
output_date_mask_csv_name	 	= "%Y%m%d_%H_%M"
prefix 							= "CTD"
separator 						= ","
inputpath						= "/tmp"
outputpath						= "/tmp"



def load_properties(file_path):
    from os import path
    global input_date_mask, output_date_mask_date, output_date_mask_sample_ref, prefix, separator,\
    outputpath, inputpath

    config = RawConfigParser()
    config.read(file_path)

    #ctd properties
    input_date_mask = config.get("ctd", "input_date_mask")
    output_date_mask_date = config.get("ctd", "output_date_mask_date")
    output_date_mask_sample_ref = config.get("ctd", "output_date_mask_sample_ref")
    prefix = config.get("ctd", "prefix")
    separator = config.get("ctd", "separator")
    outputpath = config.get("ctd", "outputpath")
    inputpath = config.get("ctd", "inputpath")

    if not (path.exists(inputpath) and path.isdir(inputpath)):
    	raise ValueError("O caminho para o diretorio de entrada %s é inesistente, sem permissão ou não é um diretório" % inputpath)

    if not (path.exists(outputpath) and path.isdir(outputpath)):
    	raise ValueError("O caminho para o diretorio de saida %s é inesistente, sem permissão ou não é um diretório" % outputpath)







def extract_p_and_date(line):
	line_array					= line.split(separator)
	depth   					= float(line_array[0])
	p = "P1" if depth else "P3" if depth > 32 else "P2"
	reading_date				= datetime.strptime(line_array[11], input_date_mask)
	return (p, reading_date)

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




def parse():

	array_header = ["Depth[m]", "Sal[PSU]", "Temp[C]", "Cond[mS/cm]", "Dens[kg/m3]",
		"SigmaT[kg/m3]", "Chl_a[mg/m3]", "Turb[NTU]", "DO[%]", "DO[mg/l]", "Site",
		"Sample Point", "Datasource", "Date", "Sample Ref"]

	csv_files = []
	for asc_filename in glob("%s/*.asc" % inputpath):
		with open(asc_filename, mode="r") as asc_file:
			p, first_date = extract_p_and_date(asc_file.readline())
			asc_file.seek(0)
			i = 1
			csv_name = "%s/%s_%s_%s.csv" % (outputpath, prefix, p, first_date.strftime(output_date_mask_csv_name))
			csvFile = open(csv_name, mode="w")
			csvwriter = csv.DictWriter(csvFile,  fieldnames=array_header)
			# writer.writerow(array_header)
			csvwriter.writeheader()
			for line in asc_file.readlines():
				map_info = extract_csv_info(line, i, p)
				csvwriter.writerow(map_info)
				i += 1

			csvFile.close()
			csv_files.append(csvFile)

	return csv_files




if __name__ == '__main__':
    caminho_arquivo_prop = argv[1] if len(argv) > 1 else 'ctd.conf'
    csv_files = parse()
    print("Arquivo gerado %s" % [file.name for file in csv_files])
