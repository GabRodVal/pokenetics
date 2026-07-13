from pokegenetics import PokeGenetics
import pandas as pd
import csv
import cupy as cp
from classes.crossover import CrossoverType

def run_experiment(
    target_dex=['001'],
    generations=['9'],
    pop_size=[32],
    max_gen=[100],
    crossover_type=[
                'mix_essential',
                'bisect',
                'swap_simple',
                'swap_channels',
                'swap_binary',
                'contrast',
                'mix_mini'
                ],
    regulate_type=['none'],
    elitism=[True],
    elitism_interval=[0],
    fitness_type=['normalize'],
    elitism_mutation=[False],
    save_imgs=[False],
    score_type=['RGBA']):
    
    lab = 0
    
    
        
    
    for a in target_dex:
        for b in generations:
            for c in pop_size:
                for d in max_gen:
                    for e in crossover_type:
                        for fi in regulate_type:
                            for g in elitism:
                                for h in elitism_mutation:
                                    for i in save_imgs:
                                        for j in score_type:
                                            for k in fitness_type:
                                                for e_i in elitism_interval:
                                                
                                                    lab += 1
                                                    
                                                    #relat.write(f' FIT: [{k}] -------\n')
                                                    pg = PokeGenetics(
                                                        target_dex=a,
                                                        generation=b,
                                                        pop_size=c,
                                                        max_gen=d,
                                                        auto_reg=(fi != 'none'),
                                                        fitness_type=k,
                                                        regulate_type=fi,
                                                        reg_pop=False,
                                                        elitism=g,
                                                        elitism_interval=e_i,
                                                        pity=True,
                                                        elitism_mutation=h,
                                                        crossover_rate=0.625,
                                                        perseverance_rate=0.1875,
                                                        mutation_rate=0.08,
                                                        elitism_rate=0.03125,
                                                        score_type=j,
                                                        crossover_type=e,
                                                        save_all_imgs=i,
                                                        serial_experiment=True,
                                                        serial_label=lab,
                                                        easy_shiny=True,
                                                        posterize=False,
                                                        posterize_hard=False
                                                        )
                                                    
                                                    result = pg.run()
                                                    with open('pk_serial_experiments.csv', mode='a', newline='') as file:
                                                        writer = csv.writer(file,csv.QUOTE_ALL)
                                                        writer.writerow(result.keys())
                                                        writer.writerow(result.values()) 
                                                        file.close()
                                                

                                                
                                                
                                                
        

    

def main():
    run_experiment(target_dex=["472"],
                   generations=['9'],
                   pop_size=[512],
                   crossover_type=[CrossoverType.ESSENTIALS.value],#['swap_borders']#, CrossoverType.BLEND.value],
                   score_type=['rgba'],#'RGBA'],#'rgb_colour_distance'],#'Delta_E_2000'],#'Delta_E_Threshold','posterbin', 'Distance'],
                   #fitness_type=['cos_progressive','normalize','cos_sin_log_progressive','adaptable_learner'],
                   fitness_type=['adaptable_learner'],
                   elitism_mutation=[True],
                   elitism_interval=[0],
                   regulate_type=['none'],
                   max_gen=[30_000],
                   save_imgs=[False])#_000]) #1000
    
if __name__ == '__main__':

    main()