#!/usr/bin/env python

###
#   By Antonio Thomacelli Gomes
#   Version 0.1  Date: 22/10/2012
#   http://www.linuxresort.blogspot.com.br
###

from gi.repository import Gtk

class JanelaFull(Gtk.Window):

 def __init__(self):
  Gtk.Window.__init__(self, title="Janela")
  self.set_border_width(150)
  
  prateleira = Gtk.Table( 5, 2, True)
  self.add(prateleira)
  
  label_nome = Gtk.Label("Nome:")
  prateleira.attach( label_nome, 0, 1, 0, 1)
  
  entrada_nome = Gtk.Entry()
  entrada_nome.get_text()
  prateleira.attach( entrada_nome, 1, 2, 0, 1)

  label_valor = Gtk.Label("Valor:")
  prateleira.attach( label_valor, 0, 1, 2, 3)
  
  entrada_valor = Gtk.Entry()
  entrada_valor.get_text()
  prateleira.attach( entrada_valor, 1, 2, 2, 3)
  
  
  botao_gravar = Gtk.Button(label="Gravar")
  botao_gravar.connect("clicked", self.gravacao)
  prateleira.attach( botao_gravar, 0, 2, 4, 5)

 def gravacao(self, button):
  print("Funcionando")     

janela = JanelaFull()
janela.connect("delete-event", Gtk.main_quit)
janela.show_all()
Gtk.main()