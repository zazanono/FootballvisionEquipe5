import sys

import cv2
import numpy as np

# Ajoute le répertoire parent au path pour importer les fonctions personnalisées
sys.path.append('../')
from VideoFootMl.Outils import mesure_Distance, mesureXYDistance


# Classe CameraMouvement : sert à estimer et visualiser le déplacement de la caméra à travers les frames d'une vidéo
class CameraMouvement():
    def __init__(self, frame):
        # Distance minimale pour considérer qu’il y a un déplacement significatif
        self.distance_Minimale = 5

        # Paramètres de l’algorithme de Lucas-Kanade (suivi optique)
        self.parametres_Lk = dict(
            winSize=(15, 15),  # Taille de la fenêtre de suivi
            maxLevel=2,  # Nombre de niveaux de la pyramide d’images
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)  # Critère d’arrêt
        )

        # Création du masque de détection de points (zones exclues à gauche et à droite)
        premiere_Frame_Grise = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        masque_Caracteristiques = np.zeros_like(premiere_Frame_Grise)
        masque_Caracteristiques[:, 0:20] = 1  # Zone de gauche
        masque_Caracteristiques[:, 900:1050] = 1  # Zone de droite

        # Paramètres de détection de coins (Good Features to Track)
        self.caracteristiques = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=3,
            blockSize=7,
            mask=masque_Caracteristiques
        )

    def ajouterPositionAjusteeAuxTracks(self, pistes, mouvement_Camera_Par_Frame):
        """
                Applique une correction sur la position des objets suivis pour retirer l'effet du mouvement de la caméra.
                Ajoute la clé 'position_adjusted' à chaque objet suivi.
                """
        for objet, pistes_Objet in pistes.items():
            for numero_Frame, piste in enumerate(pistes_Objet):
                for id_Piste, info_Piste in piste.items():
                    position = info_Piste.get('position')
                    mouvement_Camera = mouvement_Camera_Par_Frame[numero_Frame]
                    if position is not None:
                        position_Ajustee = (
                            position[0] - mouvement_Camera[0],
                            position[1] - mouvement_Camera[1]
                        )
                        pistes[objet][numero_Frame][id_Piste]['position_adjusted'] = position_Ajustee

    def getCameraMouvement(self, frames):
        """
                Calcule le mouvement de la caméra entre chaque frame à l’aide du flux optique.
                Retourne une liste de déplacements [x, y] pour chaque frame.
                """
        mouvement_Camera = [[0, 0]] * len(frames)  # Initialisation des déplacements

        ancien_Gris = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        anciennes_Caracteristiques = cv2.goodFeaturesToTrack(ancien_Gris, **self.caracteristiques)

        if anciennes_Caracteristiques is None:
            return mouvement_Camera

        for numero_Frame in range(1, len(frames)):
            frame_Gris = cv2.cvtColor(frames[numero_Frame], cv2.COLOR_BGR2GRAY)
            nouvelles_Caracteristiques, st, err = cv2.calcOpticalFlowPyrLK(
                ancien_Gris, frame_Gris, anciennes_Caracteristiques, None, **self.parametres_Lk
            )

            if nouvelles_Caracteristiques is None or anciennes_Caracteristiques is None:
                continue

            distance_Max = 0
            mouvement_X, mouvement_Y = 0, 0

            # Compare chaque paire de points (ancien/nouveau) pour calculer le déplacement
            for i, (nouvelle, ancienne) in enumerate(zip(nouvelles_Caracteristiques, anciennes_Caracteristiques)):
                if nouvelle is None or ancienne is None:
                    continue

                nouveau_Point = nouvelle.ravel()
                ancien_Point = ancienne.ravel()

                distance = mesure_Distance(nouveau_Point, ancien_Point)
                if distance > distance_Max:
                    distance_Max = distance
                    mouvement_X, mouvement_Y = mesureXYDistance(ancien_Point, nouveau_Point)

            # Si le déplacement est significatif, on l'enregistre
            if distance_Max > self.distance_Minimale:
                mouvement_Camera[numero_Frame] = [mouvement_X, mouvement_Y]
                anciennes_Caracteristiques = cv2.goodFeaturesToTrack(frame_Gris, **self.caracteristiques)

            ancien_Gris = frame_Gris.copy()

        return mouvement_Camera

    def dessinerMouvementCamera(self, frames, mouvement_Camera_Par_Frame):
        """
                Affiche visuellement les déplacements de la caméra sur chaque frame,
                en dessinant une boîte semi-transparente avec les valeurs X et Y.
                """
        frames_Sorties = []

        for num_Frame, frame in enumerate(frames):
            frame = frame.copy()

            # Dessine une boîte blanche semi-transparente
            superposition = frame.copy()
            cv2.rectangle(superposition, (0, 0), (500, 100), (255, 255, 255), -1)
            alpha = 0.6
            cv2.addWeighted(superposition, alpha, frame, 1 - alpha, 0, frame)

            # Texte du mouvement caméra
            mouvement_X, mouvement_Y = mouvement_Camera_Par_Frame[num_Frame]
            frame = cv2.putText(frame, f"Mouvement Camera X : {mouvement_X:.2f}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
            frame = cv2.putText(frame, f"Mouvement Camera Y : {mouvement_Y:.2f}", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

            frames_Sorties.append(frame)

        return frames_Sorties
