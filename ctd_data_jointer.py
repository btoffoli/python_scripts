# -*- coding: utf-8 -*-

import csv
from sys import argv
from datetime import datetime, timedelta
from glob import glob
import re
from sys import argv

#03/17/17	23:28:02	695	55	700	68
#captura a data e hora
regex_fluor_date = r'\d{2}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}'
exp_fluor_date = re.compile(regex_fluor_date)


#
regex_ctd_date = r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}'
exp_ctd_date = re.compile(regex_ctd_date)

#Examples '25.000', '10.211', '29.192', '0.002', '0.013', '4.054', '1507.444'
regex_ctd_data = r'(\d{1,4}[.]\d{3})'

exp_ctd_data = re.compile(regex_ctd_data)

class Data(object):
    """superclass with comparing"""
    def __init__(self, date_time):
        super(object, self).__init__()
        self.date_time = date_time
        # self.arg = arg

    def __hash__(self):
        return hash(self.date_time)


    def __eq__(self, other):
        if (other.date_time):
            return self.date_time is other.date_time
        return False

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
    fluors_ctds = [(i, filter(lambda ctd: ctd is i, ctds)) for i in fluors]
    # print(ctds)
    # print(fluors)
    for data in fluors_ctds:
        print("%s - %s" % (data, [i for i in data[1]]))



if __name__ == "__main__":
    print(argv)
    output_file_path      = argv[1] if len(argv) > 2 else '/tmp/ctd_fluor_jointed.txt'
    fluorimetro_file_path = argv[2] if len(argv) > 2 else '/tmp/dados_fluorimetro'
    ctd_dir_path          = argv[3] if len(argv) > 3 else '/tmp/dados_fluorimetro'
    test()


