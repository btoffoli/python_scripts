# -*- coding: utf-8 -*-

import csv
from sys import argv
from datetime import datetime
from glob import glob
import re

#03/17/17	23:28:02	695	55	700	68
#captura a data e hora
regex = r'\d{2}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}'
exp = re.compile(regex)


