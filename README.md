## Etude longitudinale d'une tumeur de cerveau en utilisant les bibliothèques VTK et ITK
Les auteurs de cette étude sont Nicolas Regnier-Vigouroux et Grégoire Vest.
Cet étude a été faite dans le cadre du projet du cours ITK-VTK.
Recalage des données: Nicolas
Segmentation des tumeurs: Grégoire


## Recalage des données
Pour voir un peu le décalage qui existait entre les deux volumes, je les ai affiché dans le même espace avec VTK et j'ai pu voir que le décalage était principalement un décalage latéral. 
J'ai en premier jet donc utilisé le TranslationTransform et eu de plutôt bon résultat.
J'ai essayé d'utiliser d'autres algorithmes de recalage que contient itk comme le Euler3DTransform ou le BSplineTransform mais je n'ai jamais réussi à avoir un résultat convenable. 
Je n'ai pas réussi à trouver les bons paramètres pour les faire bien fonctionner. Ils tournaient soit à l'infini soit avaient de très mauvais résultats. J'ai même essayé d'autres Optimizer comme le LBFGSOptimizerv4 mais je n'ai pas eu d'améliorations de résultats.
Je suis donc resté finalement sur le TranslationTransform car c'est le seul avec qui j'avais de plûtot bon résultats.
Pour les paramètres de l'optimizer, j'ai choisi de ne faire que 30 itérations car augmenter les itérations n'améliore pas le recalage, les translations sont les mêmes à, par exemple, 40 itérations.

## Segmentation de la tumeur

Pour segmenter la tumeur, ils y a plusieurs solutions. On a essayé 3 algorithmes. On a choisi d'essayer un algorithme de watershed, car c'est un algorithme que l'on a étudié et que l'on connait bien, on a essayé l'algorithme à seuillage d'Otsu car il est très facile d'utilisation car il a très peu de paramètres, et on a essayé l'algorithme de RegionGrowing, qui est efficace mais semi-automatique.

Pour l'algorithme de watershed, on a besoin de garder que les bords du volume(du cerveau) donc on va passer un fitre de gradient de magnitude couplé à un filtre gaussien. Pour avoir un résultat à peu près correct, on utilise 0.2 en niveau de segmentation et 0.003 en seuil mais les bords du cerveau sont trop saillants par rapport aux bords de la tumeur donc on n'arrive pas à détacher la tumeur du cerveau.

Pour l'algorithme à seuillage d'Otsu, l'algorithme n'a pas nécessairement besoin de prétraitement pour fonctionner. Le rendu donné par cet algorithme ne nous convient pas car il n'est pas assez prècis et il n'est pas réglable donc n'est pas fonctionnel pour notre utilisation.

Nous avons finalement acté sur l'utilisation du region growing malgré le fait qu'il soit semi-automatique. Cela nous permet d'avoir une segmentation de la tumeur propre facilement. Notre pipeline ne sera donc pas utilisable pour d'autres données car nous avons hardcodé les seed pour les deux volumes. Pour masquer le bruit, on applique un filtre gaussien sur le volume. 
Nous lançons ensuite le region growing sur le volume avec la seed trouvé à la main et les deux seuils permettant d'avoir la segmentation la plus propre possible. Nous avons trouvé les seuils et les seed en essayant jusqu'à ce que le résultat nous convienne.
