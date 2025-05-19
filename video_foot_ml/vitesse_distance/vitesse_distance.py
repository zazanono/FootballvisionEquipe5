import sys
import cv2

sys.path.append('../')

from video_foot_ml.outils import measure_distance, get_foot_position


class VitesseEtDistance():
    def __init__(self):
        self.frame_window = 5
        self.frame_rate = 24

    def suivie_de_la_vitesse_et_de_la_distance(self, tracks):
        total_distance = {}

        for object, objet_track in tracks.items():
            if object == "ball" or object == "referees":
                continue
            number_of_frames = len(objet_track)
            for frame_num in range(0, number_of_frames, self.frame_window):
                last_frame = min(frame_num + self.frame_window, number_of_frames - 1)

                for identifiant_joueur, _ in objet_track[frame_num].items():
                    if identifiant_joueur not in objet_track[last_frame]:
                        continue

                    debut_position = objet_track[frame_num][identifiant_joueur]['position_transformed']
                    fin_position = objet_track[last_frame][identifiant_joueur]['position_transformed']

                    if debut_position is None or fin_position is None:
                        continue

                    distance_parcourue = measure_distance(debut_position, fin_position)
                    temps = (last_frame - frame_num) / self.frame_rate
                    vitesse_metres_par_seconde = distance_parcourue / temps
                    vitesse_km_par_heure = vitesse_metres_par_seconde * 3.6

                    if object not in total_distance:
                        total_distance[object] = {}

                    if identifiant_joueur not in total_distance[object]:
                        total_distance[object][identifiant_joueur] = 0

                    total_distance[object][identifiant_joueur] += distance_parcourue

                    for frame_num_batch in range(frame_num, last_frame):
                        if identifiant_joueur not in tracks[object][frame_num_batch]:
                            continue
                        tracks[object][frame_num_batch][identifiant_joueur]['speed'] = vitesse_km_par_heure
                        tracks[object][frame_num_batch][identifiant_joueur]['distance'] = total_distance[object][
                            identifiant_joueur]

    def dessiner_vitesse_distance(self, frames, tracks, frame_stride=2):
        output_frames = []
        for frame_num, frame in enumerate(frames):
            frame = frame.copy()

            if frame_num % frame_stride == 0:
                for object, object_tracks in tracks.items():
                    if object == "ball" or object == "referees":
                        continue
                    for _, track_info in object_tracks[frame_num].items():
                        if "speed" in track_info:
                            speed = track_info.get('speed', None)
                            distance = track_info.get('distance', None)
                            if speed is None or distance is None:
                                continue

                            bbox = track_info['bbox']
                            position = get_foot_position(bbox)
                            position = list(position)
                            position[1] += 40

                            position = tuple(map(int, position))
                            cv2.putText(frame, f"{speed:.2f} km/h", position, cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 0, 0), 2)
                            cv2.putText(frame, f"{distance:.2f} m", (position[0], position[1] + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            output_frames.append(frame)

        return output_frames
