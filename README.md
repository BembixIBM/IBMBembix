# IBMBembix
source code and data for manuscript

## Microhabitat model
- 'Microhabitat Final Model with iterations - scales.R': source code for the microhabitat model with INLA, including 10 iterations for cross-validation (if uncommented), and choices of scales (default 1). Output will be put in the folder 'output_iterations', where a folder named 'scale_*scale*' should be made.
- 'Microhabitat Final Model visualisations of iterations.R': source code for making graphs of the microhabitat model. Datafiles needed in this script are made by 'Microhabitat Final Model with iterations.R'. Example data used in the manuscript are present in the map /output_iterations/scale_1 (except for making the graph of the spatial field, for which the previous script should be run).
- Folder 'output_iterations': folder 'scale_1' with example summary output used in the manuscript, to be used in the visualisation-script; 
- Folder 'data' with 'MicrohabitatModel_FullData_04062020.csv': raw datafile to start microhabitat model; 'RegPoints_04062020.txt': raw datafile of the regular points to make predictions of the model, the habitat suitability map; 'RealNests_withcoordinates.txt': to plot the nests; a shapefile 'Study_area_thesis': the delineation of the study site; RegPoints_clipStudyArea.scsv: used in the visualisation-script to delineate points within study area (as all points for which predictions are made include points that were not included during nest-searching: an edge/buffer around the study site).

Raw GIS data (rasters: raw data - CIR (band 1 NIR, band 3 R) DEM and derived - NDVI, insolation, slope) can be found on https://drive.google.com/drive/folders/12TNHrsqpTIvBvV4oNfkj-UeUmv68ufLx?usp=sharing

## IBM
- Bembix_model_rev.py: actual IBM, used by all Scenarios_iterations_*_s.py
- Scenarios_iterations_example.py: loops for all submodels (Random, UNIFORM, FIXED, FLEXIBLE) to make several runs for each submodel. Example is given for 10 iterations for each submodel. This output is added in the map Outputs example/official_run0/
- Scenarios_iterations_prior_predictive_check_example.py: same as previous, but for the prior predictive check. This output is added in the map Outputs example/priorpred_run0/
- Freq_number_nests.txt, Freq_periods.txt, Freq_startingday.txt: input to initialize the model and set the boundary conditions.
- Environment_array.npy: the environment (from microhabitat model) given as a numpy-arrray (resolution: 50cmx50cm) used for one of the nest choice mechanisms.
- 'Params_get_priors_s.R' and 'Summary_stats_s.R': scripts to extract summary stats and parameters from the model simulations. Takes input from the folder 'Outputs example' and creates output in the folder 'Data outputs example', where a folder exists for the prior predictive simulations (priorpred) and the actual simulations (official).
- Folder 'Analysis': helper scripts for the two previous scripts

Note: examples are given here in the output-folders (for 10 runs for each submodel). Actual data used in the manuscript is stored in the ABC-section.

## ABC
- directory 'Field data analyses': 'Extract_data_from_fieldrecords.R' makes datafiles from the raw data (coordinates and records in folder 'Raw data') to be used to make summary statistics ; 'Make_Summary_stats_field.Rmd': calculated the summary stats (as in Summary_stats_s.R in IBM-section)
- 'Field data analyses/Summary_stats_field.txt' is the output of the summary stats of the field data.
- 'ABC_Bembix_prior_predictive_check.Rmd': the prior predictive check script, to delineate useful parameter space. Uses data from folder 'Data outputs'
- 'ABC_Bembix_rev.Rmd': the actual ABC analysis with model selection.
- 'H_modelselectionABC.R': helper script coded with the actual model selection, custom made, to be able to add weights to the summary statistics.
- Folder 'Data outputs': the actual summary and parameters data-outputs from the prior predictive check (200,000 simulations) and the actual run (1,000,000 simulations); these are calculated with Params_get_priors_s.R and Summary_stats_s.R from IBM-section (the raw output data from the IBM is too large to be put online, examples can be found in the IBM-section).



Note: a selection of 'real nests' are made within the scripts (see 'Field data analyses/Extract_data_from_fieldrecords.R'), these are nests that have multiple visits on several days, where prey were brought to, or where prolonged digging was seen. This species is known for doing test diggings, and we wanted to exclude these from the analyses.
