inputPath <- "/home/wensi/workspace/tryout/result1.csv"
parameterPath <- "/home/wensi/workspace/tryout/result2.csv"
outputPath <- "/home/wensi/workspace/tryout/result3.csv"
labelPath <- "/home/wensi/workspace/tryout/label.csv"
dimension <- 6
percent_testing <- 0.2
seuil <- 1e-15

#read input files
parameters <- read.csv(parameterPath)       
input <- fread(inputPath,colClasses = c("imsi" = "character"))
input <- as.data.frame(input)
#test the part of the file counting from the end
total <- floor(length(input$imsi) * (1-percent_testing))
input <- input[(total + 1):length(input$imsi),]

# normalisation and replacing na (optional)
#for(i in 2:(dimension+1)){
#       input[,i][is.na(input[,i])] <- mean(input[,i],na.rm = T)
#	maxi <- max(input[,i])
#	mini <- min(input[,i])
#	input[,i] <- (input[,i]-mini)/(maxi-mini)
#}

list_imsi <- character()
probs <- numeric()
label <- numeric()

for (i in 1:length(input$imsi)) {
        prob <- 1
        for (j in 2:(dimension + 1)) {
                # dnorm return the density of proba which can be greater than 1, multiply dnorm by 0.02 to estimate approximately the proba
                prob <-
                        prob * dnorm(input[i,j],parameters[1,j - 1],parameters[2,j - 1]) * 0.02
        }
        
        list_imsi <- append(list_imsi,input[i,1])
        probs <- append(probs, prob)
        if (prob < seuil) {
                label <- append(label,1)
        }
        else{
                label <- append(label,0)
        }
        
}

table_prob <- data.table(imsi = list_imsi,prob = probs)
table_prob <- table_prob[order(table_prob$prob),]
# write out the results
write.table(data.table(imsi = list_imsi,prob = probs),outputPath,row.names = F,sep = ",")
write.table(data.table(imsi = list_imsi,label = label),labelPath,row.names = F,sep = ",")

