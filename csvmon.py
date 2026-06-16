import pandas as pd


jsola = pd.read_json('poke.json')
csvola = pd.read_csv('sprite_source.csv', header=None)

#print(csvola.loc[0])
#print(jsola.loc[0])

array = []

data = {}

for it in range(1, 649):
    csvola.loc[it][1] = jsola.loc[it-1][1]

for it in range(1, len(csvola)):
    data[str(csvola.loc[it][0])] = {
        "name": csvola.loc[it][1],
        "sprite": f'{str(csvola.loc[it][0])}_{str(csvola.loc[it][1]).lower()}.png',
        "sprite_shiny":f'{str(csvola.loc[it][0])}_{str(csvola.loc[it][1]).lower()}_s.png'
    }

df_data = pd.DataFrame(data)

#df_data.to_csv('poke_sprite_data.csv')
df_data.to_json('poke_sprite_data.json')