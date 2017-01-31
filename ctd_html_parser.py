
from ecoxipy.html import html5
from ecoxipy import MarkupBuilder
from sys import argv




from datetime import datetime

separator = " "

def build_html(list):
	page = '<html xmlns="http://www.w3.org/1999/xhtml">\n'
	page += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
	page += '<head>\n'
	page += '<title>Maréografo</title>\n'
	page += '</head>\n'

	page += '<body>\n'
	page += '<table>\n'
	page += '<tr>\n'
	page += '<th>Data/Hora</th>\n'
	page += '<th>Profundidade</th>\n'
	page += '<th>Col2</th>\n'
	page += '<th>Col3</th>\n'
	page += '<th>Col4</th>\n'
	page += '<th>Col5</th>\n'
	page += '</tr>\n'
	for data in list:
		page += "<tr>"
		page += '<td>%s</td>' % str(data.ctd_time)
		page += "<td>%.2f</td>" % data.depth
		page += "<td>%d</td>" % data.col2
		page += "<td>%.2f</td>" % data.col3
		page += "<td>%d</td>" % data.col4
		page += "<td>%.2f</td>" % data.col5
		page += "</tr>\n"

	page += "</table>\n"
	page += "</body>\n"
	page += "</html>\n"

	return page	



def build_html2(list):
	_b = MarkupBuilder()
	page = _b[:'html':True](
        # Method calls on a MarkupBuilder instance create elements with the
        # name equal to the method name.
        html5(
        	{'data-info': 'Created by Ecoxipy'},
        	html5.head(
        		_b.title("Mareográfo")
        	),
        	body(
        		_b.table(
        			_b.tr(
        				_b.th('teste')
        			)
        		)
        	),
        	xmlns='http://www.w3.org/1999/xhtml/'
        )
    )

	# page.table()
	# page.tr()
	# page.th('Data/Hora')
	# page.th('Profundidade')
	# page.th('Col2')
	# page.th('Col3')
	# page.th('Col4')
	# page.th('Col5')
	# for data in list:
	# 	page.tr()
	# 	page.td(str(data.ctd))
	# 	page.td("%.2f" % data.depth)
	# 	page.td("%d" % data.col2)
	# 	page.td("%.2f" % data.col3)
	# 	page.td("%.d" % data.col4)
	# 	page.td("%.2f" % data.col5)
	return page	

class CTD_DATA(object):
	def __init__(self, 	ctd_time, depth, col2, col3, col4, col5):
		self.ctd_time	= ctd_time
		self.depth 		= depth
		self.col2		= col2
		self.col3		= col3
		self.col4		= col4
		self.col5		= col5
		

	
	def __repr__(self):
		# print(self.col5)
		# print(self.depth)
		return "<%s|depth:%.2f|col2:%d|col3:%.1f|col4:%d|col5:%.1f>" % (
				str(self.ctd_time), 
				self.depth, 
				self.col2, 
				self.col3, 
				self.col4, 
				self.col5)

def generate_html(inputfilepath, outputfilepath):
	with open(inputfilepath) as ctd_file:
		dat = []
		for line in ctd_file.readlines():
			line_array = line.split("\n")[0].split(separator)
			if len(line_array) < 9:
				print(line_array)
				i = 0
				print(line_array[i])
				ctd_time = datetime.strptime(line_array[i], "%Y-%m-%d_%H:%M:%S")

				if "-2$TM" in line:
					i += 3
				elif "$TM" in line:
					i += 2
				else:
					i += 1
				ctd_depth = float(line_array[i].replace("?", "") if "?" in line_array[i] else line_array[i])		
				if ctd_depth > 0:
					i +=1 
					col2 = int(line_array[i])
					i += 1
					col3 = float(line_array[i])
					i += 1
					col4 = int(line_array[i])
					i += 1
					col5 = float(line_array[i])
					# print(col5)

					data = CTD_DATA(ctd_time, ctd_depth, col2, col3, col4, col5)
					# print(data)
					dat.insert(0, data)

		ctd_file.close()

		page = build_html(dat)

		outputfile = open(outputfilepath, mode="w")
		outputfile.write(page)
		outputfile.close()
	

			

if __name__ == "__main__":
	if len(argv) < 3:
		print('Falta paramêtros')
	inputfile = argv[1]
	outputfile = argv[2]
	generate_html(inputfile, outputfile)