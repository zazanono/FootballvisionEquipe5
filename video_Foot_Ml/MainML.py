import cv2
import os
from video_Foot_Ml.outils import sauvegarderVideo, lireVideo
from video_Foot_Ml.trackers import Tracker
from video_Foot_Ml.camera_mouvement import MouvementCamera
from video_Foot_Ml.transformation import Position_Transformee
from video_Foot_Ml.vitesse_distance import VitesseEtDistance


def analyseYolo(chemin_Video, video_Deja_Faite, rappel_Progression=None):
    # Lire la video et les tracks
    images_Video = lireVideo(chemin_Video)
    tracker = Tracker('video_Foot_Ml/models/detecteur_foot_n.pt')
    tracks = tracker.getObjetTrack(
        images_Video,
        lis_Acces=video_Deja_Faite,
        chemin_Acces=os.path.join(
            os.path.dirname(__file__),
            "stubs", "track_stubs.pkl"
        ),
        rappel_Progression=rappel_Progression
    )

    # Trouver le premier index de frame pour n'importe quel joueur
    first_Frame = next(
        (i for i, frame_Dict in enumerate(tracks['players'])
         if frame_Dict),
        None
    )
    if first_Frame is None:
        print("Aucun joueur détecté dans n'importe quelle frame.")
        return

    print(f"sauvegarder le crop de la frame #{first_Frame}, "
          f"{len(tracks['players'][first_Frame])} players found.")

    # Trouver un joueur (ou les mettre dans une boucle)
    track_Id, joueur = next(
        iter(tracks['players'][first_Frame].items())
    )
    bbox = joueur['bbox']
    frame_Image = images_Video[first_Frame]
    crop = frame_Image[
           int(bbox[1]):int(bbox[3]),
           int(bbox[0]):int(bbox[2])
           ]
    print("  • bbox:", bbox, "→ crop.shape:", crop.shape)

    # Faire un repertoire pour le output
    script_Dir = os.path.dirname(os.path.abspath(__file__))
    repo_Root = os.path.dirname(script_Dir)
    out_Dir = os.path.join(repo_Root, "video_Foot_Ml", "output_videos")
    os.makedirs(out_Dir, exist_ok=True)

    # Écrire et vérifier
    out_path = os.path.join(out_Dir, f"image_rognee_{track_Id}.jpg")
    ok = cv2.imwrite(out_path, crop)
    print(f"  • imwrite retournée {ok}")
    print("  • Fichier maintenant dans", out_Dir, "→", os.listdir(out_Dir))

    # Ajouter la position
    tracker.ajouterPositionAuxTracks(tracks)

    # Estimation du mouvement de la caméra
    camera_Mouvement = MouvementCamera(images_Video[0])
    camera_Mouvement_Par_Frame = camera_Mouvement.getMouvementCamera(images_Video)
    camera_Mouvement.ajouterPositionAjusteeAuxTracks(tracks, camera_Mouvement_Par_Frame)

    # Ajouter la transformation de position
    transformation = Position_Transformee()
    transformation.ajouterPositionTransformeeAuTracks(tracks)

    # Ajouter la vitesse (km/h)
    vitesse_Distance = VitesseEtDistance()
    vitesse_Distance.suiviDeLaVitesseEtDeLaDistance(tracks)

    images_Video_Sortie = tracker.dessinerAnnotations(images_Video, tracks)

    images_Video_Sortie = camera_Mouvement.dessinerMouvementCamera(images_Video_Sortie, camera_Mouvement_Par_Frame)

    images_Video_Sortie = vitesse_Distance.dessinerVitesseEtDistance(images_Video_Sortie, tracks)

    out_Dir = os.path.join(repo_Root, "video_Foot_Ml", "output_videos")
    sauvegarderVideo(images_Video_Sortie, out_Dir, "output_videos")


def main():
    analyseYolo('video_Foot_Ml/input_videos/foot1.mp4', True)


if __name__ == '__main__':
    main()
