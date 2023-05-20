import cv2
import numpy as np
import time
import matplotlib.pyplot as plt

# Variables globales
color_to_track = None  # Couleur à traquer (initialisée à None)
scale_factor = 1.  # Facteur d'échelle initial
last_contour = None  # Dernier contour détecté
pixels_per_meter = None  # Correspondance pixel en mètres (initialisée à None)
velocities = []  # Liste des vitesses
times = []  # Liste des temps

# Dimensions du rectangle (en mm)
rectangle_mm = (35, 25)

# Dimensions de l'échelle affichée (en mm)
echelle_affichee_mm = 50

# Chemin vers la vidéo enregistrée
video_path = "IMG_8492.MOV"

# Ouvrir la vidéo
video = cv2.VideoCapture(video_path)

# Vérifier si la vidéo a été ouverte correctement
if not video.isOpened():
    print("Impossible d'ouvrir la vidéo")
    exit()

# Obtenir la résolution de la vidéo
frame_width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Créer une fenêtre pour afficher la vidéo
cv2.namedWindow("Vidéo en temps réel")

def mouse_callback(event, x, y, flags, param):
    global color_to_track

    if event == cv2.EVENT_LBUTTONDOWN:
        # Récupérer la couleur du pixel cliqué
        color_to_track = frame[y, x]

# Attacher la fonction de rappel des clics de souris à la fenêtre
cv2.setMouseCallback("Vidéo en temps réel", mouse_callback)

while True:
    # Lire une nouvelle frame depuis la vidéo
    ret, frame = video.read()

    # Vérifier si la frame a été lue correctement
    if not ret:
        break

    # Redimensionner la frame en fonction de l'échelle
    resized_frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor)

    # Vérifier si l'utilisateur a sélectionné une couleur à traquer
    if color_to_track is not None:
        # Convertir la couleur sélectionnée en espace de couleur HSV
        hsv_color = cv2.cvtColor(np.uint8([[color_to_track]]), cv2.COLOR_BGR2HSV)
        hsv_color = hsv_color[0][0]

        # Définir les bornes de couleur en fonction de la couleur sélectionnée
        lower_color = np.array([hsv_color[0] - 10, 50, 50])
        upper_color = np.array([hsv_color[0] + 10, 255, 255])

        # Convertir la frame en espace de couleur HSV
        hsv_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2HSV)

        # Filtrer la frame pour isoler la couleur sélectionnée
        mask = cv2.inRange(hsv_frame, lower_color, upper_color)

        # Trouver les contours de la couleur sélectionnée
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Vérifier s'il y a des contours détectés
        if len(contours) > 0:
            # Trouver le contour avec la plus grande aire
            plus_grand_contour = max(contours, key=cv2.contourArea)

            # Calculer les dimensions du rectangle englobant
            x, y, w, h = cv2.boundingRect(plus_grand_contour)
            rectangle_pixels = max(w, h)

            # Calculer l'échelle en mm/pixel
            if rectangle_pixels != 0:
                pixels_per_meter = rectangle_mm[0] / (rectangle_pixels / 1000)  # Conversion de mm en mètres

                # Mettre à jour l'échelle affichée en pixels
                echelle_affichee_pixels = int((echelle_affichee_mm / 100) * pixels_per_meter * scale_factor)

                # Mettre à jour la longueur de la ligne affichée en pixels
                ligne_affichee_pixels = int((echelle_affichee_mm / 1000) * pixels_per_meter)  # Conversion de mm en mètres

                # Afficher l'échelle et la ligne
                cv2.line(resized_frame, (10, 100), (10 + echelle_affichee_pixels, 100), (0, 255, 0), 2)
                cv2.putText(resized_frame, f"Echelle: {echelle_affichee_mm} mm", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Calculer le barycentre du contour
            M = cv2.moments(plus_grand_contour)
            if M["m00"] != 0:
                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])
                center = (center_x, center_y)

                # Vérifier si c'est la première détection du contour
                if last_contour is not None:
                    # Calculer la distance en pixels entre les deux contours
                    distance_pixels = cv2.matchShapes(last_contour, plus_grand_contour, cv2.CONTOURS_MATCH_I1, 0)

                    # Calculer la distance en mètres
                    distance_meters = (distance_pixels / pixels_per_meter)  # Conversion de pixels en mètres

                    # Calculer le temps écoulé
                    elapsed_time = time.time() - last_time

                    # Calculer la vitesse en mètres par seconde
                    velocity = distance_meters / elapsed_time

                    # Ajouter la vitesse et le temps aux listes
                    velocities.append(velocity)
                    times.append(time.time())

                    # Afficher la vitesse de l'objet sur l'image
                    cv2.putText(resized_frame, f"Vitesse : {velocity:.2f} m/s", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                # Mettre à jour le dernier contour et le temps
                last_contour = plus_grand_contour
                last_time = time.time()

                # Dessiner le contour sur l'image
                cv2.drawContours(resized_frame, [plus_grand_contour], -1, (0, 255, 0), 2)

                # Dessiner le barycentre
                cv2.circle(resized_frame, center, 5, (0, 255, 255), -1)

    # Afficher la frame redimensionnée
    cv2.imshow("Vidéo en temps réel", resized_frame)

    # Attendre la touche 'q' pour quitter la boucle
    if cv2.waitKey(1) == 27:
        break

# Libérer les ressources
video.release()
cv2.destroyAllWindows()

# Afficher le graphique de la vitesse en fonction du temps
plt.plot(times, velocities)
plt.xlabel("Temps (s)")
plt.ylabel("Vitesse (m/s)")
plt.title("Variation de la vitesse")
plt.show()
