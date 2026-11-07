<div align="center">

# Focus Desk

**A personal study dashboard for Windows**

Live webcam preview · Eye openness score · Audio alerts · Session timer

[Get started](#quick-start) · [Change the sounds](#change-the-alert-sounds) · [Our products](#our-products) · [Troubleshooting](#troubleshooting)

</div>

---

Focus Desk brings your camera preview, study session timer, and distraction alerts into a charcoal and mint dashboard. It checks for closed eyes, a hidden face, and phones visible to the camera.

| Feature | What you see |
| --- | --- |
| Live camera preview | Your webcam feed with a box around detected phones |
| Eye openness score | A live reading of how wide your eye is open |
| Visual and audio alerts | Warnings for closed eyes, a missing face, and a visible phone |
| Session timer | Time elapsed since monitoring started |
| Custom sounds | Three replaceable MP3 clips for the different alerts |

The dashboard shows a live **Eye Openness Score** when it can see your face. Higher scores indicate a wider eye opening. A score below 11 for about 0.6 seconds triggers the eyes-closed alert. The score is based on eye landmarks and has no fixed maximum.

## Our products

Explore our coding, puzzle, and browser tools.

| Product | Explore |
| --- | --- |
| **CodeSmash** | A coding platform for DSA practice and interview preparation, with problem sets, quizzes, mock online assessments, and coding battles. [Visit CodeSmash](https://codesmash.in/) |
| **MyLnkly · Queens** | A logic puzzle website with Queens boards, daily challenges, online battles, and private matches with friends. [Play at MyLnkly](https://mylnkly.in/) |
| **Codeforces extension** | Our Chrome extension for Codeforces users. View its features and installation details on the store page. [Open the Chrome Web Store](https://chromewebstore.google.com/detail/begidbnffjelhnjckgpelbgfeaiiadhp) |

---

## What you need

- A 64-bit Windows PC with a working webcam and speakers or headphones.
- 64-bit Python 3.11, 3.12, or 3.13. For a fresh setup, use Python 3.13 from [python.org](https://www.python.org/downloads/). Keep the **Python Launcher** option enabled during installation so Windows can run the `py` command.
- An internet connection for the first setup. The Python packages can take several minutes to download.
- The full Focus Desk folder, including `app.py`, `Start Focus Desk.cmd`, `requirements.txt`, and `assets`. If you received a ZIP, extract it first. The `assets` folder already contains the camera models and alert sounds.

## Quick start

1. Open the extracted Focus Desk folder in File Explorer.
2. Double-click **Start Focus Desk.cmd**. A terminal window opens and installs the dependencies into a local folder called `.venv` on the first run.
3. Wait for the camera dashboard to open. Keep the terminal window open while you use the app.
4. Click the camera window and press **Q** or **Esc** to exit. For future sessions, double-click the same launcher.

## Manual setup in Command Prompt

Open the project folder in File Explorer, type `cmd` into the address bar, and press **Enter**. Run these commands one at a time:

```bat
py -3 --version
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

If the version check shows an unsupported Python version, install Python 3.13 and use `py -3.13 -m venv .venv` to create the environment for a fresh setup. Once setup succeeds, the last command starts the app directly.

### What gets installed

`requirements.txt` lists the exact Python package versions. The launcher or the manual install command installs them and their dependencies together.

| Package | Used for |
| --- | --- |
| `opencv-python` and `opencv-contrib-python` | Opening the webcam, processing frames, and drawing the dashboard |
| `mediapipe` | Finding face and eye landmarks |
| `ultralytics` | Detecting phones with the included YOLO model |
| `pygame-ce` | Playing the MP3 alerts |

## Change the alert sounds

| When the camera sees | Dashboard message | File in `assets` | Test option |
| --- | --- | --- | --- |
| Eyes closed for about 0.6 seconds | Eyes closed | `alarm.mp3` | `sleep` |
| No visible face for about 0.7 seconds | Face out of view | `faudio.mp3` | `hidden` |
| A detected phone | Phone in view | `paudio.mp3` | `phone` |

1. Close Focus Desk. Open the `assets` folder and copy the current alert file somewhere safe if you want to restore it later.
2. Choose or record the sound you want and export it as an MP3. If your recording is a WAV, M4A, or another format, convert it to MP3 first.
3. Rename the new MP3 to the exact filename in the table, then copy it into `assets` and choose **Replace the file in the destination**. For example, a custom phone alert goes in `assets\paudio.mp3`.
4. Start Focus Desk again. To hear an alert without opening the webcam, run one of these commands from the project folder in Command Prompt.

```bat
"Start Focus Desk.cmd" --test-sound sleep
"Start Focus Desk.cmd" --test-sound hidden
"Start Focus Desk.cmd" --test-sound phone
```

If you used manual setup, run `.venv\Scripts\python.exe app.py --test-sound phone` and replace `phone` with the option you want.

## Troubleshooting

- **Windows says `py` is unavailable.** Install Python with the launcher option enabled, then open a new Command Prompt.
- **Package installation fails.** Check your internet connection and Python version. Keep the terminal open so you can read the installation error.
- **The camera does not open.** Close other apps using it and check camera permissions in Windows Settings. If you have a second webcam, run `"Start Focus Desk.cmd" --camera 1` from Command Prompt.
- **There is no sound.** Check the Windows output device and volume, then try a sound test above. Check that the replacement is an MP3 and that Windows has not added a second extension such as `.mp3.mp3`.

## Project files

```text
Focus Desk/
├── app.py                    Application and dashboard
├── Start Focus Desk.cmd      Windows launcher and first-run setup
├── requirements.txt          Python dependencies
├── README.md                 Setup and usage guide
└── assets/
    ├── alarm.mp3             Eyes-closed alert
    ├── faudio.mp3            Face-out-of-view alert
    ├── paudio.mp3            Phone alert
    ├── face_landmarker.task  Face and eye model
    └── yolov8n.pt            Object detection model
```

Focus Desk processes webcam frames on your computer and displays them live.

## License

Original Focus Desk code and documentation are available under the [MIT License](LICENSE). You may use, copy, modify, and distribute these contributions while keeping the copyright and license notice.

Third-party code, dependencies, model files, and audio retain their respective rights and license terms. The MIT license applies to contributions owned by the copyright holder. The included Ultralytics YOLO model and dependency have their own licensing requirements. Review the [Ultralytics license terms](https://www.ultralytics.com/license) when using or distributing the complete application.
