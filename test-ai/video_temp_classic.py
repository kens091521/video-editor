import os
import cv2
import json
import subprocess

# 設定參數
video_id = "0UKDiJH4dtk_shorts"
start_time = 390.66   # 這是你 json 片段的 start_time
end_time = 427.32     # 這是你 json 片段的 end_time
json_path = "output_json/29/0UKDiJH4dtk_shorts/5.json"

# 1. 下載 YouTube 影片
youtube_url = f"https://www.youtube.com/watch?v={video_id}"
full_video_path = f"temp_{video_id}_full.mp4"
if not os.path.exists(full_video_path):
    print("正在下載完整影片...")
    subprocess.run([
        "yt-dlp", "-f", "mp4", "-o", full_video_path, youtube_url
    ], check=True)

# 2. 擷取片段
clip_path = f"temp_{video_id}_5_cut.mp4"
if not os.path.exists(clip_path):
    print("正在擷取片段...")
    duration = float(end_time) - float(start_time)
    subprocess.run(  [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", full_video_path,
            "-ss", "0",
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-avoid_negative_ts", "make_zero",
            clip_path
        ], check=True)

# 3. 讀取標註
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
results_dict = {frame["frame_number"]: frame["boxes"] for frame in data}

# 4. 標註影片
output_video_path = f"output_video/{video_id}-with-boxes.mp4"
cap = cv2.VideoCapture(clip_path)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

frame_idx = 0
frames_with_faces = 0
total_faces_detected = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    boxes = results_dict.get(frame_idx, [])
    if boxes:
        frames_with_faces += 1
        total_faces_detected += len(boxes)
        for box in boxes:
            x1, y1, x2, y2 = box["x1"], box["y1"], box["x2"], box["y2"]
            color = (0, 255, 0) if box.get("speaking", False) else (0, 0, 255)
            label = f"{box['raw_score']:.3f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    else:
        # 沒有 box 的 frame，畫紅色提示
        cv2.putText(frame, "NO BOX", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    out.write(frame)
    frame_idx += 1

cap.release()
out.release()
print(f"已產生標註影片：{output_video_path}")

print(f"處理了 {frame_idx} 個框架")
print(f"其中 {frames_with_faces} 個框架有臉部檢測")
if frame_idx > 0:
    print(f"檢測率: {frames_with_faces/frame_idx*100:.1f}%")
else:
    print("檢測率: N/A")
print(f"總共檢測到 {total_faces_detected} 個臉部實例")
# （可選）自動清理暫存檔
# os.remove(full_video_path)
# os.remove(clip_path)
