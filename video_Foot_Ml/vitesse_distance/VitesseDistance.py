import sys
import cv2

sys.path.append('../')

from video_Foot_Ml.outils import measure_Distance, \
    getPositionPied


class VitesseEtDistance():
    def __init__(self):
        self.fenetre_Frame = 5  # Nombre d'images à parcourir pour atteindre la vitesse moyenne
        self.taux_Frame = 24

    def suiviDeLaVitesseEtDeLaDistance(self, tracks):
        total_Distance = {}  # Stocke la distance cumulée pour chaque joueur

        # Itérer uniquement sur les joueurs (en supposant que le ballon et les arbitres n'ont pas besoin de vitesse/distance)
        if "joueurs" not in tracks:
            return

        tracks_Joueur = tracks["joueurs"]
        nombre_Frames = len(tracks_Joueur)

        for numero_Frame in range(0, nombre_Frames, self.fenetre_Frame):

            # Déterminer la dernière frame de la fenêtre, en s'assurant qu'elle se trouve dans les limites
            derniere_Frame = min(numero_Frame + self.fenetre_Frame, nombre_Frames - 1)

            # Ignorer si la fenêtre est trop petite (par exemple, à la toute fin de la vidéo)
            if derniere_Frame <= numero_Frame:  # Changed from == to <=
                continue

            for joueur_Id, _ in tracks_Joueur[numero_Frame].items():

                # Vérifie si le joueur existe dans la dernière frame de la fenêtre
                if joueur_Id not in tracks_Joueur[derniere_Frame]:
                    continue

                # Obtenir des positions transformées (en mètre sur le terrain vitruel)
                debut_Position_Transformee = tracks_Joueur[numero_Frame][joueur_Id].get('position_Transformee')
                fin_position_Transformee = tracks_Joueur[derniere_Frame][joueur_Id].get(
                    'position_Tranformee')

                # S'assurer que les positions sont valides
                if debut_Position_Transformee is None or fin_position_Transformee is None:
                    continue

                distance_Parcourue = measure_Distance(debut_Position_Transformee, fin_position_Transformee)

                # Temps écoulé en secondes
                temps_Ecoule = (derniere_Frame - numero_Frame) / self.taux_Frame
                if temps_Ecoule <= 0:  # Éviter la division par zéro si le taux de frame est désactivé ou si la fenêtre est 0
                    continue

                vitesse_M_S = distance_Parcourue / temps_Ecoule
                vitesse_Kmh = vitesse_M_S * 3.6

                # Initialiser et mettre à jour la distance totale du joueur
                total_Distance.setdefault(joueur_Id, 0.0)  # Pour avoir un float
                total_Distance[joueur_Id] += distance_Parcourue

                # Attribuer la vitesse calculée et la distance cumulée à toutes les frames de cette fenêtre
                for frame_Idx_Dans_Fenetre in range(numero_Frame, derniere_Frame):
                    if joueur_Id not in tracks_Joueur[frame_Idx_Dans_Fenetre]:
                        continue
                    tracks_Joueur[frame_Idx_Dans_Fenetre][joueur_Id]['vitesse'] = vitesse_Kmh
                    tracks_Joueur[frame_Idx_Dans_Fenetre][joueur_Id]['distance'] = total_Distance[
                        joueur_Id]

        # Vitesse de remplissage vers l'avant et distance pour les images non couvertes par le démarrage de la boucle principale
        # Cela aide si le dernier segment de cadres est plus petit que fenetre_Frame
        for joueur_Id in total_Distance.keys():  # Itérer sur les joueurs dont la distance a été calculée
            derniere_Vitesse_Connue = None
            derniere_Distance_Connue = None
            for numero_Frame in range(nombre_Frames):
                if joueur_Id in tracks_Joueur[numero_Frame]:
                    if 'vitesse' in tracks_Joueur[numero_Frame][joueur_Id]:
                        derniere_Vitesse_Connue = tracks_Joueur[numero_Frame][joueur_Id]['vitesse']
                        derniere_Distance_Connue = tracks_Joueur[numero_Frame][joueur_Id]['distance']
                    elif derniere_Vitesse_Connue is not None:  # Si l'image actuelle n'a pas de vitesse, mais que nous en avions une
                        tracks_Joueur[numero_Frame][joueur_Id]['vitesse'] = derniere_Vitesse_Connue
                        tracks_Joueur[numero_Frame][joueur_Id]['distance'] = derniere_Distance_Connue

    def dessinerVitesseEtDistance(self, frames, tracks, frame_Stride=1):
        frames_Output = []
        if "joueurs" not in tracks:  # Gérer le cas où il n'y a pas de tracks pour le joueur
            return frames  # Retourne les frames originales

        for numero_Frame, frame in enumerate(frames):
            copie_Frame = frame.copy()

            # Dessiner uniquement si c'est une stride frame
            if numero_Frame % frame_Stride == 0:
                tracks_Joueur_Par_Frame = tracks["joueurs"][numero_Frame]
                for _, track_Info in tracks_Joueur_Par_Frame.items():
                    if "vitesse" in track_Info and "distance" in track_Info:  # S'assurer que les deux soient présents
                        vitesse = track_Info.get('vitesse')
                        distance = track_Info.get('distance')

                        bbox = track_Info.get('bbox')
                        if bbox is None:
                            continue

                        # Utiliser une copie de la position du pied pour éviter de modifier la liste d'origine
                        position = list(getPositionPied(bbox))
                        position[1] += 25

                        position_Tuple = tuple(map(int, position))

                        # Texte pour la vitesse
                        cv2.putText(copie_Frame, f"{vitesse:.1f} km/h", position_Tuple, cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 0, 0), 2, cv2.LINE_AA)
                        cv2.putText(copie_Frame, f"{vitesse:.1f} km/h", (position_Tuple[0] - 1, position_Tuple[1] - 1),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (255, 255, 255), 1, cv2.LINE_AA)

                        # Texte pour la distance
                        position_Distance = (position_Tuple[0], position_Tuple[1] + 15)
                        cv2.putText(copie_Frame, f"{distance:.1f} m", position_Distance,
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
                        cv2.putText(copie_Frame, f"{distance:.1f} m",
                                    (position_Distance[0] - 1, position_Distance[1] - 1),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            frames_Output.append(copie_Frame)

        return frames_Output
