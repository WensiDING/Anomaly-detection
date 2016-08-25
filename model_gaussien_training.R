inputPath <- "/home/wensi/workspace/tryout/result.csv"
outputPath <- "/home/wensi/workspace/tryout/result1.csv"
parameterPath <- "/home/wensi/workspace/tryout/result2.csv"
dimension <- 5
percent_training <- 0.8

#read the input file
input <- fread(inputPath,colClasses=c("imsi"="character"))
input <- as.data.frame(input)

#initialise the container of results
means <- numeric()
sds <- numeric()

# normalisation (optional)
#for( i in 2:(dimension+1)){
#	maxi <- max(input[,i],na.rm=T)
#	mini <- min(input[,i],na.rm=T)
#	input[,i] <- (input[,i]-mini)/(maxi-mini)
#}

##changer la distribution des variables pour qu'elles resemblent plus à la distribution gaussienne
#hist(input[,2])
#hist(input[,2]^0.1)
#hist(log(input[,2])) faire attention à la valeur zéro quand utiliser function log()
# à modifier
input[,2]<-input[,2]^0.2
input[,3]<-input[,3]^0.1
input[,4]<-input[,4]^0.1
input[,5]<-input[,5]^0.1
input[,6]<-input[,6]^0.2
# save the updated version of data for testing
write.table(input,outputPath,row.names = F,sep=",")

# get the parameters only from the percent_training of the whole data set
total <- floor(length(input$imsi)*percent_training)
input <- input[1:total,]

# calculate les stats pour toutes les variables
for(i in 2:(dimension+1)){
        means <- append(means,mean(input[,i],na.rm = T))
        sds <- append(sds,sd(input[,i],na.rm = T))
}

# write out the training parameters
write.table(rbind(means,sds),parameterPath,row.names = F,sep=",")

