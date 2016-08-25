# Anomaly-Detection
summer internship at intersec

## preprocessing.R

transformer les données brutes aux six variables intéressées (normalisation and remplacement des NAs optionnel à la fin)

input: à modifier au début du script 
 eventsDirectory : directory pour l'ensemble des données brutes(un imsi un fichier)
 cellPath : path du fichier cell.csv
 resultPath : path pour mettre le résultat
 percent : tourner sur combien de pourcentage de données

output: ficher avec imsi dans le premier column et les six variables dans les columns suivants)

## preprocessing_ss.R

transformer les données stop-segment aux variables choisies (normalisation and remplacement des NAs optionnel à la fin)

input : à modifier au début du script
 inputPath : path de la sortie de preprocessing(pour calculer les même imsi que le preprocessing) ou path du fichier avec des imsi intéressés
 cellPath : path du fichier cell.csv
 stopseg_Directory : directory pour l'ensemble des fichiers de stop-segment
 outputPath : path pour mettre le résultat


output : fichier avec imsi dans le premier column et les variables dans les columns suivants

## choisir les variables intéressées dans les deux fichiers et refaire un fichier final avec le même format

## model_gaussien_training.R

training process pour modèle gaussien, obtenir les means et variances pour toutes les variables
normalisation and remplacement des NAs optionnel 
transformation des variables aux distributions gaussiennes optionnelle(processus non automatique, à modifier dans le script)

input: à modifier au début du script
 inputPath : path du ficher du résultat de preprocessing 
 outputPath : path du ficher avec des données updated aux distributions gaussiennes par rapport input sur l'ensemble d'imsi
 parameterPath: path pour mettre le résultat, les stats pour toutes les variables
 dimension : nombre de variables
 percent_training : pourcentage pour training (valeur: 0->1,counter à partir du début d'input)


output : fichier avec les données updated aux distributions gaussiennes(le même format) et fichier avec les stats pour les variables (premier rang:means,deuxième rang:sd)

## model_gaussien_testing.R

testing process pour modèle gaussien, obtenir les proba et les étiquettes pour tous les imsi  
normalisation and remplacement des NAs optionnel 

input: à changer au début du script
 inputPath : path de la sortie de training process, les donnees updated aux distributions gaussiennes ou directement la sortie de preprocessing
 parameterPath : path de la sortie de training process, les stats des variables
 outputPath : path pour mettre le résultat de proba
 labelPath : path du fichier des étiquettes obtenues avec le seuil donnée 
 dimension : nombre de variables
 percent_testing : pourcentage pour testing sur l'ensemble de données(valeur: 0->1,counter à partir de la fin d'input)
 seuil : seuil de proba pour selectionner les anomalies


output: ficher output avec deux columns imsi,proba; ficher label avec deux columns imsi,label

## model_lof.py

construire le modèle lof
normalisation and remplacement des NAs optionnel

input: à modifier au début du script
 inputPath : path de la sortie des données de preprocessing
 outputPath : path pour mettre le résultat
 dimension :  nombre de variables
 LB : limite inférieur de MinPts
 UB : limite supérieur de MinPts


output :  ficher avec deux columns imsi, lof

## model_hs_tree.py

construire le modèle half space tree
normalisation and remplacement des NAs optionnel

input: à modifier au début du script
 inputPath : path de la sortie des données de preprocessing
 outputPath : path pour mettre le résultat
 rd.seed(10) : seed pour produire les nombers randoms
 maxDepth = 15
 psi = 250
 numTree = 25
 dimension : nombre de variables
 sizeLimit = 25

output: ficher avec deux columns imsi, scores

## evaluation_courbe_ROC.py 

choix de seuil et l'évaluation de modèle lof et hs_tree 

input: à modifier au début du script
labelPath: path du fichier des étiquettes, premier column imsi, deuxième column label{1,0}
 inputPath: path du fichier de la sortie de model_lof.py ou model_hs_tree.py
 threshold_fp: seuil pour false positive rate
 model: "lof" or "hs_tree"


output: AUC score, seuil et courbe ROC

## evaluation_matrice_confusion.py

calculer la matrice de confusion

input: à modifier au début du script
 labelPath: path du fichier avec les vraies étiquettes, premier column imsi, deuxième column label{1,0}
 inputPath: path du fichier avec les étiquettes prédites par les modèles, deux columns imsi et étiquettes

output: Accuracy score, F1 score, confusion matrix

## randomsearch_lof.py

input: à modifier au début du script
 inputPath: path du ficher de la sortie de preprocessing
 labelPath: path du ficher avec les vraies étiquettes
 outputPath: path pour mettre le résultat
 dimension: nombre de variables
 num_iter: nombre d'itérations
 num_cv: nombre de cross validation
 tuned_params = {'MinPtsLB':sp_randint(11,31),'MinPtsUB':sp_randint(31,81),'Vars':sp_randint(0,count)}


output: ficher avec les temps de calcul pour chaque cross_validation de chaque hyperparamètre, les moyennes des scores pour chaque hyperparamètre, et finalement résumé sur l'ensemble d'essais

## randomsearch_hs.py

input: à modifier au début du script
 inputPath: path du ficher de la sortie de preprocessing
 labelPath: path du ficher avec les vraies étiquettes
 outputPath: path pour mettre le résultat
 dimension: nombre de variables
 num_iter: nombre d'itérations
 num_cv: nombre de cross validation
 tuned_params = {'maxDepth':sp_randint(3,15),'psi':sp_randint(200,300),'numTree':sp_randint(10,30),'Vars':sp_randint(0,count)}


output: ficher avec les temps de calcul pour chaque cross_validation de chaque hyperparamètre, les moyennes des scores pour chaque hyperparamètre, et finalement résumé sur l'ensemble d'essais

## efficacite.py

visulization de scores~temps de calcul avec des fichers de la sortie de random search

input: à modifier au début du script
 inputPath: path du ficher de la sortie de random search
 num_iter: nombre d'itérations
 num_cv: nombre de cross validation


output: figure scores~temps de calcul pour chaque hyperparamètre
