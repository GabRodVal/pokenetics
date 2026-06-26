import pandas as pd
import json


jsola = pd.read_json('fetchList.json')
csvola = pd.read_csv('sprite_source.csv', header=0)

#print(csvola.loc[0])
#print(jsola.loc[0])

array = []

data = {}

for it in range(0, len(csvola)):
    item = {
        "DEX" : csvola.loc[it, 'DEX'],
        "Name": csvola.loc[it, 'Name'],
        "Std_source": csvola.loc[it, 'Sprite'],
        "Shiny_source": csvola.loc[it, 'Shiny Sprite'],
    }

    print(item)
    array.append(item)

    #jsola[0].loc[it,'Name'] = csvola.loc[it, 'Name']
    #array.append(csvola.loc[it])

with open('fetchListCor.json', 'w') as f:
    json.dump(array, f)
#df_data = pd.DataFrame(array)

#df_data.to_csv('sprite_source_cor.csv', index=False)

#csvola.to_csv('sprite_source_cor.csv',index=False)
#jsola.to_json('fetchList_cor.json', index=False)
#df_data.to_json('fetchListCor.json',)
#df_data.to_json('poke_sprite_data.json')