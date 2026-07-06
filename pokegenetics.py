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
import classes.utils as utils

debug = False
seed(25696969)

# Add easy shiny
# Add Visual Crossover
class CrossoverType(Enum):
    #   Métodos de Crossover
    ##  Mix - Métodos que mesclam pixels
    ### Mescla pixels com alfa > 0, se não, troca pelo pixel visivel
    MIX_ESSENTIAL = 'mix_essential'
    ### Mescla todos os pixels
    MIX_FULL = 'mix_full'
    ### Mescla as cores
    MIX_COLOR = 'mix_color'
    ### Mescla pixels de acordo com o pokemon alvo
    MIX_SMART = 'mix_smart'
    ### Pra cada crossover, seleciona um metodo Mix aleatorio.
    MIX_ALL = 'mix_all'
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
    SWAP_CHEATING = 'swap_cheater_rgba'
    ### Troca varios pixels em sequencia
    SWAP_SERIAL = 'swap_serial'
    ### Pra cada crossover, seleciona um metodo Swap aleatorio.
    SWAP_SMART = 'swap_smart'
    ### Pra cada crossover, seleciona um metodo Mix aleatorio, exceto swap_cheater_rgba
    SWAP_DUMB = 'swap_dumb'
    ### Troca as cores dos pokemon
    SWAP_COLOR = 'swap_colors'
    ## Extras
    ### Pra cada crossover, seleciona um metodo aleatorio, com exceção de swap_cheater_rgba e mix_smart
    CHAOTIC = 'chaotic_dumb'
    ### Seleciona entre swap_cheater_rgba e mix_smart
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
            generation='9',
            pop_size=40,
            mutation_rate=0.08,
            crossover_rate=0.64,
            max_gen=100,
            score_type='RGBA',
            auto_reg=False,
            reg_pop=False,
            elitism=True,
            pity=False,
            elitism_mutation=False,
            elitism_interval=0,
            elite_couple=False,
            crossover_type=[
                'mix_essential',
                'bisect',
                'swap_simple',
                'swap_channels',
                'swap_binary',
                'contrast',
                'mix_mini'
                ],
            fitness_type='normalize',
            regulate_type='none',
            elitism_rate=0.12,
            easy_shiny=False,
            posterize=False,
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
            pity=pity,
            elitism_rate=elitism_rate,
            elitism_interval=elitism_interval,
            elite_couple=elite_couple,
            max_gen=max_gen,
            score_type=score_type.lower(),
            reg_pop=reg_pop,
            elitism_mutation=elitism_mutation,
            auto_regulate=auto_reg,
            regulate_type=regulate_type,
            fitness_type=fitness_type,
            save_all_imgs=save_all_imgs,
            posterize=posterize
            )

        # Auto Reg
        self.regulate_type=regulate_type
        self.auto_regulate = auto_reg
        self.reg_pop = reg_pop
        
        # Generation
        self.generation = generation
        #For Statistics
        self.cur_gen = 0
        self.h_scores = []#
        self.true_scores = []#
        self.low_scores = []#
        self.cross_values = []
        self.mut_values = []
        self.pop_values = []
        self.elt_values = []
        self.time_values = []
        self.fitness_values = []
        self.score_values = []
        self.first_stamp = 0
        self.start_time = ''
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
        self.pity = pity
        self.elitism_mutation = elitism_mutation
        self.elitism_interval = elitism_interval
        self.elite_couple = elite_couple
        self.fitness_type = fitness_type
        self.elitism_rate = elitism_rate
        self.score_type = score_type.lower()
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

    def register_stats(self):

        most_fit_mon = self.party.get_elite_pokemon()
        target_mon = self.party.get_target_pokemon()
        best_mon = self.party.get_GOAT_pokemon()
        
        lab=''
        
        if self.serial_experiment:
            lab = f'[SE{self.serial_label:02d}] '

        self.cur_score = int(most_fit_mon[1])
        self.cur_stamp = datetime.datetime.now().timestamp()
        #if self.pity:
        #    least_fit_mon = self.party.get_lowest_score()
        #    self.lowest_score = float(least_fit_mon)
        #    self.low_scores.append(self.lowest_score)
            
            
        stats = self.party.get_stats()

        if self.cur_score <= self.old_score and self.cur_score <= best_mon[1]:
            self.no_change_turns += 1
            self.no_change_total += 1
            if self.no_change_turns > self.no_change_max:
                self.no_change_max = self.no_change_turns
        else:
            self.no_change_turns = 0
        
        self.party.set_fitness_no_progress(self.no_change_turns, self.cur_gen)
        if self.verbose:
            if self.cur_gen == 1:
                self.first_stamp = datetime.datetime.now().timestamp()
                self.old_score = self.cur_score
                print(f'\nCruzamento Iniciado - Alvo: {target_mon[1]} ({target_mon[0]}) | Pontuação: {(target_mon[3])}pts | {self.fitness_type} | EM:{self.elitism_mutation}{self.auto_regulate*f' | Auto:{self.auto_regulate} | Regulate: {self.regulate_type}'}\n')
                print(f'{lab}{1:03d}° Gen - Valor Inicial: { (((self.cur_score - self.first_score)/(target_mon[3] - self.first_score)) * 100):.2f}% = 0.00% | {(self.cur_score)}pts | {self.pop_size} Mons | {self.max_gen} Gens | 0.0s -> {(self.cur_stamp - self.first_stamp):.1f}s')
            else:
                if self.cur_score > self.old_score and self.cur_score > best_mon[1]:
                    print(f'\033[92m{lab}{self.cur_gen:03d}° Gen - Resultado: { (((self.cur_score - self.first_score)/(target_mon[3] - self.first_score)) * 100):.2f}% ({((self.cur_score/target_mon[3]) * 100):.3f}%) | {(self.cur_score)}pts (+{((self.cur_score - self.old_score)):06d}pts) -> ({(target_mon[3]-self.cur_score)}pts/{(target_mon[3]-self.first_score)}pts) | {(self.cur_stamp - self.old_stamp):.1f}s -> {(self.cur_stamp - self.first_stamp):.1f}s')
                elif self.cur_score < self.old_score:
                    print(f'\033[91m{lab}{self.cur_gen:03d}° Gen - Resultado: { (((self.cur_score - self.first_score)/(target_mon[3] - self.first_score)) * 100):.2f}% ({((self.cur_score/target_mon[3]) * 100):.3f}%) | {(self.cur_score)}pts (-{(abs(self.cur_score - self.old_score)):06d}pts) -> ({(target_mon[3]-self.cur_score)}pts/{(target_mon[3]-self.first_score)}pts) | {(self.cur_stamp - self.old_stamp):.1f}s -> {(self.cur_stamp - self.first_stamp):.1f}s')
                else:
                    print(f'\033[93m{lab}{self.cur_gen:03d}° Gen - Resultado: { (((self.cur_score - self.first_score)/(target_mon[3] - self.first_score)) * 100):.2f}% ({((self.cur_score/target_mon[3]) * 100):.3f}%) | {(self.cur_score)}pts (={(abs(self.cur_score - self.old_score)):06d}pts) -> ({(target_mon[3]-self.cur_score)}pts/{(target_mon[3]-self.first_score)}pts) | {(self.cur_stamp - self.old_stamp):.1f}s -> {(self.cur_stamp - self.first_stamp):.1f}s')

        t_score = self.party.get_true_score(most_fit_mon[0])
        
        if self.verbose: print(f'{max(len(str(self.cur_gen)), 3) * ' '}      - Pontuação Verdadeira: {(t_score/(255 * 3 * (target_mon[2].shape[0]) * (target_mon[2].shape[1]))) * 100:.2f}% ({t_score}pts)')
        if self.verbose: print(f'{max(len(str(self.cur_gen)), 3) * ' '}      - CoR: {stats[1] * 100:.2f}% | Mut: {stats[2] * 100:.2f}% | Elt: {stats[3] * 100:.2f}% | Pop: {stats[0]}')
        if self.verbose: print(f'{max(len(str(self.cur_gen)), 3) * ' '}      - Rodadas sem progresso: {self.no_change_turns} (Max. {self.no_change_max}) | Tot. {self.no_change_total}\033[0m')

        self.h_scores.append(((self.cur_score/target_mon[3]) * 100))
        self.true_scores.append((t_score/(255 * 3 * (target_mon[2].shape[0]) * (target_mon[2].shape[1]))) * 100)
           
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


        
        if len(self.top_league) < 1 or abs(most_fit_mon[1] - self.top_league[len(self.top_league)-1][1]) > (target_mon[3]/1200):
            factor = math.ceil(256/most_fit_mon[0].shape[0])

            self.top_league.append(most_fit_mon)
            imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}g_{(most_fit_mon[1]/target_mon[3])*100:.2f}.png', utils.resize_by_factor(most_fit_mon[0], factor)) 

            
            if self.score_type != 'Grayscale'.lower() and self.score_type != 'BW'.lower():
                most_fit_difference = utils.get_difference_sprite(target_mon[2],most_fit_mon[0])
                imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}_diff.png', utils.resize_by_factor(most_fit_difference, factor))
            
            elif self.score_type == 'Grayscale'.lower():
                most_fit_gray = utils.to_grayscale(np.copy(most_fit_mon[0]))
                imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}_gray.png', utils.resize_by_factor(most_fit_gray, factor))
                most_fit_difference = utils.get_difference_sprite(utils.to_rgba(utils.to_grayscale(np.copy(target_mon[2]))), utils.to_rgba(most_fit_gray))
                imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}_graydiff.png', utils.resize_by_factor(most_fit_difference, factor))
            
            elif self.score_type == 'BW'.lower():
                most_fit_bw = utils.to_black_n_white(np.copy(most_fit_mon[0]))
                imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}_bw.png', utils.resize_by_factor(most_fit_bw, factor))
                most_fit_difference = utils.get_difference_sprite(utils.to_rgba(utils.to_black_n_white(np.copy(target_mon[2]))), utils.to_rgba(most_fit_bw))
                imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}_bwdiff.png', utils.resize_by_factor(most_fit_difference, factor))
                
            if self.score_type == 'posterize' or self.score_type == 'semiperfect_posterize':
                most_fit_post =  utils.posterize(np.copy(most_fit_mon[0]))
                imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}_post.png', utils.resize_by_factor(most_fit_post, factor))
                most_fit_difference = utils.get_difference_sprite(utils.posterize(np.copy(target_mon[2])), most_fit_post)
                imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}_postdiff.png', utils.resize_by_factor(most_fit_difference, factor))
                
            if self.score_type == 'Binposter':
                most_fit_post =  utils.posterize_binary(np.copy(most_fit_mon[0]))
                imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}_postbin.png', utils.resize_by_factor(most_fit_post, factor))
                most_fit_difference = utils.get_difference_sprite(utils.posterize(np.copy(target_mon[2])), most_fit_post)
                imio.imwrite(f'{self.base_dir}/best/{self.cur_gen}_postbindiff.png', utils.resize_by_factor(most_fit_difference, factor))
        
        if len(self.top_league) > 1800:
                self.top_league = self.top_league[:900] + self.top_league[-900:]

    def hall_of_fame(self):
        top_gif = []
        GOAT_mon = self.party.get_GOAT_pokemon()
        target = self.party.get_target_pokemon()
        imio.imwrite(f'{self.base_dir}/DIY_{target[1]}.png', GOAT_mon[0])
        self.top_league.append(GOAT_mon)
        size_fac = math.floor(512/GOAT_mon[0].shape[0])
        for iter in range(len(self.top_league)):
        #    imio.imwrite(f'{self.base_dir}/best/{iter+1}_s{self.top_league[iter][1]}.png', self.top_league[iter][0])

            champ_img = np.array(self.top_league[iter][0])
            mk = champ_img[:, :, 3] == 0
            champ_img[mk] =[255,255,255,255]
            mk2 = champ_img[:, :, 3] < 255
            champ_img[mk2, 3] = 255

            
            champ_img = utils.resize_by_factor(champ_img, size_fac)
            champ_img = Image.fromarray(champ_img).convert("RGB")

            if iter == 0 or iter == (len(self.top_league)-1):
                for _ in itertools.repeat(None, max(min(20, math.ceil(len(self.top_league)/10)), 40)):
                    top_gif.append(champ_img)
            else:
                top_gif.append(champ_img)

        imageio.mimsave(f'{self.base_dir}/best_mon.gif', top_gif, format='GIF', duration=80, loop=0)
    
    
    
    # Add a post 99 graph, and maybe something else with it by side (total points per gen?)
    def plot_progress(self):
        target_mon = self.party.get_target_pokemon()
        fitness_list = self.party.get_fitness_list()
        
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
        main_fig.imshow(plt_fig, aspect='auto',extent=[-(len(self.h_scores)/100), len(self.h_scores)-1, min(min(self.h_scores), min(self.true_scores))-0.1, max(max(self.h_scores),max(self.true_scores))+0.1])
        main_fig.grid()
        main_fig.plot(self.h_scores, '#6a329f', label='main_score', linewidth=1.6)
        main_fig.plot(self.true_scores, '#DD0022', label='true_score', linewidth=1.4)
        #if self.pity:
        #    main_fig.plot(self.low_scores, '#EE8844', label='low_score', linewidth=1.4)

        main_fig.legend()

        scr_h1_fig.set_title("H1")
        scr_h1_fig.grid()
        scr_h1_fig.plot(self.score_values[:min(math.floor(len(self.score_values)/2), 500)], '#20124d', label='score_h1', linewidth=1)

        scr_h2_fig.set_title("H2")
        scr_h2_fig.grid()
        scr_h2_fig.plot(self.score_values[-max(math.floor(len(self.score_values)/2), (len(self.score_values)-500)):], '#20124d', label='score_h2', linewidth=1)

        pop_fig.set_title(f"Population Size - Avg {mean(self.pop_values):.1f}")
        pop_fig.grid()
        pop_fig.plot(self.pop_values, '#0b5394', label='pop_size', linewidth=0.8)

        cross_fig.set_title(f"Crossover Rate - Avg {mean(self.cross_values):.2f}%")
        cross_fig.grid()
        cross_fig.plot(self.cross_values, '#f44336', label='crossover_rate', linewidth=0.8)

        elt_fig.set_title(f"Elitism Rate - Avg {mean(self.elt_values):.2f}%")
        elt_fig.grid()
        elt_fig.plot(self.elt_values, '#36a4bc', label='elt_rate', linewidth=0.8)

        fit_fig.set_title(f"{self.fitness_type.capitalize()}")
        fit_fig.grid()
        fit_fig.plot(fitness_list, "#9c0d54", label='max_fitness', linewidth=0.8)

        mut_fig.set_title(f"Mutation Rate - Avg {mean(self.mut_values):.2f}%")
        mut_fig.grid()
        mut_fig.plot(self.mut_values, '#34e301', label='mut_rate', linewidth=0.8)

        time_fig.set_title(f"Time p. Gen - Avg {mean(self.time_values):.2f}s")
        time_fig.grid()
        time_fig.plot(self.time_values, '#f1c232', label='mut_rate', linewidth=0.8)
        
        
        plt.tight_layout()

        plt.savefig(f'{self.base_dir}/progress.jpg', dpi=300)
        
        #plt.show()


    #REWORK
    #Only stats return, no string
    def get_run_stats(self):
        target = self.party.get_target_pokemon()
        
        stat_dict = {
            'target_dex': target[0],
            'target_name': target[1],
            'target_score': target[3],
            #'target':f'[{target[0]}] - {target[1]}',
            
            'score_type':self.score_type,
            'first_score': self.first_score,
            'cur_score': self.cur_score,
            'cur_score_pct': self.h_scores.pop(),
            #'score': f'{self.score_type} - {self.first_score}->{self.cur_score} | {self.h_scores.pop():.4f}%',
            'true_score': self.true_scores.pop(),
            #
            'generation': self.generation,
            'total_time': (self.cur_stamp - self.first_stamp),
            'avg_time_p_gen': ((self.cur_stamp - self.first_stamp)/self.cur_gen),
            'start_time': self.start_time,
            'end_time': datetime.datetime.today(),
            #'time':f'{(self.cur_stamp - self.first_stamp)} | avg {((self.cur_stamp - self.first_stamp)/self.cur_gen):.4f}',
            'turns_run': self.cur_gen,
            'max_turns': self.max_gen,
            #'gens': f'{self.cur_gen}/{self.max_gen}',
            'original_population':self.pop_size,
            'average_population': mean(self.pop_values),
            #'population':f'{self.pop_size} | avg {mean(self.pop_values):.4f} | tot {mean(self.pop_values) * self.cur_gen}',
            'original_crossover_rate':self.crossover_rate,
            'average_crossover_rate':mean(self.cross_values),
            'crossover_type_s':self.crossover_type,
            #'crossover': f'{self.crossover_rate}|avg {mean(self.cross_values):.4f}\n        {self.crossover_type}',
            'original_mutation_rate':self.mutation_rate,
            'average_mutation_rate': mean(self.mut_values),
            #'mutation': f'{self.mutation_rate} | avg {mean(self.mut_values):.4f}',
            'elitism': self.elitism,
            'elitism_mutation': self.elitism_mutation,
            'original_elitism_rate': self.elitism_rate,
            'average_elitism_rate': mean(self.elt_values),
            'elitism_interval': self.elitism_interval,
            'elite_couple': self.elite_couple,
            'pity': self.pity,
            #'elitism': f'on: {self.elitism} | mut:{self.elitism_mutation} - {self.elitism_rate}',
            'fitness_type':self.fitness_type,
            #'fitness': f'{self.fitness_type} | avg {mean(self.fitness_values)}',
            'auto_regulate':self.auto_regulate,
            'auto_regulate_population': self.reg_pop,
            'auto_regulate_type':self.regulate_type,
            #'stat_reg': f'on:{self.auto_regulate} | pop:{self.reg_pop} | {self.regulate_type}',
            'easy_shiny': self.easy_shiny,
            'img_gen': self.save_all_imgs,
            'turns_without_progress': self.no_change_total,
            'max_consecutive_turns_without_progress':self.no_change_max
            }
        return stat_dict
        
    def create_dir(self, cur_dir):
        try:
            os.makedirs(f'{cur_dir}')
        except Exception as e:
            print(f"An error occurred: {e}")

    # ADD PARALLEL RUN USING THE DIFFERENCE SPRITE AS A PARAMETER
    # RESET IT EVERY X00 GENERATIONS
    # WRITE THE DAMN TABLE
    def run_parallel_population(self, target, population, fitness_type, score_type):
        pass
    
    
    def run(self):
        ###self.initial_population()
        ###self.aval_target()

        self.quit_loop = False
        
        def break_loop():
            print(f'------- Loop padrão cancelado. Abortando gerações restantes. Prosseguindo para o resultado final -------')
            self.quit_loop = True

        keyboard.add_hotkey('ctrl+q', break_loop, suppress=True, trigger_on_release=True)

        self.first_stamp = datetime.datetime.now().timestamp()
        self.start_time = datetime.datetime.fromtimestamp(self.first_stamp)
        self.old_stamp = self.first_stamp
        target_mon = self.party.get_target_pokemon()

        self.base_dir = f'runs/{(f'SE{self.serial_label:02d}-')*self.serial_experiment}{str(self.first_stamp)[2:9]}-{target_mon[1]}-{self.score_type}-{f'G{self.generation}'}-p{self.pop_size}g{self.max_gen}'
        self.party.set_base_dir(self.base_dir)

        self.create_dir(cur_dir=self.base_dir)
        self.create_dir(f'{self.base_dir}/best')



        ############################################
        self.party.create_target_ref_img()
        self.party.initial_population()
        self.party.score_party()
        self.cur_gen = self.party.get_cur_gen()
        self.register_stats()

        for _ in range(self.max_gen):
            if debug:print('Imgs gen start: OK')
            if self.save_all_imgs: self.create_dir(cur_dir=f'{self.base_dir}/gen_{self.cur_gen}')
            
            if debug:print('Imgs save_all_imgs: OK')
            if self.auto_regulate:
                self.party.regulate_self()
            
            if (self.cur_score/target_mon[3]) > 0.985 and self.score_type != 'mixed':
                self.quit_loop = True
            if self.quit_loop:
                break
            if debug:print('Break loop: OK')
            
            self.party.apply_fitness()
            if debug:print('Fitness: OK')
            self.party.populate_new_gen()
            if debug:print('Genpop: OK')
            self.party.score_party()
            if debug:print('Score: OK')
            self.cur_gen = self.party.get_cur_gen()
            self.register_stats()
            if debug:print('Reg Stats: OK')
            

            

            
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