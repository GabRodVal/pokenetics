from pickle import FALSE
from random import randint, choices, seed
import math
import matplotlib.pyplot as plt
import numpy as np

class AlgoritimoGenetico():

    #def __init__(self, x_min, x_max, y_min, y_max, totalBits, tam_populacao, taxa_mutacao, taxa_crossover, num_geracoes, elitismo, fitnessKind, steadyStateOn, duplicate):
        
    def __init__(self, x1_range=(2**32), x2=(2**32), tam_populacao=100, taxa_mutacao=0.0005, taxa_crossover=0.6, num_geracoes=100, elitismo=True, fitnessKind='normalizar', steadyStateOn=True, duplicate=False):
        
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        self.totalBits = totalBits

        self.tam_populacao = tam_populacao
        self.taxa_mutacao = taxa_mutacao
        self.taxa_crossover = taxa_crossover
        self.num_geracoes = num_geracoes

        self.elitismo = elitismo

        self.fitnessKind = fitnessKind

        self.steadyStateOn = steadyStateOn
        self.duplicate = duplicate

        # calcula o número de bits do x_min e x_máx no formato binário com sinal
        print(self.totalBits/2)
        qtd_bits_x_min = int(self.totalBits/2)
        qtd_bits_x_max = int(self.totalBits/2)

        qtd_bits_y_min = int(self.totalBits/2)
        qtd_bits_y_max = int(self.totalBits/2)


        # o maior número de bits representa o número de bits a ser utilizado para gerar individuos
        self.num_bits_x = qtd_bits_x_max if qtd_bits_x_max >= qtd_bits_x_min else qtd_bits_x_min
        self.num_bits_y = qtd_bits_y_max if qtd_bits_y_max >= qtd_bits_y_min else qtd_bits_y_min
        self.num_bits = self.num_bits_x #+ self.num_bits_y

        print('X:',self.num_bits_x,'Y:',self.num_bits_y)

        # gera os individuos da população
        self.gerarpopulacao()

    def gerarpopulacao(self):
        self.populacao = [[] for i in range(self.tam_populacao)]

        for individuo in self.populacao:
            num_bin_x = ''.join(str(randint(0, 1)) for _ in range(int(self.totalBits/2)))

            num_bin_y = ''.join(str(randint(0, 1)) for _ in range(int(self.totalBits/2)))

            num_bin = num_bin_x+ "#" + num_bin_y

            for bit in num_bin:
                individuo.append(bit)
            

                

    def _funcao_objetivo(self, num_bin):
        """
            Calcula a função objetivo (F6) utilizada para avaliar as soluções produzidas
        """
        
        # converte o número binário para o formato inteiro
        f = num_bin.index('#')
        numx = num_bin[:f]
        numy = num_bin[f+1:]

        numx =  (int(''.join(numx), 2) * ((200/(2**22-1)))) - self.x_max
        numy = (int(''.join(numy), 2) * ((200/(2**22-1)))) - self.y_max

        # calcula e retorna o resultado da função objetivo
        obj = 0.5 - (((math.sin(math.sqrt((numx**2) + (numy**2)))**2) - 0.5)        /(1.0+0.001*( (numx**2) + (numy**2) ) )**2)

        '''
        if obj >= 0.999:
            print('X:',numx,'Y:',numy)'''
        
        return obj
    
    def windowing(self, num_bin):
        """
            Calcula a função objetivo utilizada para avlaiar as soluções produzidas
        """
        
        # converte o número binário para o formato inteiro
        
        return max(self._funcao_objetivo(num_bin)-min(self.avaliacao),0)
    
    
    def avaliar(self):
        """
            Avalia as souluções produzidas, associando uma nota/avalição a cada elemento da população
        """
        self.avaliacao = []
        for individuo in self.populacao:
            self.avaliacao.append(self._funcao_objetivo(individuo))

    def avalOther(self):
        """
            Avalia as souluções produzidas, associando uma nota/avalição a cada elemento da população
        """
        self.avaliacao = []
        for individuo in self.populacao:
            self.avaliacao.append(self._funcao_objetivo(individuo))

    def normalizacao_linear(self,min,max):


        self.normalizar = []
        
        aval = zip(self.populacao, self.avaliacao)
        sort_val = sorted(aval, key=lambda x: x[1])

        for individual in range(len(sort_val)):
            self.normalizar.append(min + ((max-min)/(self.tam_populacao-1)) * individual)
        
        indSort = [t[0] for t in sort_val]
        return zip(indSort, self.normalizar)


    def fitness(self):
        if self.fitnessKind == 'avaliacao':
            return zip(self.populacao, self.avaliacao)
        elif self.fitnessKind == 'windowing':
            self.windows = []
            for individuo in self.populacao:
                self.windows.append(self.windowing(individuo))
            return zip(self.populacao, self.windows)
        elif self.fitnessKind == 'normalizar':
            return self.normalizacao_linear(1,100)

    def selecionar(self):
        """
            Realiza a seleção do individuo mais apto por torneio, considerando N = 2
        """
        # agrupa os individuos com suas avaliações para gerar os participantes do torneio
        participantes_torneio = list(self.fitness())

        apt = [t[1] for t in participantes_torneio]

        selected = choices(participantes_torneio, weights=apt, k=1)

        
        
        return selected[0][0]
    
    def _ajustar(self, individuo):
        """
            Caso o individuo esteja fora dos limites de x, ele é ajustado de acordo com o limite mais próximo
        """

        
        f = individuo.index('#')
        numx=individuo[:f]
        numy =individuo[f+1:]


        if int(''.join(numx), 2) < self.x_min:
            # se o individuo é menor que o limite mínimo, ele é substituido pelo próprio limite mínimo
            ajuste = bin(self.x_min).replace('0b', '' if self.x_min < 0 else '+').zfill(self.num_bits)
            for indice, bit in enumerate(ajuste):
                numx[indice] = bit
        elif int(''.join(numx), 2) > self.x_max:
            # se o individuo é maior que o limite máximo, ele é substituido pelo próprio limite máximo
            ajuste = bin(self.x_max).replace('0b', '' if self.x_max < 0 else '+').zfill(self.num_bits)
            for indice, bit in enumerate(ajuste):
                numx[indice] = bit

        if int(''.join(numy), 2) < self.y_min:
            # se o individuo é menor que o limite mínimo, ele é substituido pelo próprio limite mínimo
            ajuste = bin(self.y_min).replace('0b', '' if self.x_min < 0 else '+').zfill(self.num_bits)
            for indice, bit in enumerate(ajuste):
                numx[indice] = bit
        elif int(''.join(numy), 2) > self.y_max:
            # se o individuo é maior que o limite máximo, ele é substituido pelo próprio limite máximo
            ajuste = bin(self.y_max).replace('0b', '' if self.x_max < 0 else '+').zfill(self.num_bits)
            for indice, bit in enumerate(ajuste):
                numy[indice] = bit


    def crossover(self, pai, mae):
        """
            Aplica o crossover de acordo com uma dada probabilidade (taxa de crossover)
        """
        if randint(1,10000)/10000 <= self.taxa_crossover:
            # caso o crossover seja aplicado os pais trocam suas caldas e com isso geram dois filhos
            ponto_de_corte = randint(1, len(pai)-1)
            filho_1 = pai[:ponto_de_corte] + mae[ponto_de_corte:]
            filho_2 = mae[:ponto_de_corte] + pai[ponto_de_corte:]
            # se algum dos filhos estiver fora dos limites de x, ele é ajustado de acordo com o limite
            # mais próximo
            self._ajustar(filho_1)
            self._ajustar(filho_2)    
        else:
            # caso contrário os filhos são cópias exatas dos pais
            filho_1 = pai[:]
            filho_2 = mae[:]

        # retorna os filhos obtidos pelo crossover
        return (filho_1, filho_2)
    
    def mutar(self, individuo):
        """
            Realiza a mutação dos bits de um indiviuo conforme uma dada probabilidade
            (taxa de mutação)
        """
        # cria a tabela com as regras de mutação
        #tabela_mutacao = str.maketrans('+-01', '-+10')
        # caso a taxa de mutação seja atingida, ela é realizada em um bit aleatório
        '''if randint(1,10000)/10000 <= self.taxa_mutacao:
            bit = randint(0, self.num_bits - 1)
            individuo[bit] = individuo[bit].translate(tabela_mutacao)
        '''

        for bit in range(len(individuo)):
            if randint(1,10000)/10000 <= self.taxa_mutacao and (individuo[bit] == '0' or individuo[bit] == '1'):
                individuo[bit] = str(randint(0,1))

        # se o individuo estiver fora dos limites de x, ele é ajustado de acordo com o
        # limite mais próximo
        self._ajustar(individuo)

    def encontrar_filho_mais_apto(self):
        """
            Busca o individuo com a melhor avaliação dentro da população
        """
        # agrupa os individuos com suas avaliações para gerar os candidatos
        candidatos = self.fitness()
        # retorna o candidato com a melhor avaliação, ou seja, o mais apto da população

        mais_apto = max(candidatos, key=lambda elemento: elemento[1])

        primo = (mais_apto[0],self._funcao_objetivo(mais_apto[0]))

        return primo
    

def steadyState(algGen, gap):

    values = list(algGen.fitness())

    sorted_values_general = sorted(values, key=lambda x: x[1])

    sorted_values = []


    for i in sorted_values_general:
        sorted_values.append(i[0])

    newGen = []

    while len(newGen) < gap:
        pai = algGen.selecionar()
        mae = algGen.selecionar()
        filho_1, filho_2 = algGen.crossover(pai, mae)

        algGen.mutar(filho_1)
        algGen.mutar(filho_2)

        newGen.append(filho_1)
        if len(newGen) < gap:
            newGen.append(filho_2)

    sorted_values[:gap] = newGen


    if algGen.duplicate == False:
        noDupeValues = []

        for v in sorted_values:
            if v not in noDupeValues:
                noDupeValues.append(v)
        
        while len(noDupeValues) < algGen.tam_populacao:
            # seleciona os pais
                pai = algGen.selecionar()
                mae = algGen.selecionar()
                # realiza o crossover dos pais para gerar os filhos
                filho_1, filho_2 = algGen.crossover(pai, mae)
                # realiza a mutação dos filhos e os adiciona à nova população
                algGen.mutar(filho_1)
                algGen.mutar(filho_2)
                if filho_1 not in noDupeValues:
                    noDupeValues.append(filho_1)

                if len(noDupeValues) < algGen.tam_populacao and filho_2 not in noDupeValues:
                    noDupeValues.append(filho_2)

        sorted_values = noDupeValues

    newValues = []
    for f in sorted_values:
        newValues.append(f)

    return newValues


def countNines(num):

    num_str = str(num)

    integ,decimal = num_str.split('.')

    consecNine = 0

    for number in decimal:
        if number == '9':
            consecNine += 1
        else:
            return consecNine
    
    return consecNine


def main():
    # executa o algoritmo por "num_gerações"

    expRes = [[0 for c in range(20)] for r in range(40)]

    seed(111)

    for ex in range(20):
        #Os valores booleanos se referem, em ordem a: Elitismo, Steady State e permitir duplicados no Steady State
        #Pode-se trocar o metodo de aptidao, os disponiveis são 'avaliacao','windowing' e 'normalizar'
        algoritmo_genetico = AlgoritimoGenetico(-100, 100, -100, 100, 44, 100, 0.008, 0.65, 40, True , 'windowing', True , False)

        #algoritmo_genetico.avaliar()
        for i in range(algoritmo_genetico.num_geracoes):
            algoritmo_genetico.avaliar()
            # imprime o resultado a cada geração, começando da população original
            filhoapto = algoritmo_genetico.encontrar_filho_mais_apto()
            print( 'Resultado {}: {}'.format(i, filhoapto))
            expRes[i][ex] = filhoapto[1]
            # cria uma nova população e a preenche enquanto não estiver completa
            nova_populacao = []


            while len(nova_populacao) < algoritmo_genetico.tam_populacao:
                # seleciona os pais
                pai = algoritmo_genetico.selecionar()
                mae = algoritmo_genetico.selecionar()
                # realiza o crossover dos pais para gerar os filhos
                filho_1, filho_2 = algoritmo_genetico.crossover(pai, mae)
                # realiza a mutação dos filhos e os adiciona à nova população
                algoritmo_genetico.mutar(filho_1)
                algoritmo_genetico.mutar(filho_2)
                nova_populacao.append(filho_1)
                if len(nova_populacao) < algoritmo_genetico.tam_populacao:
                    nova_populacao.append(filho_2)

            # substitui a população antiga pela nova e realiza sua avaliação

            algoritmo_genetico.populacao = nova_populacao
            algoritmo_genetico.avaliar()

            if algoritmo_genetico.elitismo:
                algoritmo_genetico.populacao[np.argmin(algoritmo_genetico.avaliacao)] = filhoapto[0]

            #Para utilizar o steadyState, insira o algoritmo_genetico mais o numero de invidividuos a serem trocados
            algoritmo_genetico.avaliar()
            if algoritmo_genetico.steadyStateOn:
                algoritmo_genetico.populacao = steadyState(algoritmo_genetico,35)

            
    expMeans = np.mean(expRes, axis=1)
    expMeansNines = [countNines(i) for i in expMeans]

    figA, axA = plt.subplots()
    axA.plot(expMeans, color='red')
    axA.set(xlim=(0, algoritmo_genetico.num_geracoes), xticks=np.arange(0, algoritmo_genetico.num_geracoes),
       ylim=(0.9, 1))
    plt.savefig('Values.png', format='png')
    
    figB, axB = plt.subplots()
    axB.stairs(expMeansNines, linewidth=2.5)
    axB.set(xlim=(0, algoritmo_genetico.num_geracoes), xticks=np.arange(0, algoritmo_genetico.num_geracoes),
       ylim=(0, 4), yticks=np.arange(0, 4))
    plt.savefig('Noves.png', format='png')

    plt.show()   
    
    # encerra a execução da função main
    return 0

if __name__ == '__main__':
    main()