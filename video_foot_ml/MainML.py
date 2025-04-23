from video_foot_ml.outils import sauvegarder_video, lire_video
from video_foot_ml.trackers import Tracker
import  os
from video_foot_ml.vitesse_distance import VitesseEtDistance

def analyseYolo(chemin_vid, vid_deja_faite, progression_callback=None):
    # Lire la video
    video_images = lire_video(chemin_vid)

    # Récupère le chemin du dossier actuel (du script)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Initialiser les trackers
    tracker = Tracker('video_foot_ml/models/detecteur_foot_n.pt')
    tracks = tracker.get_object_tracks(
                                        video_images,
                                        read_from_stub=vid_deja_faite,
                                        stub_path=os.path.join(BASE_DIR, "stubs", "track_stubs.pkl"), # Construis le chemin absolu du fichier
                                        progression_callback=progression_callback
    )

    #Positions des choses
    #tracker.add_position_to_tracks(tracks)

    # Vitesse et distance
    #vitesse_distance = VitesseEtDistance()
    #vitesse_distance.suivie_de_la_vitesse_et_de_la_distance(tracks)

    # Dessin video
    video_sortie_images = tracker.draw_annotations(video_images, tracks)

    #Dessin vitesse et distance
    #vitesse_distance.dessiner_vitesse_distance(video_sortie_images,tracks)

    # Sauvegarder la video
    sauvegarder_video(video_sortie_images, "video_foot_ml/output_videos/", "output_videos")



#def main():
    # Lire la video
    #video_images = lire_video("input_videos/foot1.mp4")

    # Initialiser les trackers
    #tracker = Tracker('models/detecteur_foot_n.pt')
    #tracks = tracker.get_object_tracks(video_images, read_from_stub=True,
                                       #stub_path='stubs/track_stubs.pkl')

    # Dessin video
    #video_sortie_images = tracker.draw_annotations(video_images, tracks)

    # Sauvegarder la video
    #sauvegarder_video(video_sortie_images, "output_videos/", "output_videos")


#if __name__ == '__main__':
   # main()
