# task_scheduler.py
import os
import multiprocessing
from tqdm import tqdm
from pathlib import Path
from gpu_worker import run as gpu_worker_run

def task_scheduler(json_paths, config, max_gpu=1):
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    for path in json_paths:
        task_queue.put(path)

    def worker(gpu_idx):
        while True:
            try:
                json_path = task_queue.get(timeout=5)
            except:
                break
            try:
                task_id = Path(json_path).stem
                save_dir = os.path.join("save", f"task_{task_id}")
                os.makedirs(save_dir, exist_ok=True)
                gpu_worker_run(json_path, config, gpu_idx, save_dir)
                result_queue.put((json_path, "success"))
            except Exception as e:
                result_queue.put((json_path, f"error: {e}"))

    workers = []
    for gpu_id in range(max_gpu):
        p = multiprocessing.Process(target=worker, args=(gpu_id,))
        p.start()
        workers.append(p)

    results = {}
    for _ in tqdm(range(len(json_paths)), desc="多 GPU 處理中"):
        json_path, status = result_queue.get()
        results[json_path] = status

    for p in workers:
        p.join()

    # 輸出錯誤清單
    failed = [k for k, v in results.items() if not v.startswith("success")]
    print(f"\n✅ 成功：{len(results) - len(failed)} / {len(results)}")
    if failed:
        print("❌ 失敗清單：")
        for path in failed:
            print(f"  - {path}")
