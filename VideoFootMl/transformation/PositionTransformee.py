import cv2
import numpy as np


# Classe Position_transforme :
# Sert à transformer les coordonnées des objets détectés (en pixels) vers un plan réel (vue "terrain" depuis le dessus)
class Position_transforme():
    def __init__(self):
        """
                Initialise la transformation de perspective à partir de 4 points de référence
                (pixels dans l’image) vers 4 points réels (coordonnées sur un terrain).
                """
        # Dimensions du terrain (une moitié de terrain de soccer en mètres)
        terrain_Largeur = 68  # Largeur officielle
        terrain_Longeur = 23.32  # Moitié de la longueur (si caméra centrée)

        # Points dans l'image (en pixels), à ajuster selon ton jeu de données
        self.position_Pixel = np.array([[110, 1035],  # Coin bas gauche
                                        [265, 275],  # Coin haut gauche
                                        [910, 260],  # Coin haut droit
                                        [1640, 915]])  # Coin bas droit

        # Points correspondants dans le plan "réel" (terrain) en mètres
        self.ordre_Position = np.array([
            [0, terrain_Largeur],  # Bas gauche
            [0, 0],  # haut gauche
            [terrain_Longeur, 0],  # Haut droit
            [terrain_Longeur, terrain_Largeur]  # Bas droit
        ])

        # Conversion explicite vers float32 (obligatoire pour OpenCV)
        self.position_Pixel = self.position_Pixel.astype(np.float32)
        self.ordre_Position = self.ordre_Position.astype(np.float32)

        # Calcule la matrice de transformation de perspective (homographie)
        self.changement_De_Perspective = cv2.getPerspectiveTransform(self.position_Pixel, self.ordre_Position)

    def pointTranforme(self, point):
        """
                Transforme un point donné (en pixels) vers les coordonnées du terrain (en mètres).

                Paramètre :
                    point : np.ndarray ou tuple (x, y)

                Retour :
                    coordonnées transformées ou None si le point est hors de la zone définie
                """
        p = (int(point[0]), int(point[1]))

        # Vérifie si le point est dans la zone définie (intérieur du polygone de référence)
        interieur = cv2.pointPolygonTest(self.position_Pixel, p, False) >= 0
        if not interieur:
            return None

        # Applique la transformation de perspective
        forme_Point = point.reshape(-1, 1, 2).astype(np.float32)
        tranforme_Point = cv2.perspectiveTransform(forme_Point, self.changement_De_Perspective)
        return tranforme_Point.reshape(-1, 2)

    def ajouterPositionTransformeAuTracks(self, tracks):
        """
                Pour chaque objet suivi, ajoute la position transformée (vue du dessus).

                Paramètre :
                    tracks : dict
                        Structure contenant les positions ajustées des objets (après retrait du mouvement caméra)
                """
        for object, object_Tracks in tracks.items():
            for frame_Numero, track in enumerate(object_Tracks):
                for track_Id, track_Info in track.items():
                    position = track_Info['position_adjusted']
                    position = np.array(position)
                    position_Trasnformed = self.pointTranforme(position)
                    if position_Trasnformed is not None:
                        position_Trasnformed = position_Trasnformed.squeeze().tolist()

                    # Ajoute les coordonnées "vue du dessus" aux données de tracking
                    tracks[object][frame_Numero][track_Id]['position_transformed'] = position_Trasnformed
