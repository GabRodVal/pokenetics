from pokegenetics import PokeGenetics

def run_experiment(
    target_dex=['001'],
    generations=['9'],
    pop_size=[100],
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
    fitness_type=['normalize'],
    elitism_mutation=[False],
    save_imgs=[False],
    score_type=['RGBA']):
    
    lab = 0
    
    relat = open(f'EXP-{len(target_dex)}.{target_dex[0]}_{len(score_type)}.{score_type[0]}_{len(crossover_type)}.{crossover_type[0][0]}.txt', 'a')    
    for a in target_dex:
        relat.write(f'\n ------- | #{a} | -------\n')
        for b in generations:
            relat.write(f' ------- | [G{b}] | -------\n')
            for c in pop_size:
                for d in max_gen:
                    for e in crossover_type:
                        relat.write(f' =====\n')
                        relat.write(f' {e}\n')
                        relat.write(f' =====\n')
                        for f in regulate_type:
                            for g in elitism:
                                for h in elitism_mutation:
                                    for i in save_imgs:
                                        for j in score_type:
                                            for k in fitness_type:
                                                
                                                lab += 1
                                                
                                                relat.write(f' FIT: [{k}] -------\n')
                                                pg = PokeGenetics(
                                                    target_dex=a,
                                                    generation=b,
                                                    pop_size=c,
                                                    max_gen=d,
                                                    auto_reg=(f != 'none'),
                                                    fitness_type=k,
                                                    regulate_type=f,
                                                    reg_pop=True,
                                                    elitism=g,
                                                    pity=True,
                                                    elitism_mutation=h,
                                                    elitism_rate=0.12,
                                                    score_type=j,
                                                    crossover_type=e,
                                                    save_all_imgs=i,
                                                    serial_experiment=True,
                                                    serial_label=lab
                                                    )
                                                result = pg.run()
                                                
                                                relat.write(f'\n{result['target']}')
                                                relat.write('\n    ')
                                                relat.write(f'Pontuacao => {result['score']}')
                                                relat.write('\n    ')
                                                relat.write(f'Geracao => {result['generation']}')
                                                relat.write('\n    ')
                                                relat.write(f'Tempo => {result['time']}')
                                                relat.write('\n    ')
                                                relat.write(f'Iteracoes=> {result['gens']}')
                                                relat.write('\n    ')
                                                relat.write(f'Populacao => {result['population']}')
                                                relat.write('\n    ')
                                                relat.write(f'CrossOver => {result['crossover']}')
                                                relat.write('\n    ')
                                                relat.write(f'Mutacao => {result['mutation']}')
                                                relat.write('\n    ')
                                                relat.write(f'Elitismo => {result['elitism']}')
                                                relat.write('\n    ')
                                                relat.write(f'Aptidao => {result['fitness']}')
                                                relat.write('\n    ')
                                                relat.write(f'Auto-Regulacao => {result['stat_reg']}')
                                                relat.write('\n    ')
                                                relat.write(f'Easy Shiny => {result['easy_shiny']}')
                                                relat.write('\n    ')
                                                relat.write(f'Salvamento de Imagens => {result['img_gen']}')
                                                relat.write('\n\n\n')
        
    relat.write('END')
    relat.close
    

def main():
    run_experiment(target_dex=["244"],
                   generations=['icon'],
                   pop_size=[32], #1000
                   crossover_type=[['swap_binary']],
                   #crossover_type=[['mix_essential', 'bisect','swap_colors','swap_channels', 'dark_n_light', 'contrast', 'mix_mini', 'swap_squared', 'mix_subtract','swap_chunks','difference']],
                   #crossover_type=[['swap_simple', 'swap_serial', 'mix_essential', 'bisect','swap_colors','swap_channels', 'dark_n_light', 'contrast', 'mix_mini', 'swap_squared', 'mix_subtract','swap_chunks','difference']],
                   #score_type=['BW']
                   score_type=['Grayscale', 'BW','weighted_perfect_borders_only_hard_posterize','multiple','harsh_perfect'],
                   #score_type=['RGBA', 'Perfect', 'Semiperfect', 'Posterize', 'semiperfect_posterize'],
                   #score_type=['semiperfect', 'posterize', 'semiperfect_posterize', 'semiperfect_posterize_weighted', 'semiperfect_posterize_weighted_borders'],
                   #score_type=['semiperfect_posterize_weighted_borders'],
                   #score_type=['weighted_perfect_borders_only_hard_posterize'],
                   fitness_type=['adaptable_learner'],#cos_progressive
                   #fitness_type=['cos_progressive'],
                   elitism_mutation=[True],
                   regulate_type=['wave'],
                   max_gen=[40000]) #1000
    
if __name__ == '__main__':

    main()