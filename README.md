## Etude longitudinale d'une tumeur de cerveau en utilisant les bibliothèques VTK et ITK
Les auteurs de cette étude sont Nicolas Regnier-Vigouroux et Grégoire Vest.
Cet étude a été faite dans le cadre du projet du cours ITK-VTK.
Recalage des données: Nicolas
Segmentation des tumeurs: Grégoire


## Recalage des données
Pour voir un peu le décalage qui existait entre les deux volumes, je les ai affiché dans le même espace avec VTK et j'ai pu voir que le décalage était principalement un décalage latéral. J'ai en premier jet donc utilisé le TranslationTransform et eu de plutôt bon résultat.
J'ai essayé d'utiliser d'autres algorithmes de recalage que contient itk comme le Euler3DTransform ou le BSplineTransform mais je n'ai jamais réussi à avoir un résultat convenable. Je n'ai pas réussi à trouver les bons paramètres pour les faire bien fonctionner. Ils tournaient soit à l'infini soit avaient de très mauvais résultats. J'ai même essayé d'autres Optimizer comme le LBFGSOptimizerv4 mais je n'ai pas eu d'améliorations de résultats.
Je suis donc resté finalement sur le TranslationTransform car c'est le seul avec qui j'avais de plûtot bon résultats.
