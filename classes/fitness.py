from random import choices, randint
import numpy as np
import math

import classes.utils as utils


class Fitness():
    def __init__(self, pop_size, fitness_rate, fitness_type='normalize'):
        self.fitness_type = fitness_type
        self.fitness_rate = fitness_rate
        self.pop_size = pop_size
        self.no_progress = 0
        self.cur_gen = 0
        
        self.last_used = 'none'
        self.adaptible_smart_stats = {
            "cos_progressive": {
                "success_num": 1,
                "total_num": 1,
            },
            "cos_sin_log_progressive": {
                "success_num": 1,
                "total_num": 1,
            },
            "cos_double": {
                "success_num": 1,
                "total_num": 1,
            },
            "sin_half": {
                "success_num": 1,
                "total_num": 1,
            },
            "normalize": {
                "success_num": 1,
                "total_num": 1,
            },
            "windowing": {
                "success_num": 1,
                "total_num": 1,
            },
            "score": {
                "success_num": 1,
                "total_num": 1,
            },
            }
        
        '''self.adaptible_advanced_stats = {
            "cos_progressive": {
                # pop_size
                100: {
                    # CoR
                    0.6 : {
                        # elitism
                        0.05 : {
                            "success_num": 0,
                            "total_num": 0,
                            }
                    }
                }
            },
        }'''
        
        self.fitness_list = []

    def set_no_progress_gen(self, val, gen):
        self.no_progress = val
        self.cur_gen = gen

    def normalization(self, team, min, max):
        normalize = []
        
        #aval = zip(self.populacao, self.avaliacao)
        sort_val = sorted(team, key=lambda x: x[1])

        for it in range(len(sort_val)):
            normalize.append(min + ((max-min)/(self.pop_size-1)) * it)
        
        indSort = [t[0] for t in sort_val]
        return list(zip(indSort, normalize))
    
    def cos2x_norm(self, team):
        cosnorm = []
        
        step = math.radians(360/self.pop_size)
        
        half_pop = self.pop_size/2
        
        sort_val = sorted(team, key=lambda x: x[1])

        for it in range(len(sort_val)):
            cosnorm.append(half_pop + (math.cos(step*(it*2)) * half_pop))
        
        indSort = [t[0] for t in sort_val]
        return list(zip(indSort, cosnorm))
    
    def sinh2_norm(self, team):
        sinnorm = []
        
        step = math.radians(360/self.pop_size)
        
        #onfi_pop = self.pop_size/5
        #fofi_pop = onfi_pop * 4
        
        sort_val = sorted(team, key=lambda x: x[1])

        for it in range(len(sort_val)):
            sinnorm.append((math.sin(step*(it/2)) * self.pop_size))
        
        indSort = [t[0] for t in sort_val]
        return list(zip(indSort, sinnorm))
    
    def cos_progressive(self, team, peak):
        cosnorm = []
        
        step = math.radians(360/self.pop_size)        
        
        half_pop = self.pop_size/2
        
        sort_val = sorted(team, key=lambda x: x[1])

        for it in range(len(sort_val)):
            cosnorm.append((((math.cos(step*(it*peak)) + 1) * half_pop)) * math.sqrt((step*it)/(2 * math.pi)) )
        
        indSort = [t[0] for t in sort_val]
        return list(zip(indSort, cosnorm))
    
    
    def cos_sin_log_progressive(self, team):
        sinnorm = []
        
        step = math.radians(360/self.pop_size)
        
        #onfi_pop = self.pop_size/5
        #fofi_pop = onfi_pop * 4
        
        sort_val = sorted(team, key=lambda x: x[1])

        for it in range(len(sort_val)):
            
            sinh = math.sin(step*(it/2))
            cos_sinh_2pi = math.cos(sinh * (2 * math.pi))
            log10_xs9 = math.log10((max(it,1)/9))
            prog_base = cos_sinh_2pi + (log10_xs9 + 1)
            fit_val =  prog_base * (self.pop_size/math.pi)
            
            sinnorm.append(fit_val)
        
        indSort = [t[0] for t in sort_val]
        return list(zip(indSort, sinnorm))
    
    def adaptible_sine(self, team):
        
        if self.cur_gen < 100:
            return self.normalization(team, 1, self.pop_size)
        else:
            if self.no_progress <= 50:
                turn = randint(0,4)
                if turn != 0:
                    return self.cos_progressive(team, randint(3,5))
                    # register total times called in run
                    # register ratio of changes to total
                    # add 'self.last_called'
                    # use it to calculate weights and use them to decide next one to use
                    # maybe do this shit to calculate crossover too...
                    # pkmn in crossover would need a 'source' [3] though, if randomly generated or not
                else:
                    return self.cos2x_norm(team)
            elif self.no_progress <= 100:
                return self.cos_sin_log_progressive(team)
            #elif self.no_progress <= 150:
            #    return self.sinh2_norm(team)
            else:
                turn = randint(0,4)
                match turn:
                    case 0:
                        return self.normalization(team, 1, self.pop_size)
                    case 1:
                        return self.cos_progressive(team, randint(3,5))
                    case 2:
                        return self.cos2x_norm(team)
                    case 3:
                        return self.cos_sin_log_progressive(team)
                    case 4:
                        return self.sinh2_norm(team)
                  
                  
    def adaptible_learner(self, team):
        
        if self.last_used != 'none':
            self.adaptible_smart_stats[self.last_used]["total_num"] += 1
            if self.no_progress == 0:
                self.adaptible_smart_stats[self.last_used]["success_num"] += 1
                
                
        if self.cur_gen >= 100:        
            pool = [
                ('cos_progressive', utils.safe_weight(self.adaptible_smart_stats['cos_progressive']['total_num'], self.adaptible_smart_stats['cos_progressive']['success_num'] )),
                ('cos_sin_log_progressive', utils.safe_weight(self.adaptible_smart_stats['cos_sin_log_progressive']['total_num'], self.adaptible_smart_stats['cos_sin_log_progressive']['success_num'] )),
                ('cos_double', utils.safe_weight(self.adaptible_smart_stats['cos_double']['total_num'], self.adaptible_smart_stats['cos_double']['success_num'] )),
                ('sin_half', utils.safe_weight(self.adaptible_smart_stats['sin_half']['total_num'], self.adaptible_smart_stats['sin_half']['success_num'] )),
                ('normalize', utils.safe_weight(self.adaptible_smart_stats['normalize']['total_num'], self.adaptible_smart_stats['normalize']['success_num'] )),
                ('windowing', utils.safe_weight(self.adaptible_smart_stats['windowing']['total_num'], self.adaptible_smart_stats['windowing']['success_num'] )),
                ('score', utils.safe_weight(self.adaptible_smart_stats['score']['total_num'], self.adaptible_smart_stats['score']['success_num'] )),
                    ]
            
            apt = [w[1] for w in pool]

            fit_choice = choices(pool, weights=apt, k=1)
            
            self.last_used = fit_choice[0][0]
            
            if self.cur_gen % 100 == 0:
                print(f'Dict:\n{self.adaptible_smart_stats}\n\nCur pool:\n{pool}\n')
            
            #print(f'da CHOICE:{fit_choice} <-----')
            #print(f'pooool:{pool}...END\n\n')
            #print(fit_choice[0])
            #print(fit_choice[0][0])

            match fit_choice[0][0]:
                case 'cos_progressive':
                    return self.cos_progressive(team, randint(3,5))
                case 'cos_sin_log_progressive':
                    return self.cos_sin_log_progressive(team)
                case 'cos_double':
                    return self.cos2x_norm(team)
                case 'sin_half':
                    return self.sinh2_norm(team)
                case 'normalize':
                    return self.normalization(team, 1, self.pop_size)
                case 'windowing':
                    return self.windowing(team)
                case 'score':
                    return self.just_score(team)
        else:
            return self.normalization(team, 1, self.pop_size)
        
    
    
    
    def windowing(self, team):
        pks = []
        for pk in team:
            pks.append([pk[0], max(pk[1] - min(team, key=lambda x: x[1])[1], 0.01)])
        return pks

    def just_score(self, team):
        pks = []
        for pk in team:
            pks.append([pk[0], pk[1]])
        return pks

    # normalize to middle
    # ignore middle
    # cos/sen
    # escadinha
    # conferir o site la dos shaders para pensar nuns grafos de normalização criativa

    def get_team_fitness_score(self, team):
        pks = []
        if self.fitness_type == 'score':
            pks = self.just_score(team)
        elif self.fitness_type == 'windowing':
            pks = self.windowing(team)
        elif self.fitness_type == 'normalize':
            pks = self.normalization(team, 1, self.fitness_rate)
        elif self.fitness_type == 'cos_double':
            pks = self.cos2x_norm(team)
        elif self.fitness_type == 'sin_half':
            pks = self.sinh2_norm(team)
        elif self.fitness_type == 'cos_progressive':
            pks = self.cos_progressive(team, 4)
        elif self.fitness_type == 'cos_sin_log_progressive':
            pks = self.cos_sin_log_progressive(team)
        elif self.fitness_type == 'adaptible':
            pks = self.adaptible_sine(team)
        elif self.fitness_type == 'adaptible_learner':
            pks = self.adaptible_learner(team)
        else:
            print('fitness error')
            pks = team

        self.fitness_list = pks
        return pks
        
    def selection(self):
        apt = [t[1] for t in self.fitness_list]

        while True:
            # Should return two values since this shit is only used for crossover
            selected = choices(self.fitness_list, weights=apt, k=2)

            if not(np.array_equal(selected[0][0], selected[1][0])):
                break

        
        return [selected[0][0], selected[1][0]]
    
    
    