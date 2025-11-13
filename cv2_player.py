# cv2_player.py

from ffpyplayer.player import MediaPlayer
import cv2
import numpy as np

####### 參數設定 #######
video_path = "./testvideo.mp4"

#######################


cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"無法開啟影片：{video_path}")
    exit()

player = MediaPlayer(video_path)
player.set_volume(0.3)

fps = cap.get(cv2.CAP_PROP_FPS) or 33.0
delay_ms = int(max(1, 1000.0 / fps))
val = ''


win = "Video Player"
cv2.namedWindow(win, cv2.WINDOW_NORMAL)

print("控制方式：空白鍵(p)=暫停/播放")

while val != 'eof':

    frame, val = player.get_frame()
    if val != 'eof' and frame is not None:
        img, t = frame
        w, h = img.get_size()
        buf = img.to_bytearray()[0]
        rgb = np.frombuffer(buf, dtype=np.uint8).reshape(h, w, 3)

        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        cv2.imshow(win, bgr)

    # 等待鍵盤輸入（33ms）
    key = cv2.waitKey(delay_ms) & 0xFF

    if key in (27, ord('q'), ord('Q')):     # ESC 或 q / Q
        break

    elif key in (ord('p'), ord('P'), 32):   # 空白鍵 或 p / P
        player.toggle_pause()

    elif key in (ord('a'), ord('A')):        # a / A
        player.seek(-1.0, relative=True)

    elif key in (ord('d'), ord('D')):         # d / D
        player.seek(1.0, relative=True)

    elif key in (ord('s'), ord('S')):       # s / S 降低音量
        vol = max(0.0, player.get_volume() - 0.1)
        player.set_volume(vol)
        print(f"音量: {vol:.1f}")

    elif key in (ord('w'), ord('W')):       # w / W 提高音量
        vol = min(1.0, player.get_volume() + 0.1)
        player.set_volume(vol)
        print(f"音量: {vol:.1f}")

cap.release()
cv2.destroyAllWindows()
player.close_player()