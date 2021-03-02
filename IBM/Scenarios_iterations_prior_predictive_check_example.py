"""
Created on Mon Dec 21 14:06:53 2020

"""
import Bembix_model_rev
import time
import numpy as np
import sys
#import tkinter as tk

start_time=time.perf_counter()

# begin_int = int(sys.argv[1])
# end_int = int(sys.argv[2])
# it_number = int(sys.argv[3])
# print(begin_int, end_int)
#catch arguments
begin_int = 0#begin number of simulations
end_int = 10#end number of simulations
it_number = 0 #number of iteration (to run this in bulks of 100,000, 1,000,000 not feasible in once)
# #sys.argv.append("FIXED")#scenario

for scenario in ['Random', 'UNIFORM', 'FIXED', 'FLEXIBLE']:#iteration-numbers will be done for every submodel
    for i in range(begin_int, end_int):
        #sample the nodes
        node_ENV = np.random.random_sample() #random sample from uniform distribution [0,1)
        node_LSF = np.random.random_sample() #random sample from uniform distribution [0,1)
        node_CA = np.random.random_sample() #random sample from uniform distribution [0,1)
    
        #sample parameters for processes local site fidelity and conspecific attraction
        sigma_lsf = np.random.uniform(0.1, 10) #range of gaussian distribution for local site fidelity; here uniform distribution between 0.5-20m?
        range_ca = np.random.uniform(0.2, 20)#range at which nests are taken into account; here uniform distribution between 0.5-20m?
        param_mindens_ca = np.random.uniform(-10, 10) #chance at zero density is then 1/(1+exp(-params_mindens_ca)); here -10,+10
        param_sigma_ca=np.random.uniform(0.1,15) #param for 'stretch' of sigmoïd response curve of density for conspecific attraction; here 0,10
        beh_excl = np.random.choice([True, False])
        #print('sigma_lsf {}, range_ca {}, param_mindens_ca {}, param_sigma_ca {}'.format(sigma_lsf, range_ca, param_mindens_ca, param_sigma_ca))    
        #get scenario
        
        print('Population {} {} {} {} {}'.format(i, scenario, node_ENV, node_LSF, node_CA))
        
        pop = Bembix_model_rev.Population(scenario=scenario,
                                          node_ENV=node_ENV, node_LSF=node_LSF, node_CA=node_CA, #nodes/chances for having the three processes
                                          sigma_lsf=sigma_lsf, range_ca=range_ca,
                                          param_mindens_ca=param_mindens_ca, param_sigma_ca=param_sigma_ca,
                                          beh_excl=beh_excl,
                                          number_ind=432, number_days=30)
        
        pop.let_it_run()
        pop.create_output(i, savepath='data/Outputs example/priorpred_run{}'.format(str(it_number)))
        #tk.mainloop()
    

print(str(time.perf_counter()-start_time), 'seconds')