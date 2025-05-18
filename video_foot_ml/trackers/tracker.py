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

        fps = 30  # or obtain via cv2.VideoCapture
        self.tracker = sv.ByteTrack(
            track_activation_threshold=0.25,  # keep your model’s clean detections
            lost_track_buffer=60,  # allow 60 frames (≈2 s) of occlusion
            minimum_matching_threshold=0.8,  # default
            frame_rate=fps,
            minimum_consecutive_frames=2  # ignore any object seen <2 frames
        )

    def add_position_to_tracks(sekf, tracks):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    bbox = track_info['bbox']
                    if object == 'ball':
                        position = get_center_of_bbox(bbox)
                    else:
                        position = get_foot_position(bbox)
                    tracks[object][frame_num][track_id]['position'] = position

    def detect_frames(self, frames, progression_callback=None):
        batch_size = 20
        detections = []
        for i in range(0, len(frames), batch_size):
            print("Detecting frames {}-{}/{} ...".format(i, i + batch_size - 1, len(frames)))
            detections_batch = self.model.track(frames[i: i + batch_size], conf=0.1)
            detections += detections_batch

            if progression_callback:
                pourcentage = int((i + batch_size) / len(frames) * 100)
                progression_callback(min(pourcentage, 100))

        return detections

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None, progression_callback=None):
        self.tracker.reset()

        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                tracks = pickle.load(f)
            return tracks

        detections = self.detect_frames(frames, progression_callback)

        tracks = {
            "players": [],
            "referees": [],
            "ball": []
        }

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v: k for k, v in cls_names.items()}
            print(cls_names_inv)

            # Convert to supervision detection format
            detection_supervision = sv.Detections.from_ultralytics(detection)

            # Convert goalkeeper and football-player to player
            for object_ind, class_id in enumerate(detection_supervision.class_id):
                if cls_names[class_id] == "goalkeeper" or cls_names[class_id] == "football-players":
                    detection_supervision.class_id[object_ind] = cls_names_inv["player"]

            # Track objects
            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv["player"]:
                    print("Player {} detected".format(track_id))
                    tracks["players"][frame_num][track_id] = {"bbox": bbox}

                if cls_id == cls_names_inv["referee"]:
                    print("Referee {} detected".format(track_id))
                    tracks["referees"][frame_num][track_id] = {"bbox": bbox}

            for frame_detection in detection_supervision:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]

                if cls_id == cls_names_inv["ball"]:
                    print("Ball detected")
                    tracks["ball"][frame_num][1] = {"bbox": bbox}

        if stub_path is not None:
            with open(stub_path, "wb") as f:
                pickle.dump(tracks, f)

        return tracks

    def draw_annotations(self, video_frames, tracks):
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]

            # Draw players
            for track_id, player in player_dict.items():
                # print("player", player)
                frame = self.draw_ellipse(frame, player["bbox"], (0, 0, 255), track_id)

            # Draw referees
            for track_id, referee in referee_dict.items():
                # print("referee", referee)
                frame = self.draw_ellipse(frame, referee["bbox"], (0, 255, 255))

            # Draw ball
            for track_id, ball in ball_dict.items():
                frame = self.draw_triangle_inv(frame, ball["bbox"], (0, 255, 0))

                # print("ball", ball)
                # frame = self.draw_ellipse(frame, ball["bbox"], (255, 0, 0))


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

        rectangle_widht = 40
        rectangle_height = 20
        x1_rect = x_center - rectangle_widht // 2
        x2_rect = x_center + rectangle_widht // 2
        y1_rect = (y2 - rectangle_height // 2) + 15
        y2_rect = (y2 + rectangle_height // 2) + 15

        if track_id is not None:
            cv2.rectangle(frame, (int(x1_rect), int(y1_rect)), (int(x2_rect), int(y2_rect)), color, cv2.FILLED)

            x1_text = x1_rect + 15
            if track_id > 99:
                x1_text -= 10

            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_text), int(y1_rect + 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )

        return frame

    def draw_triangle_inv(self, frame, bbox, color, track_id=None):
        y1 = int(bbox[1])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)

        triangle_points = np.array([
            [x_center, y1],
            [x_center - 10, y1 - 20],
            [x_center + 10, y1 - 20],
        ])
        cv2.drawContours(frame, [triangle_points], 0, color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points], 0, (0,0,0), 2)

        return frame