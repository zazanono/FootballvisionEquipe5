import sys
import cv2
import numpy as np  # Add if not already present for potential smoothing later

sys.path.append('../')

from VideoFootMl.Outils import mesure_Distance, \
    getPositionPieds  # get_foot_position is used in dessiner_vitesse_distance


class VitesseEtDistance():
    def __init__(self):
        self.frame_window = 5  # Number of frames to average speed over
        self.frame_rate = 24  # IMPORTANT: Ensure this matches your video's actual FPS

    def suivie_de_la_vitesse_et_de_la_distance(self, tracks):
        total_distance = {}  # Stores cumulative distance for each player

        # Iterate through players only (assuming ball and referees don't need speed/distance)
        if "players" not in tracks:
            return

        player_tracks = tracks["players"]
        number_of_frames = len(player_tracks)

        for frame_num in range(0, number_of_frames, self.frame_window):
            # Determine the end frame for this window, ensuring it's within bounds
            last_frame_in_window = min(frame_num + self.frame_window, number_of_frames - 1)

            # Skip if the window is too small (e.g., at the very end of the video)
            if last_frame_in_window <= frame_num:  # Changed from == to <=
                continue

            for identifiant_joueur, _ in player_tracks[frame_num].items():
                # Check if player exists in the last frame of the window
                if identifiant_joueur not in player_tracks[last_frame_in_window]:
                    continue

                # Get transformed positions (these are in meters on the virtual pitch)
                debut_position_transformed = player_tracks[frame_num][identifiant_joueur].get('position_transformed')
                fin_position_transformed = player_tracks[last_frame_in_window][identifiant_joueur].get(
                    'position_transformed')

                # Ensure positions are valid
                if debut_position_transformed is None or fin_position_transformed is None:
                    continue

                distance_parcourue = mesure_Distance(debut_position_transformed, fin_position_transformed)

                # Time elapsed in seconds
                temps_ecoule = (last_frame_in_window - frame_num) / self.frame_rate
                if temps_ecoule <= 0:  # Avoid division by zero if frame_rate is off or window is 0
                    continue

                vitesse_m_s = distance_parcourue / temps_ecoule
                vitesse_kmh = vitesse_m_s * 3.6

                # Initialize and update total distance for the player
                total_distance.setdefault(identifiant_joueur, 0.0)  # Ensure float
                total_distance[identifiant_joueur] += distance_parcourue

                # Assign calculated speed and cumulative distance to all frames within this window
                for frame_idx_in_window in range(frame_num, last_frame_in_window):  # Corrected loop end
                    if identifiant_joueur not in player_tracks[frame_idx_in_window]:
                        continue
                    player_tracks[frame_idx_in_window][identifiant_joueur]['speed'] = vitesse_kmh
                    player_tracks[frame_idx_in_window][identifiant_joueur]['distance'] = total_distance[
                        identifiant_joueur]

        # Forward fill speed and distance for frames not covered by the main loop's start
        # This helps if the last segment of frames is smaller than frame_window
        for identifiant_joueur in total_distance.keys():  # Iterate over players who had distance calculated
            last_known_speed = None
            last_known_distance = None
            for frame_num in range(number_of_frames):
                if identifiant_joueur in player_tracks[frame_num]:
                    if 'speed' in player_tracks[frame_num][identifiant_joueur]:
                        last_known_speed = player_tracks[frame_num][identifiant_joueur]['speed']
                        last_known_distance = player_tracks[frame_num][identifiant_joueur]['distance']
                    elif last_known_speed is not None:  # If current frame doesn't have speed, but we had one
                        player_tracks[frame_num][identifiant_joueur]['speed'] = last_known_speed
                        player_tracks[frame_num][identifiant_joueur]['distance'] = last_known_distance

    def dessiner_vitesse_distance(self, frames, tracks, frame_stride=1):  # Changed default frame_stride to 1
        output_frames = []
        if "players" not in tracks:  # Handle case where there are no player tracks
            return frames  # Return original frames

        for frame_num, frame in enumerate(frames):
            frame_copy = frame.copy()

            # Only draw if it's a stride frame (or every frame if frame_stride is 1)
            if frame_num % frame_stride == 0:
                player_tracks_for_frame = tracks["players"][frame_num]
                for _, track_info in player_tracks_for_frame.items():
                    if "speed" in track_info and "distance" in track_info:  # Ensure both are present
                        speed = track_info.get('speed')  # No default needed if we check 'in'
                        distance = track_info.get('distance')

                        bbox = track_info.get('bbox')
                        if bbox is None:
                            continue

                        # Use a copy of the foot position to avoid modifying original list
                        position = list(getPositionPieds(bbox))
                        position[1] += 25  # Adjust Y offset for text below player

                        # Ensure position coordinates are integers for cv2.putText
                        position_tuple = tuple(map(int, position))

                        # Text for speed
                        cv2.putText(frame_copy, f"{speed:.1f} km/h", position_tuple, cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 0, 0), 2, cv2.LINE_AA)  # Black text
                        cv2.putText(frame_copy, f"{speed:.1f} km/h", (position_tuple[0] - 1, position_tuple[1] - 1),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (255, 255, 255), 1, cv2.LINE_AA)  # White "outline" for better visibility

                        # Text for distance
                        dist_pos = (position_tuple[0], position_tuple[1] + 15)  # Y offset for distance text
                        cv2.putText(frame_copy, f"{distance:.1f} m", dist_pos,
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
                        cv2.putText(frame_copy, f"{distance:.1f} m", (dist_pos[0] - 1, dist_pos[1] - 1),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            output_frames.append(frame_copy)

        # The print statement for speed was inside the loop, which is too verbose.
        # If you need a final status:
        # print(f"Finished processing speed/distance drawing for {len(frames)} frames.")

        return output_frames