from ultralytics import YOLO
import supervision as sv
import pickle
import os
import numpy as np
import cv2
import sys

sys.path.append('../')
from video_foot_ml.outils import get_center_of_bbox, get_bbox_width, get_foot_position


class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

        fps = 30  # ou récupérer dynamiquement via cv2.VideoCapture
        self.tracker = sv.ByteTrack(
            track_activation_threshold=0.25,
            lost_track_buffer=60,
            minimum_matching_threshold=0.8,
            frame_rate=fps,
            minimum_consecutive_frames=2
        )

    def add_position_to_tracks(self, tracks):
        for obj, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    bbox = track_info.get('bbox')
                    if bbox:
                        if obj == 'ball':
                            position = get_center_of_bbox(bbox)
                        else:
                            position = get_foot_position(bbox)
                        tracks[obj][frame_num][track_id]['position'] = position

    def detect_frames(self, frames, progression_callback=None):
        batch_size = 20
        detections = []
        for i in range(0, len(frames), batch_size):
            detections_batch = self.model.track(frames[i: i + batch_size], conf=0.1)
            detections += detections_batch

            if progression_callback:
                pourcentage = int((i + batch_size) / len(frames) * 100)
                progression_callback(min(pourcentage, 100))

        return detections

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None, progression_callback=None):
        self.tracker.reset()

        if read_from_stub and stub_path and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                return pickle.load(f)

        detections = self.detect_frames(frames, progression_callback)

        tracks = {"players": [], "referees": [], "ball": []}

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v: k for k, v in cls_names.items()}

            detection_supervision = sv.Detections.from_ultralytics(detection)

            for i, class_id in enumerate(detection_supervision.class_id):
                if cls_names[class_id] in {"goalkeeper", "football-players"}:
                    detection_supervision.class_id[i] = cls_names_inv["player"]

            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for det in detection_with_tracks:
                bbox = det[0].tolist()
                cls_id = det[3]
                track_id = det[4]

                if cls_id == cls_names_inv["player"]:
                    tracks["players"][frame_num][track_id] = {"bbox": bbox}
                elif cls_id == cls_names_inv["referee"]:
                    tracks["referees"][frame_num][track_id] = {"bbox": bbox}

            for det in detection_supervision:
                bbox = det[0].tolist()
                cls_id = det[3]

                if cls_id == cls_names_inv["ball"]:
                    tracks["ball"][frame_num][1] = {"bbox": bbox}

        if stub_path:
            with open(stub_path, "wb") as f:
                pickle.dump(tracks, f)

        return tracks

    def draw_annotations(self, video_frames, tracks):
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            players = tracks["players"][frame_num]
            referees = tracks["referees"][frame_num]
            balls = tracks["ball"][frame_num]

            for track_id, player in players.items():
                color = player.get('couleur_équipe', (0, 0, 0))
                frame = self.draw_ellipse(frame, player["bbox"], tuple(map(int, color)), track_id)

            for track_id, referee in referees.items():
                frame = self.draw_ellipse(frame, referee["bbox"], (0, 255, 255))

            for track_id, ball in balls.items():
                frame = self.draw_triangle_inv(frame, ball["bbox"], (0, 255, 0))

            output_video_frames.append(frame)

        return output_video_frames

    def draw_ellipse(self, frame, bbox, color, track_id=None):
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)

        cv2.ellipse(
            frame,
            center=(x_center, y2),
            axes=(int(width), int(width * 0.35)),
            angle=0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4
        )

        if track_id is not None:
            rect_w, rect_h = 40, 20
            x1 = x_center - rect_w // 2
            y1 = y2 + 15 - rect_h // 2
            x2 = x1 + rect_w
            y2_rect = y1 + rect_h

            cv2.rectangle(frame, (x1, y1), (x2, y2_rect), color, cv2.FILLED)
            x_text = x1 + 15 - (10 if track_id > 99 else 0)
            cv2.putText(frame, f"{track_id}", (x_text, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return frame

    def draw_triangle_inv(self, frame, bbox, color, track_id=None):
        y1 = int(bbox[1])
        x_center, _ = get_center_of_bbox(bbox)

        triangle = np.array([
            [x_center, y1],
            [x_center - 10, y1 - 20],
            [x_center + 10, y1 - 20]
        ])

        cv2.drawContours(frame, [triangle], 0, color, cv2.FILLED)
        cv2.drawContours(frame, [triangle], 0, (0, 0, 0), 2)

        return frame
