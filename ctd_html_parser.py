
from sys import argv
import pytz

from datetime import datetime, timedelta

import pandas as pd
from matplotlib import pyplot as plt, style, dates, ticker
import numpy as np

style.use('ggplot')
separator = " "
dt_html_mask = "%d/%m/%Y %H:%M:%S"
dt_plot_mask = "%d/%m/%Y"

def build_html(list):
	page = '<html xmlns="http://www.w3.org/1999/xhtml">\n'
	page += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
	page += '<link rel="icon" href="SmallLogo.png" type="image/png" />\n'
	page += '<head>\n'
	page += '<title>Marégrafo</title>\n'
	page += '<link href="novoEstilo.css" rel="stylesheet" type="text/css">'
	page += '</head>\n'

	page += '<body>\n'
	page += '<table>\n'
	page += '<tr>\n'
	page += '<th colspan="5">\n'
	page += '<h1 id="logo" class="img-replace">\
					<a href="http://www.messenocean.com/?lang=en" title="MessenOcean">\
					<img class="logo_messen_ocean" src="400dpiLogoCropped.png" alt="Messen Ocean"></a></h1>'
	page += '</th>\n'
	page += '</tr>\n'
	page += '<tr>\n'
	page += '<th>Data/Hora</th>\n'
	page += '<th>Distância do nível da água (m)</th>\n'
	page += '<th>Pressão Barométrica (mbar)</th>\n'
	page += '<th>Maré (m)</th>\n'
	
	# page += '<th>Col4</th>\n'
	page += '<th>Voltagem(v)</th>\n'
	page += '</tr>\n'
	for data in list:
		page += "<tr>"
		page += '<td>%s</td>' % data.ctd_time.strftime(dt_html_mask)
		page += "<td>%.2f</td>" % data.distance
		page += "<td>%d</td>" % data.pressure
		page += "<td>%.2f</td>" % data.tide
		# page += "<td>%d</td>" % data.col4
		page += "<td>%.2f</td>" % data.voltage
		page += "</tr>\n"

	page += "</table>\n"
	page += "</body>\n"
	page += "</html>\n"

	return page



class CTD_DATA(object):
	def __init__(self, 	ctd_time, distance, pressure, tide, col4, voltage):
		self.ctd_time		=  convert_utc_date_to_sao_paulo(ctd_time)
		self.distance 		= distance
		self.pressure		= pressure
		self.tide			= tide
		self.col4			= col4
		self.voltage		= voltage

	def __repr__(self):
		# print(self.voltage)
		# print(self.distance)
		return "<%s|distance:%.2f|pressure:%d|tide:%.1f|col4:%d|voltage:%.1f>" % (
				str(self.ctd_time), 
				self.distance, 
				self.pressure, 
				self.tide, 
				self.col4, 
				self.voltage)


utctz = pytz.utc
# dtype = [('Distância do nível da água (m)','float32'), ('Pressão Barométrica (mbar)','int32'), ('Maré (m)','float32'), ('Voltagem (V)', 'float32')]
dtype = [('Maré (m)','float32')]
saopaulotz = pytz.timezone('America/Sao_Paulo')
def convert_utc_date_to_sao_paulo(dt):
	utc_dt = utctz.localize(dt, is_dst=None)
	saopaulodt = utc_dt.astimezone(saopaulotz)
	return saopaulodt

def build_plot(data_array, file_path):
	# print(data_array)
	num_days  		=	 20
	#obtem as leituras dos ultimos num_dias
	last_date 		= data_array[0].ctd_time
	last_day  		= last_date.day
	date_array 		= []
	pressure_array  = []
	tide_array  = []
	tide_array      = []
	voltage_array	= []
	for data in data_array:
		current_date = data.ctd_time
		#current_day = current_date.day
		# print(last_date - current_date)
		# print(timedelta(days=num_days))
		# print(last_date - current_date < timedelta(days=num_days))
		if last_date.date() - current_date.date() < timedelta(days=num_days):
			date_array.insert(0, data.ctd_time)
			pressure_array.insert(0, data.pressure)
			tide_array.insert(0, data.tide)			
			voltage_array.insert(0, data.voltage)
		else:
			break

	# values = np.array(tide_array, np.float32)	
	# print('***** %s' % str(tide_array))
	values = np.array(tide_array, np.float32)
	index = date_array
	# index = pd.date_range(current_date.date(), last_date.date(), freq='%dD' %(2))
	# print(index)
	# df = pd.DataFrame({'Maré (m)': values}, index=index)
	df = pd.DataFrame(values, index=index)
	def dt_formatter(dt, pos):
		print(dt)
		datep = datetime.fromordinal(int('%.0f' % dt))
		return datep.strftime(dt_plot_mask)
	# formatter = ticker.FuncFormatter(dt_formatter)
	# formatter = ticker.FuncFormatter(lambda dt, pos: dt.strftime(dt_plot_mask))
	plt_obj = df.plot(lw=2,colormap='jet',marker='.',markersize=10,title='Altura de maré')
	plt_obj.set_xlabel('Dia')
	plt_obj.set_ylabel('Maré (m)')
	# plt_obj.yaxis.set_major_formatter(formatter)
	


	#fig = plt.figure()
	fig = plt_obj.get_figure()
	# ax = fig.add_subplot(111)
	# ax.xaxis.set_major_formatter(formatter)
	#plt.show()
	fig.savefig(file_path)



def generate_html(inputfilepath, outputfilepath, outputplotfile='/tmp/ctd1.png'):
	with open(inputfilepath) as ctd_file:
		dat = []
		for line in ctd_file.readlines():
			line_array = line.split("\n")[0].split(separator)
			if len(line_array) < 9:
				# print(line_array)
				i = 0
				# print(line_array[i])
				ctd_time = datetime.strptime(line_array[i], "%Y-%m-%d_%H:%M:%S")

				if "-2$TM" in line:
					i += 3
				elif "$TM" in line:
					i += 2
				else:
					i += 1
				ctd_distance = float(line_array[i].replace("?", "") if "?" in line_array[i] else line_array[i])		
				if ctd_distance > 0:
					i +=1 
					pressure = int(line_array[i])
					i += 1
					tide = 3.3 - ctd_distance
					i += 1
					col4 = int(line_array[i])
					i += 1
					voltage = float(line_array[i])
					# print(voltage)

					data = CTD_DATA(ctd_time, ctd_distance, pressure, tide, col4, voltage)
					# print(data)
					dat.insert(0, data)

		ctd_file.close()

		page = build_html(dat)

		outputfile = open(outputfilepath, mode="w")
		outputfile.write(page)
		outputfile.close()
		build_plot(dat, outputplotfile)
	

			

if __name__ == "__main__":
	if len(argv) < 3:
		print('Falta paramêtros')
	inputfile = argv[1]
	outputfile = argv[2]
	if len(argv) > 3:
		outputplotfile = argv[3] 
		generate_html(inputfile, outputfile, outputplotfile)
	else:
		generate_html(inputfile, outputfile)