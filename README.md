# Automatic speed tracking
Suivi automatique de la vitesse d'un objet sélectionné par un utilisateur

# Utilisation
Lancer le script. Une fois la fenêtre de la webcam ouverte, cliquer sur la cible à tracker (un rectangle dont les dimensions sont à spécifier dans le script).

L'algorithme track l'objet et détermine automatiquement la conversion d'échelle des pixels au mm. La vitesse du barycentre de la cible est affichée en temps réel. 
La vidéo est enregistrée à la fin ainsi que le graphe de la vitesse en fonction du temps écoulé. 

# Requirements
`pip install opencv-python`
`pip install numpy`
`pip install matplotlib`
