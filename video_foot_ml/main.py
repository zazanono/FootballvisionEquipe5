from utils import sauvegarder_video, lire_video
from trackers import Tracker


def main():
    # Lire la video
    video_images = lire_video("video_foot_ml/input_videos/foot1.mp4")

    # Initialiser les trackers
    tracker = Tracker('video_foot_ml/models/football-player-detector-n.pt')
    tracks = tracker.get_object_tracks(video_images, read_from_stub=True,
                                       stub_path='video_foot_ml/stubs/track_stubs.pkl')

    # Dessin video
    video_sortie_images = tracker.draw_annotations(video_images, tracks)

    # Sauvegarder la video
    sauvegarder_video(video_sortie_images, "video_foot_ml/output_videos/", 2)


if __name__ == '__main__':
    main()
