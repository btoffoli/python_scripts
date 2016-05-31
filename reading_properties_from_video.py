# -*- coding: utf-8 -*-
from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset
from sys import argv, stderr, exit
from datetime import datetime, timedelta
import shutil, os

def extractInicioEFimDoVideo(filename):
    filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    if not parser:
        print >> stderr, "Falha ao converter arquivo."
        exit(1)
    try:
        metadata = extractMetadata(parser)
    except HachoirError, err:
        print "Falha na extração de metadado do arquivo: %s" % unicode(err)
        metadata = None
    if not metadata:
        print "Sem metadado"
        exit(1)

    text = metadata.exportPlaintext()
    data_inicial = metadata._Metadata__data['creation_date'].values[0].value
    print data_inicial
    # total_tempo_millis = metadata._Metadata__data['duration'].values[0].value.total_seconds() * 1000
    total_tempo_millis = metadata._Metadata__data['duration'].values[0].value
    print total_tempo_millis
    data_final = data_inicial + total_tempo_millis
    inicio = datetime(1970, 1, 1)
    time_millis_inicial = long((data_inicial - inicio).total_seconds() * 1000)
    time_millis_final = long((data_final - inicio).total_seconds() * 1000)
    return (time_millis_inicial, time_millis_final)


if __name__ == '__main__':
    if len(argv) != 4:
        print >>stderr, "usar: %s nomeDoArquivo" % argv[0]
        exit(1)
    diretorioEntrada = argv[1]
    diretorioSaida = argv[2]
    numeroDoCarro = argv[3]

    for file in os.listdir(diretorioEntrada):
        if file.endswith(".mp4"):
            inicio, fim = tupla_tempos = extractInicioEFimDoVideo(diretorioEntrada + file)
            print "Inicio:%d  Fim:%d" % tupla_tempos
            novoNomeDoArquivo = "%s_%d_%d.mp4" % (numeroDoCarro, inicio, fim)
            shutil.move(diretorioEntrada + file, diretorioSaida + novoNomeDoArquivo)


