import os
import pickle
import sys

import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO

# Permet d'importer les fonctions utilitaires depuis un dossier parent
sys.path.append('../')
from VideoFootMl.Outils import getCentreBbox, getLargeurBbox, getPositionPieds


# Classe Tracker : encapsule la détection et le suivi des objets dans une séquence vidéo
class Tracker:
    def __init__(self, model_path):
        """
                Initialise le modèle YOLOv8 et le traqueur ByteTrack.

                Paramètre :
                    model_path : str
                        Chemin vers le modèle YOLO pré-entraîné (.pt)
                """
        self.model = YOLO(model_path)

        fps = 30  # ou récupérer dynamiquement via cv2.VideoCapture
        self.tracker = sv.ByteTrack(
            track_activation_threshold=0.25,
            lost_track_buffer=60,
            minimum_matching_threshold=0.8,
            frame_rate=fps,
            minimum_consecutive_frames=2
        )

    def ajoutPositionTracks(self, tracks):
        """
                Ajoute la position calculée (centre ou pieds) à chaque objet détecté dans les tracks.

                Paramètre :
                    tracks : dict
                        Dictionnaire contenant les objets suivis pour chaque frame
                """
        for obj, object_Tracks in tracks.items():
            for frame_Numero, track in enumerate(object_Tracks):
                for track_Id, track_Info in track.items():
                    bbox = track_Info.get('bbox')
                    if bbox:
                        if obj == 'ball':
                            position = getCentreBbox(bbox)
                        else:
                            position = getPositionPieds(bbox)
                        tracks[obj][frame_Numero][track_Id]['position'] = position

    def detecterFrame(self, frames, progression_callback=None):
        """
                Applique la détection YOLO sur chaque frame par batch de 20.

                Paramètres :
                    frames : list
                        Liste des images (np.ndarray)
                    progression_callback : fonction(optionnel)
                        Fonction de rappel pour mettre à jour une barre de progression

                Retour :
                    detections : list
                        Liste d’objets de détection (Ultralytics)
                """
        taille_Batch = 20
        detections = []
        for i in range(0, len(frames), taille_Batch):
            detections_Batch = self.model.track(frames[i: i + taille_Batch], conf=0.1)
            detections += detections_Batch

            if progression_callback:
                pourcentage = int((i + taille_Batch) / len(frames) * 100)
                progression_callback(min(pourcentage, 100))

        return detections

    def getObjetTracks(self, frames, read_from_stub=False, stub_path=None, progression_callback=None):
        """
                Détecte et suit les objets dans chaque frame (joueurs, arbitres, ballon).
                Peut utiliser un fichier de cache (pickle) si disponible.

                Paramètres :
                    frames : list
                    read_from_stub : bool
                        True pour charger les tracks depuis un fichier existant
                    stub_path : str
                        Chemin vers le fichier de cache .pkl
                    progression_callback : fonction
                        Fonction pour mettre à jour la progression

                Retour :
                    tracks : dict
                        Dictionnaire des objets détectés par frame
                """
        self.tracker.reset()

        if read_from_stub and stub_path and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                return pickle.load(f)

        detections = self.detecterFrame(frames, progression_callback)

        tracks = {"players": [], "referees": [], "ball": []}

        for frame_Numero, detection in enumerate(detections):
            cls_Noms = detection.names
            cls_Noms_Inv = {v: k for k, v in cls_Noms.items()}

            detection_Supervision = sv.Detections.from_ultralytics(detection)

            # Harmonisation des classes (parfois "goalkeeper", parfois "football-players")
            for i, class_Id in enumerate(detection_Supervision.class_id):
                if cls_Noms[class_Id] in {"goalkeeper", "football-players"}:
                    detection_Supervision.class_id[i] = cls_Noms_Inv["player"]

            detection_With_Tracks = self.tracker.update_with_detections(detection_Supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            # Ajoute les joueurs et arbitres à la frame
            for det in detection_With_Tracks:
                bbox = det[0].tolist()
                cls_Id = det[3]
                track_Id = det[4]

                if cls_Id == cls_Noms_Inv["player"]:
                    tracks["players"][frame_Numero][track_Id] = {"bbox": bbox}
                elif cls_Id == cls_Noms_Inv["referee"]:
                    tracks["referees"][frame_Numero][track_Id] = {"bbox": bbox}

            # Ajoute le ballon (non tracké par ByteTrack)
            for det in detection_Supervision:
                bbox = det[0].tolist()
                cls_Id = det[3]

                if cls_Id == cls_Noms_Inv["ball"]:
                    tracks["ball"][frame_Numero][1] = {"bbox": bbox}

        if stub_path:
            with open(stub_path, "wb") as f:
                pickle.dump(tracks, f)

        return tracks

    def dessinerAnnotations(self, video_Frames, tracks):
        """
                Dessine les annotations (joueurs, arbitres, ballon) sur chaque frame.

                Paramètres :
                    video_Frames : list[np.ndarray]
                    tracks : dict

                Retour :
                    output_Frames_Video : list[np.ndarray]
                """
        output_Frames_Video = []
        for frame_Num, frame in enumerate(video_Frames):
            frame = frame.copy()

            players = tracks["players"][frame_Num]
            referees = tracks["referees"][frame_Num]
            balls = tracks["ball"][frame_Num]

            for track_Id, player in players.items():
                color = player.get('couleur_équipe', (112, 112, 112))  # Gris par défaut
                frame = self.dessinerEllipse(frame, player["bbox"], tuple(map(int, color)), track_Id)

            for track_Id, referee in referees.items():
                frame = self.dessinerEllipse(frame, referee["bbox"], (0, 255, 255))

            for track_Id, ball in balls.items():
                frame = self.dessinerTriangleInv(frame, ball["bbox"], (0, 255, 0))

            output_Frames_Video.append(frame)

        return output_Frames_Video

    def dessinerEllipse(self, frame, bbox, color, track_id=None):
        """
                Dessine une ellipse sous un joueur/arbitre, avec son ID si fourni.

                Paramètres :
                    frame : np.ndarray
                    bbox : liste [x1, y1, x2, y2]
                    color : tuple (B, G, R)
                    track_id : int ou None
                """
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

        # Affiche l'ID du joueur au-dessus de l'ellipse
        if track_id is not None:
            rect_L, rect_H = 40, 20
            x1 = centre_X - rect_L // 2
            y1 = y2 + 15 - rect_H // 2  # Positionne le rectangle en dessous de l'ellipse
            x2 = x1 + rect_L
            y2_rect = y1 + rect_H  # Nom de variable différent pour y2 du rectangle

            cv2.rectangle(frame, (x1, y1), (x2, y2_rect), color, cv2.FILLED)
            x_text = x1 + 15 - (10 if track_id > 99 else 0)  # Ajustement pour les nombres à 2 ou 3 chiffres
            cv2.putText(frame, f"{track_id}", (x_text, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return frame

    def dessinerTriangleInv(self, frame, bbox, color, track_id=None):
        """
               Dessine un triangle inversé pour représenter le ballon.

               Paramètres :
                   frame : np.ndarray
                   bbox : liste [x1, y1, x2, y2]
                   color : tuple (B, G, R)
                   track_id : (optionnel)
               """
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
