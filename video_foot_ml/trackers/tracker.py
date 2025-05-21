from ultralytics import YOLO
import supervision as sv
import pickle
import os
import numpy as np  # <--- ADD THIS IMPORT
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
            lost_track_buffer=60,  # Consider increasing if players disappear and reappear often
            minimum_matching_threshold=0.8,
            frame_rate=fps,
            minimum_consecutive_frames=2
        )

    # <--- START: NEW METHOD TO GET JERSEY COLOR --->
    def get_jersey_color(self, frame, bbox):
        # 1. Define ROI for the jersey from bbox
        x1, y1, x2, y2 = map(int, bbox)

        # Refine ROI: focus on the torso. These are starting points, adjust as needed.
        roi_y_start = int(y1 + (y2 - y1) * 0.15)  # Start a bit down from the top of bbox
        roi_y_end = int(y1 + (y2 - y1) * 0.60)  # End before the waist/shorts
        roi_x_start = int(x1 + (x2 - x1) * 0.1)  # Inset a bit from sides
        roi_x_end = int(x1 + (x2 - x1) * 0.9)

        roi = frame[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

        if roi.size == 0:
            return (50, 50, 50)  # Default to a neutral dark gray if ROI is empty

        # 2. Convert to HSV
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 3. Define color ranges (CRITICAL TUNING STEP)
        # These are EXAMPLES and will need significant tuning for your specific videos/teams
        # Team 1 (e.g., "Reddish" - could be orange, pinkish-red, etc.)
        # Note: Red can wrap around 0-10 and 160-180 in Hue
        lower_team1_a = np.array([0, 100, 70])  # Lower Hue, Sat, Val
        upper_team1_a = np.array([15, 255, 255])  # Upper Hue, Sat, Val
        lower_team1_b = np.array([165, 100, 70])
        upper_team1_b = np.array([180, 255, 255])

        # Team 2 (e.g., "Bluish" - could be light blue, dark blue, purplish-blue)
        lower_team2 = np.array([95, 100, 70])  # Example for blue
        upper_team2 = np.array([135, 255, 255])  # Example for blue

        # (Optional) Team 3 / Other distinct color (e.g., Goalkeeper or a very distinct third team)
        # lower_team3 = np.array([20, 100, 70]) # Example for Yellow/Greenish
        # upper_team3 = np.array([80, 255, 255])

        # 4. Create masks and count pixels
        mask_team1_a = cv2.inRange(hsv_roi, lower_team1_a, upper_team1_a)
        mask_team1_b = cv2.inRange(hsv_roi, lower_team1_b, upper_team1_b)
        mask_team1 = cv2.bitwise_or(mask_team1_a, mask_team1_b)

        mask_team2 = cv2.inRange(hsv_roi, lower_team2, upper_team2)
        # mask_team3 = cv2.inRange(hsv_roi, lower_team3, upper_team3)

        count_team1 = np.count_nonzero(mask_team1)
        count_team2 = np.count_nonzero(mask_team2)
        # count_team3 = np.count_nonzero(mask_team3)

        # Determine team based on pixel count
        # These are BGR colors for drawing the ellipses later
        color_team1_draw = (0, 0, 200)  # Red BGR
        color_team2_draw = (200, 0, 0)  # Blue BGR
        # color_team3_draw = (0, 200, 0)  # Green BGR
        default_color_draw = (70, 70, 70)  # Dark Gray for undetermined

        # Add a simple threshold to ensure a certain amount of color is present
        min_pixel_threshold = (roi.shape[0] * roi.shape[1]) * 0.05  # e.g., 5% of ROI pixels must match

        # Logic to decide the color
        counts = {"team1": count_team1, "team2": count_team2}  # , "team3": count_team3}

        # Find the team with the max count
        if not counts:  # Should not happen if ROI is not empty
            return default_color_draw

        max_team = max(counts, key=counts.get)
        max_count = counts[max_team]

        if max_count > min_pixel_threshold:
            if max_team == "team1":
                return color_team1_draw
            elif max_team == "team2":
                return color_team2_draw
            # elif max_team == "team3":
            #     return color_team3_draw

        return default_color_draw

    # <--- END: NEW METHOD TO GET JERSEY COLOR --->

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
            detections_batch = self.model.track(frames[i: i + batch_size],
                                                conf=0.1)  # Lowered conf for more detections initially
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

            # <--- ADDED: Get the current frame image for color detection --->
            current_frame_image = frames[frame_num]

            detection_supervision = sv.Detections.from_ultralytics(detection)

            # Consolidate player classes before tracking
            for i, class_id_val in enumerate(detection_supervision.class_id):
                original_class_name = cls_names.get(class_id_val)
                if original_class_name in {"goalkeeper",
                                           "football-players"}:  # "player" if your model already uses that
                    # Ensure "player" is a key in cls_names_inv, otherwise, this needs adjustment
                    # or handle it by directly using the class name "player"
                    if "player" in cls_names_inv:
                        detection_supervision.class_id[i] = cls_names_inv["player"]
                    # If your model outputs "player" for "football-players" and "goalkeeper" for goalkeepers,
                    # and you want to treat them all as one category "player" for tracking color:
                    # you might need to adjust your class mapping logic slightly if "player" isn't a direct output class name
                    # that can be inverted. For simplicity, we assume "player" is a target unified class name.

            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for det_tracked in detection_with_tracks:  # Renamed 'det' to 'det_tracked' to avoid conflict
                bbox = det_tracked[0].tolist()
                # class_id here is from detection_supervision *after* potential modification
                # but ByteTrack update_with_detections returns the Detections object which includes xyxy, mask, confidence, class_id, tracker_id
                cls_id = det_tracked[3]
                track_id = det_tracked[4]

                # Make sure cls_id is correctly interpreted according to cls_names
                # It's possible cls_id here is the *unified* ID if you changed it above.

                # <--- MODIFIED SECTION FOR PLAYERS --->
                # Check if the class name corresponding to cls_id is one of your player categories
                # This logic assumes your model has distinct classes that you map to "player" or you directly detect "player"
                # If cls_names[cls_id] was changed to cls_names_inv["player"] then cls_id is now the numeric ID for "player"

                is_player_class = False
                if "player" in cls_names_inv and cls_id == cls_names_inv["player"]:
                    is_player_class = True
                # Or, if your model detects "football-players" and "goalkeeper" separately and you didn't unify their IDs *before* tracking:
                # elif cls_names.get(cls_id) in {"goalkeeper", "football-players"}:
                #    is_player_class = True

                if is_player_class:
                    # <--- CALL get_jersey_color HERE --->
                    jersey_color = self.get_jersey_color(current_frame_image, bbox)
                    tracks["players"][frame_num][track_id] = {"bbox": bbox, "couleur_équipe": jersey_color}
                elif "referee" in cls_names_inv and cls_id == cls_names_inv["referee"]:
                    tracks["referees"][frame_num][track_id] = {"bbox": bbox}
                # <--- END MODIFIED SECTION --->

            # Ball detection remains separate as it's not typically tracked with ByteTrack in the same way
            # It usually doesn't have a persistent track_id like players.
            for det_ball in detection_supervision:  # Iterate over original detections for the ball
                bbox_ball = det_ball[0].tolist()
                cls_id_ball = det_ball[3]  # class_id from original detection_supervision

                if "ball" in cls_names_inv and cls_id_ball == cls_names_inv["ball"]:
                    tracks["ball"][frame_num][1] = {"bbox": bbox_ball}  # Assuming one ball, track_id 1

        if stub_path:
            os.makedirs(os.path.dirname(stub_path), exist_ok=True)  # Ensure directory exists
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

            for track_id, player_info in players.items():  # Changed 'player' to 'player_info'
                # Now 'couleur_équipe' is determined by get_jersey_color
                color = player_info.get('couleur_équipe', (50, 50, 50))  # Default to dark gray
                frame = self.draw_ellipse(frame, player_info["bbox"], tuple(map(int, color)), track_id)

            for track_id, referee_info in referees.items():  # Changed 'referee' to 'referee_info'
                frame = self.draw_ellipse(frame, referee_info["bbox"], (0, 255, 255))  # Default Cyan for referee

            for track_id, ball_info in balls.items():  # Changed 'ball' to 'ball_info'
                frame = self.draw_triangle_inv(frame, ball_info["bbox"], (0, 255, 0))  # Green for ball

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
            # Adjust text box position to be above the ellipse slightly
            rect_y_center = int(y2 - width * 0.35 - rect_h)  # Position it above the ellipse

            x1_rect = x_center - rect_w // 2
            y1_rect = rect_y_center - rect_h // 2
            x2_rect = x1_rect + rect_w
            y2_rect = y1_rect + rect_h

            cv2.rectangle(frame, (x1_rect, y1_rect), (x2_rect, y2_rect), color, cv2.FILLED)

            text_size, _ = cv2.getTextSize(str(track_id), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            text_x = x1_rect + (rect_w - text_size[0]) // 2
            text_y = y1_rect + (rect_h + text_size[1]) // 2

            cv2.putText(frame, str(track_id), (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

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