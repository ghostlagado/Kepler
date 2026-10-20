# Importação de config.
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox as Qmsg
from os import system
from sys import exit
from qdarktheme import setup_theme as st
import requests as rq, json

# Importação de modulos próprios
from metas import Metas
from hxh import mainHxh
from pa import PA
from vj import VJ
from estore import es
from atualizarEstore import init


class App():
    def __init__(self):
        # Variavel de Metas
        self.m = Metas
        self.m.fl = 'L062'
        self.m()
        self.metaLbl = self.m().soma

        # Settings
        self.app = QApplication([])
        self.winLogin = uic.loadUi('uic//login.ui') # Exporta o design da Login windown 
        self.mainWin = uic.loadUi('uic//main.ui') # Exporta o design da Main windown
        st() # Setar tema escuro


        # Callback dos Buttons
        self.mainWin.btnhxh.clicked.connect(self.hxh)
        self.mainWin.btnestore.clicked.connect(self.estore)
        self.mainWin.paBtn.clicked.connect(self.pa)
        self.mainWin.btnvj.clicked.connect(self.vj)

        self.mainWin.logout.clicked.connect(self.logout)

        self.mainWin.metaBtn.clicked.connect(self.localMetas)
        self.mainWin.atualizarEstore.clicked.connect(self.atuEs)

        self.mainWin.btnAdd.clicked.connect(self.addUser)
        self.mainWin.btnSenha.clicked.connect(self.atuSenha)
        self.mainWin.btnEdit.clicked.connect(self.editarUser)
        self.mainWin.btnAtua.clicked.connect(self.atuaNome)

        self.winLogin.btnLogin.clicked.connect(self.cons)
        self.slvBtn = self.winLogin.salvarUser
        self.mainWin.metaLbl.setText(f'Meta: R${self.metaLbl:.2f}') # Setar o texto com a meta dia
        #  Executando a Tela de Login
        self.winLogin.show()
        self.app.exec()

    # Login Config
    def cons(self):
        # Pega valores do campo de texto
        self.user = self.winLogin.mat.text()
        self.pasw = self.winLogin.pas.text()

        # Try Login
        try:
            linkc = f"https://dados-9be06-default-rtdb.firebaseio.com/users/{self.user}.json"
            r = rq.get(linkc)
            dados = r.json()
            for d in dados:
                key = d
            self.dados = dados[key]
            senha = self.dados['senha']
            self.nome = self.dados['nome']

            if self.pasw == senha:
                self.msg(self.winLogin, f'Seja bem vindo {self.nome}')
                self.mainWin.lblUser.setText(f'{self.nome}')
                self.winLogin.close()
                self.mainWin.show()
            else:
                self.msg(self.winLogin, 'Senha Incorreta !!')
        except:
            self.msg(self.winLogin, 'Usuário não encontrado !!')

    def addUser(self):
        if self.user != 'admin':
            self.msg(self.mainWin, 'Função de ADM!!')
    
    def atuSenha(self):
        if self.user != 'admin':
            self.msg(self.mainWin, 'Função de ADM!!')

    def editarUser(self):
        if self.user != 'admin':
            self.msg(self.mainWin, 'Função de ADM!!')

    def atuaNome(self):
        if self.user != 'admin':
            self.msg(self.mainWin, 'Função de ADM!!')

    # MessageBox 
    def msg(self, win, msg):
        self.tt = 'LOGIN'
        Qmsg.about(win, self.tt, msg)

    # E-Store
    def estore(self):
        system('cd pln && estore.xlsx')
        es().iniciar()

    # Hora X Hora
    def hxh(self):
        with open('txt\\texto.txt', 'w') as doc:
            text = self.mainWin.entex.toPlainText()
            doc.write(text)
        mainHxh()

    # Participação
    def pa(self):
        with open('txt\\clb.txt', 'w') as doc:
            text = self.mainWin.entex.toPlainText()
            doc.write(text)
        PA().cons()

    # Vendas com Juros
    def vj(self):
        with open('txt\\vj.txt', 'w') as doc:
            text = self.mainWin.entex.toPlainText()
            doc.write(text)
        VJ().code()
    
    # Puxa 1% das metas do .XLSX 
    def atuEs(self):
        self.msg(self.winLogin, 'Atualizando...')
        init()
        self.msg(self.winLogin, 'Metas de Estore Atualizada!!!')

    # Local das metas .XLSX
    def localMetas(self):
        system('explorer metas')

    # Logout !
    def logout(self):
        if self.slvBtn.isChecked():
            self.winLogin.mat.setText(self.user)
        else:
            self.winLogin.mat.setText('')
        self.winLogin.pas.setText('')
        self.mainWin.close()
        self.winLogin.show()
App()