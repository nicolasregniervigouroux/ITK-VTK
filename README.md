## Etude longitudinale d'une tumeur de cerveau en utilisant les bibliothèques VTK et ITK
Les auteurs de cette étude sont Nicolas Regnier-Vigouroux et Grégoire Vest.
Cette étude a été faite dans le cadre du projet du cours ITK-VTK.
Recalage des données: Nicolas
Segmentation des tumeurs et VTK: Grégoire


## Recalage des données
Pour voir un peu le décalage qui existait entre les deux volumes, nous les avons affiché dans le même espace avec VTK et nous avons pu voir que le décalage était principalement un décalage latéral. Nous avons en premier jet donc utilisé le TranslationTransform et eu de plutôt bons résultats.
Nous avons essayé d'utiliser d'autres algorithmes de recalage que contient itk comme le Euler3DTransform ou le BSplineTransform mais nous n'avons jamais réussi à avoir un résultat convenable. Nous n'avons pas réussi à trouver les bons paramètres pour les faire bien fonctionner. Ils tournaient soit à l'infini soit avaient de très mauvais résultats. Nous avons même essayé d'autres Optimizer comme le LBFGSOptimizerv4 mais Nous n'avons pas eu d'améliorations de résultats.
Nous sommes donc restés finalement sur le TranslationTransform car c'est le seul avec qui nous avions de plûtot bon résultats.


## Segmentation
Le côté segmentation a été un gros souci pour ce projet. En effet, nous sommes partis de la base du TP qui consistait à trouver une seed qui permet d'avoir la segmentation optimale de la tumeur. Malheureusement, avec cette technique il y avait toujours des résidus (plutôt gros) qui apparaissaient. Nous avons donc cherché à améliorer cela de différentes manières : tout d'abord en modifiant les paramètres (seed, lower threshold, upper threshold...), puis en appliquant des filtres de prétraitrement (comme du floutage) et enfin en appliquant des algorithmes de post traitement (morphologie mathématique, sélection d'une zone etc.).
La façon la plus simple que nous aurions pu utiliser était de sélectionner la zone intérieure du cerveau à la main (en délimitant une "boite") mais cela n'a pas vraiment de sens car cela voudrait dire que l'algorithme n'est pas du tout automatisé. Nous nous sommes donc plutôt penché sur la morphologie mathématiques.
Nous avons donc cherché beaucoup de différentes manières de bien segmenter la zone que l'on voulait, mais aucune n'était optimale et nous n'avons pas réussi à obtenir un résultat exploitable. Nous pensons que nous n'avons pas assez exploré la piste des seed et des threshold concernant la segmentation d'ITK, mais nous n'avions plus d'idée sur la façon de procéder à cela.


## Affichage avec VTK
Pour la partie VTK, nous voulions simplement superposer la segmentation de la tumeur avec une versions "simplifiée" (en réalité c'est une semi-segmentation) du cerveau pour que l'on puisse voir facilement cette tumeur. Nous avons fait cela pour les 2 images, puis nous avons créé une 3e image qui résulte de la différence entre les deux premières images simplifiée. C'est sur cette 3e image que l'on voit très bien la tumeur apparaître.
Nous avons créé 3 zones différentes pour mieux voir chaque image et leur segmentation correspondante.


## Utilisation du projet
Pour utiliser le projet, il faut simplement posséder les bibliothèques itk et vtk pour lancer le fichier "main.py" qui contient toutes les parties du code du projet. La partie processing prend un peu de temps et il y a des affichages réguliers qui permettent de savoir où en est l'algorithme.


Version ITK utilisée : 5.4.0
Version VTK utilisée : 9.3.1