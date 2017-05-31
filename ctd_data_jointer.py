# -*- coding: utf-8 -*-

from sys import argv
from datetime import datetime, timedelta
from glob import glob
import re
from sys import argv, platform

directory_separator = '/'
cell_separator = ';'
pressure_to_depth_const = 1.025
chlorophyll_const = 0.0123
turbidity_const = 0.0246

#03/17/17	23:28:02	695	55	700	68
#captura a data e hora
regex_fluor_date = r'\d{2}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}'
exp_fluor_date = re.compile(regex_fluor_date)
regex_fluor_data = r'\d{3}\t+[-]?\d{1,3}'
exp_fluor_data = re.compile(regex_fluor_data)


#Regex with milleseconds
# regex_ctd_date = r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}[.]\d{3}'
regex_ctd_date = r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}'
exp_ctd_date = re.compile(regex_ctd_date)

#Examples '25.000', '10.211', '29.192', '0.002', '0.013', '4.054', '1507.444'
regex_ctd_data = r'(\d{1,4}[.]\d{3})'

exp_ctd_data = re.compile(regex_ctd_data)


def build_fluor_obj(line):    
    #finding date
    m1 = exp_fluor_date.match(line)
    # print(m1)
    d = datetime.strptime(m1.group(), '%m/%d/%y\t%H:%M:%S')
    fluors_data = exp_fluor_data.findall(line)
    # print(fluors_data) #['695\t51', '700\t61']
    chlorophyll = float(fluors_data[0].split('\t')[1]) if fluors_data else 0.0
    # print(turbidity)
    turbidity = float(fluors_data[1].split('\t')[1]) if len(fluors_data) > 1 else 0.0
    # print(chlorophyll)
    fluor = Fluorimeter(d, turbidity, chlorophyll)
    # print(ctd.pressure)
    return fluor    

def load_fluor(fluor_file_path):
    fluors = []
    with open(fluor_file_path, 'r') as fluor_file:
        #for line in filter(lambda ctd_dir_path)
        line_num = 0
        while True:
            line_num += 1
            # print("line_number = %d" % line_num)
            line = fluor_file.readline()
            if not line:
                break
            # print(line)
            m = exp_fluor_date.match(line)
            # print(m)
            if m:
                fluors.append(build_fluor_obj(line))
                print('.', end='')

    #calc average per second of fluor_data
    def find_calc_avg(list, data):
        fluor_temp = data
        list_of_data = [i for i in list if i == data]
        # print('%s - %d' % (str(fluor_temp.date_time), len(list_of_data)))
        fluor_temp.turbidity = sum(map(lambda i: i.turbidity, list_of_data))/float(len(list_of_data))
        fluor_temp.chlorophyll = sum(map(lambda i: i.chlorophyll, list_of_data))/float(len(list_of_data))
        # print("in fluor.turbidity: %f" % fluor_temp.turbidity)

    
    resp = []
    for fluor in fluors:
        if fluor not in resp:
            # print("before fluor.turbidity: %f" % fluor.turbidity)
            find_calc_avg(fluors, fluor)
            # print("after fluor.turbidity: %f\n" % fluor.turbidity)
            resp.append(fluor)
            print('.', end='')

    resp = sorted(resp)        

    return resp



def build_ctd_obj(line):    
    #finding date
    m1 = exp_ctd_date.match(line)
    # print(m1)
    #format with milleseconds
    # d = datetime.strptime(m1.group(), '%d/%m/%Y %H:%M:%S.%f')
    #format without  milleseconds
    d = datetime.strptime(m1.group(), '%d/%m/%Y %H:%M:%S')
    ctds_data = exp_ctd_data.findall(line)
    # print(ctds_data)
    #the first is trash
    ctd = CTD(d, float(ctds_data[1]), float(ctds_data[2]), \
        float(ctds_data[3]), float(ctds_data[4]), float(ctds_data[5]), float(ctds_data[6]))
    # print("ctd=%s" % ctd)
    return ctd    

def load_ctd(ctd_file_path):
    ctds = []
    with open(ctd_file_path, 'r') as ctd_file:
        #for line in filter(lambda ctd_dir_path)
        while True:            
            line = ctd_file.readline()
            if not line:
                break
            # print(line)
            m = exp_ctd_date.match(line)
            # print(m)
            if m:
                ctds.append(build_ctd_obj(line))    
                print('.', end='')

    #calc average per second of fluor_data
    def find_calc_avg(list, data):
        ctd_temp = data
        list_of_data = [i for i in list if i == data]
        # print('%s - %d' % (str(ctd_temp.date_time), len(list_of_data)))
        ctd_temp.pressure = sum(map(lambda i: i.pressure, list_of_data))/float(len(list_of_data))
        ctd_temp.temperature = sum(map(lambda i: i.temperature, list_of_data))/float(len(list_of_data))
        ctd_temp.conductivity = sum(map(lambda i: i.conductivity, list_of_data))/float(len(list_of_data))
        ctd_temp.salinity = sum(map(lambda i: i.salinity, list_of_data))/float(len(list_of_data))
        ctd_temp.density = sum(map(lambda i: i.density, list_of_data))/float(len(list_of_data))
        ctd_temp.sos = sum(map(lambda i: i.sos, list_of_data))/float(len(list_of_data))
        # print("in ctd.pressure: %f" % ctd_temp.pressure)

    
    resp = []
    for ctd in ctds:        
        if ctd not in resp:                        
            find_calc_avg(ctds, ctd)            
            resp.append(ctd)
            print('.', end='')

    resp = sorted(resp)                        

    return resp

class Data(object):
    """superclass with comparing"""
    def __init__(self, date_time):
        super(object, self).__init__()
        self.date_time = date_time
        # self.arg = arg

    def __hash__(self):
        # print("invocou hash")
        return hash(self.date_time)

    
    def __eq__(self, other):
        # print("invocou eq")
        if (other.date_time):
            return self.date_time == other.date_time
        return False

    def __lt__(self, other):
        # print("invocou eq")
        if (other.date_time):
            return self.date_time < other.date_time
        return False

    #isn't working
    def __cmp__(self, other):        
        return self.date_time - other.date_time

    def __repr__(self):
        return "<%s - d: %s>" %(type(self), str(self.date_time))



class CTD(Data):
    """docstring for CTD"""
    def __init__(self, date_time, pressure, \
        temperature, conductivity, salinity, density, sos):
        super(CTD, self).__init__(date_time)
        self.pressure = pressure
        self.temperature = temperature
        self.conductivity = conductivity
        self.salinity = salinity
        self.density = density
        self.sos = sos



class Fluorimeter(Data):
    """docstring for ClassName"""
    def __init__(self, date_time, chlorophyll, turbidity):
        super(Fluorimeter, self).__init__(date_time)
        self.chlorophyll = chlorophyll
        self.turbidity = turbidity





def test():
    d = datetime.now()
    # dts = map(lambda x: d + timedelta(seconds=x), range(60))
    dts = [d + timedelta(seconds=x) for x in range(60)]
    ctds = [CTD(d, 10, 10, 10, 10, 10, 10) for d in dts]
    fluors = [Fluorimeter(d, 10, 10) for d in dts]
    fluors_ctds = [(i, filter(lambda ctd: ctd == i, ctds)) for i in fluors]
    # print(ctds)
    # print(fluors)
    for data in fluors_ctds:
        print("%s - %s" % (data, [i for i in data[1]]))


def build_output(fluors, ctds):
    # print(ctds)
    fluors_ctds = ((i, next((ctd for ctd in ctds if ctd == i), None)) for i in fluors)
    return fluors_ctds


if __name__ == "__main__":
    print(argv)
    output_dir_path      = argv[1] if len(argv) > 1 else '/tmp'
    fluorimetro_file_path = argv[2] if len(argv) > 2 else '/home/btoffoli/var/ctd_jointer/dados_fluorimetro'
    ctd_dir_path          = argv[3] if len(argv) > 3 else '/home/btoffoli/var/ctd_jointer/Data/41301/14032017/*.000'
    # test()
    print('Loading Fluorimeter Data', end='')
    fluors = load_fluor(fluorimetro_file_path)
    print('OK')
    # prefix_file = fluors[0].date_time.strftime('%d_%m_%y')

    if platform == "linux" or platform == "linux2":
        prefix_file = ctd_dir_path.split('/')[-2]    
    elif platform == "win32":
        prefix_file = ctd_dir_path.split('\\')[-2]


    g = glob(ctd_dir_path)

    for ctd_file_path in g:
        print('Loading CTD Data from %s' % ctd_file_path, end='')
        ctds = load_ctd(ctd_file_path)        
        fluors_ctds = build_output(fluors, ctds)
        ctd_prefix_file_name = ctd_file_path.split('/')[-1].split('.')[0] if platform in ["linux", "linux2"]
        name_file = "%s/%s_%s.csv" % (output_dir_path, prefix_file, ctd_prefix_file_name)
        print("Generating arquivo %s: " %name_file)
        f = open(name_file, 'w')
        f.write("%s\n" % cell_separator.join(['Date', 'Prof(m)', 'Sal(PSU)', 'Temp(ºC)','Cond(mS/cm)', 'Dens(kg/m³)', 'Chl_a(mg/m³)', 'Turb(NTU)']))
        for fluor, ctd in ((fluor, ctd) for fluor, ctd in fluors_ctds if ctd):
            # print("%s - %s" %(fluor, ctd))      
            #mult pressure per const to find the depth  
            depth = ctd.pressure * pressure_to_depth_const
            sal = ctd.salinity
            temp = ctd.temperature
            cond = ctd.conductivity
            dens = ctd.density
            chl_a = chlorophyll_const * (fluor.chlorophyll - 49)
            turb = turbidity_const * (fluor.turbidity - 50) 
            data_tuple = (fluor.date_time, depth, sal, temp, cond, dens, chl_a, turb)
            data_str = cell_separator.join(map(str, data_tuple))
            f.write("%s\n" % data_str)
            print('.', end='')
        print('OK')
        f.flush()
        f.close()


