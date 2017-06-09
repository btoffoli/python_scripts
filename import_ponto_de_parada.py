import csv

# from sqlalchemy.engine import create_engine
# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select
# from sqlalchemy.sql.schema import metadata
from sys import argv



from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData, func, funcfilter
from sqlalchemy.orm import sessionmaker

import requests
import json

from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry, WKTElement
import geoalchemy2

print(argv)

#Parâmetros
if len(argv) < 4:
    raise AssertionError("Parametros esperados: ipOuNome usuario senha caminhoArquivo loginUsuarioPontual usuarioCeturb senhaCeturb")

ip_nome = argv[1]
usuario = argv[2]
senha = argv[3]
url_ceturb = argv[4]
usuario_ceturb = argv[5] if len(argv) > 5 else 'xxxxxxxx'
senha_ceturb = argv[6] if len(argv) > 6 else 'xxxxxxxxx'

print("usuario_ceturb - %s | senha_ceturb - %s" % (usuario_ceturb, senha_ceturb))
headers = {"Content-Type": "application/json"}
user_data_ceturb = {"usuario": [{"login": usuario_ceturb, "password": senha_ceturb}]}



if len(argv) > 5:
    login_pontual = argv[5]
else:
    login_pontual = 'admin%'

if (len(argv) > 6 and argv[6].upper() == 'TRUE'):
    limpar_tabela = True
else:
    limpar_tabela = False

def listar_pontos_ceturb():
	r = requests.post(url_ceturb, data=json.dumps(user_data_ceturb), headers=headers)
	resp = []
	if r.status_code == 200:
		conteudo = r.json()
		resp = conteudo.get("data") 

	return resp


def is_diff(pnto_geo, pnto_ceturb):
	return pnto_geo.logradouro != pnto_ceturb['logradouro']\
		or pnto_geo.bairro != pnto_ceturb['localidade']\
		or pnto_geo.municipio != pnto_ceturb['municipio']
		# or pnto_geo.referencia != pnto_ceturb['ds_referencia']


		# float(pnto_geo.longitude) != pnto_ceturb['stop_lon']\
		# or float(pnto_geo.latitude) != pnto_ceturb['stop_lat']\
		# or


def contruir_geometria(lon, lat):
	return  WKTElement("srid=4326; POINT(%.13f %.13f)" %(lon, lat), srid=4326)




#Mapeia a database do pontual
__m = MetaData(schema='pontual')
# __m2 = MetaData(schema='seguranca')
# __m = MetaData()
url = "postgresql://%s:%s@%s/pontual" % (usuario, senha, ip_nome)
__engine = create_engine(url)
# __m.reflect(__engine, only=['linha', 'area_de_fiscalizacao', 'ponto_de_parada'])
# __m2.reflect(__engine, only=['user'])
__Base = automap_base(bind=__engine, metadata=__m)
__Base.prepare(__engine, reflect=True)
# __Base2 = automap_base(bind=__engine, metadata=__m2)
# __Base2.prepare(__engine, reflect=True)


#Objeto ORMs do sqlalchmy do pontual
# User = __Base2.classes.user
# Linha = __Base.classes.linha
# AreaDeFiscalizacao = __Base.classes.area_de_fiscalizacao
PontoDeParada = __Base.classes.ponto_de_parada
# PontoDeParada.geometria = Column('geometria', Geometry('Point', srid=4326))
# print(PontoDeParada.geometria)
# PontoDeParada.geometria = Column(Geometry('POINT', srid=4326))
# print(type(PontoDeParada.geometria))


Sessao = sessionmaker(bind=__engine)

sessao = Sessao()

pontos_ceturb = listar_pontos_ceturb()

print("Total de pontos da ceturb = %d" % len(pontos_ceturb))

count_inseridos = 0
count_atualizados = 0
for pnto_ceturb in pontos_ceturb:
	#encontra o ponto do pontual
	q = sessao.query(PontoDeParada, func.ST_ASTEXT(PontoDeParada.geometria).label('localizacao'),\
	func.ST_X(PontoDeParada.geometria).label('longitude'), func.ST_Y(PontoDeParada.geometria).label('latitude'))\
	.filter_by(codigo=pnto_ceturb['stop_code'])
	ponto_geo_tuple = q.first()
	pnto_geo, localizacao, longitude, latitude = ponto_geo_tuple if ponto_geo_tuple else (None, None, None, None)
	if pnto_geo:
		# pnto_geo.geometria = localizacao
		pnto_geo.longitude = longitude
		pnto_geo.latitude  = latitude
		if is_diff(pnto_geo, pnto_ceturb):
			# print("pnto_ceturb diferente de pnto_geo %s - %s" %(pnto_geo, pnto_ceturb))
			# pnto_geo.geometria =  contruir_geometria(pnto_ceturb['stop_lon'], pnto_ceturb['stop_lat'])
			pnto_geo.logradouro = pnto_ceturb['logradouro']
			pnto_geo.bairro		= pnto_ceturb['localidade']
			pnto_geo.municipio  = pnto_ceturb['municipio']
			# pnto_geo.referencia = pnto_ceturb['ds_referencia'].lstrip() if pnto_ceturb['ds_referencia'] and pnto_ceturb['ds_referencia'].lstrip() else None
			count_atualizados += 1
	else:
		pnto_geo = PontoDeParada(
				codigo=pnto_ceturb['stop_code'],
				municipio=pnto_ceturb['municipio'],
				bairro=pnto_ceturb['localidade'],
				logradouro=pnto_ceturb['logradouro']
				#,geometria=contruir_geometria(pnto_ceturb['stop_lon'], pnto_ceturb['stop_lat'])
				,referencia=pnto_ceturb['ds_referencia'].lstrip() if pnto_ceturb['ds_referencia'] and pnto_ceturb['ds_referencia'].lstrip() else None
			)
		sessao.add(pnto_geo)
		count_inseridos += 1


	#verificar se o bloco 110 a 112 irá causar o update
sessao.commit()

print("Total de inseridos %d, total de atualizados %d" %(count_inseridos, count_atualizados))


