eventsDirectory <-
        "/srv/data/spool/anomaly_detection/events_sorted_by_imsis/"
cellPath <- "cells.csv"
resultPath <- "/home/wensi/workspace/tryout/result.csv"
percent <- 0.6

# load libraries
library(data.table)
library(plyr)

# dataframe eventsFiles with two columns $imsi and $file (the exact path of every file)
eventsFiles <- data.table(file = list.files(eventsDirectory))
eventsFiles$imsi <-
        vapply(
                eventsFiles$file, FUN.VALUE = character(1),
                FUN = function(x) {
                        strsplit(x, split = "\\.")[[1]][1]
                }
        )
eventsFiles$file <-
        paste(eventsDirectory, eventsFiles$file, sep = '')


#read the file of cells and select only certain columns (mcc;mnc;lac;ci;latitude;longitude;radius)
cells <- read.table(cellPath,header = T,sep = ";")
cells <- cells[c(2,3,4,5,7,8)]

#construct cgi with the first four columns
cells$cgi <-
        paste(cells$mcc, cells$mnc, cells$lac, cells$ci, sep = "-")

#initialise the container of results
variables <- numeric()
list_imsi <- character()

#function for calculating the distance
cal_distance <- function(longitude_interval,latitude_interval,lat) {
        longitude_interval <- longitude_interval * pi / 180
        latitude_interval <- latitude_interval * pi / 180
        lat1 <- lat[-c(length(lat))] * pi / 180
        lat2 <- lat[-c(1)] * pi / 180
        R <- 6371000 # Earth mean radius
        a <-
                sin(latitude_interval / 2) ^ 2 + cos(lat1) * cos(lat2) * (sin(longitude_interval /
                                                                                      2) ^ 2)
        a <- sqrt(a)
        a[a > 1] <- 1
        c <- 2 * asin(a)
        d = R * c
        return(d)
}

#function for creating four variables with data of one imsi in one day
operations <- function(events) {
        # loop over the whole data, keep the first entrance event in one certain cell if there are several consecutive entrances
        i <- 1
        j <- 2
        list_sel <- vector('logical')
        list_sel <- append(list_sel,TRUE)
        while (j <= length(events$cgi)) {
                if (events$cgi[i] == events$cgi[j] |
                    cal_distance(
                            events$longitude[i] - events$longitude[j],events$latitude[i] - events$latitude[j],c(events$latitude[i],events$latitude[j])
                    ) == 0) {
                        list_sel <- append(list_sel,FALSE)
                        j <- j + 1
                }
                else{
                        i <- j
                        list_sel <- append(list_sel,TRUE)
                        j <- j + 1
                }
        }
        events <- events[list_sel,]
        # situation: one event in a day
        if (length(events$cgi) < 2) {
                return (c(0,0,1,24 * 3600))
        }
        else{
                # construct intervals for time,latitude and longitude
                events1 <- events[-c(1),]
                events2 <- events[-c(length(events$timestamp)),]
                interval <- events1$timestamp - events2$timestamp
                longitude_interval <-
                        events1$longitude - events2$longitude
                latitude_interval <-
                        events1$latitude - events2$latitude
                #calculate distance
                distance <-
                        cal_distance(longitude_interval,latitude_interval,events$latitude)
                rm(events1,events2,longitude_interval,latitude_interval)
                sel <- (interval != 0)
                interval <- interval[sel]
                distance <- distance[sel]
                vitesse <- distance / interval
                sel <- (distance < 2000) & (vitesse > 100)
                interval <- interval[!sel]
                distance <- distance[!sel]
                vitesse <- vitesse[!sel]
                if (length(interval) == 0) {
                        return (c(0,0,1,24 * 3600))
                }
                else{
                        #calculate the number of events in one day
                        times <- length(interval) + 1
                        # indice for calculating the sum of stop time
                        indic <- (interval > 1800) & (distance < 4000)
                        
                        return(c(
                                max(vitesse),mean(vitesse),times,sum(interval[indic])
                        ))
                }
        }
}

# choose the length of files for training
total <- floor(length(eventsFiles$file) * percent)

for (i in 1:total) {
        #read the data file
        data <- read.csv(eventsFiles$file[i],header = T)
        data <- data[c(1,7,8,10)]
        
        #choose only the record with event==enter
        data <- data[data$event == "CELL_ENTER",]
        
        # merge the file with the information of cells
        events <- merge(data, cells, by = "cgi")
        
	# only work with files of more than 500 entries
        if (length(events$timestamp) < 500) {
                next
        }
        
        events <- events[order(events$timestamp),]
        
        # set the values of longitude and latitude to normal
        events$longitude <- events$longitude / (10 ^ 6)
        events$latitude <- events$latitude / (10 ^ 6)
        
        events$date <-
                strftime(as.POSIXct(as.numeric(events$timestamp),origin = "1970-01-01"),format = "%Y-%m-%d")
        
        cal_variables <- ddply(events, .(date), operations)
        
        #calculate final variables with the four returned and add them to the final result
        var1 <- max(cal_variables$V1,na.rm = TRUE)
        var2 <- mean(cal_variables$V2,na.rm = TRUE)
        var3 <- mean(cal_variables$V3)
        var4 <- sd(cal_variables$V3,na.rm = TRUE)
        var5 <- mean(cal_variables$V4)
        var6 <- sd(cal_variables$V4,na.rm = TRUE)
        variables_accumulate <- c(var1,var2,var3,var4,var5,var6)
        
        variables <- rbind(variables,variables_accumulate)
        list_imsi <- append(list_imsi,eventsFiles$imsi[i])
}


# normalisation and replacing na (optional)
variables <- as.data.frame(variables)
dimension <- 6
for( i in 1:dimension){
        maxi <- max(variables[,i],na.rm = T)
        mini <- min(variables[,i],na.rm = T)
        variables[,i] <- (variables[,i]-mini)/(maxi-mini)
	variables[,i][is.na(variables[,i])] <- mean(variables[,i],na.rm = T)
}

# write out the final result
result <- data.table(imsi = list_imsi,variables)
write.table(result,resultPath,row.names = F, sep = ",")

