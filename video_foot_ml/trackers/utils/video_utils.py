import cv2

def lire_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

def sauvegarder_video(output_video_frames, output_video_path, output_video_num):
    fourcc = int(cv2.VideoWriter.fourcc(*'mp4v'))
    out = cv2.VideoWriter("output_videos/outputfoot"+ str(output_video_num) + ".mp4", fourcc, 24.0, (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))
    for frame in output_video_frames:
        out.write(frame)
    out.release()