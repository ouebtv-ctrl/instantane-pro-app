# Instantané Pro, version web (Netlify)

Copie stable d'Instantané Pro pour l'usage quotidien et le partage. La version Claude reste l'atelier : on y développe et on y teste.

## Mettre à jour
1. Récupérer l'index.html (et le dossier accueil/) de la version Claude dans un dossier, par exemple `source/`.
2. `python3 outils/build_netlify.py source .`
3. Envoyer les fichiers sur GitHub : Netlify publie tout seul.

Le script refait toujours les mêmes transformations (boutons « mon IA », bouton Aide, manifeste, icône, brouillons protégés) et s'arrête si la version Claude a changé à un endroit qu'il modifie.
