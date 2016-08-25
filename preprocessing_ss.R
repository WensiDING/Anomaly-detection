inputPath <- "/home/wensi/workspace/tryout/result.csv"
cellPath <- "/home/wensi/workspace/tryout/cells.csv"
stopseg_Directory <- "/home/wensi/workspace/stop-segment/"
outputPath <- "/home/wensi/workspace/tryout/result_ss.csv"

library(plyr)
library(data.table)

# files of stop-segment
stopseg_Files <- data.table(file = list.files(stopseg_Directory))
stopseg_Files$file <- paste(stopseg_Directory, stopseg_Files$file, sep = '')

#read the file of cells
cells <- read.table(cellPath,header = T,sep = ";",colClasses = c("character",rep("NULL",5),"integer","integer",rep("NULL",10)))
cells <- unique(cells)

# set the values of longitude and latitude to normal
cells$longitude <- cells$longitude / (10^6)
cells$latitude <- cells$latitude / (10^6)

#function for calculating the distance
cal_distance <- function(longitudes,latitudes) {
        longitudes <- longitudes * pi / 180
        latitudes <- latitudes * pi /180
        longitude_interval <- longitudes[-1] - longitudes[-length(longitudes)]
        latitude_interval <- latitudes[-1] - latitudes[-length(latitudes)]
        lat1 <- latitudes[-c(length(latitudes))]
        lat2 <- latitudes[-c(1)]
        R <- 6371000 # Earth mean radius 
        a <- sin(latitude_interval/2)^2 + cos(lat1) * cos(lat2) * (sin(longitude_interval/2)^2)
        a <- sqrt(a)
        a[a>1] <- 1
        c <- 2 * asin(a)
        d = R * c
        return(d) 
}

distance_last_stop <- function(cuids){
        latitudes <- sapply(cuids,function(x) cells$latitude[cells$cuid==x])
        longitudes <- sapply(cuids,function(x) cells$longitude[cells$cuid==x])
        distances <- cal_distance(longitudes,latitudes)
}
operations_date <- function(data_date){
        v_mean <- mean(data_date$speed)
        v_max <- max(data_date$speed)
        duration <- sum(data_date$duration[data_date$segmentType=="STOP"])
        number_stop <- length(data_date$imsi[data_date$segmentType=="STOP"])
        if(length(data_date$cuid[data_date$segmentType=="STOP"])==0){
                cuid_final <- "0"
        }else {
                cuid_final <- tail(data_date$cuid[data_date$segmentType=="STOP"],1) }
        return (c(v_max,v_mean,number_stop,duration,cuid_final))
}

operations_imsi <- function(data_imsi){
        res_inter<-daply(data_imsi,.(date),operations_date)
        if(length(res_inter)==5){
                return(c(res_inter[1],res_inter[2],res_inter[3],NA,res_inter[4],NA,0))
        }
        cuids <- res_inter[,5]
        cuids <- cuids[cuids!="0"]
        if(length(cuids)<2)
                return (c(max(as.numeric(res_inter[,1])),mean(as.numeric(res_inter[,2])),mean(as.numeric(res_inter[,3])),sd(as.numeric(res_inter[,3])),mean(as.numeric(res_inter[,4])),sd(as.numeric(res_inter[,4])),0))
        distances <- distance_last_stop(cuids)
	# if no data for certain days, add zeros in the distances
        n_jour <- as.Date(data_imsi$date[length(data_imsi$date)])-as.Date(data_imsi$date[1])
        n_jour <- as.numeric(n_jour)
        n <- length(distances)
        dif <- n_jour-n
        distances <- append(distances,rep(0,dif))
        return(c(max(as.numeric(res_inter[,1])),mean(as.numeric(res_inter[,2])),mean(as.numeric(res_inter[,3])),sd(as.numeric(res_inter[,3])),mean(as.numeric(res_inter[,4])),sd(as.numeric(res_inter[,4])),median(distances)/1000))
}

#select imsi that are in the input file
result <- numeric()
compare <- fread(inputPath,select = "imsi")
setkey(compare,"imsi")
total <- data.table()
for(i in 1:length(stopseg_Files$file)){
        stop_seg <- fread(stopseg_Files$file[i],select = c("imsi","tsStart","tsEnd","segmentType","speed","cuidStart"),colClasses = c("imsi"="character","tsStart"="integer","tsEnd"="integer","segmentType"="character","speed"="numeric","cuidStart"="integer"))
        setkey(stop_seg,NULL)
        stop_seg <- unique(stop_seg)
        setkey(stop_seg,"imsi")
        stop_seg <- merge(stop_seg,compare,by="imsi")
        stop_seg$date <- strftime(as.POSIXct(as.numeric(stop_seg$tsStart),origin = "1970-01-01"),format = "%Y-%m-%d")
        stop_seg$duration <- stop_seg$tsEnd - stop_seg$tsStart
        setnames(stop_seg,"cuidStart","cuid")
        total <- rbind(total,stop_seg)
}

# get values of all variables for the selected imsi
stop_seg <- total
stop_seg <- stop_seg[order(stop_seg$imsi,stop_seg$date),]
result <- daply(stop_seg,.(imsi),operations_imsi)
save <- data.table(result)
save <-save[,imsi:=names(result[,1])]
#set names to variables
setnames(save,c("1","2","3","4","5","6","7"),c("v_max_ss","v_mean_ss","n_stop_mean","n_stop_sd","duree_stop_ss_mean","duree_stop_ss_sd","dis_ss"))
setkey(save,NULL)
save <- unique(save)
save<- as.data.frame(save)
# normalisation and replacing na (optional)
dimension <- 7
for( i in 2:(dimension+1)){
        maxi <- max(save[,i],na.rm = T)
        mini <- min(save[,i],na.rm = T)
        save[,i] <- (save[,i]-mini)/(maxi-mini)
        save[,i][is.na(save[,i])] <- mean(save[,i],na.rm = T)
}
write.csv(save,outputPath,row.names = F)

