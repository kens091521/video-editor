import requests
import cv2
import json
from mixModel import getOutcomeJson
import os
import subprocess
from pathlib import Path
import concurrent.futures
import shutil
import math
import ssl

ssl._create_default_https_context = ssl._create_stdlib_context
try:
    from pytube import YouTube
except ImportError:
    print("Warning: pytube not installed, will use yt-dlp as fallback")
    YouTube = None

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
    "output_json_dir": "output_json",
    "use_local_video":  False,  # True: 使用本地影片, False: 使用網絡下載
    "youtube_base_url": "https://www.youtube.com/watch?v=",  # YouTube 基礎 URL
    "local_video_base_path": "/home/wongsstudio/talkNet/shorts",  # 本地影片基礎路徑
}


def download_youtube(url, out_path):
    # 使用 pytube 下載影片，增強錯誤處理
    try:
        print(f"下載影片: {url}")
        
        if YouTube is None:
            raise Exception("pytube 未安裝，使用 yt-dlp")
        
        # 嘗試修復 pytube
        fix_pytube_cipher()
        
        # 設置 pytube 的 User-Agent 來避免 400 錯誤
        try:
            from pytube.innertube import _default_clients
            
            # 更新客戶端配置來避免 400 錯誤
            _default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
            _default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
            _default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
            _default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
        except ImportError:
            pass  # 如果無法導入 innertube，則跳過配置
        
        # 嘗試不同的 YouTube 初始化參數
        try:
            yt = YouTube(url, use_oauth=False, allow_oauth_cache=True)
        except:
            try:
                yt = YouTube(url)
            except:
                raise Exception("無法初始化 YouTube 物件")
        
        # 獲取影片流，優先選擇 progressive 流
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        if streams:
            stream = streams.get_highest_resolution()
        else:
            # 如果沒有 progressive 流，嘗試獲取 adaptive 流
            streams = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True)
            if streams:
                stream = streams.get_highest_resolution()
            else:
                # 最後嘗試獲取任何可用的 mp4 流
                streams = yt.streams.filter(file_extension='mp4')
                if streams:
                    stream = streams.first()
                else:
                    raise Exception("無法找到任何適合的影片流")
        
        if stream is None:
            raise Exception("無法找到適合的影片流")

        # 獲取輸出目錄和檔名
        output_dir = os.path.dirname(out_path)
        filename = os.path.basename(out_path)

        # 確保輸出目錄存在
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 下載影片
        print(f"正在下載: {yt.title}")
        print(f"影片解析度: {stream.resolution}")
        stream.download(output_path=output_dir, filename=filename)
        print(f"下載完成: {out_path}")

    except Exception as e:
        print(f"pytube 下載失敗: {e}")
        # 如果 pytube 失敗，嘗試使用 yt-dlp 作為備選方案
        print("嘗試使用 yt-dlp 作為備選方案...")
        try:
            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "--merge-output-format", "mp4",
                "-o", out_path,
                url
            ]
            subprocess.run(cmd, check=True)
            print(f"yt-dlp 下載完成: {out_path}")
        except Exception as e2:
            print(f"yt-dlp 也失敗了: {e2}")
            raise Exception(f"所有下載方法都失敗了。pytube 錯誤: {e}, yt-dlp 錯誤: {e2}")


def cut_video(input_path, output_path, start, end):
    duration = float(end) - float(start)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start),
        "-i",
        input_path,
        "-ss",
        "0",
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-avoid_negative_ts",
        "make_zero",
        output_path,
    ]
    print(f"精確擷取影片區間（音畫同步）: {start} ~ {end}")
    subprocess.run(cmd, check=True)


def analyze_video(video_path, save_path="save"):
    # 這裡呼叫你現有的分析函數
    # 假設 getOutcomeJson(video_path) 會回傳分析結果 dict
    from mixModel import getOutcomeJson

    return getOutcomeJson(video_path, save_path=save_path)


def has_nan_in_result(result):
    # 假設 result 是 list of dict，每個 dict 有 boxes: list of dict
    for frame in result:
        for box in frame.get("boxes", []):
            if math.isnan(box.get("raw_score", 0)):
                return True
    return False


def analyze_video_no_nan(video_path, save_path="save", max_retry=5):
    from mixModel import getOutcomeJson

    for attempt in range(1, max_retry + 1):
        result = getOutcomeJson(video_path, save_path=save_path)
        if not has_nan_in_result(result):
            if attempt > 1:
                print(f"第 {attempt} 次重試後成功，無 nan")
            return result, None  # 無失敗
        print(f"第 {attempt} 次分析出現 nan，重新分析...")
    print(f"重試 {max_retry} 次後仍有 nan，返回最後一次結果")
    return result, video_path  # 失敗，回傳 video_path


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def process_json(json_path, config, save_dir=None):
    with open(json_path, "r", encoding="utf-8") as f:
        segments = json.load(f)
    video_id = Path(json_path).stem  # 例如 -m1A3Ym3kXE_shorts
    print(f"處理影片 ID: {video_id}")

    # 從 json_path 提取資料夾編號
    # 例如：output/252/2FUVXf8GIqw_shorts.json -> 252
    folder_number = os.path.basename(os.path.dirname(json_path))
    print(f"對應的資料夾編號: {folder_number}")

    fail_list = []
    for item in segments:
        seg_id = item.get("id")
        start_time = item.get("start_time")
        end_time = item.get("end_time")
        if start_time is None or end_time is None:
            print(f"片段 {seg_id} 缺少 start_time 或 end_time，略過")
            continue
        print(f"分析 {json_path} 片段 {seg_id}，時間區間：{start_time} ~ {end_time}")
        temp_cut = f"temp_{video_id}_{seg_id}_cut.mp4"

        video_acquired = False

        if config.get("use_local_video", True):
            # 使用本地影片模式
            print("使用本地影片模式")
            shorts_base_path = os.path.expanduser(
                config.get("local_video_base_path", "/home/wongsstudio/talkNet/shorts")
            )

            # 移除 _shorts 後綴用於搜尋本地檔案
            search_video_id = video_id.replace("_shorts", "")
            expected_video = ""

            # 使用與 output 資料夾相同的數字
            folder_path = os.path.join(shorts_base_path, folder_number)
            if os.path.exists(folder_path):
                video_folder = os.path.join(folder_path, search_video_id)
                expected_video = os.path.join(
                    video_folder, f"{search_video_id}_{seg_id}.mp4"
                )
                if os.path.exists(video_folder):
                    # 檢查是否有對應的影片檔案
                    if os.path.exists(expected_video):
                        print(f"找到本地影片檔案: {expected_video}")
                        # 複製到臨時檔案
                        shutil.copy2(expected_video, temp_cut)
                        video_acquired = True

            if not video_acquired:
                print(f"未找到本地影片檔案，跳過片段 {expected_video}")
                continue
        else:
            # 使用網絡下載模式
            print("使用網絡下載模式")
            search_video_id = video_id.replace("_shorts", "")
            youtube_url = (
                config.get("youtube_base_url", "https://www.youtube.com/watch?v=")
                + search_video_id
            )
            temp_full = f"temp_{video_id}_full.mp4"

            try:
                # 下載完整影片
                if not download_youtube_with_check(youtube_url, temp_full):
                    print(f"下載影片失敗，跳過片段 {seg_id}")
                    continue

                # 切割影片片段
                if not safe_cut_video(temp_full, temp_cut, start_time, end_time):
                    print(f"切割影片失敗，跳過片段 {seg_id}")
                    if os.path.exists(temp_full):
                        os.remove(temp_full)
                    continue

                # 清理完整影片
                if os.path.exists(temp_full):
                    os.remove(temp_full)

                video_acquired = True
                print(f"成功下載並切割影片片段: {temp_cut}")

            except Exception as e:
                print(f"下載或處理影片時發生錯誤: {e}")
                # 清理可能存在的檔案
                for temp_file in [temp_full, temp_cut]:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                continue

        if not video_acquired:
            continue

        if temp_cut is None or not os.path.exists(temp_cut):
            continue

        # 每個 frame 都建立 save/task_{task_id}-frame{seg_id}
        task_id = Path(json_path).stem  # 保留 _shorts 後綴用於輸出資料夾
        frame_save_dir = os.path.join("save", f"task_{task_id}-frame{seg_id}")
        ensure_dir(frame_save_dir)
        # 未來可將 frame_save_dir 傳給分析函數
        result, fail_video = analyze_video_no_nan(temp_cut, save_path=frame_save_dir)
        if fail_video:
            # 記錄失敗
            fail_list.append(seg_id)
            # 複製 json 並只保留失敗 key
            rel_dir = os.path.dirname(json_path)
            if rel_dir.startswith("output"):
                rel_dir = rel_dir[len("output") :].lstrip(os.sep)
            fail_json_dir = os.path.join("fail_json", rel_dir)
            os.makedirs(fail_json_dir, exist_ok=True)
            fail_json_path = os.path.join(fail_json_dir, os.path.basename(json_path))
            with open(json_path, "r", encoding="utf-8") as f:
                all_data = json.load(f)
            fail_data = [item for item in all_data if item.get("id") == seg_id]
            with open(fail_json_path, "w", encoding="utf-8") as f:
                json.dump(fail_data, f, ensure_ascii=False, indent=2)
        rel_path = os.path.relpath(json_path, config["output_dir"])
        out_dir = os.path.join(
            config["output_json_dir"], os.path.dirname(rel_path), Path(json_path).stem
        )
        ensure_dir(out_dir)
        out_json = os.path.join(out_dir, f"{seg_id}.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"已儲存分析結果: {out_json}")
        os.remove(temp_cut)
    return fail_list


def get_gpu_count():
    try:
        result = subprocess.run(
            ["nvidia-smi", "-L"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        gpus = [line for line in result.stdout.split("\n") if "GPU" in line]
        return len(gpus) if gpus else 1
    except Exception:
        return 1


def process_json_with_gpu(json_path, config, gpu_idx, save_dir=None):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_idx)
    return process_json(json_path, config, save_dir=save_dir)


def check_video_integrity(video_path):
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", video_path, "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.stderr:
        print(f"影片 {video_path} 有損壞：\n{result.stderr}")
        return False
    return True


def safe_cut_video(input_path, output_path, start, end, max_retry=3):
    duration = float(end) - float(start)
    for attempt in range(max_retry):
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start),
            "-i",
            input_path,
            "-ss",
            "0",
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-avoid_negative_ts",
            "make_zero",
            output_path,
        ]
        subprocess.run(cmd, check=True)
        if check_video_integrity(output_path):
            return True
        print(f"第 {attempt+1} 次切割失敗，重試...")
    print(f"重試 {max_retry} 次後仍損壞，跳過該片段")
    return False


def download_youtube_with_check(url, out_path, max_retry=3):
    for attempt in range(1, max_retry + 1):
        try:
            download_youtube(url, out_path)
            if os.path.exists(out_path) and check_video_integrity(out_path):
                if attempt > 1:
                    print(f"第 {attempt} 次下載後影片完整")
                return True
            print(f"第 {attempt} 次下載後影片損壞，重新下載...")
        except Exception as e:
            print(f"第 {attempt} 次下載失敗: {e}")
            # 清理可能存在的損壞檔案
            if os.path.exists(out_path):
                os.remove(out_path)
    print(f"重試 {max_retry} 次後影片仍無法下載，放棄該影片")
    return False


def main():
    if CONFIG["packing"]:
        output_root = CONFIG["output_dir"]
        subfolders = [
            d
            for d in os.listdir(output_root)
            if os.path.isdir(os.path.join(output_root, d))
        ]
        # 只處理純數字資料夾並排序
        subfolders_sorted = sorted([x for x in subfolders if x.isdigit()], key=int)
        max_workers = min(get_gpu_count(), 1)  # 降低同時處理數量，減少 nan 機率
        print(f"偵測到 GPU 數量：{max_workers}，每批同時處理 {max_workers} 個 json")
        for folder in subfolders_sorted:
            folder_path = os.path.join(output_root, folder)
            json_files = [
                f for f in sorted(os.listdir(folder_path)) if f.endswith(".json")
            ]
            json_paths = [os.path.join(folder_path, f) for f in json_files]
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=max_workers
            ) as executor:
                future_to_json = {}
                for idx, json_path in enumerate(json_paths):
                    gpu_idx = idx % max_workers
                    # 決定 save_dir
                    if max_workers > 1:
                        task_id = Path(json_path).stem
                        save_dir = os.path.join("save", f"task_{task_id}")
                        ensure_dir(save_dir)
                    else:
                        save_dir = None
                    future = executor.submit(
                        process_json_with_gpu, json_path, CONFIG, gpu_idx, save_dir
                    )
                    future_to_json[future] = json_path
                try:
                    for future in concurrent.futures.as_completed(future_to_json):
                        json_path = future_to_json[future]
                        future.result()  # 若有錯誤會直接 raise
                except Exception as e:
                    print(f"處理 {json_path} 時發生錯誤: {e}")
                    executor.shutdown(wait=False, cancel_futures=True)
                    import sys

                    sys.exit(1)
    else:
        # 單一影片處理流程（可自行擴充）
        pass


def fix_pytube_cipher():
    """修復 pytube 的 cipher 問題"""
    try:
        import pytube.cipher as cipher
        import re
        
        def get_throttling_function_name(js: str) -> str:
            function_patterns = [
                r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
                r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
                r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
            ]
            
            for pattern in function_patterns:
                regex = re.compile(pattern)
                function_match = regex.search(js)
                if function_match:
                    if len(function_match.groups()) == 1:
                        return function_match.group(1)
                    idx = function_match.group(2)
                    if idx:
                        idx = idx.strip("[]")
                        array = re.search(
                            r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                                nfunc=re.escape(function_match.group(1))
                            ),
                            js
                        )
                        if array:
                            array = array.group(1).strip("[]").split(",")
                            array = [x.strip() for x in array]
                            return array[int(idx)]
            
            raise Exception("無法找到 throttling function name")

        cipher.get_throttling_function_name = get_throttling_function_name
        print("已應用 pytube cipher 修復")
    except Exception as e:
        print(f"pytube cipher 修復失敗: {e}")


if __name__ == "__main__":
    fix_pytube_cipher()
    main()
