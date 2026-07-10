from random import randint, choices, sample, uniform, seed
import numpy as np
import math
import imageio.v3 as imio

import classes.pokedex as pokedex
import classes.mutation as mutation
import classes.crossover as crossover
import classes.fitness as fitness
import classes.utils as utils

debug = True

class Party():
    def __init__(
            self,
            target_dex,
            easy_shiny=False,
            generation='9',
            pop_size=40,
            crossover_rate=0.72,
            mutation_rate=0.02,
            perseverance_rate=0.12,
            elitism_rate=0.01,
            max_gen=24,
            score_type='RGBA',
            auto_regulate=True,
            reg_pop=False,
            regulate_type='wave',
            elitism=True,
            pity=False,
            elitism_mutation=False,
            elitism_interval=0,
            elite_couple=False,
            crossover_type=['bisect', 'swap_simple', 'swap_even', 'swap_cheater_rgba', 'swap_serial', 'swap_colors'],
            fitness_type='normalize',
            verbose=False,
            save_all_imgs=True,
            posterize=False,
            posterize_hard=False
            ):
        
        self.score_type = score_type.lower()
        self.fitness_rate = pop_size

        # Pokedex
        self.pokedex = pokedex.Pokedex(target_dex=target_dex, easy_shiny=easy_shiny, score_type=self.score_type, generation=generation, posterize=posterize, posterize_hard=posterize_hard)

        self.target_dex = target_dex
        self.target_mon = self.pokedex.get_target_pokemon()

        self.crossover = crossover.Crossover(crossover_type=crossover_type, target_mon=self.target_mon)
        self.mutation = mutation.Mutation()
        self.fitness = fitness.Fitness(pop_size=pop_size, fitness_rate=self.fitness_rate, fitness_type=fitness_type)

        #team
        self.cur_gen = 0
        self.team = []
        self.fit_team = []
        #
        self.dupes = True
        #
        self.base_dir = ''
        self.elitism_interval = (elitism_interval +1)
        #
        self.og_pop_size = pop_size
        self.pop_size = pop_size
        #
        self.og_mutation_rate = mutation_rate
        self.mutation_rate = mutation_rate
        #
        self.og_crossover_rate = crossover_rate
        self.crossover_rate = crossover_rate
        #
        self.max_gen = max_gen
        #
        self.auto_regulate = auto_regulate
        self.reg_pop = reg_pop
        self.regulate_type = regulate_type
        #
        self.perserverance_rate = perseverance_rate
        #
        self.elitism = elitism
        self.pity = pity
        self.elitism_mutation = elitism_mutation
        if self.elitism:
            self.elitism_rate = elitism_rate
        else:
            self.elitism_rate = 0
        self.og_elitism_rate = self.elitism_rate
        self.best_mon = []
        self.elite_couple = elite_couple
        #
        self.fitness_rate = self.og_pop_size
        #self.fitness_list = []
        #
        self.verbose = verbose
        self.save_all_imgs = save_all_imgs

    def set_fitness_no_progress(self, val, gen):
        self.fitness.set_no_progress_gen(val=val, gen=gen)

    def get_team(self):
        return self.team
    
    def get_cur_gen(self):
        return self.cur_gen
    
    def get_stats(self):
        stats = []
        stats.append(len(self.team))
        stats.append(self.crossover_rate)
        stats.append(self.mutation_rate)
        stats.append(self.elitism_rate)
        stats.append(self.fitness_rate)

        return stats

    def set_base_dir(self, base_dir):
        self.base_dir = base_dir

    def regulate_self(self):
        if self.auto_regulate:
            if self.regulate_type == 'chaotic':
                self.regulate_self_chaotic()
            elif self.regulate_type == 'wave':
                self.regulate_self_wavering()
            else:
                self.regulate_self_standard()
        
        if (self.elitism_rate + self.crossover_rate) > 1.0:
            reg_reg = 1.0/(self.elitism_rate + self.crossover_rate)
            self.elitism_rate = self.elitism_rate * reg_reg
            self.crossover_rate = self.crossover_rate * reg_reg


    def regulate_self_standard(self):
        self.crossover_rate = 0.48 + (0.36 - (0.36*(self.cur_gen/self.max_gen)))
        self.mutation_rate = 0.005 + max(0.355 - (0.355 * ((self.max_gen - self.cur_gen)/self.max_gen)), 0)
        
        #if self.elitism:
        #    self.elitism_rate = max(min(0.50, (self.og_elitism_rate/2) + ((0.50 - (self.og_elitism_rate/2))/(self.cur_gen/self.max_gen))), self.og_elitism_rate/2)

        if self.reg_pop:
            self.pop_size = math.floor(max(8, (np.int32(self.og_pop_size * (1.2 * (self.cur_gen/self.max_gen))))))

        #fit_reg = False
        #if fit_reg:
        #    self.fitness_rate = max(8, (np.int32(self.pop_size * (1.5 * (self.cur_gen/self.max_gen)))))

    def regulate_self_chaotic(self):
        match randint(0,2):
            case 0:
                self.regulate_self_standard()
            case 1:
                self.regulate_self_wavering()
            case 2:
                self.crossover_rate = uniform(0.05,0.99)
                self.mutation_rate = uniform(0.001, 0.0099)*(10*randint(0,1))*(10*randint(0,1))
                #if self.elitism:
                #    self.elitism_rate = uniform(0.01, 0.5)

                if self.reg_pop:
                    self.pop_size = max(8, randint(np.int16(self.og_pop_size/4), np.int16(self.og_pop_size * 2)))
                
                fit_reg =False
                if fit_reg:
                    self.fitness_rate = max(8, randint(np.int16(self.pop_size/3), np.int16(self.pop_size * 2)))

        
    #apply min and max on base regulate function
    # Test instead of doubling waves using prime numbers
    def regulate_self_wavering(self):
        #if self.reg_pop:
        #    self.pop_size = min(max(round(self.og_pop_size + ((self.og_pop_size/2) * math.cos(math.radians(self.cur_gen * 3)))), 8), self.pokedex.get_pokedex_length())
        # Test lower variation rate for crossover? 0.2? 0.25? 0.15? higher maybe? 0.33?
        self.crossover_rate = 0.64 + (0.16 * math.cos(math.radians(self.cur_gen * 2 )))

        #if self.elitism:
        #    self.elitism_rate = min(max(self.og_elitism_rate + ((self.og_elitism_rate * 0.875) * math.sin(math.radians(self.cur_gen * 3))), 0.005), 0.5) 
        
        self.mutation_rate = self.og_mutation_rate + ((self.og_mutation_rate/2) * math.sin(math.radians(self.cur_gen * 5))) + ((self.cur_gen/self.max_gen) * 0.225)

    def get_new_crossover_mutation(self):
        selected = self.selection(2)
        mama = selected[0]
        papa = selected[1]
        #select max 3 crossover types for the rest of the turn
        c_a, c_b = self.crossover.crossover_couple(mama[0], papa[0])
        #print('Crossovers_crossing: OK')

        if randint(0, 100_000) < (self.mutation_rate * 100_000):
            c_a = self.mutation.mutate(c_a)
        if randint(0, 100_000) < (self.mutation_rate * 100_000):
            c_b = self.mutation.mutate(c_b)
        #print('Crossovers_MUTANT: OK')

        return c_a, c_b

    def royal_marriage(self, el_a, el_b):
        c_a, c_b = self.crossover.crossover_couple(el_a, el_b)
        print('AAAAAAAAAAAA')
        if self.elitism_mutation:
            if randint(0, 100_000) < (self.mutation_rate * 100_000):
                c_a = self.mutation.mutate(c_a)
            if randint(0, 100_000) < (self.mutation_rate * 100_000):
                c_b = self.mutation.mutate(c_b)
                
        return c_a, c_b

    def create_target_ref_img(self):
        factor = math.floor(512/self.target_mon[2].shape[0])
        
        imio.imwrite(f'{self.base_dir}/target.png', utils.resize_by_factor(self.target_mon[2], factor))
        
        border_1, border_2 = self.pokedex.get_borders()
        imio.imwrite(f'{self.base_dir}/target_b1.png', utils.resize_by_factor(border_1, factor))
        imio.imwrite(f'{self.base_dir}/target_b2.png', utils.resize_by_factor(border_2, factor))
        
        gray_target = utils.to_rgba(utils.to_grayscale(np.copy(self.target_mon[2])))
        imio.imwrite(f'{self.base_dir}/target_gray.png', utils.resize_by_factor(gray_target, factor))
        bw_target = utils.to_rgba(utils.to_black_n_white(np.copy(self.target_mon[2])))
        imio.imwrite(f'{self.base_dir}/target_bw.png', utils.resize_by_factor(bw_target, factor))
        posterized_target = utils.posterize(np.copy(self.target_mon[2]))
        imio.imwrite(f'{self.base_dir}/target_post.png', utils.resize_by_factor(posterized_target, factor))
        hard_posterized_target = utils.posterize_hard(np.copy(self.target_mon[2]))
        imio.imwrite(f'{self.base_dir}/target_h_post.png', utils.resize_by_factor(hard_posterized_target, factor))
        binary_posterized_target = utils.posterize_binary(np.copy(self.target_mon[2]))
        imio.imwrite(f'{self.base_dir}/target_bin_post.png', utils.resize_by_factor(binary_posterized_target, factor))
    
    def selection(self, select_num):
        apt = [t[2] for t in self.team]

        while True:
            # Should return two values since this shit is only used for crossover
            selected = choices(self.team, weights=apt, k=select_num)

            if not(np.array_equal(selected[0][0], selected[1][0])):
                break

        return selected
    
    
    def initial_population(self):
        poke_keys = self.pokedex.get_pokedex_keys()
        
        max_pull = min(self.pop_size, math.floor(self.pokedex.get_pokedex_length() * 0.99))
        pop_dex = choices(poke_keys, k=max_pull)
        for pk in pop_dex:
            poke_img = self.pokedex.get_another_pokemon(pk)
            self.team.append([poke_img, 0,0])
        while len(self.team) < self.pop_size:
            self.team.append([self.pokedex.get_random_pokemon(),0,0])

    def find_elite(self, team):
        s_team = sorted(team, key=lambda x: x[1])
        #return max(team, key=lambda elemento: elemento[1])
        el_te = s_team.pop()
        return el_te

    def get_elite_pokemon(self):
        return self.find_elite(self.team)
    
    def get_target_pokemon(self):
        return self.pokedex.get_target_pokemon()

    def get_GOAT_pokemon(self):
        return self.best_mon.copy()
    
    def selection_tournament(self):
        choices
    
    #maybe its time to implement steady state...
    def populate_new_gen(self):
        
        fittest_few = []


        tournament = self.selection(np.int16(self.pop_size*self.perserverance_rate))

        
        new_gen = []
        while len(new_gen) < self.pop_size * (self.crossover_rate):
            pkm_a, pkm_b = self.get_new_crossover_mutation()       
            new_gen.append(pkm_a)
            new_gen.append(pkm_b)
        
        for it in range(len(tournament)):
            if randint(0, 100_000) < (self.mutation_rate * 100_000):
                t_m = self.mutation.mutate(tournament[it][0])
                new_gen.append(t_m)
            else:
                new_gen.append(tournament[it][0])
            if self.save_all_imgs:imio.imwrite(f'{self.base_dir}/gen_{self.cur_gen}/{(tournament[it][1]/self.target_mon[3])*100}_WW{it}.png', tournament[it][0])
        
        sorted_team = sorted(self.team, key=lambda x: x[1])
        
        if self.elitism:
            most_fit_mon = sorted_team.pop()
            if len(self.best_mon) < 1:
                self.best_mon = most_fit_mon.copy()
            elif self.best_mon[1] < most_fit_mon[1]:
                self.best_mon = most_fit_mon.copy()
            
            if self.cur_gen % self.elitism_interval == 0:
                if self.elitism_mutation and randint(0, 100_000) < (self.mutation_rate * 100_000):
                        fittest_few.append(self.mutation.mutate(np.copy(self.best_mon[0])))
                else:
                    fittest_few.append(np.copy(self.best_mon[0]))
                if self.save_all_imgs: imio.imwrite(f'{self.base_dir}/gen_{self.cur_gen}/{(most_fit_mon[1]/self.target_mon[3])*100}_SR0.png', most_fit_mon[0])
            
            if self.pity:
                least_fit_mon = sorted_team.pop(0)
                if self.save_all_imgs: imio.imwrite(f'{self.base_dir}/gen_{self.cur_gen}/{(least_fit_mon[1]/self.target_mon[3])*100}_FFF0.png', most_fit_mon[0])
                new_gen.append(least_fit_mon[0])
                if self.elitism_mutation and randint(0, 100_000) < (self.mutation_rate * 100_000):
                    new_gen.append(self.mutation.mutate(np.copy(least_fit_mon[0])))
        
        
        for iter in range(len(self.team)):
            if self.elitism and (len(fittest_few) < self.pop_size * self.elitism_rate) and len(sorted_team) > 0 and self.cur_gen % self.elitism_interval == 0:
                # or... just sort it once and pop shit until you're done
                heir = sorted_team.pop()
                if self.elitism_mutation and randint(0, 100_000) < (self.mutation_rate * 100_000): #conditional?
                    fittest_few.append(self.mutation.mutate(heir[0]))
                else:
                    fittest_few.append(heir[0])
                
                if self.save_all_imgs: imio.imwrite(f'{self.base_dir}/gen_{self.cur_gen}/{(heir[1]/self.target_mon[3])*100}_R{iter}.png', heir[0])
            elif self.save_all_imgs and len(sorted_team) > 0:
                old_poke = sorted_team.pop()
                imio.imwrite(f'{self.base_dir}/gen_{self.cur_gen}/{(old_poke[1]/self.target_mon[3])*100}_C{iter}.png', old_poke[0])
        
        self.team.clear()
        
        if self.elitism and self.cur_gen % self.elitism_interval == 0:
            for ft in fittest_few:
                new_gen.append(ft)
                
                
                
        dupelen = len(new_gen)
        self.team = utils.format_team_pk_scr_fit(new_gen, dupes=self.dupes)
        unqlen = len(self.team)
        new_gen.clear()
        
        #for pk in new_gen:
        #    self.team.append(pk)
            
        if dupelen != unqlen and debug and not(self.dupes):
            print(f'\033[94m [Duplicatas removidas: Tam. Equipe {dupelen} -> {unqlen} (-{dupelen-unqlen})] \033[0m')

        if len(self.team) < self.pop_size:
            poke_keys = self.pokedex.get_pokedex_keys()
            search_list = choices(poke_keys, k=(self.pop_size - len(self.team)))
            for dk in search_list:
                if randint(0, 100_000) < (self.mutation_rate * 100_000):
                    self.team.append([self.mutation.mutate(self.pokedex.get_another_pokemon(dk)), 0, 0])
                else:
                    self.team.append([self.pokedex.get_another_pokemon(dk), 0, 0])
                
    def score_party(self):
        for it in range(len(self.team)):
            self.team[it][1] = self.pokedex.aval_target(self.target_mon[2], self.team[it][0])
        self.pokedex.close_colormap()
        self.cur_gen += 1
        
    
    def get_true_score(self, pkm):
        return self.pokedex.aval_target_standard(self.target_mon[2], pkm)
    
    def get_lowest_score(self):
        t_c = self.team.copy()
        s_team = sorted(t_c, key=lambda x: x[1], reverse=True)
        #return max(team, key=lambda elemento: elemento[1])
        low_pkm = s_team.pop()
        return ((low_pkm[1]/self.target_mon[3]) * 100.0)
    
    def apply_fitness(self):
        self.team = self.fitness.get_team_fitness_score(self.team)
        #self.team[:,2] = self.fit_team[:]

    #def get_fitness_list(self):
        #f_list = self.fitness.get_fitness_list()
    #    f_values = [f[1] for f in f_list]
    #    return f_values