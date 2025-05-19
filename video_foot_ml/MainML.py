import cv2
import os
from pprint import pprint
from video_foot_ml.outils import sauvegarder_video, lire_video
from video_foot_ml.trackers import Tracker
from video_foot_ml.camera_mouvement import CameraMouvement
from video_foot_ml.transformation import Position_transforme
from video_foot_ml.vitesse_distance import VitesseEtDistance

def analyseYolo(chemin_vid, vid_deja_faite, progression_callback=None):
    # 1) Read video & tracks
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

    # 2) Find first frame index with any players
    first_frame = next(
        (i for i, frame_dict in enumerate(tracks['players'])
         if frame_dict),
        None
    )
    if first_frame is None:
        print("⚠️ No players detected in any frame.")
        return

    print(f"👉 Saving crop from frame #{first_frame}, "
          f"{len(tracks['players'][first_frame])} players found.")

    # 3) Pick one player (or loop them all)
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

    # 4) Build absolute output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root  = os.path.dirname(script_dir)
    out_dir    = os.path.join(repo_root, "video_foot_ml", "output_videos")
    os.makedirs(out_dir, exist_ok=True)

    # 5) Write and verify
    out_path = os.path.join(out_dir, f"image_rognee_{track_id}.jpg")
    ok       = cv2.imwrite(out_path, crop)
    print(f"  • imwrite returned {ok}")
    print("  • Files now in", out_dir, "→", os.listdir(out_dir))

    # Ajouter la position
    tracker.add_position_to_tracks(tracks)
    # camera movement estimator
    camera_movement_estimator = CameraMouvement(video_images[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_images)
    camera_movement_estimator.add_adjust_positions_to_tracks(tracks, camera_movement_per_frame)
    # Ajouter transformation de position et vitesse apres (j'ai le code pour ca juste dit quand tas regler)

    # …then your existing draw & save-video calls
    video_sortie_images = tracker.draw_annotations(video_images, tracks)
    video_sortie_images = camera_movement_estimator.draw_camera_movement(video_sortie_images,camera_movement_per_frame)

    out_dir = os.path.join(repo_root, "video_foot_ml", "output_videos")
    sauvegarder_video(video_sortie_images, out_dir, "output_videos")


def main():
    analyseYolo('video_foot_ml/input_videos/foot1.mp4', True)

if __name__ == '__main__':
    main()