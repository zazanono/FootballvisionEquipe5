from video_foot_ml.utils.video_utils import sauvegarder_video, lire_video
from trackers import Tracker

def main(video_path):
    # Lire la video
    video_images = lire_video(video_path)

    # Initialiser les trackers
    tracker = Tracker('models/football-player-detector-n.pt')
    tracks = tracker.get_object_tracks(video_images, read_from_stub=True, stub_path='stubs/track_stubs.pkl')

    # Dessin video
    video_sortie_images = tracker.draw_annotations(video_images, tracks)

    # Sauvegarder la video
    sauvegarder_video(video_sortie_images, "/output_videos_outputfoot.mp4", 2)


if __name__ == '__main__':
    main()
