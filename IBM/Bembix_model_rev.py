'''
Created on 07-12-2020
'''

#import matplotlib.image as mpimg
# import matplotlib
# matplotlib.use('Agg')
#import tkinter as tk
import numpy as np
import math
#import colorsys
import os
import datetime

save_path = 'data' #submap where to save the output


"""
*************************************************************
General functions
*************************************************************
"""

def choose_processes(node_ENV, node_LSF, node_CA):
    """
    function to choose which mechanisms are present (for population, individual, or individual choice-step)
    The presence of a mechanism is chosen according to its 'node': the probability or relative strength
    This function returns 3 times True/False for environment, local site fidelity and conspecific attraction respectively
    """
    bool_ENV = bool(np.random.choice((1,0), p=[node_ENV, 1-node_ENV]))
    bool_LSF = bool(np.random.choice((1,0), p=[node_LSF, 1-node_LSF]))
    bool_CA = bool(np.random.choice((1,0), p=[node_CA, 1-node_CA]))
    
    return bool_ENV, bool_LSF, bool_CA

'''
***********************************************************************************************
Initialisation of the model
Field data to get 1) number of nests per individual, 2) starting day, 3) period between nests
***********************************************************************************************
'''
#Distribution of number of nests for each individual
#Frequency of number of nests from field data
load_numbernests = np.loadtxt('Freq_number_nests.txt', delimiter=';', usecols=(1,2,), skiprows=1)
number_nests_fn = sum([a*b for a, b in zip(load_numbernests[:,1], load_numbernests[:,0])])
p_number_nests = (load_numbernests[:,[1]]/sum(load_numbernests[:,[1]])[0]).flatten().tolist() #[0.7639, 0.1806, 0.0486, 0.0069]

#Starting day: the number of new wasps that made a nest each day
#Load frequency of starting day from field data and change into chance (p) of starting a nest on every day
load_startingday = np.loadtxt('Freq_startingday.txt', delimiter=';', usecols=(1,2,), skiprows=1)
number_nests_sd = sum(load_startingday[:,[1]])[0]
p_startingday = (load_startingday[:,[1]]/number_nests_sd).flatten().tolist()

#Distribution of number of days between two consecutive nests of one individual
#Load frequency of period between two nests
load_periods = np.loadtxt('Freq_periods.txt', delimiter=';', usecols=(1,2,), skiprows=1)
number_subs_nests = sum(load_periods[:,[1]])[0]
p_periods = (load_periods[:,[1]]/number_subs_nests).flatten().tolist()

'''
# ******************************************************************************
# Definition of classes
# class Visual is to make a visual output
# Second, classes are defined to make Wasp, Nest and Population objects
# ******************************************************************************
# '''
 
# class Visual:
#     '''This class arranges the visual output.'''
#     def __init__(self, max_x, max_y):
#         '''Initialize the visual class'''
#         self.zoom = 5
#         self.max_x = max_x
#         self.max_y = max_y
#         self.root = tk.Tk()
#         self.canvas = tk.Canvas(self.root, 
#                                 width =  self.max_x * self.zoom, 
#                                 height = self.max_y * self.zoom) #create window
#         self.canvas.pack()
#         self.canvas.config(background = 'white')
#         self.squares = np.empty((self.max_x, self.max_y),dtype=object)
#         self.initialize_squares()
           
#     def create_nest(self,nest, day, number_days):       
#         '''Create circle for nest'''
#         x, y = nest.x, nest.y
#         radius = 0.5
#         #generating colour according to day
#         color = float(day/float(number_days))
#         if color < 0:
#             color = 0
#         elif color > 1:
#             color = 1
#         #color range including all colours is best in hls system    
#         red, green, blue = colorsys.hls_to_rgb(color, 0.5, 1)
#         rgb = int(red*255), int(green*255), int(blue*255)
#         hex_code = '#%02x%02x%02x' % rgb
           
#         return self.canvas.create_oval((x - radius) * self.zoom,
#                                         (y - radius) * self.zoom,
#                                         (x + radius) * self.zoom,
#                                         (y + radius) * self.zoom,
#                                         outline=str(hex_code), 
#                                         fill=str(hex_code))                                      
           
#     def color_square(self, resources, x, y):
#         '''Colors the square relative to the suitability of that point'''
#         '''white is 1, black is 0'''
#         #trying gray values: rgb are equal to each other then        
#         color = float(resources)
#         # if color < 0:
#         #     color = 0
#         if color > 1:
#             color = 1
   
#         blue = int(255*color)    
#         green = int(255*color)
#         red = int(255*color)     
           
#         rgb = red, green, blue     
#         hex_code = '#%02x%02x%02x' % rgb
#         if color < 0: #for the -1, outside of the environment
#             hex_code = '#%02x%02x%02x' % (255,250,205)
#         self.canvas.itemconfigure(self.squares[x, y],fill = str(hex_code))
           
#     def initialize_squares(self):
#         '''returns a square (drawing object)'''
#         for x in range(self.max_x):
#             for y in range(self.max_y):
#                 self.squares[x, y] = self.canvas.create_rectangle(self.zoom * x,
#                                                       self.zoom * y, 
#                                                       self.zoom * x + self.zoom,
#                                                       self.zoom * y + self.zoom,
#                                                       outline = '', 
#                                                       fill = 'black')

class Nest:
    """
    Creates nest objects with a position, day of initialization and which mechanisms (bool) are used to choice nest location
    """
    def __init__(self, x, y, day, bool_ENV, bool_LSF, bool_CA):
        self.x = x
        self.y = y
        self.day=day
        self.bool_ENV = bool_ENV
        self.bool_LSF = bool_LSF
        self.bool_CA = bool_CA
        
    def __repr__(self):
        return 'Nest{}'.format(id(self))
        
    def __str__(self):
        return '({},{})'.format(self.x, self.y)
    
class Wasp:
    """
    Class wasp, which creates a Bembix rostrata individual
    has function search, which lets the wasp search for a nest according to a combination of max 3 different mechanisms
    """
    #initialise object wasp with needed properties
    def __init__(self, pop,
                bool_ENV, bool_LSF, bool_CA, #mechanisms that are present (TRUE/FALSE) 
                starting_day, number_nests, periods):
        
        self.pop = pop #population the wasp belongs to, for inheritance of its state variables
        
        #variables important for timing
        self.starting_day = starting_day #starting day of the wasp
        self.day_next_nest = starting_day #day of next nest building
        self.number_nests = number_nests #number of nests the wasp will make in total
        #self.distances=distances #list with distances between subsequent nests
        self.periods = periods #list with periods between the subsequent nests
        
        #variables for processes/search functions
        self.bool_ENV, self.bool_LSF, self.bool_CA = bool_ENV, bool_LSF, bool_CA #depending on scenario
        self.no_CA=False #to initialise option for non-mutually exclusive LSF and CA
        
        #variables that are properties of the wasp
        self.nests = [] #list with objects Nests for this individual

    
    def search(self, environment):
        chosen = False #init chosen, if chosen is True, while loop is exited
        while not chosen:
            #select randomly a position to evaluate
            y_rn, x_rn = np.random.uniform(0,environment.shape[0]), np.random.uniform(0,environment.shape[1])
            #check if it is inside the focal landscape, while not, choose another random position
            while environment[int(y_rn), int(x_rn)] == -1: 
                y_rn, x_rn = np.random.uniform(0,environment.shape[0]), np.random.uniform(0,environment.shape[1])
            
            #if an individual already has made a nest and behavioural mechanisms are not mutually exclusive
            #if bool_LSF and bool_CA are both TRUE and beh_excl is TRUE, then only local site fidelity
            if (self.nests and self.pop.beh_excl and self.bool_LSF and self.bool_CA):
                #print(self.nests, self.bool_CA, self.bool_LSF)
                self.no_CA=True
            else:
                self.no_CA=False
            
            #if mechanisms are present, position is assessed according to that mechanism
            p_env = self.eval_env(environment, x_rn, y_rn) if self.bool_ENV else None
            #when wasp hasn't made nests yet, local site fidelity is not possible 
            p_lsf = self.eval_lsf(x_rn, y_rn) if (self.bool_LSF and self.nests) else None
            #if only first nest in population or non-mutually exclusive with LSF, conspecific attraction is not possible
            p_ca = self.eval_ca(x_rn, y_rn) if (self.bool_CA and self.pop.number_nests>0 and not self.no_CA) else None

            #probability is 1 if scenario is random or all mechanisms are None (bool_ENV,bool_LSF ,bool_CA) or False
            #or if all chances are None
            if (self.pop.scenario=='Random' or #if scenario is random
                not (self.bool_ENV or self.bool_LSF or self.bool_CA) or #if no mechanism is available
                (p_env == p_lsf == p_ca == None)): #if all chances are None (non-existent, see previous)
                
                chance = 1
                
            else:
                #count which probabilities are not None, to use as denominator to calculate average
                chances_notNone = len(list(filter(None, [p_env, p_lsf, p_ca])))
                #if all chances are zero, whole chance is 0 (all None is dealt with in previous statement)
                if chances_notNone==0:
                    chance=0
                #otherwise, mean of chances is calculated
                else:
                    #when the p's are None, they are filtered
                    chance = sum(filter(None, [p_env, p_lsf, p_ca]))/chances_notNone
                    if chance >1:#flatting off the Gaussian curve when chance >1; when a very small sigma is chosen, this is possible
                        chance=1
            chosen = bool(np.random.choice((1,0), p=[chance, 1-chance]))
        
        self.dig(x_rn, y_rn)
        
        #if scenario is flexible, new mechanisms are chosen for next choice
        if self.pop.scenario=='FLEXIBLE':
            self.bool_ENV, self.bool_LSF, self.bool_CA = choose_processes(self.pop.node_ENV, self.pop.node_LSF, self.pop.node_CA)
        
    def eval_env(self, environment, x_eval, y_eval):
        """
        Function to get evaluation of environment, the suitability of a certain position
        is the chance of making a nest at the position x,y based on the environment
        """
        chance = environment[int(y_eval), int(x_eval)]
        
        return chance
        
    def eval_lsf(self, x_eval, y_eval):
        """
        Function to get evaluation of local site fidelity,
        is the chance of making a nest at that distance from position x,y to previous nest
        """
        #calculate distance from previous nest
        x_w, y_w = self.nests[-1].x, self.nests[-1].y
        dist = math.sqrt((x_eval - x_w)**2 + (y_eval - y_w)**2)
        #dist in meters
        dist_m = dist*self.pop.pixel_dist
        #calculate probability of that distance according to Gaussian kernel around previous nest
        chance = (1/( self.pop.sigma_lsf*np.sqrt( 2*np.pi ) ))*np.exp(( -1/2 )*( dist_m**2 )/( self.pop.sigma_lsf**2 ))
        
        return chance
    
    def eval_ca(self, x_eval, y_eval):
        """
        Function to get evaluation of conspecific attraction,
        is the chance of making a nest at the density found of other nests at position x,y
        """
        #calculate amount of nests within radius/range
        number_nests_within_range = self.calc_kernel_ca(x_eval=x_eval, y_eval=y_eval)
        #calculate chance according to sigmoid function
        chance = 1/(1 + np.exp(-(self.pop.param_mindens_ca + self.pop.param_sigma_ca*number_nests_within_range)))
        
        return chance
    
    def calc_kernel_ca(self, x_eval, y_eval):
        """
        Helper function that calculates number of nests in given range at position x_eval, y_eval
        """
        #get numpy-array of all nests in population
        pop_nests_ar = np.array(self.pop.pop_nests)
        #get x and y coordinates
        x_pop = pop_nests_ar[:,0]
        y_pop = pop_nests_ar[:,1]
        #calculate distances of eval-position to all nests (with numpy-methods)
        dist_nests = np.sqrt(( x_pop - x_eval )**2 + ( y_pop - y_eval )**2)
        dist_nests_m = dist_nests*self.pop.pixel_dist#get distance in m
        within_range = sum([1 if a <= self.pop.range_ca else 0 for a in dist_nests_m])#count which are within range

        return within_range
    
    def dig(self, x, y):
        """
        A wasp digs a nest
        number of nests it will make is minus one
        the day of the next nest is added with period between nests
        """
        self.number_nests -= 1
        self.nests.append(Nest(x, y, self.day_next_nest, self.bool_ENV, self.bool_LSF, self.bool_CA))
        if self.number_nests !=0:
            self.day_next_nest += self.periods[-self.number_nests]
            
    def __str__(self):
        return "{} with starting day={}, next nest day={}, nests to make ={}".format(
            self.__class__.__name__, self.starting_day, self.day_next_nest, self.number_nests)
    
    def __repr__(self):
        return "Wasp{}".format(id(self))
        
class Population:
    """
    Class population, which will contain all the wasps and change in time
    """
    
    def __init__(self, scenario,
                node_ENV, node_LSF, node_CA, #nodes/chances for having the three mechanisms
                sigma_lsf, range_ca, param_mindens_ca, param_sigma_ca,
                p_startingdays = p_startingday, p_periods = p_periods, p_number_nests=p_number_nests,
                beh_excl=False,
                number_ind=20, number_days=30, pixel_dist = 0.5,
                environment=np.load('Environment_array.npy')):
        
        #variables important for mechanisms/search functions
        self.scenario= scenario #scenario: random, 'UNIFORM' uniform strategy (population), 'FIXED' fixed strategy (individuals), 'FLEXIBLE' flexible strategy (per choice)
        self.node_ENV, self.node_LSF, self.node_CA = node_ENV, node_LSF, node_CA
        self.beh_excl = beh_excl
        
        #parameters for mechanisms
        self.sigma_lsf = sigma_lsf
        self.range_ca = range_ca
        self.param_mindens_ca = param_mindens_ca
        self.param_sigma_ca = param_sigma_ca
        
        #variables describing initial population/landscape
        self.number_ind = number_ind
        self.number_days = number_days
        self.pixel_dist = pixel_dist
        self.environment = environment
        
        #probabilities for starting day, periods and number of nests for individuals in the population
        #from field data
        self.p_startingdays = p_startingdays
        self.p_periods = p_periods
        self.p_number_nests = p_number_nests
        
        #properties of the population that are transient during run
        self.population = [] #init the list with wasps in the population
        self.number_nests = 0 #init total number of nests of the population
        self.pop_nests = []
        self.day_count = 1

        self.initialise(self.number_ind) #wasps created and added to the population



        # #visualisation of the landscape
        # self.x_max, self.y_max = self.environment.shape[1], self.environment.shape[0]
        # self.visual = Visual(self.x_max, self.y_max)
        # self.visual.initialize_squares()
        # for y in range(self.y_max):
        #     for x in range(self.x_max):
        #         self.visual.color_square(self.environment[y,x], x, y)
                
    def init_timing_wasp(self):
        '''Helper function to initialise parameters for timing of a wasp, according to population preconditions'''
        #choose number of nests will be made
        n_nests = np.random.choice(np.arange(1,len(self.p_number_nests)+1), p=self.p_number_nests)
        #choose periods, make sure starting day + sum of periods is !> number of days
        timing_chosen = False
        while not timing_chosen:
            startingday_wasp = np.random.choice(np.arange(1, len(self.p_startingdays)+1), p=self.p_startingdays)
            periods_wasp = np.random.choice(np.arange(1, len(self.p_periods)+1), n_nests -1, p=self.p_periods).tolist()
            #if the last day of the final nest is outside of observation period (30 days)
            if startingday_wasp + sum(periods_wasp) <= self.number_days:
                timing_chosen=True
        
        return(n_nests, startingday_wasp, periods_wasp)
    
    def initialise(self, number_ind):
        '''Wasps created and added to the population'''
        
        if self.scenario=='UNIFORM':
            #mechanisms are fixed for whole population, same for every wasp
            bool_ENV, bool_LSF, bool_CA = choose_processes(self.node_ENV, self.node_LSF, self.node_CA)
            
            for _ in range(number_ind):
                #get timing info for the wasp
                n_nests, starting_day, periods_ind = self.init_timing_wasp()
                #add the wasp to the population
                self.population.append(Wasp(pop=self,
                                            bool_ENV=bool_ENV, bool_LSF=bool_LSF, bool_CA=bool_CA, 
                                            starting_day = starting_day,
                                            number_nests = n_nests,
                                            periods = periods_ind))
                
        elif (self.scenario=='FIXED' or self.scenario=='FLEXIBLE'):
            #mechanisms are different for every individual
            #for FIXED: here the strategy for each indvidual is chosen
            #for FLEXIBLE: here the initial strategy for each individual is chosen
            for _ in range(number_ind):
                bool_ENV, bool_LSF, bool_CA = choose_processes(self.node_ENV, self.node_LSF, self.node_CA)
                
                #get timing info for the wasp
                n_nests, starting_day, periods_ind = self.init_timing_wasp()
                #add the wasp to the population
                self.population.append(Wasp(pop=self,
                                            bool_ENV=bool_ENV, bool_LSF=bool_LSF, bool_CA=bool_CA, 
                                            starting_day = starting_day,
                                            number_nests = n_nests,
                                            periods = periods_ind))
                
        else :
            #then scenario is normally random
            for _ in range(number_ind):
                #get timing info for the wasp
                n_nests, starting_day, periods_ind = self.init_timing_wasp()
                #add the wasp to the population
                self.population.append(Wasp(pop=self,
                                            bool_ENV=None, bool_LSF=None, bool_CA=None, 
                                            starting_day = starting_day,
                                            number_nests = n_nests,
                                            periods = periods_ind))
                
                
    def __str__(self):
        return '{} with {} wasps'.format(self.__class__.__name__, self.number_ind) #+ '\n' + '\n'.join(
            #str(repr(ind)) for ind in self.population)
        
    def __repr__(self):
        return "Population object"
    
    def day(self):
        for ind in self.population:
            #print(ind.scenario) 
            if ind.day_next_nest == self.day_count and ind.number_nests > 0:#if the day of building its next nest is equal to current day and it has still remaining nests to build
                ind.search(self.environment)
                # self.visual.create_nest(ind.nests[-1], self.day_count, self.number_days)#nest is visualised
                self.number_nests += 1 #number of nests of the population +1
                self.pop_nests.append((ind.nests[-1].x, ind.nests[-1].y))#add position of nest to list of nests in the population
                #print(len(self.pop_nests), self.number_nests)
                #print(self.pop_nests[-1])
        self.day_count +=1
        
    def let_it_run(self):
        for _ in range(1, self.number_days+1):
            #print('DAY {}'.format(i))
            self.day()
            
    def create_output(self, number, savepath = save_path):
        '''
        **********************************************************************
        Function to create output
        3 files will be created: parameters, output and distances
        ************************************************************************
        '''
        #output file with waspID, nestID, x, y, day
        file_name = 'Output {} {} {}.txt'.format(self.scenario, number, datetime.datetime.now().strftime("%d_%m_%Y %H_%M"))
        writer = open(os.path.join(savepath, file_name), 'w')
        writer.write('waspID\tnestID\tx\ty\tday\tbool_ENV\tbool_LSF\tbool_CA\n')
        for wasp in self.population:
            for nest in wasp.nests:
                writer.write(repr(wasp) +'\t'+ repr(nest) +'\t'+ str(nest.x*self.pixel_dist) +'\t'+ str(nest.y*self.pixel_dist) +'\t'+ str(nest.day) +'\t'+
                             str(nest.bool_ENV) +'\t'+ str(nest.bool_ENV) +'\t'+ str(nest.bool_CA) +'\t'+ '\n')
        writer.close()
        
        #output file with waspID, nest1, nest2, distance
        file_name_w = 'Distances {} {} {}.txt'.format(self.scenario, number, datetime.datetime.now().strftime("%d_%m_%Y %H_%M"))
        writer_dist = open(os.path.join(savepath, file_name_w), 'w')
        writer_dist.write('waspID\tnest1\tnest2\tdistance\n')
        for wasp in self.population:
            if len(wasp.nests) > 1:
                for i in range(len(wasp.nests)-1):
                    dist = math.sqrt((wasp.nests[i].x - wasp.nests[i+1].x)**2 + (wasp.nests[i].y - wasp.nests[i+1].y)**2)*self.pixel_dist
                    writer_dist.write(repr(wasp) + '\t' + repr(wasp.nests[i]) + '\t' + repr(wasp.nests[i+1]) + '\t' + str(dist) + '\n')
        writer_dist.close()
        #output file with parameters
        file_name_par = 'Parameters {} {} {}.txt'.format(self.scenario, number, datetime.datetime.now().strftime("%d_%m_%Y %H_%M"))
        writer = open(os.path.join(savepath, file_name_par), 'w')
        writer.write('scenario\tnode_ENV\tnode_LSF\tnode_CA\tbeh_excl\tsigma_lsf\trange_ca\tparam_mindens_ca\tparam_sigma_ca\n')
        writer.write(self.scenario +'\t'+ str(self.node_ENV) +'\t'+ str(self.node_LSF) +'\t'+ str(self.node_CA) +'\t'+ 
                     str(self.beh_excl) + '\t' +
                     str(self.sigma_lsf) +'\t'+ str(self.range_ca) +'\t'+ str(self.param_mindens_ca) +'\t'+ str(self.param_sigma_ca) +'\n')
        writer.close()
        

# '''
# # ******************************************************************************
# # Models are run and output is created
# # ******************************************************************************
# # '''

# #sample params
# node_ENV = np.random.random_sample()#1#round(np.random.uniform(0.0, 1.0), 2) [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
# node_LSF = np.random.random_sample()#1#round(np.random.uniform(0.0, 1.0), 2)
# node_CA = np.random.random_sample()#1#round(np.random.uniform(0.0, 1.0), 2)
# #params mechanisms
# sigma_lsf = np.random.uniform(0.1, 10) #range of gaussian distribution for local site fidelity; here uniform distribution between 0.5-20m?
# range_ca = np.random.uniform(0.2, 5)#range at which nests are taken into account; here uniform distribution between 0.5-20m?
# param_mindens_ca = np.random.uniform(-10, 0) #chance at zero density is then 1/(1+exp(-params_mindens_ca)); here -10,+10
# param_sigma_ca=np.random.uniform(0.2, 20) #param for 'stretch' of sigmoïd response curve of density for conspecific attraction; here 0,10
# beh_excl = np.random.choice([True, False])
# #submodel
# scenario = np.random.choice(['Random', 'UNIFORM', 'FIXED', 'FLEXIBLE'])
# """
# ***scenarios***
# 'Random'
# 'UNIFORM' uniform strategy (population)
# 'FIXED' fixed strategy (individuals)
# 'FLEXIBLE' flexible strategy (per choice)
# """

# pop = Population(scenario=scenario,
#                   p_startingdays=p_startingday, p_periods=p_periods, p_number_nests=p_number_nests,
#                 node_ENV=node_ENV, node_LSF=node_LSF, node_CA=node_CA, #nodes/chances for having the three mechanisms
#                 sigma_lsf=sigma_lsf,
#                 range_ca=range_ca, param_mindens_ca=param_mindens_ca, param_sigma_ca=param_sigma_ca,
#                 beh_excl=True,
#                 number_ind=432, number_days=30)
# pop.let_it_run()

# pop.create_output(1, savepath='data')
      
# print('{} population {}'.format(scenario, 1))
# print('node env {}, node lsf {}, node ca {}'.format(node_ENV, node_LSF, node_CA))
# tk.mainloop()