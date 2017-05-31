
from sys import argv, exit
import pytz

from datetime import datetime, timedelta

import pandas as pd
from matplotlib import pyplot as plt, style, dates, ticker, use
import numpy as np
import re
import matplotlib.patches as mpatches
import math

style.use('ggplot')
use('Agg')
separator = " "
dt_html_mask = "%d/%m/%Y %H:%M:%S"
dt_plot_mask = "%d/%m/%Y"
num_regs_max = 1000

regexp = r'\-?\d{1,5}\.{1}\d{2}|\-?\d{2,4}|NAN'
# regexp = r'\d{1,3}\.{1}\d{2}|\d{2,4}'
matcher = re.compile(regexp)


def build_html(list, outputplotfilepressure, outputplotfiledepth):
	filepressure = re.sub(r'(/.+/)', '', outputplotfilepressure)
	filedepth = re.sub(r'(/.+/)', '', outputplotfiledepth)
	page = '<html xmlns="http://www.w3.org/1999/xhtml">\n'
	page += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
	page += '<link rel="icon" href="SmallLogo.png" type="image/png" />\n'
	page += '<head>\n'
	page += '<title>Marégrafo</title>\n'
	page += '<link href="novoEstilo.css" rel="stylesheet" type="text/css">'
	page += '</head>\n'

	page += '<body>\n'
	page += '<div id="container">\n'
	page += '<div class="div_data">\n'
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
	page += '<th>Prof. ADCP(m)</th>\n'
	page += '<th>Prof. Aanderra(m)</th>\n'
	page += '<th>Pressão Barométrica (mmHg)</th>\n'
	page += '<th>Temperatura(ºC)</th>\n'
	
	# page += '<th>Col4</th>\n'
	page += '<th>Voltagem(v)</th>\n'
	page += '</tr>\n'
	for data in list:
		page += "<tr>"
		page += '<td>%s</td>' % data.ctd_time.strftime(dt_html_mask)
		page += "<td>%.2f</td>" % data.depth_adcp
		page += "<td>%.2f</td>" % data.depth_aanderra
		page += "<td>%d</td>" % data.pressure
		page += "<td>%.2f</td>" % data.temperature_aanderra
		# page += "<td>%d</td>" % data.temperature_aanderra
		page += "<td>%.2f</td>" % data.voltage
		page += "</tr>\n"

	page += "</table>\n"
	page += "</div>\n"
	page += '<div class="div_data">\n'
	page += '<img src="%s"/><br>\n'	% filepressure
	page += '<img src="%s"/>\n'	% filedepth
	page += "</div>\n"
	page += "</body>\n"
	page += "</html>\n"

	return page



class CTD_DATA(object):
	def __init__(self, 	ctd_time, depth_adcp, depth_aanderra, pressure, temperature_aanderra, voltage):
		# self.ctd_time						=  convert_utc_date_to_sao_paulo(ctd_time)
		self.ctd_time						=  ctd_time
		self.depth_adcp 					= depth_adcp
		self.depth_aanderra 				= depth_aanderra 
		self.pressure						= pressure
		self.temperature_aanderra			= temperature_aanderra
		self.voltage						= voltage

	def __repr__(self):
		# print(self.voltage)
		# print(self.depth_adcp)
		return "<%s|depth_adcp:%.2f|pressure:%d|tide:%.1f|temperature_aanderra:%d|voltage:%.1f>" % (
				str(self.ctd_time), 
				self.depth_adcp, 
				self.depth_aanderra, 
				self.pressure, 
				self.temperature_aanderra, 
				self.voltage)
	def to_dict(self):
            d = {
                'datetime'          : self.ctd_time,
                'adcp'              : self.depth_adcp,
                'aanderra'          : self.depth_aanderra,
                'pressure'          : self.pressure,
                'temperature'       : self.temperature_aanderra,
                'voltage'           : self.voltage
            }
            return d


utctz = pytz.utc
saopaulotz = pytz.timezone('America/Sao_Paulo')
def convert_utc_date_to_sao_paulo(dt):
	utc_dt = utctz.localize(dt, is_dst=None)
	saopaulodt = utc_dt.astimezone(saopaulotz)
	return saopaulodt

def build_pressure_plot(data_array, file_path):
	#obtem as leitur		as dos ultimos num_dias
	data_array 				= data_array[:num_regs_max]
	last_date 				= data_array[0].ctd_time
	last_day  				= last_date.day
	date_array 				= []
	pressure_array  		= []
	depth_adcp_array		= []
	depth_aanderra_array	= []
	temperature_array		= []
	voltage_array			= []
	for data in data_array:
		date_array.insert(0,data.ctd_time)
		pressure_array.insert(0,data.pressure)
		depth_adcp_array.insert(0,data.depth_adcp)
		depth_aanderra_array.insert(0,data.depth_aanderra)
		# tide_array.insert(0, (data.ctd_time, data.tide))
		temperature_array.insert(0,data.temperature_aanderra)
		voltage_array.insert(0,data.voltage)
	

	# values = np.array(tide_array, np.float32)	
	# print('***** %s' % str(tide_array))
	values_pressure = np.array(pressure_array, np.float32)
	# values = tide_array
	# index = date_array
	# index = pd.Series(dates.date2num(date_array))
	# index = core.index.datetimes.DatetimeIndex(date_array, dtype='datetime64[ns]', freq=None)
	# index = map(pd.Timestamp, date_array)
	# index = [pd.Timestamp(i) for i in date_array]
	# index = pd.to_datetime(date_array)
	index = [i.strftime(dt_html_mask) for i in date_array]

	print(type(index))

	
	#check if all date are the same day
	more_days = len(set(map(lambda i: i.date(), date_array))) > 1

	# index = pd.date_range(current_date.date(), last_date.date(), freq='%dD' %(2))
	# print(index)
	# df = pd.DataFrame({'Maré (m)': values}, index=index)
	df = pd.DataFrame(values_pressure, index=index)
	def dt_formatter(dt, pos):
		print(dt)
		print(type(dt))
		datep = datetime.fromordinal(int('%.0f' % dt))
		# datep = datetime.fromordinal(float(dt))
		print(str(datep))
		return datep.strftime(dt_html_mask if more_days else '%H:%M')
	# formatter = ticker.FuncFormatter(dt_formatter)
	formatter = ticker.FuncFormatter(lambda dt, pos: dt.strftime(dt_html_mask))
	# plt_obj = df.plot(lw=2,colormap='jet',marker='.',markersize=10,title='Altura de maré')
	plt_obj = df.plot(title='Pressão Barométrica')
	plt_obj.set_xlabel('Dia' if more_days else "Dia %s" % date_array[0].date().strftime(dt_plot_mask))
	plt_obj.set_ylabel('Pressão (mmHg)')
	# plt_obj.xaxis.set_major_formatter(formatter)
	


	#fig = plt.figure()
	fig = plt_obj.get_figure()
	ax = fig.add_subplot(111)
	ax.legend('')
	fig.autofmt_xdate()
	# ax.plot(label='')	
	# ax.xaxis.set_major_formatter(formatter)
	#plt.show()
	fig.savefig(file_path)

def build_depth_plot(data_array, file_path):	
	data_array = data_array[:num_regs_max]
	date_array = []
	depth_adcp_array = []
	depth_aanderra_array = []	
	for ctd in data_array:
		date_array.insert(0, ctd.ctd_time)
		depth_adcp_array.insert(0, ctd.depth_adcp)
		depth_aanderra_array.insert(0, ctd.depth_aanderra)
	mdates_array = dates.date2num(date_array)
	dt_init = date_array[0]
	dt_end  = date_array[-1]
	# mdates_array = dates.drange(dt_init, 
 #                     dt_end,
 #                     (dt_end - dt_init)/len(depth_adcp_array))

	#print("len dates: %d  - len adcp: %d -  len aanderra: %d" % (len(date_array), len(depth_adcp_array), len(depth_aanderra_array)))
	# plt.plot(dates_array, depth_adcp_array)
	# fig = plt.figure()
	fig, ax = plt.subplots()
	ax.set_title('Profundidade ADCP x Aanderra (m)')

	# print(depth_adcp_array)


	more_days = len(set(map(lambda i: i.date(), date_array))) > 1

	plt.plot_date(mdates_array, depth_adcp_array)
	plt.plot_date(mdates_array, depth_aanderra_array)
	ax.legend(('ADCP', 'Aanderra'))

	
	formatter = dates.DateFormatter(dt_html_mask if more_days else '%H:%M')
	ax.xaxis.set_major_formatter(formatter)

	
	# ax.set_xlabel('Dia' if more_days else "Dia %s" % date_array[0].date().strftime(dt_html_mask))
	# ax.set_ylabel('Profundidade (m)')
	fig.autofmt_xdate()
	# ax.autoscale_view()
	# ax.plot_dates(date_array, depth_adcp_array, 'ADCP')
	# plt.show()

	fig.savefig(file_path)
	

	





def generate_html(inputfilepath, outputfilepath, outputplotfilepressure='/tmp/pressure.png', outputplotfiledepth='/tmp/depth.png'):
	with open(inputfilepath) as ctd_file:
		dat = []
		

		for line in ctd_file.readlines():
			# line_array = line.split("\n")[0].split(separator)
			line_array = matcher.findall(line)
			if line_array and len(line_array) > 9:
				print(line_array)
				# print(line_array[i])
				# ctd_time = datetime.strptime(line_array[i], "%Y-%m-%d_%H:%M:%S")
				year 			= int(line_array[0])
				month 			= int(line_array[1])
				day 			= int(line_array[2])
				hour 			= int(line_array[3])
				minute 			= int(line_array[4])
				voltage  		= float(line_array[5])
				depth_adcp 		= float(line_array[6])
				depth_aanderra 	= float(line_array[7])
				pressure 		= float(line_array[8])
				temperature		= float(line_array[9])
				ctd_time	 	= datetime(year, month, day, hour, minute)
				
				if depth_adcp < 1 or depth_adcp > 100:
					depth_adcp = float('NAN')
				

				if depth_aanderra < 1 or depth_aanderra > 100:
					depth_aanderra = float('NAN')
				else:
					last_depth_aanderra_valid = depth_aanderra

				data = CTD_DATA(ctd_time, depth_adcp, depth_aanderra, pressure, temperature, voltage)
				dat.insert(0,data)

		ctd_file.close()

		page = build_html(dat[:10000], outputplotfilepressure, outputplotfiledepth)

		outputfile = open(outputfilepath, mode="w")
		outputfile.write(page)
		outputfile.close()
		build_pressure_plot(dat, outputplotfilepressure)
		build_depth_plot(dat, outputplotfiledepth)
	

			

if __name__ == "__main__":
	if len(argv) < 5:
		print('Falta paramêtros')
		exit(1)
	inputfile = argv[1]
	outputfile = argv[2]	
	outputplotfilepressure = argv[3] 
	outputplotfiledepth = argv[4]
	generate_html(inputfile, outputfile, outputplotfilepressure, outputplotfiledepth)
	
