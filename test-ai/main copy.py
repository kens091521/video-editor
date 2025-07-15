import requests
import cv2
import json
from mixModel import getOutcomeJson
import os
import subprocess
from pathlib import Path

# video_url = "https://storage.googleapis.com/sieve-prod-us-central1-public-file-upload-bucket/d979a930-f2a5-4e0d-84fe-a9b233985c4e/dba9cbf3-8374-44bc-8d9d-cc9833d3f502-input-file.mp4"
# input_video_path = "test_vid.mp4"
# output_video_path = "output_with_boxes.mp4"

# # with requests.get(video_url, stream=True) as r:
# #     r.raise_for_status()
# #     with open(input_video_path, 'wb') as f:
# #         for chunk in r.iter_content(chunk_size=8192):
# #             f.write(chunk)


# # if the output.json file already exists, no need to call getOutcomeJson again
# if not os.path.exists("output.json"):
#     print("Processing video to get active speaker detection results...")
#     # Call the function to process the video and get the results
#     getOutcomeJson()

# cap = cv2.VideoCapture(input_video_path)
# fps = cap.get(cv2.CAP_PROP_FPS)
# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

# with open("output.json", "r", encoding="utf-8") as f:
#     results = json.load(f)

# # 建立 frame_number -> boxes 的對應
# results_dict = {}
# for item in results:
#     frame_number = item.get("frame_number")
#     boxes = item.get("boxes")
#     results_dict[frame_number] = boxes

# print(f"載入了 {len(results)} 個框架的檢測結果")
# print(
#     f"框架範圍: {min(results_dict.keys()) if results_dict else 'N/A'} - {max(results_dict.keys()) if results_dict else 'N/A'}"
# )
# print(f"總共檢測到的臉部數量: {sum(len(boxes) for boxes in results_dict.values())}")

# # 檢查前幾個框架的檢測情況
# for i in range(min(10, len(results_dict))):
#     if i in results_dict:
#         print(f"框架 {i}: {len(results_dict[i])} 個臉部")
#     else:
#         print(f"框架 {i}: 無檢測結果")

# frame_idx = 0
# frames_with_faces = 0
# total_faces_detected = 0

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # 無論是否有檢測結果都要處理框架
#     if frame_idx in results_dict and results_dict[frame_idx]:
#         faces_in_frame = len(results_dict[frame_idx])
#         frames_with_faces += 1
#         total_faces_detected += faces_in_frame

#         for face in results_dict[frame_idx]:
#             x1, y1, x2, y2 = face["x1"], face["y1"], face["x2"], face["y2"]

#             if face["raw_score"] < 0:
#                 color = (0, 0, 255)  # 紅色 - 不在說話
#             else:
#                 color = (0, 255, 0)  # 綠色 - 在說話

#             # 格式化分數顯示
#             label = f"{face['raw_score']:.3f}"

#             # 畫邊界框
#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

#             # 添加文字標籤
#             cv2.putText(
#                 frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
#             )

#     # 無論有沒有檢測結果都要寫入框架
#     out.write(frame)
#     frame_idx += 1

# print(f"處理了 {frame_idx} 個框架")
# print(f"其中 {frames_with_faces} 個框架有臉部檢測")
# print(f"檢測率: {frames_with_faces/frame_idx*100:.1f}%")
# print(f"總共檢測到 {total_faces_detected} 個臉部實例")

# cap.release()
# out.release()
# print("已產生標註影片：", output_video_path)

# if os.path.exists(input_video_path):
#     os.remove(input_video_path)

# if os.path.exists("output.json"):
#     os.remove("output.json")

# 你可以根據需要修改這裡的 config
CONFIG = {
    "packing": True,
    "start_time": 0.0,
    "end_time": 10.0,
    "output_dir": "output",
    "output_json_dir": "output_json"
}

def download_youtube(url, out_path):
    # 使用 yt-dlp 下載影片
    cmd = [
        "yt-dlp",
        "-f", "mp4",
        "-o", out_path,
        url
    ]
    print(f"下載影片: {url}")
    subprocess.run(cmd, check=True)

def cut_video(input_path, output_path, start, end):
    # 使用 ffmpeg 擷取區間
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ss", str(start),
        "-to", str(end),
        "-c", "copy",
        output_path
    ]
    print(f"擷取影片區間: {start} ~ {end}")
    subprocess.run(cmd, check=True)


def process_json(json_path, config):
    with open(json_path, "r", encoding="utf-8") as f:
        segments = json.load(f)
    # 根據檔名自動推導 YouTube 影片網址
    video_id = Path(json_path).stem  # 例如 -m1A3Ym3kXE_shorts
    # if filename.endswith("_shorts"):
    #     video_id = filename.replace("_shorts", "").lstrip("-")
    # else:
        # video_id = filename.lstrip("-")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"自動推導影片網址: {video_url}")

    # 下載一次完整影片
    temp_video = f"temp_{video_id}.mp4"
    download_youtube(video_url, temp_video)

    # 逐一處理每個片段
    for item in segments:
        seg_id = item.get("id")
        start_time = item.get("start_time")
        end_time = item.get("end_time")
        if start_time is None or end_time is None:
            print(f"片段 {seg_id} 缺少 start_time 或 end_time，略過")
            continue
        print(f"分析 {json_path} 片段 {seg_id}，時間區間：{start_time} ~ {end_time}")

        temp_cut = f"temp_{video_id}_{seg_id}_cut.mp4"
        # 擷取片段
        cut_video(temp_video, temp_cut, start_time, end_time)
        # 分析
        result = analyze_video(temp_cut)
        # 儲存
        rel_path = os.path.relpath(json_path, config["output_dir"])
        out_dir = os.path.join(config["output_json_dir"], os.path.dirname(rel_path), Path(json_path).stem)
        ensure_dir(out_dir)
        out_json = os.path.join(out_dir, f"{seg_id}.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"已儲存分析結果: {out_json}")
        os.remove(temp_cut)
    # 處理完所有片段後刪除完整影片
    os.remove(temp_video)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def process_json(json_path, config):
    with open(json_path, "r", encoding="utf-8") as f:
        segments = json.load(f)
    # 根據檔名自動推導 YouTube 影片網址
    video_id = Path(json_path).stem  # 例如 -m1A3Ym3kXE_shorts
    # if filename.endswith("_shorts"):
    #     video_id = filename.replace("_shorts", "").lstrip("-")
    # else:
        # video_id = filename.lstrip("-")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"自動推導影片網址: {video_url}")

    # 下載一次完整影片
    temp_video = f"temp_{video_id}.mp4"
    download_youtube(video_url, temp_video)

    # 逐一處理每個片段
    for item in segments:
        seg_id = item.get("id")
        start_time = item.get("start_time")
        end_time = item.get("end_time")
        if start_time is None or end_time is None:
            print(f"片段 {seg_id} 缺少 start_time 或 end_time，略過")
            continue
        print(f"分析 {json_path} 片段 {seg_id}，時間區間：{start_time} ~ {end_time}")

        temp_cut = f"temp_{video_id}_{seg_id}_cut.mp4"
        # 擷取片段
        cut_video(temp_video, temp_cut, start_time, end_time)
        # 分析
        result = analyze_video(temp_cut)
        # 儲存
        rel_path = os.path.relpath(json_path, config["output_dir"])
        out_dir = os.path.join(config["output_json_dir"], os.path.dirname(rel_path), Path(json_path).stem)
        ensure_dir(out_dir)
        out_json = os.path.join(out_dir, f"{seg_id}.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"已儲存分析結果: {out_json}")
        os.remove(temp_cut)
    # 處理完所有片段後刪除完整影片
    os.remove(temp_video)

def main():
    if CONFIG["packing"]:
        for root, dirs, files in os.walk(CONFIG["output_dir"]):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(root, file)
                    try:
                        process_json(json_path, CONFIG)
                    except Exception as e:
                        print(f"處理 {json_path} 時發生錯誤: {e}")
    else:
        # 單一影片處理流程（可自行擴充）
        pass

if __name__ == "__main__":
    main()
