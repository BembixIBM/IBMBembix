#*********************************************#
#Script to filter subsequent nests from data###
#*********************************************#
library(dplyr)
library(tidyr)

records <- read.table("Raw data/Records.txt", header=T, sep=";")
days <- read.table("Raw data/Days.txt", header=T, sep=";")

head(records)
#View(days)

##add Daynumber to records (instead of date, easier to work with)
records <- records %>% left_join(dplyr::select(days, Dagnummer, Datum), by=c("Datum")) %>%
#delete records that weren't at a nest (were records for CMR-analysis) and delete males
  drop_na(NestID) %>% filter(Opmerkingen != "Male")


####Real nests####
#make dataframe listing wespID + nestID real nests according to 4 assumptions
#1) if prey brought to nest
prey_feeding <- records %>% filter(Prooi==1) %>% dplyr::select(WespID, NestID)
#2) if same individual is seen at same nest for several days (without prey)
several_days <- records %>% group_by(WespID, NestID, Dagnummer) %>% summarise(n=n()) %>% ungroup() %>%
  group_by(WespID, NestID) %>% summarise(n=n()) %>%
  filter(n>1)  %>%
  dplyr::select(WespID, NestID)
#3) if prey are found next to nest or wasp cleans nest from prey residu
prey_atnest <- records %>% filter(grepl('Prooi|prooi', Opmerkingen))  %>% dplyr::select(WespID, NestID)
#4) if individual was intensively digging at a nest during one whole day
back_oneday <- records %>% filter(Terug==1) %>% dplyr::select(WespID, NestID)
several_times_oneday <- records %>% group_by(WespID, NestID, Dagnummer) %>% summarise(n=n()) %>%
  filter(n>1)  %>%
  dplyr::select(WespID, NestID)
closed_behind <- records %>% filter(Toe==1) %>% dplyr::select(WespID, NestID)

realnests <- prey_feeding %>% bind_rows(several_days) %>%
  bind_rows(prey_atnest) %>% bind_rows(several_times_oneday) %>%
  bind_rows(back_oneday) %>% bind_rows(closed_behind) %>%
  distinct()
nrow(realnests)
#Amount of individuals that have 'real nests'
length(unique(realnests$WespID))
realnests <- realnests %>% mutate(real_nest = rep(1, nrow(realnests)))

#write.table(realnests, file="Derived data/RealNests.txt", sep=";")


####Parasitised nests#####
par_record <- records %>% filter(Parasiet==1) %>% dplyr::select(NestID, Parasiet)
par_record <- unique(par_record)
#all nests
nrow(par_record)
#real nests
par_record_real <- inner_join(realnests, par_record, by="NestID")
nrow(par_record_real)

#write.table(par_record, file="Derived data/ParasitizedNests.txt", sep=";")

#####Subsequent nests#####

#Join records and dataset with real nests
records_real <- records %>% left_join(realnests, by=c("WespID", "NestID")) %>%
  filter(real_nest==1)
nrow(records_real)

#write.table(records_real, "Derived data/Records_realnests.txt", sep=";")
#Get the first day/record of each nest (always WespID and NestID coupled)
#first, filter the first day of each wesp-nesten 
startdays <- records_real %>% group_by(WespID, NestID) %>% filter(row_number(abs(Dagnummer))==1)
freq_startdays <- startdays %>% group_by(Dagnummer) %>% summarise(n=n())
hist(startdays$Dagnummer)

#write.table(freq_startdays, "Derived data/Freq_startingday.txt", sep=";")

#subseqsuent nests
#first filter first day of each wesp-nest
nest_sequence <- records_real %>% group_by(WespID, NestID) %>% filter(row_number(abs(Dagnummer))==1) %>%
#then, filter give number to subsequent nest per individual
  ungroup() %>% group_by(WespID) %>% mutate(nest_number= row_number((abs(Dagnummer))))
View(nest_sequence)


#get max of nest_number per individual
n_nests <- nest_sequence %>% group_by(WespID) %>% summarise(nnests = max(nest_number))
#frequency of number of nests
freq_n_nests <- n_nests %>% group_by(nnests) %>% summarise(n=n())

#write.table(freq_n_nests, "Derived data/Freq_number_nests.txt", sep=";")

#make dataset with links (so WespID nest1 nest2)
subs_nests <- data.frame(WespID=character(), Nest1=numeric(), Nest2=numeric(), startday1=numeric(), startday2=numeric())

for (wesp in unique(realnests$WespID)){
  #filter in subs_nests
  nests <- nest_sequence %>% filter(WespID==wesp)
  if (nrow(nests) >= 2){
    for (i in 1:(nrow(nests)-1)){
      subs_nests <- subs_nests %>% add_row(WespID=wesp, Nest1=nests$NestID[i], Nest2=nests$NestID[i+1],
                                           startday1=nests$Dagnummer[i], startday2=nests$Dagnummer[i+1])
    }
  }
}
nrow(subs_nests)
View(subs_nests)

#Frequency of period between subsequent nests
seq_periods <- as.data.frame(seq(1:30))
colnames(seq_periods) <- c("period")

freq_period <- subs_nests %>% mutate(period = startday2-startday1) %>% group_by(period) %>% summarise(n=n())

freq_period <- freq_period %>% right_join(seq_periods) %>% mutate(n=coalesce(n, 0)) %>% arrange(period)

#write.table(freq_period, "Derived data/Freq_periods.txt", sep=";")

#write.table(subs_nests, "Derived data/SuccessiveNestsperWasp.txt", sep=";")
