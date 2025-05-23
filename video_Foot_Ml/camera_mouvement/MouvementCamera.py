import pickle
import cv2
import numpy as np
import os
import sys

sys.path.append('../')
from video_Foot_Ml.outils import measure_Distance, mesure_XY_Distance


class MouvementCamera():
    def __init__(self, frame):
        self.distance_Minimale = 5

        self.parametres_Lk = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )

        premiere_Frame_Grise = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        masque_Caracteristiques = np.zeros_like(premiere_Frame_Grise)
        masque_Caracteristiques[:, 0:20] = 1
        masque_Caracteristiques[:, 900:1050] = 1

        self.caracteristiques = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=3,
            blockSize=7,
            mask=masque_Caracteristiques
        )

    def ajouterPositionAjusteeAuxTracks(self, pistes, mouvement_Camera_Par_Frame):
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

    def getMouvementCamera(self, frames):
        mouvement_Camera = [[0, 0]] * len(frames)

        ancien_Gris = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        anciennes_Caracteristiques = cv2.goodFeaturesToTrack(ancien_Gris, **self.caracteristiques)

        if anciennes_Caracteristiques is None:
            return mouvement_Camera

        for numero_Frame in range(1, len(frames)):
            frame_Grise = cv2.cvtColor(frames[numero_Frame], cv2.COLOR_BGR2GRAY)
            nouvelles_Caracteristiques, st, err = cv2.calcOpticalFlowPyrLK(
                ancien_Gris, frame_Grise, anciennes_Caracteristiques, None, **self.parametres_Lk
            )

            if nouvelles_Caracteristiques is None or anciennes_Caracteristiques is None:
                continue

            distance_Max = 0
            mouvement_X, mouvement_Y = 0, 0

            for i, (nouvelle, ancienne) in enumerate(zip(nouvelles_Caracteristiques, anciennes_Caracteristiques)):
                if nouvelle is None or ancienne is None:
                    continue

                nouveau_Point = nouvelle.ravel()
                ancien_Point = ancienne.ravel()

                distance = measure_Distance(nouveau_Point, ancien_Point)
                if distance > distance_Max:
                    distance_Max = distance
                    mouvement_X, mouvement_Y = mesure_XY_Distance(ancien_Point, nouveau_Point)

            if distance_Max > self.distance_Minimale:
                mouvement_Camera[numero_Frame] = [mouvement_X, mouvement_Y]
                anciennes_Caracteristiques = cv2.goodFeaturesToTrack(frame_Grise, **self.caracteristiques)

            ancien_Gris = frame_Grise.copy()

        return mouvement_Camera

    def dessinerMouvementCamera(self, frames, mouvement_Camera_Par_Frame):
        frames_Sorties = []

        for numero_Frame, frame in enumerate(frames):
            frame = frame.copy()

            superposition = frame.copy()
            cv2.rectangle(superposition, (0, 0), (500, 100), (255, 255, 255), -1)
            alpha = 0.6
            cv2.addWeighted(superposition, alpha, frame, 1 - alpha, 0, frame)

            mouvement_X, mouvement_Y = mouvement_Camera_Par_Frame[numero_Frame]
            frame = cv2.putText(frame, f"Mouvement Camera X : {mouvement_X:.2f}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
            frame = cv2.putText(frame, f"Mouvement Camera Y : {mouvement_Y:.2f}", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

            frames_Sorties.append(frame)

        return frames_Sorties
