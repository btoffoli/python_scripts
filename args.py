#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

import glob
from dominate import document
from dominate.tags import *


def listaTensao = []
def listaRumo = []
def listaPressao = []
def listaTemperatura = []
def listaPitch = []
def listaRoll = []
def listaAltSign = []
def listaDirPicoPrim = []
def listaPerPicoPrim = []

def refBeansCorr = [:]
def refBeansDirCorr = [:]

def listaCorrDoBeam1 = refBeansCorr[1] = []
def listaDirCorrBeam1 = refBeansDirCorr[1] = []

def listaCorrDoBeam2 = refBeansCorr[2] = []
def listaDirCorrBeam2 = refBeansDirCorr[2] = []

def listaCorrDoBeam3 = refBeansCorr[3] = []
def listaDirCorrBeam3 = refBeansDirCorr[3] = []

def listaCorrDoBeam4 = refBeansCorr[4] = []
def listaDirCorrBeam4 = refBeansDirCorr[4] = []

def listaCorrDoBeam5 = refBeansCorr[5] = []
def listaDirCorrBeam5 = refBeansDirCorr[5] = []

def listaCorrDoBeam6 = refBeansCorr[6] = []
def listaDirCorrBeam6 = refBeansDirCorr[6] = []

def listaCorrDoBeam7 = refBeansCorr[7] = []
def listaDirCorrBeam7 = refBeansDirCorr[7] = []

def listaCorrDoBeam8 = refBeansCorr[8] = []
def listaDirCorrBeam8 = refBeansDirCorr[8] = []

def listaCorrDoBeam9 = refBeansCorr[9] = []
def listaDirCorrBeam9 = refBeansDirCorr[9] = []

def listaCorrDoBeam10 = refBeansCorr[10] = []
def listaDirCorrBeam10 = refBeansDirCorr[10] = []

def listaCorrDoBeam11 = refBeansCorr[11] = []
def listaDirCorrBeam11 = refBeansDirCorr[11] = []

def listaCorrDoBeam12 = refBeansCorr[12] = []
def listaDirCorrBeam12 = refBeansDirCorr[12] = []

def listaCorrDoBeam13 = refBeansCorr[13] = []
def listaDirCorrBeam13 = refBeansDirCorr[13] = []

def listaCorrDoBeam14 = refBeansCorr[14] = []
def listaDirCorrBeam14 = refBeansDirCorr[14] = []

def listaCorrDoBeam15 = refBeansCorr[15] = []
def listaDirCorrBeam15 = refBeansDirCorr[15] = []

def listaCorrDoBeam16 = refBeansCorr[16] = []
def listaDirCorrBeam16 = refBeansDirCorr[16] = []

def listaCorrDoBeam17 = refBeansCorr[17] = []
def listaDirCorrBeam17 = refBeansDirCorr[17] = []

def listaCorrDoBeam18 = refBeansCorr[18] = []
def listaDirCorrBeam18 = refBeansDirCorr[18] = []

def listaCorrDoBeam19 = refBeansCorr[19] = []
def listaDirCorrBeam19 = refBeansDirCorr[19] = []

def listaCorrDoBeam20 = refBeansCorr[20] = []
def listaDirCorrBeam20 = refBeansDirCorr[20] = []

def listaCorrDoBeam21 = refBeansCorr[21] = []
def listaDirCorrBeam21 = refBeansDirCorr[21] = []

def listaCorrDoBeam22 = refBeansCorr[22] = []
def listaDirCorrBeam22 = refBeansDirCorr[22] = []

def listaAno = []
def listaMes = []
def listaDia = []
def listaHora = []
def listaMinuto = [] 

Integer numLinhaTotal = 0

    

photos = glob.glob('photos/*.jpg')

with document(title='Photos') as doc:
    #h1('Photos')
    #for path in photos:
    #    div(img(src=path), _class='photo')
    


with open('/tmp/gallery.html', 'w') as f:
    f.write(doc.render())



args = sys.argv


print(args[1])