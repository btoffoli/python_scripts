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
inputpath						= "/tmp/"
outputpath						= "/tmp/"
txt_separator = "\t"



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
	p = "P1" if depth < 10 else "P3" if depth > 32 else "P2"
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

def extract_txt_info(line):
	line_array = line.split(separator)

	depth 						= float(line_array[0])
	sal 				 		= float(line_array[1])
	temp 				 		= float(line_array[2])
	cond 					 	= float(line_array[3])
	dens 				 		= float(line_array[4])
	sigma						= float(line_array[5])
	chl 						= float(line_array[6])
	turb						= float(line_array[7])
	do_per						= float(line_array[8])
	do_mg_l						= float(line_array[9])
	nao_sei						= float(line_array[10])
	reading_date				= datetime.strptime(line_array[11], input_date_mask)

	day 						= reading_date.day
	month 						= reading_date.month
	year 						= reading_date.year
	hour 						= reading_date.hour
	minute 						= reading_date.minute
	second 						= reading_date.second


	resp_array = [
		depth,
		sal,
		temp,
		cond,
		dens,
		sigma,
		chl,
		turb,
		do_per,
		do_mg_l,
		nao_sei,
		day,
		month,
		year,
		hour,
		minute,
		second
	]

	# resp_str = txt_separator.join(map(lambda x: str(x), resp_array))
	resp_str = txt_separator.join(map(str, resp_array))
	print(resp_str)

	return resp_str




def parse():

	array_header = ["Depth[m]", "Sal[PSU]", "Temp[C]", "Cond[mS/cm]", "Dens[kg/m3]",
		"SigmaT[kg/m3]", "Chl_a[mg/m3]", "Turb[NTU]", "DO[%]", "DO[mg/l]", "Site",
		"Sample Point", "Datasource", "Date", "Sample Ref"]

	csv_files = []
	txt_files = []
	p_map_count = {
		'P1': 0,
		'P2': 0,
		'P3': 0
	}
	for asc_filename in glob("%s*.asc" % inputpath):
		with open(asc_filename, mode="r") as asc_file:
			try:
				# print(asc_file.name)
				p, first_date = (None,None)
				for line in asc_file.readlines():
					p, first_date = extract_p_and_date(line)
				asc_file.seek(0)
				i = 1
				#CSV
				csv_name = "%s%s_%s_%s.csv" % (outputpath, prefix, p, first_date.strftime(output_date_mask_csv_name))
				csvFile = open(csv_name, mode="w")
				csvwriter = csv.DictWriter(csvFile,  fieldnames=array_header)
				csvwriter.writeheader()

				#TXT
				p_map_count[p] += 1
				txt_name = "%s%s_Relatorio_%s_%d.txt" % (outputpath, prefix, p, p_map_count[p])
				txt_file = open(txt_name, mode="w")


				for line in asc_file.readlines():
					# CSV
					map_info = extract_csv_info(line, i, p)
					csvwriter.writerow(map_info)

					# TXT
					txt_line = extract_txt_info(line)
					txt_file.write("%s\n" % txt_line)


					i += 1

				txt_file.close()
				txt_files.append(txt_file)
				csvFile.close()
				csv_files.append(csvFile)
			except Exception as e:
				print("Erro %s em %s", str(e), asc_filename)
			finally:
				asc_file.close()


	return (csv_files, txt_files)




if __name__ == '__main__':
    caminho_arquivo_prop = argv[1] if len(argv) > 1 else 'ctd.conf'
    files = parse()
    print("Arquivos csv gerados %s" % [file.name for file in files[0]])
    print("Arquivos txt gerados %s" % [file.name for file in files[1]])
