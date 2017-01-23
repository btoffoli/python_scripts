#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf-8 -*-
import json
from configparser import RawConfigParser
from datetime import date, datetime
import pytz
from sys import argv, version_info
from tzlocal import get_localzone
import smtplib
from email.mime.text import MIMEText
import requests


VERSAO='1.1.3'


# tzone = pytz.timezone('America/Sao_Paulo')
tzone = get_localzone()
# epoch = datetime.utcfromtimestamp(0)
#Fazendo as operações de conversão de epoch em 0 mas no timezone de sampa
epoch = datetime.fromtimestamp(0, tz=pytz.UTC)
url_base = None
prefix_file_name = "invocador_winsiturb"
#
login_email = None
url_email_smtp_server = "smtp.geocontrol.com.br"
port_email = 465
senha_email = None
diretorio_saida = "/tmp/"


def carregar_propriedades(file_path):
    from os import path
    global url_base, prefix_file_name, diretorio_saida, url_email_smtp_server, port_email, login_email,\
        senha_email, destinatarios_email, titulo_email, prefixo_email, prefixo_sucesso_email, sufixo_email, assinatura_email

    config = RawConfigParser()
    config.read(file_path)

    #geral
    url_base = config.get("invocador", "url_base")
    prefix_file_name = config.get("invocador", "prefix_file_name")
    diretorio_saida = config.get("invocador", "diretorio_saida")

    if not (path.exists(diretorio_saida) and path.isdir(diretorio_saida)):
        raise ValueError(u"O caminho %s é inesistente, sem permissão ou não é um diretório" % diretorio_saida)


    #email
    url_email_smtp_server = str(config.get("email", "url_smtp_server"))
    port_email = int(config.get("email", "port"))
    login_email = config.get("email", "login")
    senha_email = config.get("email", "senha")
    destinatarios_email = eval(config.get("email", "destinatarios"))
    titulo_email = config.get("email", "titulo")
    prefixo_email = config.get("email", "prefixo")
    prefixo_sucesso_email = config.get("email", "prefixo_sucesso")
    sufixo_email = config.get("email", "sufixo")
    assinatura_email = config.get("email", "assinatura")




def to_timemillis(data):
    return None if not data else data.timestamp() if verificar_python_maior33() else int((data - epoch).total_seconds() * 1000)

def from_timemillis(timemillis, timezone=pytz.UTC):
    if not type(timemillis) == float:
        return datetime.utcfromtimestamp(float(timemillis)/1000).replace(tzinfo=timezone)
    return datetime.utcfromtimestamp(timemillis/1000).replace(tzinfo=timezone)

def str_date(data):
    # return data.isoformat() if data else None
    if type(data) is datetime:
        return data.astimezone(tzone).isoformat() if data else None
    return data.isoformat() if data else None

def str_date_geo(data):
    return data.strftime("%d-%m-%Y %H:%M:%S") if type(data) is datetime else data.strftime("%d-%m-%Y")

def enviar_email(data_hora_execucao, mensagem):
    agora = datetime.now(tz=tzone)
    if agora.hour in range(6, 12):
        saudacao = "Bom dia"
    elif agora.hour in range(12, 18):
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"
    prefixo_final = (prefixo_email if mensagem else prefixo_sucesso_email)  % saudacao
    titulo_final = titulo_email % str_date_geo(data_hora_execucao)
    # mensagem_final = "%s.\n\n%s\n\n%s\n%s" %(prefixo_final, mensagem, sufixo_email, assinatura_email)
    mensagem_final = "%s.\n\n%s\n\n%s\n%s" % (prefixo_final, mensagem, sufixo_email, assinatura_email)
    if not verificar_python_maior33():
        mensagem_final = mensagem_final.encode("utf8")
    msg = MIMEText(mensagem_final, 'plain', 'utf8')

    # me == the sender"s email address
    # you == the recipient"s email address
    msg["Subject"] = titulo_final
    msg["From"] = login_email
    msg["To"] = ",".join(destinatarios_email)


    # Send the message via our own SMTP server.
    s = smtplib.SMTP_SSL(url_email_smtp_server, port_email)
    s.login(login_email, senha_email)
    if verificar_python_maior33():
        resp = s.send_message(msg)
    else:
        resp = s.sendmail(login_email, destinatarios_email, msg.as_string())
    s.quit()
    return resp


def verificar_python_maior33():
    return version_info.major > 2 and version_info.minor > 3




def str_codigos_nao_encontrados(obtj_nao_enc_dict):
        return "Codigo-%s, osos-%s" % (
            obtj_nao_enc_dict['codigo'],
            obtj_nao_enc_dict['osos'])


def str_codigos_nao_encontrados_itinerario(obtj_nao_enc_dict):
        return "Codigo-%s, Linha-%s, osos-%s" % (
            obtj_nao_enc_dict['codigo'],
            obtj_nao_enc_dict['linha'],
            obtj_nao_enc_dict['osos'])


class Noticificacao:

    def __init__(self, data_hora_inicio, importacoes_list):
        self.data_hora_inicio = data_hora_inicio
        self.importacoes_list = importacoes_list


    @property
    def __falhou(self):
        return any(not i.sucesso for i in self.importacoes_list)

    @property
    def __sucesso(self):
        return all(i.sucesso for i in self.importacoes_list)

    @property
    def __existe_linha_excluida(self):
        return any(len(i.linhas_excluidas) for i in self.importacoes_list)

    @property
    def __existe_linha_excluida_7_dias_atras(self):
        return any(len(i.linhas_excluidas_7_dias_atras) for i in self.importacoes_list)

    @property
    def __existe_linha_nao_encontrada(self):
        return any(len(i.linhas_nao_encontradas) for i in self.importacoes_list)

    @property
    def __existe_itinerario_nao_encontrado(self):
        return any(len(i.itinerarios_nao_encontrados) for i in self.importacoes_list)

    @property
    def __existe_empresa_nao_encontrada(self):
        return any(len(i.empresas_nao_encontradas) for i in self.importacoes_list)

    @property
    def __existe_tipo_veiculo_nao_encontrado(self):
        return any(len(i.tipos_veiculo_nao_encontrados) for i in self.importacoes_list)

    @property
    def __existe_conflito_de_carga(self):
        return any(i.conflito_de_carga for i in self.importacoes_list)

    @property
    def __existe_erro_winsiturb(self):
        return any(i.erro_winsiturb for i in self.importacoes_list)

    @property
    def __importacoes_com_linhas_excluidas(self):
        return filter(lambda i: i.linhas_excluidas, self.importacoes_list)

    @property
    def __importacoes_com_linhas_excluidas_7_dias_atras(self):
        return filter(lambda i: i.linhas_excluidas_7_dias_atras, self.importacoes_list)

    @property
    def __importacoes_com_linhas_nao_encontradas(self):
        return filter(lambda i: i.linhas_nao_encontradas, self.importacoes_list)

    @property
    def __importacoes_com_itinerarios_nao_encontrados(self):
        return filter(lambda i: i.itinerarios_nao_encontrados, self.importacoes_list)

    @property
    def __importacoes_com_empresas_nao_encontradas(self):
        return filter(lambda i: i.empresas_nao_encontradas, self.importacoes_list)

    @property
    def __importacoes_com_tipos_veiculos_nao_encontrados(self):
        return filter(lambda i: i.tipos_veiculo_nao_encontrados, self.importacoes_list)

    @property
    def __importacoes_com_conflito_de_carga(self):
        return filter(lambda i: i.conflito_de_carga, self.importacoes_list)

    @property
    def __importacoes_com_erro_winsiturb(self):
        return filter(lambda i: i.erro_winsiturb, self.importacoes_list)

    @property
    def __precisa_enviar_email(self):
        return True
        # return self.__falhou or \
        #        self.__existe_linha_excluida \
        #         or self.__existe_linha_excluida_7_dias_atras \
        #         or self.__existe_linha_nao_encontrada \
        #         or self.__existe_itinerario_nao_encontrado \
        #         or self.__existe_empresa_nao_encontrada \
        #         or self.__existe_tipo_veiculo_nao_encontrado


    def __enviar_email(self):
        self.__inicio_envio_email = datetime.now(tz=tzone)
        try:
            #array de str dia e linhas
            mensagem = ""
            if self.__existe_conflito_de_carga:
                dias_carga_conflitantes = ("Dia: %s\t\t\t %s" % (str_date_geo(i.dia), i.erro_customizado) for i in
                                         self.__importacoes_com_conflito_de_carga)
                mensagem = str("%s\n%s\n\n" % ("Problema de carga:", "\n".join(dias_carga_conflitantes)))

            if self.__existe_erro_winsiturb:
                dias_erro_winsiturb = (str_date_geo(i.dia) for i in self.__importacoes_com_erro_winsiturb)
                mensagem = str("%s:\t\t%s\n\n" % (u"Falha no servico winsiturb:", "\t".join(dias_erro_winsiturb)))

            if self.__existe_linha_excluida:
                dias_linhas_excluidas = ("Dia: %s \t (carga - %s):\t %s" %(str_date_geo(i.dia), i.winsiturb_carga_id, ", ".join(i.linhas_excluidas)) for i in self.__importacoes_com_linhas_excluidas)
                mensagem = "%s%s\n%s\n\n" % (mensagem, "Linhas excluidas:", "\n".join(dias_linhas_excluidas))

            if self.__existe_linha_excluida_7_dias_atras:
                dias_linhas_excluidas_7_dias_atras = ("Dia: %s \t (carga - %s):\t %s" % (
                str_date_geo(i.dia), i.winsiturb_carga_id, ", ".join(i.linhas_excluidas_7_dias_atras)) for i in
                                         self.__importacoes_com_linhas_excluidas_7_dias_atras)
                mensagem = "%s%s\n%s\n\n" % (mensagem, u"Linhas excluidas de uma semana atrás:", "\n".join(dias_linhas_excluidas_7_dias_atras))

            if self.__existe_linha_nao_encontrada:
                dias_linhas_nao_encontradas = ("Dia: %s (carga - %s):\n%s" %(str_date_geo(i.dia), i.winsiturb_carga_id, "\n".join(i.linhas_nao_encontradas)) for i in self.__importacoes_com_linhas_nao_encontradas)
                mensagem = "%s%s\n%s\n\n" % (mensagem, u"Linhas não encontradas:", "\n\n".join(dias_linhas_nao_encontradas))

            if self.__existe_itinerario_nao_encontrado:
                dias_itinerarios_nao_encontrados = ("Dia: %s (carga - %s):\n%s" % (str_date_geo(i.dia), i.winsiturb_carga_id, "\n".join(i.itinerarios_nao_encontrados)) for i in self.__importacoes_com_itinerarios_nao_encontrados)
                mensagem = "%s%s\n%s\n\n" % (mensagem, u"Itinerários não encontrados:", "\n\n".join(dias_itinerarios_nao_encontrados))

            if self.__existe_empresa_nao_encontrada:
                dias_empresas_nao_encontradas = ("Dia: %s (carga - %s):\n%s" %(str_date_geo(i.dia), i.winsiturb_carga_id, "\n".join(i.empresas_nao_encontradas)) for i in self.__importacoes_com_empresas_nao_encontradas)
                mensagem = "%s%s\n%s\n\n" % (mensagem, u"Empresas não encontradas:", "\n\n".join(dias_empresas_nao_encontradas))

            if self.__existe_tipo_veiculo_nao_encontrado:
                dias_tipos_veiculo_nao_encontrados = ("Dia: %s (carga - %s):\n%s" %(str_date_geo(i.dia), i.winsiturb_carga_id, "\n".join(i.tipos_veiculo_nao_encontrados)) for i in self.__importacoes_com_tipos_veiculos_nao_encontrados)
                mensagem = "%s%s\n%s\n\n" % (mensagem, u"Tipos de veículo não encontrados:", "\n\n".join(dias_tipos_veiculo_nao_encontrados))


            self.__erro_envio_email = enviar_email(self.data_hora_inicio, mensagem)

        except Exception as ex:
            self.__erro_envio_email = str(ex)
        self.__termino_envio_email = datetime.now(tz=tzone)

    def processar(self):
        if self.__precisa_enviar_email:
            self.__enviar_email()

        file = open("%s/%s_%s.json" %(diretorio_saida, prefix_file_name, to_timemillis(self.data_hora_inicio)), "w")
        json.dump(self.to_map(), file, ensure_ascii=False)
        file.close()


    def to_map(self):
        mapeado = {
            "sucessoExecucao": self.__sucesso,
            "ultimaExecucao": {
                "iso": str_date(self.data_hora_inicio),
                "timestamp": to_timemillis(self.data_hora_inicio)
            },
            "importacoes":  [i.to_map() for i in self.importacoes_list]
        }


        if self.__precisa_enviar_email and self.__inicio_envio_email and self.__termino_envio_email:
            envio_email = {
                "to": destinatarios_email,
                "horarioConclusaoEnvio": {
                    "iso": self.__termino_envio_email.isoformat(),
                    "timestamp": to_timemillis(self.__termino_envio_email)
                },
                "sucessoOperacaoEnvio": not self.__erro_envio_email,
                "motivoFalha": self.__erro_envio_email
            }
        else:
            envio_email = {}

        notificacao_map = {
            "sucesso": self.__sucesso,
            "envioNecessario": self.__precisa_enviar_email,
            "envioEmail": envio_email
        }

        mapeado["notificacao"] = notificacao_map
        return mapeado

    def to_json(self):
        return json.dumps(self.to_map(), sort_keys=True, indent=4, ensure_ascii=True)








class Importacao:
    def __init__(self, dia, **kwargs):
        detalhes_importacao = kwargs.get("pontual_resposta")
        self.dia = dia
        self.pontual_winsiturb_sinc = {
            "idCarga": kwargs.get("winsiturbsinc_carga_id"),
            "dataHoraCriacao": str_date(kwargs.get("winsiturbsinc_carga_data_hora_criacao")),
            "totalViagens": kwargs.get("winsiturbsinc_carga_total_viagens")
        }
        self.winsiturb = {
            "idCarga": kwargs.get("winsiturb_carga_id"),
            "dataInicio": str_date(kwargs.get("winsiturb_carga_data_inicio")),
            "dataFim": str_date(kwargs.get("winsiturb_carga_data_fim")),
            "tipoDeDia": kwargs.get("winsiturb_carga_tipo_dia")
        }

        pontual_data_envio_requisicao = kwargs.get("pontual_data_envio_requisicao")
        pontual_data_envio_resposta = kwargs.get("pontual_data_envio_resposta")
        self.pontual = {
            "resposta": detalhes_importacao,
            "perfil": {
                "envioRequisicao": {
                    "iso": str_date(pontual_data_envio_requisicao),
                    "timestamp": to_timemillis(pontual_data_envio_requisicao)
                },
                "recebimentoResposta": {
                    "iso": str_date(pontual_data_envio_resposta),
                    "timestamp": to_timemillis(pontual_data_envio_resposta)
                },
                "duracaoTotalEmSegundos": (pontual_data_envio_resposta - pontual_data_envio_requisicao).total_seconds() if pontual_data_envio_resposta and pontual_data_envio_requisicao else 0
            }
        }
        self.winsiturb_carga_id = kwargs.get('winsiturb_carga_id')
        #Problemas de viagem que fazem alertar a ceturb sobre possiveis problemas na importacao
        self.linhas_excluidas = detalhes_importacao["linhasExcluidas"] if detalhes_importacao else []
        self.linhas_excluidas_7_dias_atras = detalhes_importacao["linhasExcluidas7DiasAtras"] if detalhes_importacao else []
        self.linhas_nao_encontradas = map(str_codigos_nao_encontrados, detalhes_importacao["linhasNaoEncontradas"]) if detalhes_importacao else []
        self.itinerarios_nao_encontrados = map(str_codigos_nao_encontrados_itinerario, detalhes_importacao["itinerariosNaoEncontrados"]) if detalhes_importacao else []
        self.empresas_nao_encontradas = map(str_codigos_nao_encontrados, detalhes_importacao["empresasNaoEncontradas"]) if detalhes_importacao else []
        self.tipos_veiculo_nao_encontrados = map(str_codigos_nao_encontrados, detalhes_importacao["tiposVeiculoNaoEncontrados"]) if detalhes_importacao else []

        self.sucesso = kwargs.get("sucesso")
        self.detalhe_resultado = kwargs.get("detalhe_resultado")
        self.erro = kwargs.get("error")
        self.argumentos_do_erro = kwargs.get("error_arguments")
        self.conflito_de_carga = False
        self.erro_customizado = None
        if self.erro and 'CONFLITO_DE_CARGA' in self.erro:
            self.conflito_de_carga = True
            self.cargas_conflitantes = self.argumentos_do_erro
            self.erro_customizado = "Cargas conflitantes: %s." % ",".join(self.argumentos_do_erro)
        else:
            self.cargas_conflitantes = None


        if self.erro and 'NENHUMA_CARGA' in self.erro:
            self.conflito_de_carga = True
            self.erro_customizado = "Nenhuma carga encontrada."

        if self.erro and 'ERRO_WINSITURB' in self.erro:
            self.erro_winsiturb = True
            self.httpErroCode = self.argumentos_do_erro[0] if self.argumentos_do_erro else None
        else:
            self.erro_winsiturb = False

    def to_map(self):
        mapeado = {
            "dia": str(self.dia),
            "pontual_winsiturb_sinc": self.pontual_winsiturb_sinc,
            "winsiturb": self.winsiturb,
            "pontual": self.pontual,
            "sucesso": True
        }
        if not self.sucesso:
            mapeado["sucesso"] = False
            mapeado["detalhe_resultado"] = self.detalhe_resultado
            mapeado["erro"] = self.erro if type(self.erro) == str else self.erro.encode('utf8')

            if self.cargas_conflitantes:
                mapeado["cargas_conflitantes"] = self.cargas_conflitantes

            if self.erro_winsiturb and self.httpErroCode:
                mapeado["erro_winsiturb"] = "HttpStatus = %s" % self.httpErroCode

        return mapeado

    def to_json(self):
        return json.dumps(self.to_map(), sort_keys=True, indent=4)


def sincronizar_dia(dia):
    importacao_corrente = None
    dia_str = dia.strftime("%d-%m-%Y")
    url_sincronismo = "/".join([url_base, "sincronismoCompleto", dia_str])
    url_remocao = "/".join([url_base, "removerSincronismo", dia_str])
    #tenta garantir a remocao

    # print(r)
    # print(conteudo)
    try:
        r = requests.get(url_remocao)
        r = requests.get(url_sincronismo)
        r.encoding = 'utf-8'
        conteudo = r.json()
        print("importacao: %s - httpCode: %d - conteudo: %s" % (dia_str, r.status_code, conteudo))
        if r.status_code == 200:
            carga_obj = conteudo.get("carga")
            if carga_obj:
                winsiturbsinc_carga_id = carga_obj["id"]
                winsiturbsinc_carga_data_hora_criacao = from_timemillis(carga_obj["dataHoraCriacao"])
                winsiturb_carga_id = carga_obj["idCarga"]
                winsiturb_carga_data_inicio = from_timemillis(carga_obj["dataInicio"]).date()
                winsiturb_carga_data_fim = from_timemillis(carga_obj["dataFim"]).date()
                winsiturb_carga_tipo_dia = carga_obj["tipoDeDia"]


            winsiturbsinc_carga_total_viagens = conteudo.get("viagensWinsiturb")

            viagem_pontual = conteudo.get("viagensPontual")

            if viagem_pontual:
                pontual_data_envio_requisicao = from_timemillis(viagem_pontual["dtInicioSincronismoComPontual"])
                pontual_data_envio_resposta = from_timemillis(viagem_pontual["dtFimSincronismoComPontual"])


            importacao_corrente = Importacao(dia, winsiturbsinc_carga_id=winsiturbsinc_carga_id,
                                    winsiturbsinc_carga_data_hora_criacao=winsiturbsinc_carga_data_hora_criacao,
                                    winsiturbsinc_carga_total_viagens=winsiturbsinc_carga_total_viagens,
                                    winsiturb_carga_id=winsiturb_carga_id,
                                    winsiturb_carga_data_inicio=winsiturb_carga_data_inicio,
                                    winsiturb_carga_data_fim=winsiturb_carga_data_fim,
                                    winsiturb_carga_tipo_dia=winsiturb_carga_tipo_dia,
                                    pontual_resposta=viagem_pontual,
                                    pontual_data_envio_requisicao=pontual_data_envio_requisicao,
                                    pontual_data_envio_resposta=pontual_data_envio_resposta,
                                    sucesso=conteudo["sucesso"],
                                    error=conteudo.get("error"),
                                    detalhe_resultado=conteudo.get("msg")
                                    )

        else:
            importacao_corrente = Importacao(
                dia,
                sucesso=False,
                error=conteudo.get("error"),
                detalhe_resultado=conteudo.get("msg"),
                error_arguments=conteudo.get("error_arguments"))

    except Exception as conExp:
        importacao_corrente = Importacao(dia, sucesso=False, error=str(conExp))

    return importacao_corrente








# semana = ("Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo")
# A ideia é considerar segunda-feira o marco zero de inicio, portanto fazendo-se a carga com o maximo de dias 12 - date.today().weekday()
# Lembrando que em python a semana começa na segunda-feira com o valor 0

def importacao():
    importacoes = []
    inicio = datetime.now(tz=tzone)
    hj = date.today()
    max_dias = 13 - hj.weekday()
    for i in range(1, max_dias):
        dia = date.fromordinal(hj.toordinal() + i)
        importacao = sincronizar_dia(dia)
        importacoes.append(importacao)

    # dia = date(day=23, month=1, year=2017)
    # importacao = sincronizar_dia(dia)
    # importacoes.append(importacao)

    notificacao = Noticificacao(inicio, importacoes)
    notificacao.processar()

def help():
    print("Versão: %s   " % VERSAO)
    print("Modos: [0: 'help', 1: 'importacao', 2: 'ultimo_sincronismo', 3: 'test_email']")
    print("Exemplo: python invocador_winsiturb.py arquivo-de-configuracao numero-do-modo-descrito-acima")

def test_email():
    enviar_email(datetime.now(tz=tzone), "")

def ultimo_sincronismo():
    import glob
    arquivos = glob.glob1(diretorio_saida, "%s*.json" % prefix_file_name)
    # print(arquivos)
    #todo obter o ultimo arquivo
    # timestamps = map(lambda i: i.split("_")[2], arquivos)

    timestamps = [i.split("_")[2].split('.')[0] for i in arquivos]
    # print(timestamps)
    maior_timestamp = max(timestamps)
    with open("%s/%s_%s.json" %(diretorio_saida, prefix_file_name, maior_timestamp)) as file:
        print(file.readlines()[0])




if __name__ == '__main__':
    #modulo_importacao = ['help', 'importacao', 'ultimo_sincronismo']
    modulo_importacao = argv[2] if len(argv) > 2 else 0
    caminho_arquivo_prop = argv[1] if len(argv) > 1 else 'invocador.properties'
    carregar_propriedades(caminho_arquivo_prop)
    opcoes = {
        0: help,
        1: importacao,
        2: ultimo_sincronismo,
        3: test_email
    }
    modo = opcoes.get(int(modulo_importacao))
    if not modo:
        opcoes.get(0)()
    else:
        modo()

