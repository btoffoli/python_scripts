from datetime import datetime
from elasticsearch import Elasticsearch
from gerador_html_onixat import CTD_DATA, matcher
import math

inputfilepath = '/tmp/01018136SKYFBB5.txt'
url_elastic   = 'http://localhost:9200/'
idx_name      = 'umi_data'
doc_type      = 'ctd_data_umi'

def list_data(inputfilepath):
    dat = []
    with open(inputfilepath) as ctd_file:
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
                    depth_aanderra 		= float(line_array[7])
                    pressure 		= float(line_array[8])
                    temperature		= float(line_array[9])
                    ctd_time	 	= datetime(year, month, day, hour, minute)
                    
                    if depth_adcp < 0 or depth_adcp > 100 or math.isnan(depth_adcp):
                            depth_adcp = 0.0
                    if depth_aanderra < 0 or depth_aanderra > 100 or math.isnan(depth_aanderra):
                            depth_aanderra = 0.0	
                    if math.isnan(pressure):
                            presssure = 0.0
                    if math.isnan(temperature):
                            temerature = 0.0
                    data = CTD_DATA(ctd_time, depth_adcp, depth_aanderra, pressure, temperature, voltage)
                    dat.insert(0,data)				
        ctd_file.close()
    return dat    

def import_data(url_elastic, idx_name, data_list):
    es = Elasticsearch([url_elastic])
    es.indices.create(index=idx_name, ignore=400)
    for ctd_data in data_list:
        #res = es.search(index=idx_name, body={'query': {'match': ctd_data.to_dict()}})
        res = es.get(index=idx_name, doc_type=doc_type, id=ctd_data.ctd_time.timestamp() * 1000, ignore=[400, 404])
        print(res)
        count_got = res['hits']['total'] if res.get('hits') else None
        if not count_got:
            res = es.index(index=idx_name, doc_type=doc_type, id=ctd_data.ctd_time.timestamp() * 1000, body=ctd_data.to_dict())
            print(res['created'])
    
    
    


if __name__ == "__main__":
    list = list_data(inputfilepath)
    import_data(url_elastic, idx_name, list)
    
    

