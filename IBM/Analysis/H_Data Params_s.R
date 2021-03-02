#function to analyse spatial pattern, returns list with 3 tibbles: densities, ripley'sK values, mark corr values
data_params <- function(scenario_run, file_path){
  
  #open all parameters files for current scenario
  Parameters_files <- list.files(path=file_path, pattern=sprintf('Parameters %s *', scenario_run))
  #initialising dataframe for current scenario_run
  params_scen <- tibble(pf=factor(), scenario=factor(), node_ENV=numeric(0), node_LSF=numeric(0),
                        node_CA=numeric(0), beh_excl=factor(),
                        sigma_lsf=numeric(0), range_ca=numeric(0),
                        param_mindens_ca=numeric(0), param_sigma_ca=numeric(0))
  #for every scenario, parameters are extracted from parameters-files
  for (file_title in Parameters_files){
    title_full = paste(file_path, file_title, sep="/")
    d = read.table(title_full, header=T)
    params_scen <- add_row(params_scen,
                           pf=file_title, scenario=d[[1]],
                           node_ENV=d[[2]],
                           node_LSF=d[[3]],
                           node_CA=d[[4]],
                           beh_excl=d[[5]],
                           sigma_lsf=d[[6]],
                           range_ca=d[[7]],
                           param_mindens_ca=d[[8]],
                           param_sigma_ca =d[[9]] )
  }
  return(params_scen)
}