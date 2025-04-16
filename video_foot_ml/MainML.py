from video_foot_ml.utils import sauvegarder_video, lire_video
from video_foot_ml.trackers import Tracker

def analyseYolo(chemin_vid, vid_deja_faite):
    # Lire la video
    video_images = lire_video(chemin_vid)

    # Initialiser les trackers
    tracker = Tracker('video_foot_ml/models/detecteur_foot_n.pt')
    tracks = tracker.get_object_tracks(video_images, read_from_stub=vid_deja_faite,
                                       stub_path='stubs/track_stubs.pkl')

    # Dessin video
    video_sortie_images = tracker.draw_annotations(video_images, tracks)

    # Sauvegarder la video
    sauvegarder_video(video_sortie_images, "output_videos/", "output_videos")

    # Dire au chargement que le traitement video est terminé



def main():
    # Lire la video
    video_images = lire_video("input_videos/foot1.mp4")

    # Initialiser les trackers
    tracker = Tracker('models/detecteur_foot_n.pt')
    tracks = tracker.get_object_tracks(video_images, read_from_stub=True,
                                       stub_path='stubs/track_stubs.pkl')

    # Dessin video
    video_sortie_images = tracker.draw_annotations(video_images, tracks)

    # Sauvegarder la video
    sauvegarder_video(video_sortie_images, "output_videos/", "output_videos")


if __name__ == '__main__':
    main()
