import os

import cv2

from VideoFootMl.MouvementsCamera import CameraMouvement
from VideoFootMl.Outils import sauvegarderVideo, lireVideo
from VideoFootMl.Trackers import Tracker
from VideoFootMl.VitesseDistance import VitesseEtDistance
from VideoFootMl.transformation import Position_transforme


def analyseYolo(chemin_vid, vid_deja_faite, progression_callback=None):
    """
        Fonction principale qui exécute toutes les étapes d’analyse :
        - Lecture de la vidéo
        - Détection et suivi des objets
        - Estimation du mouvement de la caméra
        - Transformation des positions vers un plan réel
        - Calcul de la vitesse
        - Annotation et sauvegarde de la vidéo
        """
    # 1) Lecture de la vidéo et détection des objets (ou chargement depuis un fichier cache)
    video_Images = lireVideo(chemin_vid)
    tracker = Tracker('VideoFootMl/Models/detecteur_foot_n.pt')
    tracks = tracker.getObjetTracks(
        video_Images,
        read_from_stub=vid_deja_faite,
        stub_path=os.path.join(
            os.path.dirname(__file__),
            "Stubs", "track_stubs.pkl"
        ),
        progression_callback=progression_callback
    )

    # 2) Recherche de la première frame contenant au moins un joueur
    premiere_Frame = next(
        (i for i, frame_Dict in enumerate(tracks['players'])
         if frame_Dict),
        None
    )
    if premiere_Frame is None:
        print("No players detected in any frame.")
        return

    print(f"Saving crop from frame #{premiere_Frame}, "
          f"{len(tracks['players'][premiere_Frame])} players found.")

    # 3) Sélection d’un joueur (le premier trouvé ici)
    track_Id, joueur = next(
        iter(tracks['players'][premiere_Frame].items())
    )
    bbox = joueur['bbox']
    frame_Image = video_Images[premiere_Frame]
    crop = frame_Image[
           int(bbox[1]):int(bbox[3]),
           int(bbox[0]):int(bbox[2])
           ]
    print("  • bbox:", bbox, "→ crop.shape:", crop.shape)

    # 4) Construction du chemin absolu de sortie
    repertoire_Script = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(repertoire_Script)
    repertoire_Sortie = os.path.join(repo_root, "VideoFootMl", "VideosOutput")
    os.makedirs(repertoire_Sortie, exist_ok=True)

    # 5) Sauvegarde de l'image rognée
    chemin_Sortie = os.path.join(repertoire_Sortie, f"image_rognee_{track_Id}.jpg")
    ok = cv2.imwrite(chemin_Sortie, crop)
    print(f"  • imwrite returned {ok}")
    print("  • Files now in", repertoire_Sortie, "→", os.listdir(repertoire_Sortie))

    # Ajout de la position centrale ou des pieds dans les tracks
    tracker.ajoutPositionTracks(tracks)
    # Estimation du mouvement de la caméra
    mouvement_Camera = CameraMouvement(video_Images[0])
    camera_Movement_Par_Frame = mouvement_Camera.getCameraMouvement(video_Images)
    mouvement_Camera.ajouterPositionAjusteeAuxTracks(tracks, camera_Movement_Par_Frame)
    # Transformation des coordonnées vers le plan du terrain (vue du dessus)
    transformation = Position_transforme()
    transformation.ajouterPositionTransformeAuTracks(tracks)
    # Calcul des vitesses et distances parcourues
    vitesse_Distance = VitesseEtDistance()
    vitesse_Distance.suivie_de_la_vitesse_et_de_la_distance(tracks)
    # Génération de la vidéo avec annotations
    video_Sortie_Images = tracker.dessinerAnnotations(video_Images, tracks)

    video_Sortie_Images = mouvement_Camera.dessinerMouvementCamera(video_Sortie_Images, camera_Movement_Par_Frame)

    video_Sortie_Images = vitesse_Distance.dessiner_vitesse_distance(video_Sortie_Images, tracks)

    # Sauvegarde de la vidéo finale annotée
    repertoire_Sortie = os.path.join(repo_root, "VideoFootMl", "VideosOutput")
    sauvegarderVideo(video_Sortie_Images, repertoire_Sortie, "VideosOutput")


def main():
    """
        Point d’entrée du code : lance l’analyse d’une vidéo d’entrée.
        """
    analyseYolo('VideoFootMl/VideosInput/foot1.mp4', True)


if __name__ == '__main__':
    main()
