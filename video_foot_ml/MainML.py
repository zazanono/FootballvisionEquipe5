import cv2
import os
from pprint import pprint
from video_foot_ml.outils import sauvegarder_video, lire_video
from video_foot_ml.trackers import Tracker
from .couleur_equipes import *

def analyseYolo(chemin_vid, vid_deja_faite, progression_callback=None):
    # Lire vidéo & tracks
    video_images = lire_video(chemin_vid)
    tracker = Tracker('video_foot_ml/models/detecteur_foot_n.pt')
    tracks  = tracker.get_object_tracks(
        video_images,
        read_from_stub=vid_deja_faite,
        stub_path=os.path.join(
            os.path.dirname(__file__),
            "stubs", "track_stubs.pkl"
        ),
        progression_callback=progression_callback
    )

    # Trouver la première image avec des joueurs
    first_frame = next(
        (i for i, frame_dict in enumerate(tracks['players'])
         if frame_dict),
        None
    )
    if first_frame is None:
        print("Aucun joueur dans les images.")
        return

    print(f"Sauvegarde de l'image rognée #{first_frame}, "
          f"{len(tracks['players'][first_frame])} joueurs trouvés.")

    # Choisir un joueur
    track_id, player = next(
        iter(tracks['players'][first_frame].items())
    )
    bbox      = player['bbox']
    frame_img = video_images[first_frame]
    crop = frame_img[
        int(bbox[1]):int(bbox[3]),
        int(bbox[0]):int(bbox[2])
    ]
    print("  • bbox:", bbox, "→ crop.shape:", crop.shape)

    # Construction du chemin de sortie
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root  = os.path.dirname(script_dir)
    out_dir    = os.path.join(repo_root, "video_foot_ml", "output_videos")
    os.makedirs(out_dir, exist_ok=True)

    # Vérification
    out_path = os.path.join(out_dir, f"image_rognee_{track_id}.jpg")
    ok       = cv2.imwrite(out_path, crop)
    print("  • Fichier dans ", out_dir, "→", os.listdir(out_dir))

    # Assigner les équipes
    couleurs_equipes = CouleurEquipe()
    couleurs_equipes.assignation_couleur(frame_img, tracks['players'][first_frame])

    for num_image, track_joueur in enumerate(tracks['players']):
        for id_joueur, track in track_joueur.items():
            equipe = couleurs_equipes.get_equipe_joueur(video_images[num_image], track['bbox'], id_joueur)
            tracks['players'][num_image][id_joueur]['équipe'] = equipe
            tracks['players'][num_image][id_joueur]['couleur_équipe'] = couleurs_equipes.couleur_equipe[equipe]


    # Sauvegarder la vidéo
    video_sortie_images = tracker.draw_annotations(video_images, tracks)

    sauvegarder_video(video_sortie_images,
                      os.path.join(repo_root, "/video_foot_ml/output_videos/"),
                      "output_videos1")


def main():
    analyseYolo('video_foot_ml/input_videos/foot1.mp4', True)

if __name__ == '__main__':
    main()
