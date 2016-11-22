#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv

from sqlalchemy.engine import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import MetaData
from sys import argv


#Parâmetros
if len(argv) < 5:
    raise AssertionError("Parametros esperados: ipOuNome usuario senha caminhoArquivo loginUsuarioPontual limparTabelaAreaFiscalizacao")

ip_nome = argv[1]
usuario = argv[2]
senha = argv[3]
caminho_arquivo = argv[4]

if len(argv) > 5:
    login_pontual = argv[5]
else:
    login_pontual = 'admin%'

if (len(argv) > 6 and argv[6].upper() == 'TRUE'):
    limpar_tabela = True
else:
    limpar_tabela = False




#Mapeia a database do pontual
__m = MetaData(schema='pontual')
__m2 = MetaData(schema='seguranca')
# __m = MetaData()
url = "postgresql://%s:%s@%s/pontual" % (usuario, senha, ip_nome)
__engine = create_engine(url)
# __m.reflect(__engine, only=['linha', 'area_de_fiscalizacao', 'ponto_de_parada'])
__m2.reflect(__engine, only=['user'])
__Base = automap_base(bind=__engine, metadata=__m)
__Base.prepare(__engine, reflect=True)
__Base2 = automap_base(bind=__engine, metadata=__m2)
__Base2.prepare(__engine, reflect=True)


#Objeto ORMs do sqlalchmy do pontual
User = __Base2.classes.user
Linha = __Base.classes.linha
AreaDeFiscalizacao = __Base.classes.area_de_fiscalizacao
PontoDeParada = __Base.classes.ponto_de_parada


Sessao = sessionmaker(bind=__engine)

sessao = Sessao()

q = sessao.query(User).filter(User.login.ilike(login_pontual))

user = q.first()



if limpar_tabela:
    conexao = __engine.connect()
    area_fiscalizacao_table = __m.tables['pontual.area_de_fiscalizacao']
    conexao.execute(area_fiscalizacao_table.delete())
    conexao.close()



with open(caminho_arquivo) as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar=' ')
    # descarta a primeira linha
    next(spamreader)
    # spamreader.__next__()
    terminal = None
    linha = None
    areas = {}
    for nomeTerminal, nomeLinha, numArea in spamreader:
        if not (terminal and terminal.codigo == nomeTerminal):
            queryTerminal = sessao.query(PontoDeParada).filter(PontoDeParada.terminal == True, PontoDeParada.codigo == nomeTerminal)
            terminal = queryTerminal.first()
            areas[terminal] = {}

        if not terminal:
            print("Nao encontrado terminal com codigo: %s" % nomeTerminal)

        if not (linha and linha.codigo == nomeLinha):
            queryLinha = sessao.query(Linha).filter(Linha.codigo == nomeLinha)
            linha = queryLinha.first()

        if not linha:
            print("Nao encontrada linha com codigo: %s" %nomeLinha)


        if linha and terminal:
            #(areas[terminal][linha]).append(linha.id)
            if numArea not in areas[terminal]:
                areas[terminal][numArea] = []
            areas[terminal][numArea].append(linha.id)


    for terminal, areaMap in areas.items():
        for numArea, linhaIds in areaMap.items():
            area = AreaDeFiscalizacao(nome=numArea, ponto_de_parada=terminal, linhas=linhaIds, usuario_atualizacao_id=user.oid)
            sessao.add(area)

    sessao.commit()





