start_time <- Sys.time()
#defining scenarios to analyse; get it from input
#args <- commandArgs(TRUE)
scenarios <- c("Random", "UNIFORM", "FIXED", "FLEXIBLE")
file_path_number <- 0#as.character(args[1])
prior_pred_bool <- FALSE #if the runs are for prior predictive check or not (then it is offcial run)
if (prior_pred_bool==T){
  file_path <- paste0('./data/Outputs example/priorpred_run', file_path_number)} else {
  file_path <- paste0('./data/Outputs example/official_run', file_path_number)
  }

#load Spatstat
library(ggplot2)
library(gridExtra)
library(dplyr)
library(tidyr)

#open files
params_scen <- tibble(pf=factor(),scenario=factor(), node_ENV=numeric(0), node_LSF=numeric(0),
                      node_CA=numeric(0), beh_excl=factor(),
                      sigma_lsf=numeric(0), range_ca=numeric(0),
                      param_mindens_ca=numeric(0), param_sigma_ca=numeric(0))

#Separate function in a file was created to have a function that puts all parameters in a dataframe/tibble
source("./Analysis/H_Data Params_s.R")
#looping over the different scenarios and putting the parameters values into one dataframe
for (scen in scenarios) {
  print(scen)
  b <- data_params(scen, file_path)
  params_scen <- bind_rows(params_scen, b)}

#making output file

#omit columns which contain NA values
params_scen = params_scen[,colSums(is.na(params_scen)) == 0]

#output table
if (prior_pred_bool==T){
  data_output_path <- paste0('./data/Data outputs example/priorpred/')} else {
  data_output_path <- paste0('./data/Data outputs example/official/')
  }
write.table(params_scen, sprintf(paste0(data_output_path, "Params_run%s_%s.txt"), file_path_number, Sys.Date()), sep="\t")

end_time <- Sys.time()
print(end_time-start_time)