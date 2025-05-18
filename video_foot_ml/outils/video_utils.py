import cv2
import os


def lire_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

def sauvegarder_video(output_video_frames, output_video_path, output_video_nom):
    # Ensure the output directory exists
    os.makedirs(output_video_path, exist_ok=True)

    # Build the filename safely
    out_path = os.path.join(output_video_path, f"{output_video_nom}.mp4")

    fourcc = int(cv2.VideoWriter.fourcc(*'mp4v'))
    height, width = output_video_frames[0].shape[:2]
    out = cv2.VideoWriter(out_path, fourcc, 24.0, (width, height))

    for frame in output_video_frames:
        out.write(frame)
    out.release()
    print(f"Saved video to {out_path}")

# def sauvegarder_video(output_video_frames, output_video_path, output_video_nom):
#     fourcc = int(cv2.VideoWriter.fourcc(*'mp4v'))
#     out = cv2.VideoWriter(output_video_path + output_video_nom + ".mp4", fourcc, 24.0,
#                           (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))
#     for frame in output_video_frames:
#         out.write(frame)
#     out.release()
