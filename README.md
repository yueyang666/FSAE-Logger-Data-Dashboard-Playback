# FSAE Data Logger Dashboard Playback

此專案將影片播放與車輛感測資料（CSV）同步，透過一個可互動的 Matplotlib 儀表板顯示多個參數（例如 rpm、溫度、踏板位置等），並以影片播放比例驅動時間軸上的游標。

本專案包含兩個主要腳本：

- `cv2_player.py`：簡單的影片（含音訊）播放器，使用 `ffpyplayer` + `opencv`。支援暫停/播放與音量調整。
- `logger_playback.py`：主要的 dashboard 腳本。讀取 `.csv`、繪製多個時間序列子圖，啟動背景影片播放執行緒，依影片播放比例移動每個子圖上的紅色時間指示線。

## 主要功能

- 支援互動控制：暫停/播放、音量上下、結束。
- 使用多執行緒：影片播放在背景執行緒，Matplotlib 顯示在主執行緒，兩者透過共享狀態（ratio）溝通。

## 相依性

建議使用虛擬環境（venv / conda）。主要 Python 套件：

- Python 3.10
- ffpyplayer
- opencv-python
- pandas
- matplotlib

ffpyplayer 需要系統上有 ffmpeg（或其相依元件），請確保 ffmpeg 可用或參考 ffpyplayer 的安裝說明。

## 使用說明

1. 請先到 NAS 下載準備資料

2. 播放單純影片（僅影音播放器）

```powershell
python cv2_player.py
```

控制鍵：
- 空白鍵 / p : 暫停/播放
- s : 降低音量
- w : 提高音量
- ESC 或 q : 離開

3. 啟動 Dashboard（CSV + 影片同步）

```powershell
python logger_playback.py
```



控制方式（與影片播放互動）：
- 空白鍵 / p : 暫停/播放（會同時暫停影片音訊）
- s / w : 音量下/上
- ESC / q : 結束程式（會關閉視窗並要求背景執行緒停止）

## 檔案說明

- `cv2_player.py`：示範如何使用 `ffpyplayer` 與 `cv2` 同步播放影片與音訊，並處理鍵盤控制。
- `logger_playback.py`：主程式，負責讀取 CSV、建立 Matplotlib 圖表、啟動影片背景執行緒，並根據 `SharedState.ratio()` 更新時間指示線位置。


## 注意事項與建議

- ffpyplayer 的安裝在某些平台上可能較為複雜，必要時可改用其他音訊/視訊播放套件（如直接使用 ffmpeg + subprocess，或使用 VLC bindings）。
- 若資料量很大，Matplotlib 即時動畫效能可能受限，可考慮使用更適合即時視覺化的工具（例如 Bokeh、Plotly Dash、Dashboards）或降採樣資料。


## TODO

- 加入 `--video` / `--csv` CLI 選項。
- LOGGER Data 與影片同步
- 將 `logger_playback.py` 的 I/O 轉成可選檔案路徑或 GUI 檔案選擇。
- 提供一個小型範例資料包（含 30s 的 testvideo.mp4 與對應時間標記的 CSV）。  
- 新增 `requirements.txt`，方便他人快速上手。
- 修正影片前進後退音軌無法同步問題


## 聯絡

歡迎提供 Issue 或 PR，或與我聯繫了解更多

