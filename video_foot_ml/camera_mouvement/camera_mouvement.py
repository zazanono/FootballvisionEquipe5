import pickle
import cv2
import numpy as np
import os
import sys

sys.path.append('../')
from video_foot_ml.outils import measure_distance, measure_xy_distance


class CameraMouvement():
    def __init__(self, frame):
        self.distance_minimale = 5

        self.parametres_lk = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )

        premiere_frame_gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        masque_caracteristiques = np.zeros_like(premiere_frame_gris)
        masque_caracteristiques[:, 0:20] = 1
        masque_caracteristiques[:, 900:1050] = 1

        self.caracteristiques = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=3,
            blockSize=7,
            mask=masque_caracteristiques
        )

    def ajouter_position_ajustee_aux_tracks(self, pistes, mouvement_camera_par_frame):
        for objet, pistes_objet in pistes.items():
            for num_frame, piste in enumerate(pistes_objet):
                for id_piste, info_piste in piste.items():
                    position = info_piste.get('position')
                    mouvement_camera = mouvement_camera_par_frame[num_frame]
                    if position is not None:
                        position_ajustee = (
                            position[0] - mouvement_camera[0],
                            position[1] - mouvement_camera[1]
                        )
                        pistes[objet][num_frame][id_piste]['position_adjusted'] = position_ajustee

    def obtenir_mouvement_camera(self, frames):
        mouvement_camera = [[0, 0]] * len(frames)

        ancien_gris = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        anciennes_caracteristiques = cv2.goodFeaturesToTrack(ancien_gris, **self.caracteristiques)

        if anciennes_caracteristiques is None:
            return mouvement_camera

        for num_frame in range(1, len(frames)):
            frame_gris = cv2.cvtColor(frames[num_frame], cv2.COLOR_BGR2GRAY)
            nouvelles_caracteristiques, st, err = cv2.calcOpticalFlowPyrLK(
                ancien_gris, frame_gris, anciennes_caracteristiques, None, **self.parametres_lk
            )

            if nouvelles_caracteristiques is None or anciennes_caracteristiques is None:
                continue

            distance_max = 0
            mouvement_x, mouvement_y = 0, 0

            for i, (nouvelle, ancienne) in enumerate(zip(nouvelles_caracteristiques, anciennes_caracteristiques)):
                if nouvelle is None or ancienne is None:
                    continue

                nouveau_point = nouvelle.ravel()
                ancien_point = ancienne.ravel()

                distance = measure_distance(nouveau_point, ancien_point)
                if distance > distance_max:
                    distance_max = distance
                    mouvement_x, mouvement_y = measure_xy_distance(ancien_point, nouveau_point)

            if distance_max > self.distance_minimale:
                mouvement_camera[num_frame] = [mouvement_x, mouvement_y]
                anciennes_caracteristiques = cv2.goodFeaturesToTrack(frame_gris, **self.caracteristiques)

            ancien_gris = frame_gris.copy()

        return mouvement_camera

    def dessiner_mouvement_camera(self, frames, mouvement_camera_par_frame):
        frames_sorties = []

        for num_frame, frame in enumerate(frames):
            frame = frame.copy()

            superposition = frame.copy()
            cv2.rectangle(superposition, (0, 0), (500, 100), (255, 255, 255), -1)
            alpha = 0.6
            cv2.addWeighted(superposition, alpha, frame, 1 - alpha, 0, frame)

            mouvement_x, mouvement_y = mouvement_camera_par_frame[num_frame]
            frame = cv2.putText(frame, f"Mouvement Caméra X : {mouvement_x:.2f}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
            frame = cv2.putText(frame, f"Mouvement Caméra Y : {mouvement_y:.2f}", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

            frames_sorties.append(frame)

        return frames_sorties
