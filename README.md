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
Pour segmenter la tumeur, il y a plusieurs solutions. On a essayé 3 algorithmes. On a choisi d'essayer un algorithme de watershed, car c'est un algorithme que l'on a étudié et que l'on connait bien, on a essayé l'algorithme à seuillage d'Otsu car il est très facile d'utilisation du fait qu'il a très peu de paramètres, et on a essayé l'algorithme de RegionGrowing, qui est efficace mais semi-automatique.

- Pour l'algorithme de watershed, on a besoin de garder que les bords du volume (du cerveau) donc on va passer un fitre de gradient de magnitude couplé à un filtre gaussien. Pour avoir un résultat à peu près correct, on utilise 0.2 en niveau de segmentation et 0.003 en seuil mais les bords du cerveau sont trop saillants par rapport aux bords de la tumeur donc on n'arrive pas à détacher la tumeur du cerveau.
- Pour l'algorithme à seuillage d'Otsu, l'algorithme n'a pas nécessairement besoin de prétraitement pour fonctionner. Le rendu donné par cet algorithme ne nous convient pas car il n'est pas assez prècis et il n'est pas réglable donc n'est pas fonctionnel pour notre utilisation.
- Nous avons finalement acté sur l'utilisation du region growing malgré le fait qu'il soit semi-automatique. Cela nous permet d'avoir une segmentation de la tumeur propre facilement. Notre pipeline ne sera donc pas utilisable pour d'autres données car nous avons hardcodé les seed pour les deux volumes.

Le côté segmentation a été un gros souci pour ce projet. En effet, avec la technique utilisée, il faut trouver la seed et les threshold qui permettent de ne pas avoir de résidu et nous n'avons pas réussi à les trouver. Nous avons donc cherché à améliorer cela de différentes manières : tout d'abord en modifiant les paramètres (seed, lower threshold, upper threshold...), puis en appliquant des filtres de prétraitrement (comme du floutage) et enfin en appliquant des algorithmes de post traitement (morphologie mathématique, sélection d'une zone etc.).

La façon la plus simple que nous aurions pu utiliser était de sélectionner la zone intérieure du cerveau à la main (en délimitant une "boite") mais cela n'a pas vraiment de sens car cela voudrait dire que l'algorithme n'est pas du tout automatisé. Nous nous sommes donc plutôt penché sur la morphologie mathématiques.

Nous avons donc cherché beaucoup de différentes manières de bien segmenter la zone que l'on voulait, mais aucune n'était optimale et nous n'avons pas réussi à obtenir un résultat exploitable. Nous pensons que nous n'avons pas assez exploré la piste des seed et des thresholds concernant la segmentation d'ITK, mais nous n'avions plus d'idée sur la façon de procéder à cela.
Dans notre code final, la segmentation se fait en deux parties : une semgentation "légère" qui permet de voir les gros vide qu'il y a dans le cerveau, et une segmentation plus "lourde" qui permet de voir les parties importantes à regarder.


## Affichage avec VTK
Pour la partie VTK, nous voulions simplement superposer la segmentation de la tumeur avec une versions "simplifiée" (en réalité c'est une semi-segmentation) du cerveau pour que l'on puisse voir facilement cette tumeur. Nous avons fait cela pour les 2 images, puis nous avons créé une 3e image qui résulte de la différence entre les deux premières images simplifiée. C'est sur cette 3e image que l'on voit très bien la tumeur apparaître.

Nous avons créé 3 zones différentes pour mieux voir chaque image et leur segmentation correspondante. Les segmentation des deux images sont une superposistion de leur segmentation "légère" et "lourde".


## Utilisation du projet
Pour utiliser le projet, il faut simplement posséder les bibliothèques itk et vtk pour lancer le fichier "main.py" qui contient toutes les parties du code du projet. La partie processing prend un peu de temps et il y a des affichages réguliers qui permettent de savoir où en est l'algorithme.


Version ITK utilisée : 5.4.0

Version VTK utilisée : 9.3.1

Lien du GitHub : https://github.com/nicolasregniervigouroux/ITK-VTK