from random import choices
import numpy as np
class Fitness():
    def __init__(self, pop_size, fitness_rate, fitness_type='normalize'):
        self.fitness_type = fitness_type
        self.fitness_rate = fitness_rate
        self.pop_size = pop_size

        self.fitness_list = []



    def normalization(self, team, min, max):
        self.normalize = []
        
        #aval = zip(self.populacao, self.avaliacao)
        sort_val = sorted(team, key=lambda x: x[1])

        for it in range(len(sort_val)):
            self.normalize.append(min + ((max-min)/(self.pop_size-1)) * it)
        
        indSort = [t[0] for t in sort_val]
        return list(zip(indSort, self.normalize))
    
    def windowing(self, team, pokedude):
                
        return max(pokedude[1] - min(team, key=lambda x: x[1])[1], 0.01)


    def get_team_fitness_score(self, team):
        pks = []
        if self.fitness_type == 'score':
            for poke in team:
                pks.append([poke[0], poke[1]])
        elif self.fitness_type == 'windowing':
            for poke in team:
                pks.append([poke[0], self.windowing(team, poke)])
        elif self.fitness_type == 'normalize':
            pks = self.normalization(team, 1, self.fitness_rate)
        else:
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
    
    