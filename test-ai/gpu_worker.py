# gpu_worker.py
import os
from main import process_json_with_gpu

def run(json_path, config, gpu_idx, save_dir=None):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_idx)
    return process_json_with_gpu(json_path, config, gpu_idx, save_dir)
