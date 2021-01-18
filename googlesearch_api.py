# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 12:36:51 2020

@author: luisr
"""
from credentials import api_key, cse_id
from googleapiclient.discovery import build
import time
import datetime
from dateutil.relativedelta import *
import pandas as pd
result_df = pd.DataFrame()

selected_metadata = ['Kind', 'Title', 'htmlTitle', 'link', 'snippet',
                     'og:site_name', 'og:description', 'og:type',
                     'author', 'og:title', 'abstract', 'og:locale', 'og:url',
                     'article:published_time', 'title']
#%%
#cse - https://cse.google.com.br/cse/
#kwargs - https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
#referencia - https://towardsdatascience.com/current-google-search-packages-using-python-3-7-a-simple-tutorial-3606e459e0d4

#Função de bsuca utilizando a google search api
def google_query(query, api_key, cse_id, **kwargs):
    query_service = build("customsearch", "v1", developerKey=api_key)
    query_results = query_service.cse().list(q=query,    # Query
                                             cx=cse_id,  # CSE ID
                                             **kwargs
                                             ).execute()
    return query_results

#%%Mapeamento dos metadados para cada site.
def trataestruturametadados(date,result):
    result_dict = {}
    
    result_dict['date_interval'] = date

    for result_key in result.keys():

        if result_key in selected_metadata:
            result_dict[result_key] = result[result_key]
            
        if 'pagemap' in result.keys():
            for metatag_key in result['pagemap']['metatags'][0].keys():
        
                if metatag_key in selected_metadata:
                    result_dict[metatag_key] = result['pagemap']['metatags'][0][metatag_key]

    return result_dict


#%% Busca Mensal - Ajustar de Acordo com os resultados
date_list = []
date_object = datetime.date.today() #Data atual

for i in range(732): #Preciso definir o intervalo de ano aqui
    date_list.append(date_object)
    date_object = date_object-relativedelta(days=+5) #defino aqui o intervalo de data
    
print(len(date_list))
#%%
site = 'correiobraziliense.com.br'
minhalista = [] 
breakCount = 0

for dateI in range(len(date_list)): #Itera pela lista de datas
    
    print(dateI+1)
    
    if dateI+1 >= len(date_list):
        break
    query= """"universidade de brasília" AND ("inven*" OR "produto" OR "inov*" OR "patente" 
    OR "premi*" OR "desenvolv*" OR "cria*" OR "serviço*" OR "processo*")
    after:{} before:{} site:{}""".format(date_list[dateI+1],date_list[dateI], site)
    #Tentar comparar o uso ou não do intitle e tentar inrul também.
    
    print("Pesquisando resultados entre {} e {}".format(date_list[dateI+1], date_list[dateI]))
    
    
    start_i = 1 #Variável aux para paginação dos resutlados (ver cse args)
    count = 1 #Variável para contar quantos resultados foram recuperados
    
    for i in range(10):
        
        my_results = google_query(query,api_key, cse_id, num = 10,
                                  start = start_i)
        
        if 'items' not in my_results.keys():
            break #Pula iteração se não houver resultados
        
        print("Verificando a página {} de resultados".format(int((start_i-1)/10)), end="; ")
                
        for result in my_results['items']:
            
            result_df = result_df.append(trataestruturametadados(str(date_list[dateI+1])+" e "+str(date_list[dateI]),
                                                                 result), ignore_index = True)
            count+=1

        start_i+=10
        time.sleep(3)

    print("{} resultados coletados".format(count))
    time.sleep(5)
    
    breakCount +=1
    
    #if breakCount == 5:
        #break
#%% 
result_df.to_csv('resultado_df.csv', index=False)
