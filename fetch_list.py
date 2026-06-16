import pandas as pd
import json

data = pd.read_csv("sprite_source.csv")


dex = []

for i in range(len(data)):
    print(f'progress:{i}/{len(data)}')
    entry = {
        "DEX": data['DEX'].iloc[i],
        "Name": f'{i}-mon',
        "Std_source": data['Sprite'].iloc[i],
        "Shiny_source": data['Shiny Sprite'].iloc[i],
    }
    dex.append(entry)
    
    #json.dump('{',f)
    #json.dump(json.loads(f'"DEX": {data['DEX'].iloc[i]},"Name": {data['Name'].iloc[i]},"Std_source": {data['Sprite'].iloc[i]},"Shiny_source": {data['Shiny Sprite'].iloc[i]}'), f)
    #json.dump('},',f)

with open('fetchList.json', 'w') as f:
    json.dump(dex, f)