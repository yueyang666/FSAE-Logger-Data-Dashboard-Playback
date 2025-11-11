# logger_playback.py


import math
import threading
import time
from dataclasses import dataclass

import cv2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from ffpyplayer.player import MediaPlayer


@dataclass
class SharedState:
    """跨執行緒共享狀態。"""
    frame_idx: int = 0
    total_frames: int = 1
    paused: bool = False
    quit: bool = False

    def __post_init__(self):
        self._lock = threading.Lock()

    def set_total(self, n: int) -> None:
        """設定影片總幀數。"""
        with self._lock:
            self.total_frames = max(1, int(n))

    def set_idx(self, i: int) -> None:
        """設定當前幀索引。"""
        with self._lock:
            self.frame_idx = int(max(0, min(i, self.total_frames - 1)))

    def step(self, delta: int) -> int:
        """幀索引加減並回傳新值。"""
        with self._lock:
            self.frame_idx = int(max(0, min(self.frame_idx + delta, self.total_frames - 1)))
            return self.frame_idx

    def set_paused(self, p: bool) -> None:
        """切換暫停狀態。"""
        with self._lock:
            self.paused = bool(p)

    def set_quit(self) -> None:
        """要求各執行緒結束。"""
        with self._lock:
            self.quit = True

    def snapshot(self):
        """取得目前狀態快照（避免長時間持鎖）。"""
        with self._lock:
            return self.frame_idx, self.total_frames, self.paused, self.quit

    def ratio(self) -> float:
        """依目前幀索引回傳播放比例（0~1）。"""
        with self._lock:
            if self.total_frames <= 1:
                return 0.0
            return self.frame_idx / float(self.total_frames - 1)


def run_video_thread(state: SharedState, video_path: str) -> None:
    """
    影片+音訊播放執行緒（無滑桿版）。
    控制方式：
      空白鍵 / p  暫停/播放
      ← / →       單幀或一秒移動
      ESC / q     離開
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"無法開啟影片：{video_path}")
        state.set_quit()
        return

    player = MediaPlayer(video_path)
    player.set_volume(0.3)
    
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 33.0
    delay_ms = int(max(1, 1000.0 / fps))
    state.set_total(total)

    win = "Video Player"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    last_frame = None  # 暫停時維持最後畫面

    print("控制方式：空白鍵(p)=暫停/播放")

    while True:
        idx, tot, paused, quit_flag = state.snapshot()
        if quit_flag:
            break

        if not paused:
            ret, frame = cap.read()
            audio_frame, val = player.get_frame()

            if not ret:
                state.set_quit()
                break

            last_frame = frame
            cv2.imshow(win, frame)
            current_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            state.set_idx(current_pos)

            if val != 'eof' and audio_frame is not None:
                _img, _t = audio_frame
        else:
            if last_frame is not None:
                cv2.imshow(win, last_frame)

        key = cv2.waitKey(delay_ms if not paused else 10) & 0xFF
        if key in (27, ord('q'), ord('Q')):     # ESC 或 q / Q
            state.set_quit()
            break

        elif key in (ord('p'), ord('P'), 32):   # 空白鍵 或 p / P
            new_p = not paused
            state.set_paused(new_p)
            player.set_pause(new_p)

        # elif key in (ord('a'), ord('A')):  # a / A
        #     new_idx = state.step(int(-fps))  # 往前一秒
        #     cap.set(cv2.CAP_PROP_POS_FRAMES, new_idx)
        #     current_time = new_idx / fps

        #     player.set_pause(True)
        #     player.seek(max(0.0, current_time), relative=False)
        #     time.sleep(0.05)  # 等待 ffpyplayer 內部解碼器穩定
        #     player.set_pause(paused)
        #     print(f"跳到 {current_time:.2f} 秒")

        # elif key in (ord('d'), ord('D')):  # d / D
        #     new_idx = state.step(int(fps))   # 往後一秒
        #     cap.set(cv2.CAP_PROP_POS_FRAMES, new_idx)
        #     current_time = new_idx / fps

        #     player.set_pause(True)
        #     player.seek(min(current_time, total / fps - 0.1), relative=False)
        #     time.sleep(0.05)
        #     player.set_pause(paused)
        #     print(f"跳到 {current_time:.2f} 秒")

        elif key in (ord('s'), ord('S')):  # s / S 降低音量
            vol = max(0.0, player.get_volume() - 0.1)
            player.set_volume(vol)
            print(f"音量: {vol:.1f}")

        elif key in (ord('w'), ord('W')):  # w / W 提高音量
            vol = min(1.0, player.get_volume() + 0.1)
            player.set_volume(vol)
            print(f"音量: {vol:.1f}")
    
    cap.release()
    cv2.destroyWindow(win)
    

def main():
    # === 讀取 CSV ===
    csv_file = "10180230.csv"
    df = pd.read_csv(csv_file)

    # 轉換時間欄位
    time_col = "Year_Date_Time"
    df[time_col] = pd.to_datetime(df[time_col], format="%Y-%m-%d %H:%M:%S:%f", errors="coerce")
    df = df.dropna(subset=[time_col])

    # === 顯示可選欄位並讓使用者以序號選擇 ===
    numeric_cols = [c for c in df.columns if c != time_col and pd.api.types.is_numeric_dtype(df[c])]
    print("\n可用參數如下：")
    for i, col in enumerate(numeric_cols, 1):
        print(f"{i:2d}. {col}")

    user_input = input("\n請輸入想要播放的參數序號（以逗號分隔，例如: 1,3,7）：\n> ")
    try:
        sel_idx = [int(x.strip()) for x in user_input.split(",") if x.strip().isdigit()]
        cols_to_plot = [numeric_cols[i - 1] for i in sel_idx if 1 <= i <= len(numeric_cols)]
    except Exception:
        cols_to_plot = []

    if not cols_to_plot:
        print("未輸入有效參數，使用預設：['rpm', 'Motor Temp', 'Pedal']")
        cols_to_plot = ["rpm", "Motor Temp", "Pedal"]

    # === 建立 Matplotlib 子圖 ===
    n = len(cols_to_plot)
    cols = 2
    rows = math.ceil(n / cols)

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, axes = plt.subplots(rows, cols, figsize=(12, rows * 2.5), sharex=True)
    axes = axes.flatten()

    indicators = []
    for i, col in enumerate(cols_to_plot):
        ax = axes[i]
        ax.plot(df[time_col], df[col], label=col, linewidth=1)
        ax.set_title(col, fontsize=10)
        ax.legend(loc="upper right", fontsize=8)
        ax.tick_params(axis="x", rotation=15)
        indicator = ax.axvline(df[time_col].iloc[0], color="red", linestyle="-", linewidth=1)
        indicators.append(indicator)
    # 隱藏多餘 subplot
    if len(axes) > n:
        for j in range(n, len(axes)):
            axes[j].set_visible(False)

    fig.suptitle("Multi-parameter dashboard (threaded, video-synced by ratio)", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    # === 啟動影片播放執行緒 ===
    video_path = "./testvideo.mp4"
    state = SharedState()
    vt = threading.Thread(target=run_video_thread, args=(state, video_path), daemon=True)
    vt.start()

    # === Matplotlib 更新函式：依比例移動紅線 ===
    t_min, t_max = df[time_col].iloc[0], df[time_col].iloc[-1]

    def update(_frame):
        """根據影片播放比例更新紅線位置。"""
        r = state.ratio()  # 0~1
        current_time = t_min + (t_max - t_min) * r
        for ind in indicators:
            ind.set_xdata([current_time])
        # 當背景執行緒發出 quit 時，讓動畫停止
        _, _, _, q = state.snapshot()
        if q:
            plt.close(fig)
        return indicators

    # === 動畫設定 ===
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(df),
        interval=10,   # 毫秒，控制播放速度
        blit=True,
        repeat=False
    )
    try:
        plt.show()
    finally:
        # 當視窗關閉，要求背景執行緒結束
        state.set_quit()
        vt.join(timeout=2.0)


if __name__ == "__main__":
    main()
