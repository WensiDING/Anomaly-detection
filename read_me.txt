1.1 preprocessing.R

transformer les données brutes aux six variables intéressées (normalisation and remplacement des NAs optionnel à la fin)

input: à modifier au début du script 
{eventsDirectory : directory pour l'ensemble des données brutes(un imsi un fichier)
 cellPath : path du fichier cell.csv
 resultPath : path pour mettre le résultat
 percent : tourner sur combien de pourcentage de données}

output: ficher avec imsi dans le premier column et les six variables dans les columns suivants)

1.2 preprocessing.R

transformer les données stop-segment aux variables choisies (normalisation and remplacement des NAs optionnel à la fin)

input : à modifier au début du script
{inputPath : path de la sortie de preprocessing(pour calculer les même imsi que le preprocessing) ou path du fichier avec des imsi intéressés
 cellPath : path du fichier cell.csv
 stopseg_Directory : directory pour l'ensemble des fichiers de stop-segment
 outputPath : path pour mettre le résultat
}

output : fichier avec imsi dans le premier column et les variables dans les columns suivants

1.3 choisir les variables intéressées dans les deux fichiers et refaire un fichier final avec le même format

2. model_gaussien_training.R

training process pour modèle gaussien, obtenir les means et variances pour toutes les variables
normalisation and remplacement des NAs optionnel 
transformation des variables aux distributions gaussiennes optionnelle(processus non automatique, à modifier dans le script)


input: à modifier au début du script
{inputPath : path du ficher du résultat de preprocessing 
 outputPath : path du ficher avec des données updated aux distributions gaussiennes par rapport input sur l'ensemble d'imsi
 parameterPath: path pour mettre le résultat, les stats pour toutes les variables
 dimension : nombre de variables
 percent_training : pourcentage pour training (valeur: 0->1,counter à partir du début d'input)
}

output : fichier avec les données updated aux distributions gaussiennes(le même format) et fichier avec les stats pour les variables (premier rang:means,deuxième rang:sd)

3. model_gaussien_testing.R

testing process pour modèle gaussien, obtenir les proba et les étiquettes pour tous les imsi  
normalisation and remplacement des NAs optionnel 

input: à changer au début du script
{inputPath : path de la sortie de training process, les donnees updated aux distributions gaussiennes ou directement la sortie de preprocessing
 parameterPath : path de la sortie de training process, les stats des variables
 outputPath : path pour mettre le résultat de proba
 labelPath : path du fichier des étiquettes obtenues avec le seuil donnée 
 dimension : nombre de variables
 percent_testing : pourcentage pour testing sur l'ensemble de données(valeur: 0->1,counter à partir de la fin d'input)
 seuil : seuil de proba pour selectionner les anomalies
}

output: ficher output avec deux columns imsi,proba; ficher label avec deux columns imsi,label

4. model_lof.py

construire le modèle lof
normalisation and remplacement des NAs optionnel

input: à modifier au début du script
{inputPath : path de la sortie des données de preprocessing
 outputPath : path pour mettre le résultat
 dimension :  nombre de variables
 LB : limite inférieur de MinPts
 UB : limite supérieur de MinPts
}

output :  ficher avec deux columns imsi, lof

5. model_hs_tree.py

construire le modèle half space tree
normalisation and remplacement des NAs optionnel

input: à modifier au début du script
{inputPath : path de la sortie des données de preprocessing
 outputPath : path pour mettre le résultat
 rd.seed(10) : seed pour produire les nombers randoms
 maxDepth = 15
 psi = 250
 numTree = 25
 dimension : nombre de variables
 sizeLimit = 25
}

output: ficher avec deux columns imsi, scores



