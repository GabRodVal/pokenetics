import os
from random import randint, choices, sample, uniform, seed
import math
import matplotlib.pyplot as plt
import numpy as np
import imageio.v3 as imio
import imageio
from PIL import Image, ImageFile, ImageOps
ImageFile.LOAD_TRUNCATED_IMAGES = True
import datetime
import itertools
from enum import Enum
from statistics import mean
import keyboard

import classes.party

debug = False
seed(25696969)

# Add easy shiny
# Add Visual Crossover
class CrossoverType(Enum):
    #   Métodos de Crossover
    ##  Mesh - Métodos que mesclam pixels
    ### Mescla pixels com alfa > 0, se não, troca pelo pixel visivel
    MESH_ESSENTIAL = 'mesh_essential'
    ### Mescla todos os pixels
    MESH_FULL = 'mesh_full'
    ### Mescla as cores
    MESH_COLOR = 'mesh_color'
    ### Mescla pixels de acordo com o pokemon alvo
    MESH_SMART = 'mesh_smart'
    ### Pra cada crossover, seleciona um metodo Mesh aleatorio.
    MESH_ALL = 'mesh_all'
    ##  Swap - Métodos que trocam pixels
    ### Parte ambos os pokemon ao meio e junta as partes diferentes
    SWAP_BISECT = 'bisect'
    ### Converte em binário e troca os bits
    SWAP_BINARY = 'binary'
    ### Troca pixels aleatoriamente
    SWAP_SIMPLE = 'swap_simple'
    ### Troca um pixel sim, um pixel não
    SWAP_EVEN = 'swap_even'
    ### Troca pixels de acordo com o pokemon alvoAdd commentMore actions
    SWAP_CHEATING = 'swap_sensible'
    ### Troca varios pixels em sequencia
    SWAP_SERIAL = 'swap_serial'
    ### Pra cada crossover, seleciona um metodo Swap aleatorio.
    SWAP_SMART = 'swap_smart'
    ### Pra cada crossover, seleciona um metodo Mesh aleatorio, exceto swap_sensible
    SWAP_DUMB = 'swap_dumb'
    ### Troca as cores dos pokemon
    SWAP_COLOR = 'swap_colors'
    ## Extras
    ### Pra cada crossover, seleciona um metodo aleatorio, com exceção de swap_sensible e mesh_smart
    CHAOTIC = 'chaotic_dumb'
    ### Seleciona entre swap_sensible e mesh_smart
    SMART = 'smart_only'
    ### Pra cada crossover, seleciona um metodo aleatorio.
    ALL_IN = 'chaotic_smart'
    ### Usa os métodos relacionados a cores.
    COLORFUL = 'color_all'
    ### Pra cada crossover, seleciona entre uma lista customizada de métodos para realizar.
    CUSTOM = 'custom'

# Botar essa porra num arduino e fazer um bot de bluesky
# Seriously my dude, cut out with the loops
class PokeGenetics():

    def __init__(
            self,
            target_dex,
            generation=9,
            pop_size=40,
            mutation_rate=0.05,
            crossover_rate=0.6,
            max_gen=100,
            score_type='RGBA',
            auto_reg=False,
            reg_pop=False,
            elitism=True,
            elitism_mutation=False,
            crossover_type=[
                'mesh_essential',
                'bisect',
                'swap_simple',
                'swap_channels',
                'swap_binary',
                'contrast',
                'mesh_mini'
                ],
            fitness_type='normalize',
            regulate_type='none',
            elitism_rate=0.05,
            easy_shiny=False,
            verbose=True,
            save_all_imgs=True,
            serial_experiment=False,
            serial_label=0
            ):
        
        self.party = classes.party.Party(
            target_dex=target_dex,
            easy_shiny=easy_shiny,
            generation=generation,
            pop_size=pop_size,
            crossover_rate=crossover_rate,
            crossover_type=crossover_type,
            mutation_rate=mutation_rate,
            elitism=elitism,
            elitism_rate=elitism_rate,
            max_gen=max_gen,
            score_type=score_type,
            reg_pop=reg_pop,
            elitism_mutation=elitism_mutation,
            auto_regulate=auto_reg,
            regulate_type=regulate_type,
            fitness_type=fitness_type,
            save_all_imgs=save_all_imgs
            )

        # Auto Reg
        self.regulate_type=regulate_type
        self.auto_regulate = auto_reg
        self.reg_pop = reg_pop
        
        # Generation
        self.generation = generation
        #For Statistics
        self.cur_gen = 0
        self.h_scores = []
        self.cross_values = []
        self.mut_values = []
        self.pop_values = []
        self.elt_values = []
        self.time_values = []
        self.fitness_values = []
        self.score_values = []
        self.first_stamp = 0
        self.old_stamp = 0
        self.cur_stamp = 0
        self.first_score = 0
        self.old_score = 0
        self.cur_score = 0
        self.top_league = []
        self.base_dir = ''
        self.easy_shiny = easy_shiny
        self.no_change_turns = 0
        self.no_change_total = 0
        self.no_change_max = 0

        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.max_gen = max_gen
        self.elitism = elitism
        self.elitism_mutation = elitism_mutation
        self.fitness_type = fitness_type
        self.elitism_rate = elitism_rate
        self.score_type = score_type
        self.crossover_type = crossover_type
        
        self.verbose = verbose
        self.save_all_imgs = save_all_imgs
        self.serial_experiment = serial_experiment
        self.serial_label = serial_label


    def set_params(self):
        pass

    def set_target(self):
        pass

    # add 1.5x mutation for when there was no change since last gen/ x1.01 for stagnant gen
    # oooorrrrr create a entire new regulate_self which is adaptive
    # regulate fitness

    # Add fitness plot, and figure out the little window
    def register_stats(self):

        most_fit_mon = self.party.get_elite_pokemon()
        target_mon = self.party.get_target_pokemon()
        lab=''
        
        if self.serial_experiment:
            lab = f'[SE{self.serial_label:02d}] '

        self.cur_score = int(most_fit_mon[1])
        self.cur_stamp = datetime.datetime.now().timestamp()

        stats = self.party.get_stats()

        if self.cur_score == self.old_score:
            self.no_change_turns += 1
            self.no_change_total += 1
            if self.no_change_turns > self.no_change_max:
                self.no_change_max = self.no_change_turns
        else:
            self.no_change_turns = 0
        
        self.party.set_fitness_no_progress(self.no_change_turns, self.cur_gen)
        if self.verbose:
            print(f'\n\033[0m')
            if self.cur_gen == 1:
                self.first_stamp = datetime.datetime.now().timestamp()
                self.old_score = self.cur_score
                print(f'\nCruzamento Iniciado - Alvo: {target_mon[1]} ({target_mon[0]}) | Pontuação: {(target_mon[3])}pts | {self.fitness_type} | EM:{self.elitism_mutation}{self.auto_regulate*f' | Auto:{self.auto_regulate} | Regulate: {self.regulate_type}'}\n')
                print(f'{lab}{1:03d}° Gen - Valor Inicial: { (((self.cur_score - self.first_score)/(target_mon[3] - self.first_score)) * 100):.2f}% = 0.00% | {(self.cur_score)}pts | {self.pop_size} Mons | {self.max_gen} Gens | 0.0s -> {(self.cur_stamp - self.first_stamp):.1f}s')
            else:
                if self.cur_score > self.old_score:
                    print(f'\033[92m{lab}{self.cur_gen:03d}° Gen - Resultado: { (((self.cur_score - self.first_score)/(target_mon[3] - self.first_score)) * 100):.2f}% ({((self.cur_score/target_mon[3]) * 100):.3f}%) | {(self.cur_score)}pts (+{((self.cur_score - self.old_score)):06d}pts) -> ({(target_mon[3]-self.cur_score)}pts/{(target_mon[3]-self.first_score)}pts) | {(self.cur_stamp - self.old_stamp):.1f}s -> {(self.cur_stamp - self.first_stamp):.1f}s')
                elif self.cur_score < self.old_score:
                    print(f'\033[91m{lab}{self.cur_gen:03d}° Gen - Resultado: { (((self.cur_score - self.first_score)/(target_mon[3] - self.first_score)) * 100):.2f}% ({((self.cur_score/target_mon[3]) * 100):.3f}%) | {(self.cur_score)}pts (-{(abs(self.cur_score - self.old_score)):06d}pts) -> ({(target_mon[3]-self.cur_score)}pts/{(target_mon[3]-self.first_score)}pts) | {(self.cur_stamp - self.old_stamp):.1f}s -> {(self.cur_stamp - self.first_stamp):.1f}s')
                else:
                    print(f'\033[93m{lab}{self.cur_gen:03d}° Gen - Resultado: { (((self.cur_score - self.first_score)/(target_mon[3] - self.first_score)) * 100):.2f}% ({((self.cur_score/target_mon[3]) * 100):.3f}%) | {(self.cur_score)}pts (={(abs(self.cur_score - self.old_score)):06d}pts) -> ({(target_mon[3]-self.cur_score)}pts/{(target_mon[3]-self.first_score)}pts) | {(self.cur_stamp - self.old_stamp):.1f}s -> {(self.cur_stamp - self.first_stamp):.1f}s')

        if self.verbose: print(f'{max(len(str(self.cur_gen)), 3) * ' '}      - CoR: {stats[1] * 100:.2f}% | Mut: {stats[2] * 100:.2f}% | Elt: {stats[3] * 100:.2f}% | Pop: {stats[0]}')
        if self.verbose: print(f'{max(len(str(self.cur_gen)), 3) * ' '}      - Rodadas sem mudança: {self.no_change_turns} (Max. {self.no_change_max}) | Tot. {self.no_change_total}')

        self.h_scores.append(((self.cur_score/target_mon[3]) * 100))        
        if self.cur_gen == 1:
            self.first_score = self.cur_score
        else:
            self.score_values.append(self.cur_score - self.old_score)

        self.old_score = self.cur_score

        self.pop_values.append(stats[0])
        self.cross_values.append(stats[1] * 100)
        self.mut_values.append(stats[2] * 100)
        self.elt_values.append(stats[3] * 100)
        self.fitness_values.append(stats[4])
        self.time_values.append(self.cur_stamp - self.old_stamp)
        self.old_stamp = self.cur_stamp
        #self.fitness_values.append(self.fitness_rate)

        if len(self.top_league) < 1:
            self.top_league.append(most_fit_mon)
        elif abs(most_fit_mon[1] - self.top_league[len(self.top_league)-1][1]) > (target_mon[3])/10000:
            self.top_league.append(most_fit_mon)
        if len(self.top_league) > 1000:
                self.top_league = self.top_league[:500] + self.top_league[-500:]

    def hall_of_fame(self):
        top_gif = []
        for iter in range(len(self.top_league)):
            imio.imwrite(f'{self.base_dir}/best/{iter+1}_s{self.top_league[iter][1]}.png', self.top_league[iter][0])

            champ_img = np.array(self.top_league[iter][0])
            mk = champ_img[:, :, 3] == 0
            champ_img[mk] =[255,255,255,255]
            mk2 = champ_img[:, :, 3] < 255
            champ_img[mk2, 3] = 255

            champ_img = Image.fromarray(champ_img).resize((480, 480), Image.Resampling.NEAREST)

            if iter == 0 or iter == (len(self.top_league)-1):
                for _ in itertools.repeat(None, max(min(10, math.ceil(len(self.top_league)/20)), 8)):
                    top_gif.append(champ_img)
            else:
                top_gif.append(champ_img)

        imageio.mimsave(f'{self.base_dir}/best/best_mon.gif', top_gif, format='GIF', duration=80, loop=0)
    
    
    
    # Add a post 99 graph, and maybe something else with it by side (total points per gen?)
    def plot_progress(self):
        target_mon = self.party.get_target_pokemon()
        
        plt.figure(figsize=(24, 18))
        
        # Return EM not, add others too
        # make elitism 0 if turned off/ make it regulate only when turned on
        plt.suptitle(f"{target_mon[0]} - {target_mon[1]} | {self.pop_size} | elt_mut: {self.elitism_mutation} | {self.regulate_type}", weight=600, size='xx-large' )

        main_fig = plt.subplot2grid(shape=(12,16), loc=(0, 0), colspan=10, rowspan=10)
        scr_h1_fig = plt.subplot2grid(shape=(12,16), loc=(10, 0), colspan=5, rowspan=2)
        scr_h2_fig = plt.subplot2grid(shape=(12,16), loc=(10, 5), colspan=5, rowspan=2)
        pop_fig = plt.subplot2grid(shape=(12,16), loc=(0, 10), colspan=6, rowspan=2)
        cross_fig = plt.subplot2grid(shape=(12,16), loc=(2, 10), colspan=6, rowspan=2)
        elt_fig = plt.subplot2grid(shape=(12,16), loc=(4, 10), colspan=6, rowspan=2)
        fit_fig = plt.subplot2grid(shape=(12,16), loc=(6, 10), colspan=6, rowspan=2)
        mut_fig = plt.subplot2grid(shape=(12,16), loc=(8, 10), colspan=6, rowspan=2)
        time_fig = plt.subplot2grid(shape=(12,16), loc=(10, 10), colspan=6, rowspan=2)

        plt_fig = target_mon[2]
        mk = plt_fig[:, :, 3] == 0
        plt_fig[mk] = [255,255,255,255]
        plt_fig[:, :, 3] = 64

        main_fig.set_ylabel("Precision Score")
        main_fig.set_xlabel(f"Generation - Avg {mean(self.h_scores):.1f}")
        main_fig.imshow(plt_fig, aspect='auto',extent=[-(len(self.h_scores)/100), len(self.h_scores)-1, min(self.h_scores)-0.1, max(self.h_scores)+0.1])
        main_fig.grid()
        main_fig.plot(self.h_scores, '#6a329f', label='score', linewidth=1.6)

        scr_h1_fig.set_title("H1")
        scr_h1_fig.grid()
        scr_h1_fig.plot(self.score_values[:min(math.floor(len(self.score_values)/2), 360)], '#20124d', label='score_h1', linewidth=1)

        scr_h2_fig.set_title("H2")
        scr_h2_fig.grid()
        scr_h2_fig.plot(self.score_values[-max(math.floor(len(self.score_values)/2), (len(self.score_values)-360)):], '#20124d', label='score_h2', linewidth=1)

        pop_fig.set_title(f"Population Size - Avg {mean(self.pop_values):.1f}")
        pop_fig.grid()
        pop_fig.plot(self.pop_values, '#0b5394', label='pop_size', linewidth=0.8)

        cross_fig.set_title(f"Crossover Rate - Avg {mean(self.cross_values):.2f}%")
        cross_fig.grid()
        cross_fig.plot(self.cross_values, '#f44336', label='crossover_rate', linewidth=0.8)

        elt_fig.set_title(f"Elitism Rate - Avg {mean(self.elt_values):.2f}%")
        elt_fig.grid()
        elt_fig.plot(self.elt_values, '#36a4bc', label='elt_rate', linewidth=0.8)

        fit_fig.set_title(f"Max Fitness - Avg {mean(self.fitness_values):.1f}")
        fit_fig.grid()
        fit_fig.plot(self.fitness_values, '#a64d79', label='max_fitness', linewidth=0.8)

        mut_fig.set_title(f"Mutation Rate - Avg {mean(self.mut_values):.2f}%")
        mut_fig.grid()
        mut_fig.plot(self.mut_values, '#34e301', label='mut_rate', linewidth=0.8)

        time_fig.set_title(f"Time p. Gen - Avg {mean(self.time_values):.2f}s")
        time_fig.grid()
        time_fig.plot(self.time_values, '#f1c232', label='mut_rate', linewidth=0.8)
        
        
        plt.tight_layout()

        plt.savefig(f'{self.base_dir}/progress.jpg', dpi=300)
        
        #plt.show()

    def get_run_stats(self):
        target = self.party.get_target_pokemon()
        return {
            'target':f'[{target[0]}] - {target[1]}',
            'score': f'{self.score_type} - {self.first_score}->{self.cur_score} | {self.h_scores.pop():.4f}%',
            'generation': self.generation,
            'time':f'{(self.cur_stamp - self.first_stamp)} | avg {((self.cur_stamp - self.first_stamp)/self.cur_gen):.4f}',
            'gens': f'{self.cur_gen}/{self.max_gen}',
            'population':f'{self.pop_size} | avg {mean(self.pop_values):.4f} | tot {mean(self.pop_values) * self.cur_gen}',
            'crossover': f'{self.crossover_rate}|avg {mean(self.cross_values):.4f}\n        {self.crossover_type}',
            'mutation': f'{self.mutation_rate} | avg {mean(self.mut_values):.4f}',
            'elitism': f'on: {self.elitism} | mut:{self.elitism_mutation} - {self.elitism_rate}',
            'fitness': f'{self.fitness_type} | avg {mean(self.fitness_values)}',
            'stat_reg': f'on:{self.auto_regulate} | pop:{self.reg_pop} | {self.regulate_type}',
            'easy_shiny': f'on:{self.easy_shiny}',
            'img_gen': f'on:{self.save_all_imgs}'
            }
        
        

    def create_dir(self, cur_dir):
        try:
            os.makedirs(f'{cur_dir}')
        except Exception as e:
            print(f"An error occurred: {e}")


    def run(self):
        ###self.initial_population()
        ###self.aval_target()

        self.quit_loop = False
        
        def break_loop():
            print(f'------- Loop padrão cancelado. Abortando gerações restantes. Prosseguindo para o resultado final -------')
            self.quit_loop = True

        keyboard.add_hotkey('ctrl+q', break_loop, suppress=True, trigger_on_release=True)

        self.first_stamp = datetime.datetime.now().timestamp()
        self.old_stamp = self.first_stamp
        target_mon = self.party.get_target_pokemon()

        self.base_dir = f'runs/{str(self.first_stamp)[:7]}-{str(self.first_stamp)[-7:]}-{target_mon[1]}-{self.score_type}-{f'G{self.generation}'}-{self.crossover_type[0]}-{'pp-' * (len(self.crossover_type)>=2)}p{self.pop_size}g{self.max_gen}'
        self.party.set_base_dir(self.base_dir)

        self.create_dir(cur_dir=self.base_dir)
        self.create_dir(f'{self.base_dir}/best')



        ############################################
        self.party.initial_population()
        self.party.score_party()
        self.cur_gen = self.party.get_cur_gen()
        self.register_stats()

        for _ in range(self.max_gen):
            if self.save_all_imgs: self.create_dir(cur_dir=f'{self.base_dir}/gen_{self.cur_gen}')
            
            if (self.cur_score/target_mon[3]) > 0.985:
                self.quit_loop = True
            if self.quit_loop:
                break
            
            self.party.apply_fitness()
            self.party.populate_new_gen()
            self.party.score_party()
            self.cur_gen = self.party.get_cur_gen()
            self.register_stats()
            

            if self.auto_regulate:
                self.party.regulate_self()

            
        self.hall_of_fame()
        if self.verbose: print(f'\nResultado Final: {((self.cur_score/target_mon[3]) * 100):.4f}% | {self.first_score}pts -> {self.cur_score}pts | {(self.cur_stamp - self.first_stamp):.1f}s, {((self.cur_stamp - self.first_stamp)/self.cur_gen):.3f}s por Gen\n')

        self.plot_progress()

        return self.get_run_stats()

    

        
#CPU THINGIES
'''

    #isso aqui é tudo de python 2.7
    from multiprocessing import Pool, cpu_count
    import math
    import psutil
    import os

    def f(i):
        return math.sqrt(i)

    def limit_cpu():
        "is called at every process start"
        p = psutil.Process(os.getpid())
        # set to lowest priority, this is windows only, on Unix use ps.nice(19)
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

    if __name__ == '__main__':
        # start "number of cores" processes
        pool = Pool(None, limit_cpu)
        for p in pool.imap(f, range(10**8)):
            pass

    #pool = Pool(max(cpu_count()//2, 1))

    #from time import sleep

    #def f(i):
    #    sleep(0.01)
    #    return math.sqrt(i)
'''
def main():
    
    poke_gen = PokeGenetics(
        # Número da Dex do Pokémon alvo, único parametro não opcional
        target_dex="159",
        # Qual set de sprites será utilizado, atualmente apenas 1 -> (56x56, 151 sprites) e 9-> (96x96, 1100+ sprites)
        generation=2,
        # Tamanho padrão da população
        pop_size=32,
        # Chance de acontecer mutação pra cada membro da nova geração (ignora elitismo)
        mutation_rate=0.05,
        # Porcentagem da população a ser povoada por crossover
        crossover_rate=0.667,
        # Geração máxima
        max_gen=10000, 
        # Tipo de avaliação usada (atualmente RGBA e Grayscale)
        score_type='Border',
        #score_type='Grayscale',
        #score_type='perfect',
        # Regulação automatica dos valores crossover_rate, mutation_rate e elitism_rate.
        auto_reg=False,
        # Tipo de regulação automatica, entre Standard, Wave, Chaotic e None
        regulate_type='wave',
        # Se a regulação automática, quando ativada, deveria alterar o tamanho da população
        reg_pop=False,
        # Se os melhores da geração passada deveriam ser transferidos para a nova geração
        elitism=True,
        # Habilita a chance de elitismo acontecer com Pokémon inseridos por elitismo
        elitism_mutation=False,
        # Porcentagem da população a ser preenchida por elitismo
        elitism_rate=0.08,
        # Tipo de crossover
        #spc
        #crossover_type=['swap_sensible'],
        #strong
        crossover_type=['swap_binary', 'bisect', 'swap_simple', 'swap_serial', 'swap_channels', 'contrast', 'mesh_essential', 'mesh_mini','mesh_subtract'],
        #all
        #crossover_type=['mesh_essential', 'bisect', 'multisect', 'swap_simple', 'swap_serial', 'swap_colors','swap_channels', 'swap_even', 'swap_binary', 'dark_n_light', 'contrast', 'mesh_mini', 'checker_stack', 'swap_squared', 'mesh_subtract'],
        # Tipo de fitness a seguir
        #fitness_type='adaptible_learner',
        fitness_type='cos_progressive',
        # Salva imagens de todas as populações geradas em 'runs'
        save_all_imgs=True,
        # Faz shinys serem faceis de achar
        easy_shiny=True
        )
    
    jooj = poke_gen.run()
    
    print(jooj)
    
    '''run_experiment(target_dex=["151"],
                   generations=[1,2,9],
                   pop_size=[50],
                   fitness_type=['normalize', 'cos2', 'sin_half'],
                   crossover_type=[['swap_binary', 'bisect', 'swap_simple', 'swap_serial', 'swap_channels', 'contrast', 'mesh_essential', 'mesh_mini','mesh_subtract']],
                   score_type=['RGBA'],
                   max_gen=[200])'''
    
    #run_experiment(target_dex=['244'], generations=[2,9], score_type=['RGBA', 'Grayscale', 'Binary', 'Perfect'])
    '''crossovers_to_test = [
        ['swap_sensible'],
        ['no_cross'],
        ['mesh_essential'],
        ['bisect'],
        ['multisect'],
        ['swap_simple'],
        ['swap_serial'],
        ['swap_colors'],
        ['swap_channels'],
        ['swap_even'],
        ['swap_binary'],
        ['dark_n_light'],
        ['contrast'],
        ['mesh_mini'],
        ['checker_stack'],
        ['swap_squared'],
        ['mesh_subtract'],
        ['mesh_essential', 'bisect', 'multisect', 'swap_simple', 'swap_serial', 'swap_colors','swap_channels', 'swap_even', 'swap_binary', 'dark_n_light', 'contrast', 'mesh_mini', 'checker_stack', 'swap_squared', 'mesh_subtract']
        ]'''




def run_experiment(
    target_dex=['001'],
    generations=[9],
    pop_size=[100],
    max_gen=[100],
    crossover_type=[
                'mesh_essential',
                'bisect',
                'swap_simple',
                'swap_channels',
                'swap_binary',
                'contrast',
                'mesh_mini'
                ],
    regulate_type=['none'],
    elitism=[True],
    fitness_type=['normalize'],
    elitism_mutation=[False],
    save_imgs=[False],
    score_type=['RGBA']):
    
    lab = 0
    
    relat = open(f'EXP-{len(target_dex)}.{target_dex[0]}_{len(score_type)}.{score_type[0]}_{len(crossover_type)}.{crossover_type[0]}.txt', 'w')    
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
                                                    elitism=g,
                                                    elitism_mutation=h,
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
    
    
    
    
#pity - anti-elitism/anti-fitness rate
#luck - no fitness rate
#elitism -- when long

# elitism = 8%
# total crossover = 72%
# pity = 8%
# luck = 16%
# crossover = luck rate + pity rate + std rate 
# std crossover = 72% - (8% + 16%) = 72 % - 24% = 48%
# population = 48% + 24% + 8% = 80% + 20%
# insertion = 20%


if __name__ == '__main__':

    #['RGBA', 'Grayscale', 'Binary']
    main()