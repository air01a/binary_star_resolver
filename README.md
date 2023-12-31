# binary_star_resolver
Find binary star parameters with speckle interferometry processing

Use wx to create windows program to implement algorithm described in this project : 
https://github.com/air01a/speckles-interferometry


![Alt text](images/capture.png "Interface") 


# Principe de l'analyse

## Algorithme

A ma connaissance, cet algorithme n'a jamais été utilisé pour calculer les paramètres des étoiles doubles. La base, correspondant à l'auto corrélation et l'application d'un filtre est très bien documentée, mais la partie consistant à supprimer le pic central, bien que très simple, ne me semble pas avoir été implémentée. Les résultats réalisés sur environ 40 images de tests semblent plutôt bon. 


## Image de base

L'image obtenue par un téléscope avec une focale élevée d'une étoile double dans un cas idéal devrait ressembler à deux tâches d'Airy distinctes comme sur le schéma-ci dessous. Ces deux tâches sont liées au phénomène de diffraction engendré par le système optique permettant l'observation. 

![Alt text](images/airy.png "Etoiles doubles") 

La présence de l'atmosphère "dégrade" l'image. On peut considérer que l'atmosphère est composée de "bulles" plus ou moins grandes ayant des indices de réfraction différents, engendrant la présence de multiples trajets pour la lumière.

![Alt text](images/atmosphere.png "Etoiles doubles") 


Pour réduire au maximum ces perturbations, on prend des temps de pose très courts pour "figer" l'atmosphère, et on multiplie les images (de 1000 à 3000 images pour un système d'étoiles). Les images reçues ressemblent à cela : 

![Alt text](images/cou619.png "Etoiles doubles") 

## Autocorrélation

Afin d'extraire les informations utiles, à savoir l'angle formé par les 2 étoiles et la distance angulaire, on réalise l'intercorrélation de chaque image, et on réalise la somme de ces résultats. 
L'autocorrélation consiste à réaliser l'opération suivante : 
$$R(\tau_x, \tau_y) = \sum_{x=1}^{M}\sum_{y=1}^{N} f(x, y) \cdot f(x + \tau_x, y + \tau_y)$$

Chaque pixel X,Y de l'image créée sera donc la somme des multiplications des pixels de l'image de base par l'image de base décalée de X et Y pixels. Si on imagine une couple d'étoiles représentées (en signal sur une dimension) par deux pics de dirac : 

![Alt text](images/figure_1.png "Pics de Dirac") 

La figure d'autocorrélation comportera 3 pics. Un pic central (l'image multipliée par elle même sans décalage) mais aussi deux autres pics, qui correspondront à un décalage X,Y égal à la distance séparant les étoiles :

![Alt text](images/figure_2.png "Pics de Dirac") 

Cela signifie que l'angle obtenue sur l'autocorrélation aura un biais possible de 180 °. 

C'est ce que fait le script main.py, en calculant la densité spectrale de puissance (qui par le théorème de  Wiener-Khinchin est analogue à l'auto corrélation de l'image).

En pratique sur des images réelles, cela donne : 

![Alt text](images/a1453.png "Auto corrélation") 

Pour diminuer le bruit, on applique un filtre médian :

![Alt text](images/a1453_mean_filtering.png "Auto corrélation + filtre médian") 


## Suppression du pic central

Le problème est que l'image est alors composée de 3 pics. Le pic central d'autocorrélation, et les deux pics secondaires liés à la corrélation de l'étoile principale et l'étoile secondaire. Ces 3 pics circulaires se confondent rendant difficile de trouver les 3 centres nécessaires pour calculer distance et angle. 

![Alt text](images/double.png "pics corrélation")

Le pic central est ... centré sur l'image. On connaît donc très bien son centre. Reste à déterminer le centre d'au moins l'un des deux autres pics. Pour cela, le programme calcule l'ellipse qui englobe le mieux l'image obtenue. Puis, en il calcule la perpendiculaire à l'axe principal de l'ellipse et extrait un vecteur contenant les valeurs de l'image sur cette perpendiculaire.

![Alt text](images/doubleellipse.png "Auto corrélation") 

Ce vecteur contient en fait la contribution du pic central à l'image. Le script transforme ensuite ce vecteur en un masque circulaire qu'il applique à l'image :

![Alt text](images/doubleequation.png "Auto corrélation") 

Une fois cela fait, il ne reste qu'a détecter les pics secondaires, calculer la distance et l'angle...

## En pratique

Pour reprendre l'exemple précédent : 

![Alt text](images/a1453_mean_filtering.png "Auto corrélation") 

Voici le masque circulaire obtenue via le vecteur perpendiculaire à l'axe principal de l'ellipse : 

![Alt text](images/a1453_central_contribution.png "Auto corrélation") 

Et voici l'image obtenue en soustrayant le masque. 

![Alt text](images/a1453_result.png "Auto corrélation") 

En traçant le graph correspondant à l'image obtenue le long de l'axe principal de l'ellipse, on retrouve bien les deux pics secondaires :

![Alt text](images/a1453_graph.png "Auto corrélation") 

