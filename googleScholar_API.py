import json
import requests as req
import pandas as pd
from itertools import combinations
import time

resultado = pd.DataFrame()
dbDf = pd.read_csv("gruposCI_UnB_21082020.csv")

endpoint = "https://serpapi.com/search"

for i in range(len(dbDf['Pesq_Est'])):
    
    comb = combinations(dbDf['Pesq_Est'][i].split(", "), 2)
    ano = dbDf['Ano formação'][i]
    identifier = dbDf['Link do DGP'][i]
    
    print("Pesquisando publicações do  grupo {} a partir do ano {}".format(identifier, ano))
    
    for authorL in list(comb):
        
        query = '"'+authorL[0]+'" AND "'+authorL[1]+'"'
        
        #query = '''"André Porto Ancona Lopez" AND "Darcilene Sena Rezende"'''
        
        print("    * Pesquisando a coautoria {} do grupo {}".format(query, identifier))
        
        parameters = {'q':'author:'+query,
              'as_ylo':ano,
              'engine':'google_scholar',
              'as_vis':'1',
              'api_key':''}
        api_results = req.get(endpoint, params=parameters).json()
        time.sleep(1)
        
        resultDict = {}
        if 'organic_results' in api_results.keys():
            print("    * Publicações encontradas, coletando informações")
            
            for result in api_results['organic_results']:
                #print(result)
                resultDict = {}
                
                
                resultDict['grupo_id'] = identifier
                resultDict['ano'] = ano
                resultDict['query'] = query
                resultDict['title'] = result['title']
                resultDict['link'] = result['link']
                
                resultado  = resultado.append(resultDict, ignore_index=True)
        else:
            print("    * Publicações não encontradas")
            resultDict['grupo_id'] = identifier
            resultDict['ano'] = ano
            resultDict['query'] = query
            resultDict['title'] = api_results['error']
            
            print("Erro: {}".format(api_results['error']))
            
            resultado  = resultado.append(resultDict, ignore_index=True)

resultado.to_csv("resultado_coleta.csv", index = False)
