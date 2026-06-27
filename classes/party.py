from random import randint, choices, sample, uniform, seed
import numpy as np
import math
import imageio.v3 as imio

import classes.pokedex as pokedex
import classes.mutation as mutation
import classes.crossover as crossover
import classes.fitness as fitness

debug = True

class Party():
    def __init__(
            self,
            target_dex,
            easy_shiny=False,
            generation=9,
            pop_size=40,
            crossover_rate=0.72,
            mutation_rate=0.02,
            elitism_rate=0.08,
            max_gen=24,
            score_type='RGBA',
            auto_regulate=True,
            reg_pop=False,
            regulate_type='wave',
            elitism=True,
            elitism_mutation=False,
            crossover_type=['bisect', 'swap_simple', 'swap_even', 'swap_sensible', 'swap_serial', 'swap_colors'],
            fitness_type='normalize',
            verbose=False,
            save_all_imgs=True
            ):
        
        self.score_type = score_type

        # Pokedex
        self.pokedex = pokedex.Pokedex(target_dex=target_dex, easy_shiny=easy_shiny, score_type=self.score_type, generation=generation)

        self.target_dex = target_dex
        self.target_mon = self.pokedex.get_target_pokemon()

        self.crossover = crossover.Crossover(crossover_type=crossover_type, target_mon=self.target_mon)
        self.mutation = mutation.Mutation()
        self.fitness = fitness.Fitness(pop_size=pop_size, fitness_rate=pop_size, fitness_type=fitness_type)

        #team
        self.cur_gen = 0
        self.team = []
        self.fit_team = []

        self.base_dir = ''
        
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
        self.elitism = elitism
        self.elitism_mutation = elitism_mutation
        if self.elitism:
            self.elitism_rate = elitism_rate
        else:
            self.elitism_rate = 0
        self.og_elitism_rate = self.elitism_rate
        #
        self.fitness_rate = self.og_pop_size
        self.fitness_list = []
        #
        self.verbose = verbose
        self.save_all_imgs = save_all_imgs


    def get_team(self):
        return self.team
    
    def get_cur_gen(self):
        return self.cur_gen
    
    def get_stats(self):
        stats = []
        stats.append(self.pop_size)
        stats.append(self.crossover_rate)
        stats.append(self.mutation_rate)
        stats.append(self.elitism_rate)

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
        self.crossover_rate = max(min(0.92, (self.og_crossover_rate/2) + (0.92 - ((self.og_crossover_rate/2))/(self.cur_gen/self.max_gen))), (self.og_crossover_rate/2))
        self.mutation_rate = max(min(0.12, (self.og_mutation_rate/2) + ((0.12,0 - (self.og_mutation_rate/2))/(self.cur_gen/self.max_gen))), (self.og_mutation_rate/2))
        
        #if self.elitism:
        #    self.elitism_rate = max(min(0.50, (self.og_elitism_rate/2) + ((0.50 - (self.og_elitism_rate/2))/(self.cur_gen/self.max_gen))), self.og_elitism_rate/2)

        if self.reg_pop:
            self.pop_size = math.floor(max(8, (np.int32(self.og_pop_size * (1.5 * (self.cur_gen/self.max_gen))))))

        self.fitness_rate = max(8, (np.int32(self.pop_size * (1.5 * (self.cur_gen/self.max_gen)))))

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

                self.fitness_rate = max(8, randint(np.int16(self.pop_size/3), np.int16(self.pop_size * 2)))

        
    #apply min and max on base regulate function
    # Test instead of doubling waves using prime numbers
    def regulate_self_wavering(self):
        if self.reg_pop:
            self.pop_size = min(max(round(self.og_pop_size + ((self.og_pop_size/2) * math.sin(math.radians(self.cur_gen * 3)))), 8), self.pokedex.get_pokedex_length())
        # Test lower variation rate for crossover? 0.2? 0.25? 0.15? higher maybe? 0.33?
        self.crossover_rate = 0.7 + (0.25 * math.sin(math.radians(self.cur_gen * 5)))

        #if self.elitism:
        #    self.elitism_rate = min(max(self.og_elitism_rate + ((self.og_elitism_rate/1.3333) * math.sin (math.radians(self.cur_gen * 7))), 0.005), 0.75)
        
        self.fitness_rate = max(self.pop_size * 2 * math.cos(math.atan(math.radians(self.cur_gen/3))), (max((self.cur_gen/300) -3, 0) * 0.125) * (self.pop_size * math.sin(math.radians(self.cur_gen)))) * math.cos(math.sin(math.radians(self.cur_gen)))

        self.mutation_rate = min(max(self.og_mutation_rate + (((self.og_mutation_rate/2) * math.sin (math.radians(self.cur_gen * 11))) * max(0.4 + ((self.cur_gen * 0.0012) * math.cos(self.cur_gen/8)), 0.01) ), 0.001), 0.75)

    def get_new_crossover_mutation(self):

        mama, papa = self.fitness.selection()
        c_a, c_b = self.crossover.crossover_couple(mama, papa)

        if randint(0, 10000) < (self.mutation_rate * 10000):
            c_a = self.mutation.mutate(c_a)
        if randint(0, 10000) < (self.mutation_rate * 10000):
            c_b = self.mutation.mutate(c_b)

        return c_a, c_b


    def initial_population(self):
        poke_keys = self.pokedex.get_pokedex_keys()

        pop_dex = choices(poke_keys, k=self.pop_size)
        for pk in pop_dex:
            poke_img = self.pokedex.get_another_pokemon(pk)
            self.team.append([poke_img, 0])    

    def find_elite(self, team):
        return max(team, key=lambda elemento: elemento[1])

    def get_elite_pokemon(self):
        return self.find_elite(self.team)
    
    def get_target_pokemon(self):
        return self.pokedex.get_target_pokemon()

    #maybe its time to implement steady state...
    def populate_new_gen(self):
        new_gen = list()

        #self.fitness_list = list(self.fitness())
        while len(new_gen) < self.pop_size * (self.crossover_rate):
            pkm_a, pkm_b = self.get_new_crossover_mutation()       
            new_gen.append(pkm_a)
            new_gen.append(pkm_b)  

        fittest_few = list()
        sorted_team = sorted(self.team, key=lambda x: x[1])
        most_fit_mon = sorted_team.pop()
        fittest_few.append(most_fit_mon)
        
        for it in range(len(self.team)):
            if self.elitism and (len(fittest_few) < math.ceil(self.pop_size * self.elitism_rate)) and len(sorted_team) > 0:
                # or... just sort it once and pop shit until you're done
                heir = sorted_team.pop()
                if self.elitism_mutation: #conditional?
                    fittest_few.append([self.mutation.mutate(heir[0]), 0])
                else:
                    fittest_few.append(heir)
                #self.team.remove(heir)
                
                if self.save_all_imgs: imio.imwrite(f'{self.base_dir}/gen_{self.cur_gen}/{heir[1]}_{it}.png', heir[0])
            elif self.save_all_imgs and len(sorted_team) > 0:
                old_poke = sorted_team.pop()
                imio.imwrite(f'{self.base_dir}/gen_{self.cur_gen}/{old_poke[1]}_{it}.png', old_poke[0])
        
        self.team.clear()
        
        if self.elitism:
            for ft in fittest_few:
                new_gen.append(ft[0])
        
        for pk in new_gen:
            self.team.append([pk, 0])

        if len(self.team) < self.pop_size:
            poke_keys = self.pokedex.get_pokedex_keys()
            search_list = choices(poke_keys, k=(self.pop_size - len(self.team)))
            for dk in search_list:
                if randint(0, 10000) < (self.mutation_rate * 10000):
                    self.team.append([self.mutation.mutate(self.pokedex.get_another_pokemon(dk)), 0])
                else:
                    self.team.append([self.pokedex.get_another_pokemon(dk), 0])
                
    def score_party(self):
        if self.score_type == 'RGBA':
            for it in range(len(self.team)):
                self.team[it][1] = self.pokedex.aval_target(self.target_mon, self.team[it])
        elif self.score_type == 'Grayscale':
            for it in range(len(self.team)):
                self.team[it][1] = self.pokedex.aval_target_grayscale(self.target_mon, self.team[it])
                
        #fit_team = self.fitness.get_team_fitness_score(self.team)
        #self.team = fit_team

        self.cur_gen += 1


    def apply_fitness(self):
        self.fit_team = self.fitness.get_team_fitness_score(self.team)

