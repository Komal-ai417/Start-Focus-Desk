"""Local webcam study monitor."""

import argparse
from math import hypot
from pathlib import Path
from time import monotonic


ASSETS = Path(__file__).resolve().parent / "assets"
WINDOW = "Focus Desk"
ALERTS = {
    "hidden": ("Face out of view", "faudio.mp3", (224, 185, 148)),
    "sleep": ("Eyes closed", "alarm.mp3", (145, 178, 250)),
    "phone": ("Phone in view", "paudio.mp3", (180, 150, 249)),
}


def draw_dashboard(cv2, frame, ratio, alert, phones, elapsed):
    background = (27, 28, 32)
    surface = (41, 42, 48)
    text = (242, 244, 245)
    muted = (164, 173, 178)
    mint = (175, 223, 131)
    title, _, accent = ALERTS.get(alert, ("Monitoring", None, mint))
    hints = {
        "hidden": "Move back into frame.",
        "sleep": "Open your eyes when ready.",
        "phone": "Set your phone aside.",
    }
    height, width = frame.shape[:2]
    scale = min(624 / width, 458 / height)
    preview = cv2.resize(frame, (max(1, int(width * scale)), max(1, int(height * scale))))
    image_height, image_width = preview.shape[:2]
    left = 28 + (624 - image_width) // 2
    top = 136 + (458 - image_height) // 2
    canvas = cv2.copyMakeBorder(
        preview, top, 650 - top - image_height, left, 960 - left - image_width,
        cv2.BORDER_CONSTANT, value=background,
    )

    def write(message, x, y, size=0.5, color=text, thickness=1):
        cv2.putText(canvas, message, (x, y), cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness, cv2.LINE_AA)

    cv2.line(canvas, (28, 103), (932, 103), surface, 1)
    cv2.circle(canvas, (43, 56), 15, mint, 2, cv2.LINE_AA)
    cv2.circle(canvas, (43, 56), 4, mint, -1, cv2.LINE_AA)
    write("Focus Desk", 70, 64, 1.0, text, 2)
    write("PERSONAL STUDY MONITOR", 72, 86, 0.36, muted)
    cv2.circle(canvas, (826, 61), 4, mint, -1, cv2.LINE_AA)
    write("CAMERA LIVE", 838, 66, 0.41, mint)
    cv2.rectangle(canvas, (27, 135), (652, 594), surface, 1)

    for box in phones.xyxy.tolist():
        x1, y1, x2, y2 = box
        cv2.rectangle(
            canvas, (left + int(x1 * scale), top + int(y1 * scale)),
            (left + int(x2 * scale), top + int(y2 * scale)), ALERTS["phone"][2], 2,
        )

    cv2.rectangle(canvas, (674, 136), (932, 594), surface, -1)
    cv2.rectangle(canvas, (674, 136), (932, 140), accent, -1)
    write("SESSION STATUS", 697, 178, 0.43, muted)
    write(title, 697, 218, 0.81, accent, 2)
    write(hints.get(alert, "Camera checks are active."), 697, 248, 0.45, text)
    cv2.line(canvas, (697, 278), (909, 278), muted, 1)
    write("ELAPSED", 697, 314, 0.43, muted)
    minutes, seconds = divmod(int(elapsed), 60)
    write(f"{minutes:02d}:{seconds:02d}", 697, 350, 0.9, text, 2)
    write("FACE", 697, 403, 0.43, muted)
    write("In frame" if ratio is not None else "Unavailable", 697, 430, 0.55)
    write("PHONE", 697, 480, 0.43, muted)
    write("Detected" if len(phones) else "None detected", 697, 507, 0.55)
    write("EYE OPENNESS SCORE", 697, 550, 0.43, muted)
    write(f"{ratio:.1f}" if ratio is not None else "Unavailable", 697, 576, 0.55)
    write("LOCAL CAMERA PREVIEW", 28, 624, 0.4, muted)
    write("Q / ESC TO EXIT", 804, 624, 0.42, muted)
    return canvas


def eye_ratio(face, width, height):
    def distance(first, second):
        a, b = face[first], face[second]
        return hypot((a.x - b.x) * width, (a.y - b.y) * height)

    eye_width = distance(130, 243)
    return 100 * distance(159, 145) / eye_width if eye_width else None


def warning(hidden_seconds, closed_seconds, phone_visible):
    if hidden_seconds >= 0.7:
        return "hidden"
    if closed_seconds >= 0.6:
        return "sleep"
    if phone_visible:
        return "phone"
    return None


def run(args):
    import pygame

    pygame.mixer.init()
    try:
        sounds = {
            key: pygame.mixer.Sound(str(ASSETS / filename))
            for key, (_, filename, _) in ALERTS.items()
        }
        channel = pygame.mixer.Channel(0)
        if args.test_sound:
            channel.play(sounds[args.test_sound])
            while channel.get_busy():
                pygame.time.wait(30)
            return
        monitor(args, sounds, channel)
    finally:
        pygame.mixer.quit()


def monitor(args, sounds, channel):
    import cv2
    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions, vision
    from ultralytics import YOLO

    options = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(ASSETS / "face_landmarker.task")),
        running_mode=vision.RunningMode.VIDEO,
    )
    model_path = ASSETS / "yolov8n.pt"
    if not model_path.is_file():
        raise RuntimeError("Missing assets/yolov8n.pt. Run Start Focus Desk.cmd to set up the app.")
    phone_model = YOLO(str(model_path))
    capture = cv2.VideoCapture(args.video if args.video else args.camera)
    try:
        if not capture.isOpened():
            raise RuntimeError("Could not open the camera or video source.")
        with vision.FaceLandmarker.create_from_options(options) as face_model:
            hidden_since = closed_since = None
            playing = None
            started = monotonic()
            frame_number = 0
            fps = capture.get(cv2.CAP_PROP_FPS) or 30
            last_timestamp = -1
            while True:
                ok, frame = capture.read()
                if not ok:
                    if args.video:
                        break
                    raise RuntimeError("The camera stopped sending frames.")
                if args.crop:
                    x, y, width, height = args.crop
                    frame = frame[y:y + height, x:x + width]
                    if not frame.size:
                        raise RuntimeError("The crop falls outside the video.")
                now = frame_number / fps if args.video else monotonic() - started
                frame_number += 1
                timestamp = max(last_timestamp + 1, int(now * 1000))
                last_timestamp = timestamp
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                faces = face_model.detect_for_video(
                    mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp
                ).face_landmarks
                height, width = frame.shape[:2]
                ratio = eye_ratio(faces[0], width, height) if faces else None
                if faces:
                    hidden_since = None
                elif hidden_since is None:
                    hidden_since = now
                if ratio is None or ratio >= 11:
                    closed_since = None
                elif closed_since is None:
                    closed_since = now
                phones = phone_model.predict(frame, classes=[67], conf=0.5, verbose=False)[0].boxes
                alert = warning(
                    now - hidden_since if hidden_since is not None else 0,
                    now - closed_since if closed_since is not None else 0,
                    len(phones) > 0,
                )
                if args.check:
                    if alert and alert != playing:
                        print(f"{now:.2f}s {alert}", flush=True)
                    playing = alert
                    continue
                if not channel.get_busy():
                    playing = alert
                    if playing:
                        channel.play(sounds[playing])
                dashboard = draw_dashboard(cv2, frame, ratio, alert or playing, phones, now)
                cv2.imshow(WINDOW, dashboard)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27) or cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                    break
    finally:
        capture.release()
        if not args.check:
            cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--video", help="Use a video file in place of the webcam")
    parser.add_argument("--crop", type=int, nargs=4, metavar=("X", "Y", "W", "H"))
    parser.add_argument("--check", action="store_true", help="Print detections from a video without opening a window")
    parser.add_argument("--test-sound", choices=ALERTS)
    args = parser.parse_args()
    if args.check and not args.video:
        parser.error("--check requires --video")
    try:
        if args.check:
            monitor(args, {}, None)
        else:
            run(args)
    except (ImportError, OSError, RuntimeError) as error:
        parser.exit(1, f"{WINDOW}: {error}\n")


if __name__ == "__main__":
    main()
