import numpy as np
import cv2


class Position_transforme():
    def __init__(self):
        #largeur et longueur d'une moitie de terrain
        terrain_largeur = 68
        terrain_longeur = 23.32

        self.position_pixel = np.array([[110, 1035],
                                        [265, 275],
                                        [910, 260],
                                        [1640, 915]])

        self.ordre_position = np.array([
            [0, terrain_largeur],
            [0, 0],
            [terrain_longeur, 0],
            [terrain_longeur, terrain_largeur]
        ])

        self.position_pixel = self.position_pixel.astype(np.float32)
        self.ordre_position = self.ordre_position.astype(np.float32)

        self.changement_de_perspective = cv2.getPerspectiveTransform(self.position_pixel, self.ordre_position)

    def point_tranforme(self, point):
        p = (int(point[0]), int(point[1]))
        interieur = cv2.pointPolygonTest(self.position_pixel, p, False) >= 0
        if not interieur:
            return None

        forme_point = point.reshape(-1, 1, 2).astype(np.float32)
        tranforme_point = cv2.perspectiveTransform(forme_point, self.changement_de_perspective)
        return tranforme_point.reshape(-1, 2)

    def ajouter_position_transforme_au_tracks(self, tracks):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info['position_adjusted']
                    position = np.array(position)
                    position_trasnformed = self.point_tranforme(position)
                    if position_trasnformed is not None:
                        position_trasnformed = position_trasnformed.squeeze().tolist()
                    tracks[object][frame_num][track_id]['position_transformed'] = position_trasnformed