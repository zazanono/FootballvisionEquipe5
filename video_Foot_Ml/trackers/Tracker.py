from ultralytics import YOLO
import supervision as sv
import pickle
import os
import numpy as np
import cv2
import sys

sys.path.append('../')
from video_Foot_Ml.outils import getCentreBbox, getLargeurBbox, getPositionPied


class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

        fps = 30  # Ou récupérer dynamiquement via cv2.VideoCapture
        self.tracker = sv.ByteTrack(
            track_activation_threshold=0.25,
            lost_track_buffer=60,
            minimum_matching_threshold=0.8,
            frame_rate=fps,
            minimum_consecutive_frames=2
        )

    def ajouterPositionAuxTracks(self, tracks):
        for obj, object_Tracks in tracks.items():
            for numero_Frame, track in enumerate(object_Tracks):
                for track_Id, track_Info in track.items():
                    bbox = track_Info.get('bbox')
                    if bbox:
                        if obj == 'ball':
                            position = getCentreBbox(bbox)
                        else:
                            position = getPositionPied(bbox)
                        tracks[obj][numero_Frame][track_Id]['position'] = position

    def detecter_Frames(self, frames, rappel_Progression=None):
        taille_Batch = 20
        detections = []
        for i in range(0, len(frames), taille_Batch):
            detections_Batch = self.model.track(frames[i: i + taille_Batch], conf=0.1)
            detections += detections_Batch

            if rappel_Progression:
                pourcentage = int((i + taille_Batch) / len(frames) * 100)
                rappel_Progression(min(pourcentage, 100))

        return detections

    def getObjetTrack(self, frames, lis_Acces=False, chemin_Acces=None, rappel_Progression=None):
        self.tracker.reset()

        if lis_Acces and chemin_Acces and os.path.exists(chemin_Acces):
            with open(chemin_Acces, 'rb') as f:
                return pickle.load(f)

        detections = self.detecter_Frames(frames, rappel_Progression)

        tracks = {"players": [], "referees": [], "ball": []}

        for numero_Frame, detection in enumerate(detections):
            nom_Cls = detection.names
            noms_Cls_Inv = {v: k for k, v in nom_Cls.items()}

            detection_Supervision = sv.Detections.from_ultralytics(detection)

            for i, classe_Id in enumerate(detection_Supervision.class_id):
                if nom_Cls[classe_Id] in {"goalkeeper", "football-players"}:
                    detection_Supervision.class_id[i] = noms_Cls_Inv["player"]

            detection_Avec_Tracks = self.tracker.update_with_detections(detection_Supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for det in detection_Avec_Tracks:
                bbox = det[0].tolist()
                cls_Id = det[3]
                track_Id = det[4]

                if cls_Id == noms_Cls_Inv["player"]:
                    tracks["players"][numero_Frame][track_Id] = {"bbox": bbox}
                elif cls_Id == noms_Cls_Inv["referee"]:
                    tracks["referees"][numero_Frame][track_Id] = {"bbox": bbox}

            for det in detection_Supervision:
                bbox = det[0].tolist()
                cls_Id = det[3]

                if cls_Id == noms_Cls_Inv["ball"]:
                    tracks["ball"][numero_Frame][1] = {"bbox": bbox}

        if chemin_Acces:
            with open(chemin_Acces, "wb") as f:
                pickle.dump(tracks, f)

        return tracks

    def dessinerAnnotations(self, video_Frames, tracks):
        output_Video_Frames = []
        for numero_Frame, frame in enumerate(video_Frames):
            frame = frame.copy()

            joueurs = tracks["players"][numero_Frame]
            arbitres = tracks["referees"][numero_Frame]
            balls = tracks["ball"][numero_Frame]

            for track_Id, player in joueurs.items():
                color = player.get('couleur_équipe', (112, 112, 112))  # gris par défaut
                frame = self.dessinerEllipse(frame, player["bbox"], tuple(map(int, color)), track_Id)

            for track_Id, referee in arbitres.items():
                frame = self.dessinerEllipse(frame, referee["bbox"], (0, 255, 255))

            for track_Id, ball in balls.items():
                frame = self.dessineTriangleInv(frame, ball["bbox"], (0, 255, 0))

            output_Video_Frames.append(frame)

        return output_Video_Frames

    def dessinerEllipse(self, frame, bbox, color, track_Id=None):
        y2 = int(bbox[3])
        centre_X, _ = getCentreBbox(bbox)
        largeur = getLargeurBbox(bbox)

        cv2.ellipse(
            frame,
            center=(centre_X, y2),
            axes=(int(largeur), int(largeur * 0.35)),
            angle=0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4
        )

        if track_Id is not None:
            largeur_Rectangle, hauteur_Rectangle = 40, 20
            x1 = centre_X - largeur_Rectangle // 2
            y1 = y2 + 15 - hauteur_Rectangle // 2  # Positionne le rectangle en dessous de l'ellipse
            x2 = x1 + largeur_Rectangle
            y2_rect = y1 + hauteur_Rectangle  # Nom de variable différent pour y2 du rectangle

            cv2.rectangle(frame, (x1, y1), (x2, y2_rect), color, cv2.FILLED)
            x_text = x1 + 15 - (10 if track_Id > 99 else 0)  # Ajustement pour les nombres à 2 ou 3 chiffres
            cv2.putText(frame, f"{track_Id}", (x_text, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return frame

    def dessineTriangleInv(self, frame, bbox, color, track_id=None):
        y1 = int(bbox[1])
        centre_X, _ = getCentreBbox(bbox)

        triangle = np.array([
            [centre_X, y1],
            [centre_X - 10, y1 - 20],
            [centre_X + 10, y1 - 20]
        ])

        cv2.drawContours(frame, [triangle], 0, color, cv2.FILLED)
        cv2.drawContours(frame, [triangle], 0, (0, 0, 0), 2)

        return frame
