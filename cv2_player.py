# cv2_player.py

from ffpyplayer.player import MediaPlayer
import cv2

video_path = "./testvideo.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"無法開啟影片：{video_path}")
    exit()

player = MediaPlayer(video_path)
player.set_volume(0.3)
paused = False
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS) or 33.0
delay_ms = int(max(1, 1000.0 / fps))


win = "Video Player"
cv2.namedWindow(win, cv2.WINDOW_NORMAL)

last_frame = None  # 暫停時維持最後畫面

print("控制方式：空白鍵(p)=暫停/播放")

while True:

    if not paused:
        ret, frame = cap.read()
        audio_frame, val = player.get_frame()

        if not ret:
            break

        last_frame = frame
        cv2.imshow(win, frame)
        current_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        if val != 'eof' and audio_frame is not None:
            _img, _t = audio_frame
    else:
        if last_frame is not None:
            cv2.imshow(win, last_frame)

    # 等待鍵盤輸入（33ms）
    key = cv2.waitKey(delay_ms if not paused else 10) & 0xFF

    if key in (27, ord('q'), ord('Q')):     # ESC 或 q / Q
        break

    elif key in (ord('p'), ord('P'), 32):   # 空白鍵 或 p / P
        new_p = not paused
        player.set_pause(new_p)
    elif key in (ord('s'), ord('S')):  # s / S 降低音量
        vol = max(0.0, player.get_volume() - 0.1)
        player.set_volume(vol)
        print(f"音量: {vol:.1f}")

    elif key in (ord('w'), ord('W')):  # w / W 提高音量
        vol = min(1.0, player.get_volume() + 0.1)
        player.set_volume(vol)
        print(f"音量: {vol:.1f}")

cap.release()
cv2.destroyAllWindows()
