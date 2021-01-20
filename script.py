# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:31:07 2019

@author: Lucas
"""

import pandas as pd
import plotly.express as px
from datetime import datetime
from datetime import timedelta
import plotly.io as pio
from plotly.offline import plot
import plotly.graph_objs as go


class Evento:
    def __init__(self,deltae,ptot, imed, deltat, sheet_name, path_file):
        
        """
        Essa funcao define os parametros para definicao de um evento
        deltae e o tempo entre eventos em minutos,
        ptot e a precipitacao total de um evento em milimetros,
        imed e a intensidade media de um evento em milimetros por hora
        Certifique-se que seu arq está atualizado para utilizar o script
        certifique-se que sua planilha esteja no mesmo padrão que a disponibilizada na pasta de Dados
        deste repositorio
        """
        
        
        arq = path_file
        self.df = pd.read_excel(arq, sheet_name = sheet_name)
        c = self.df['Sydney']
        d = self.df[1]
        self.deltae = timedelta(minutes = deltae)
        self.ptot = float(ptot)
        self.imed = float(imed)
        self.tempo_d = str(deltat)
        self.deltat = timedelta(minutes = deltat)
        lista = []
        for i in range(len(self.df)):
            try:
                data = datetime(c[i].year, c[i].month, c[i].day, d[i].hour, d[i].minute, d[i].second)
            except:
                data = data.replace(year=2050)
            lista.append(data)
        
        self.df['data'] = lista
        self.dframe = dict()
        
    
    def def_eventos(self):
        
        """
        Essa funcao define os eventos com duracao menor que o deltae
        """
        
        aux = 0
        eventos = list()
        df1 = list()
        size = self.df.shape[0]
        while aux < size:
            try:
                dtime = self.df['data'][aux+1] - self.df['data'][aux]
                if self.deltae.total_seconds() >= dtime.total_seconds():
                    df1.append([self.df.loc[aux]['data'],self.df.loc[aux]['MLD144']])
                    aux +=1
                else:
                    df1.append([self.df.loc[aux]['data'],self.df.loc[aux]['MLD144']])
                    eventos.append(df1)
                    df1 = list()
                    aux+=1
            except:
                eventos.append(df1)
                df1 = list()
                aux+=1
        self.dframe = {i: pd.DataFrame(eventos[i], columns = ['data','pre']) for i in range(len(eventos))}  #mexiaqui      

        
    def sel_by_ptot(self, retornar=False):
        
        """
        Essa funcao define os eventos com relacao a ptot e a imed
        """
        aux_list = []
        popped = False
        for i in self.dframe.copy().keys():
            if self.dframe[i]['pre'].sum() <self.ptot:
                self.dframe.pop(i)
                popped=True
            if retornar==True and popped==False:
                aux_list.append(self.dframe[i]['pre'].sum())
            popped=False
        if retornar==True:
            return aux_list

                
    def sel_by_imed(self, retornar=False):
        imed_list = []
        dur_list = []
        popped = False
        for j in self.dframe.copy().keys():
            self.timedelta = self.dframe[j]['data'].tail(1)[len(self.dframe[j])-1] - self.dframe[j]['data'][0]
            intensidade = (self.dframe[j]['pre'].sum()*3600)/self.timedelta.total_seconds()
            if intensidade< self.imed or intensidade >1000:
                self.dframe.pop(j)
                popped=True 
            if retornar==True and popped==False:
                #retorna uma lista de intensidade e duração do evento
                imed_list.append(((self.dframe[j]['pre'].sum()*3600)/self.timedelta.total_seconds()))
                dur_list.append(self.timedelta.total_seconds()/3600)
            popped=False
        if retornar==True:
            return imed_list, dur_list
                

    def discretizando(self):
        eventos_disc = list()
        lista = list()
        aux = 0
        for i in self.dframe.keys():
            starting = self.dframe[i]['data'][0]
            ending = self.dframe[i]['data'].tail(1)[len(self.dframe[i])-1]       
            date_range = pd.date_range(start = starting, end = ending, freq = self.tempo_d+'min' )
            #o contador percorre o dframe, ou seja, não discretizado
            contador = 0
            #aux percorre o date_range, ou seja, discretizado
            aux = 0  
            prec_acumulada = 0
            while contador < len(self.dframe[i]['data']) and aux < len(date_range):
                
                date_r = date_range[aux].to_pydatetime()                                #date time discretizado
                date_j = self.dframe[i]['data'][contador].to_pydatetime()               #lista de eventos
            
                if date_j <= date_r + self.deltat:                       
                    prec_acumulada += self.dframe[i]['pre'][contador]
                    contador+=1
                else:
                    lista.append([date_r,prec_acumulada])
                    prec_acumulada = 0
                    aux += 1
                    
            lista.append([date_r,prec_acumulada])
            eventos_disc.append(lista)
            lista = list() 
        self.dframe = {k: pd.DataFrame(eventos_disc[k], columns = ['data','pre']) for k in range(len(eventos_disc))}
    
    def grafico(self,key):
        df = self.dframe[key]
        print(type(df))
        fig = px.bar(df, x = 'data', y ='pre')
        
        
        pio.write_html(fig, file='first_figure.html', auto_open=True)



###############fim##################################
        
pathfile = r"C:\Users\Lucas\Desktop\UFAL\PIBIC19_20\dados\TodosOsDadosPluFeitosa.xlsx"
sheet = '2020'
evento = Evento(deltae=10,ptot=10,imed=0,deltat=5, sheet_name=sheet, path_file= pathfile)

evento.def_eventos()
evento.sel_by_ptot()
evento.sel_by_imed()
evento.discretizando()
evento.grafico(15) 

p = 405
dicionario = {}



lista_ptot = []
lista_imed, lista_dur = [],[]

evento = Evento(p,0.4,3,1, sheet_name='2014', path_file= pathfile)
evento.def_eventos()
lista_ptot += evento.sel_by_ptot(retornar=True)
li_imed, li_dur = evento.sel_by_imed(retornar=True)
lista_imed += li_imed
lista_dur += li_dur
dicionario[405] = [lista_ptot,lista_imed,lista_dur]

def box_plot(arg1=False,arg2=False,arg3=False):
    #Se arg1 é True, retorna um boxplot de precipitação(mm),
    #Se arg2 é true, r etorna um boxplot de duração(h),e
    #Se ar3 é True, retorna um boxplot de intensidade(mm/h)
    fig = go.Figure()
    if arg1==True:
        for key in dicionario.keys():
            modelo = dicionario[key][0]
            fig.add_trace(go.Box(y=modelo, name=key))
            file = 'boxplot_prec.html'
    elif arg2==True:
        for key in dicionario.keys():
            modelo = dicionario[key][1]
            fig.add_trace(go.Box(y=modelo, name=key))
            file = 'boxplot_dur.html'
    elif arg3==True:
        for key in dicionario.keys():
            modelo = dicionario[key][2]
            fig.add_trace(go.Box(y=modelo, name=key))
            file = 'boxplot_imed.html'
    pio.write_html(fig, file= file, auto_open=True)

box_plot(arg1=True)

    
with pd.ExcelWriter('dur_box.xlsx') as writer:  
    for i in p:
        a = pd.DataFrame(dicionario[i][2])
        a.to_excel(writer, str(i))



"""


for kleber in sheet:    
    evento = Evento(525600,0,0,5, sheet_name=kleber, path_file= pathfile)
    evento.def_eventos()
    evento.discretizando()
    nome = 'EventosFeitosaDisc{}.xlsx'.format(kleber)
    evento.dframe[0].to_excel(nome, sheet_name=kleber)
    print(kleber)
    

big_df = pd.DataFrame()
for i in evento.dframe.keys():
    top_row = pd.Series(['evento:',i+1])
    ndf = evento.dframe[i]
    
    arow = pd.DataFrame([top_row])
    result = pd.concat([arow,ndf],ignore_index= True)
    big_df = big_df.append(result, ignore_index= True)
    result = pd.DataFrame()

big_df = pd.DataFrame()
for i in dicionario.keys():
    for j in dicionario[i][3].keys():
        top_row = pd.Series(['evento:',j+1])
        ndf = dicionario[i][3][j]
        
        arow = pd.DataFrame([top_row])
        result = pd.concat([arow,ndf],ignore_index= True)
        big_df = big_df.append(result, ignore_index= True)
        result = pd.DataFrame()
    file = 'eventos19{}.xlsx'.format(i)
    big_df.to_excel(file,sheet_name='2019')



evento = Evento(deltae=60,ptot=5,imed=3,deltat=10)
evento.def_eventos()
evento.sel_by_ptot()
evento.sel_by_imed()
        
        
evento.discretizando()
evento.grafico(escreva aqui alguma key de um dos eventos selecionados)
"""  