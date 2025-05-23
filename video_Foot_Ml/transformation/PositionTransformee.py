import numpy as np
import cv2


class Position_Transformee():
    def __init__(self):
        # largeur et longueur d'une moitie de terrain
        largeur_Terrain = 68
        longueur_Terrain = 23.32

        self.position_Pixel = np.array([[110, 1035],
                                        [265, 275],
                                        [910, 260],
                                        [1640, 915]])

        self.position_Ordre = np.array([
            [0, largeur_Terrain],
            [0, 0],
            [longueur_Terrain, 0],
            [longueur_Terrain, largeur_Terrain]
        ])

        self.position_Pixel = self.position_Pixel.astype(np.float32)
        self.position_Ordre = self.position_Ordre.astype(np.float32)

        self.changement_De_Perspective = cv2.getPerspectiveTransform(self.position_Pixel, self.position_Ordre)

    def pointTransforme(self, point):
        p = (int(point[0]), int(point[1]))
        interieur = cv2.pointPolygonTest(self.position_Pixel, p, False) >= 0
        if not interieur:
            return None

        point_Forme = point.reshape(-1, 1, 2).astype(np.float32)
        point_Transforme = cv2.perspectiveTransform(point_Forme, self.changement_De_Perspective)
        return point_Transforme.reshape(-1, 2)

    def ajouterPositionTransformeeAuTracks(self, tracks):
        for object, object_Tracks in tracks.items():
            for numero_Frame, track in enumerate(object_Tracks):
                for track_Id, track_Info in track.items():
                    position = track_Info['position_adjusted']
                    position = np.array(position)
                    position_Transformee = self.pointTransforme(position)
                    if position_Transformee is not None:
                        position_Transformee = position_Transformee.squeeze().tolist()
                    tracks[object][numero_Frame][track_Id]['position_transformed'] = position_Transformee
