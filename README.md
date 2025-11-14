# FSAE Data Logger Dashboard Playback

此專案將 TTR data logger 與影片結合，透過 Matplotlib 儀表板顯示多個參數（例如 rpm、溫度、踏板位置等），同步顯示影片方便後續追蹤車輛動態。

本專案包含兩個主要腳本：

- `cv2_player.py`：基本的影片（含音訊）播放器，
- `logger_playback.py`：主程式。讀取 `data_logger_YYYYMMDD_HHmmSS.csv`、繪製多個時間序列子圖，啟動背景影片播放執行緒，依影片播放比例移動每個子圖上的紅色時間指示線。

## 主要功能

- 支援互動控制：暫停/播放、音量上下、快進後退、結束。
- 使用多執行緒：影片播放在背景執行緒，Matplotlib 顯示在主執行緒，兩者透過多線程共享狀態。  

## 相依性

建議使用虛擬環境（Conda / Miniconda）。主要 Python 套件：

- Python 3.10
- opencv-python
- numpy
- pandas
- matplotlib
- ffpyplayer

ffpyplayer 需要系統上有其相依元件，請確保 ffmpeg 可用或參考 ffpyplayer 的[安裝說明](https://matham.github.io/ffpyplayer/installation.html)。

## 使用說明

1. 請先到 NAS 下載準備資料

2. 請在 script 輸入你的影片路徑

3. 播放單純影片

```powershell
python cv2_player.py
```

4. 啟動 Dashboard（CSV + 影片同步）

```powershell
python logger_playback.py
```

影片撥放器控制方式 ：
- 空白鍵 / p : 暫停/播放（會同時暫停影片音訊）
- s / w : 音量下/上
- a / d : 快進或後退
- ESC / q : 結束程式

## 檔案說明

- `cv2_player.py`：示範如何使用 `ffpyplayer` 與 `cv2` 同步播放影片與音訊，並處理鍵盤控制。
- `logger_playback.py`：主程式，負責讀取 CSV、建立 Matplotlib 圖表、啟動影片背景執行緒，並根據 `SharedState.ratio()` 更新時間指示線位置。


## 注意事項與建議

- ffpyplayer 的安裝在 windows 相依性較為複雜，請務必使用虛擬環境安裝，或者使用 linux 環境。  
- 目前已知 windows 環境下 Matplotlib 即時動畫效能受限，為了避免畫面延遲過重，程式中預設開啟非同步渲染 `blit=True`，但會造成移動視窗跟 scaling 時指標可能出現非預期狀態，只要回到初始狀態即可恢復正常。  


## TODO

- 加入 `--video` / `--csv` CLI 選項。
- logger Data 與影片同步
- 將 `logger_playback.py` 的 I/O 轉成可選檔案路徑或 GUI 檔案選擇。
- 提供一個小型範例資料包（含 30s 的 testvideo.mp4 與對應時間標記的 CSV）。  
- 新增 `requirements.txt`，方便他人快速上手。(已修正)
- 修正影片前進後退音軌無法同步問題。(已修正)


## 聯絡

歡迎提供 Issue 或 PR，或與我聯繫了解更多

