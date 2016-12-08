#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from configparser import RawConfigParser
from datetime import date, datetime
import pytz
from sys import argv, version_info
from tzlocal import get_localzone



import requests

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
        senha_email, destinatarios_email, titulo_email, prefixo_email, sufixo_email, assinatura_email

    config = RawConfigParser()
    config.read(file_path)

    #geral
    url_base = config.get("invocador", "url_base")
    prefix_file_name = config.get("invocador", "prefix_file_name")
    diretorio_saida = config.get("invocador", "diretorio_saida")

    if not (path.exists(diretorio_saida) and path.isdir(diretorio_saida)):
        raise ValueError("O caminho %s é inesistente, sem permissão ou não é um diretório" % diretorio_saida)


    #email
    url_email_smtp_server = str(config.get("email", "url_smtp_server"))
    port_email = int(config.get("email", "port"))
    login_email = config.get("email", "login")
    senha_email = config.get("email", "senha")
    destinatarios_email = eval(config.get("email", "destinatarios"))
    titulo_email = config.get("email", "titulo")
    prefixo_email = config.get("email", "prefixo")
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
    import smtplib
    from email.mime.text import MIMEText
    agora = datetime.now(tz=tzone)
    if agora.hour in range(6, 12):
        saudacao = "Bom dia"
    elif agora.hour in range(12, 18):
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"
    prefixo_final = prefixo_email % saudacao
    titulo_final = titulo_email % str_date_geo(data_hora_execucao)
    mensagem_final = "%s.\n\n%s\n\n%s\n%s" %(prefixo_final, mensagem, sufixo_email, assinatura_email)
    msg = MIMEText(mensagem_final)

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
        resp = s.sendmail(login_email, msg["To"], msg.as_string())
    s.quit()
    return resp


def verificar_python_maior33():
    return version_info.major > 2 and version_info.minor > 3






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
    def __importacoes_com_linhas_excluidas(self):
        return filter(lambda i: i.linhas_excluidas, self.importacoes_list)


    @property
    def __precisa_enviar_email(self):
        return self.__falhou or self.__existe_linha_excluida


    def __enviar_email(self):
        self.__inicio_envio_email = datetime.now(tz=tzone)
        try:
            #array de str dia e linhas
            dias_linhas_excluidas = ("Dia: %s \t\t\t Linha%s: %s" %(str_date_geo(i.dia), "s" if len(i.linhas_excluidas) > 1 else "", ", ".join(i.linhas_excluidas)) for i in self.__importacoes_com_linhas_excluidas)
            self.__erro_envio_email = enviar_email(self.data_hora_inicio, "\n".join(dias_linhas_excluidas))

        except Exception as ex:
            self.__erro_envio_email = str(ex)
        self.__termino_envio_email = datetime.now(tz=tzone)

    def processar(self):
        if self.__precisa_enviar_email:
            self.__enviar_email()

        file = open("%s/%s_%s.json" %(diretorio_saida, prefix_file_name, to_timemillis(self.data_hora_inicio)), "w")
        json.dump(self.to_map(), file)
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
        self.linhas_excluidas = detalhes_importacao["linhasExcluidas"] if detalhes_importacao else None
        self.sucesso = kwargs.get("sucesso")
        self.detalhe_resultado = kwargs.get("detalhe_resultado")
        self.erro = kwargs.get("error")


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
            mapeado["erro"] = self.erro
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
            importacao_corrente = Importacao(dia, sucesso=False, error=conteudo.get("error"), detalhe_resultado=conteudo.get("msg"))

    except Exception as conExp:
        importacao_corrente = Importacao(dia, sucesso=False, error=str(conExp))

    return importacao_corrente








# semana = ("Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo")
# A ideia é considerar segunda-feira o marco zero de inicio, portanto fazendo-se a carga com o maximo de dias 12 - date.today().weekday()
# Lembrando que em python a semana começa na segunda-feira com o valor 0

def importacao():
    hj = date.today()
    max_dias = 6 - hj.weekday()
    importacoes = []
    inicio = datetime.now(tz=tzone)
    for i in range(1, max_dias):
        dia = date.fromordinal(hj.toordinal() + i)
        importacao = sincronizar_dia(dia)
        importacoes.append(importacao)

    notificacao = Noticificacao(inicio, importacoes)
    notificacao.processar()

def help():
    print("[0: 'help', 1: 'importacao', 2: 'ultimo_sincronismo', 3: 'test_email']\n")

def test_email():
    enviar_email(datetime.now(tz=tzone), "Grande teste")

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

















