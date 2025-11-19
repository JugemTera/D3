import os
from glob import glob
from moviepy.editor import VideoFileClip
import multiprocessing
import math
import random


def get_video_length(file_path):
    video = VideoFileClip(file_path)
    return video.duration

def process_video(video_path, dataset_path):
    video_name = video_path.split('/')[-1]
    video_name = video_name.split('.')[:-1]
    video_name = '.'.join(video_name)

    path = video_path.split('/')[4:-1]
    path = '/'.join(path)
    image_path = f'{dataset_path}/frames/'+path+'/'+ video_name+'/'
    
    if os.path.exists(image_path):
        print(video_name, "frames exist")
    else:
        print(video_name, end='\r')
        try:
            try:
                frame_rate = 8
                duration = 3
                video_length = get_video_length(video_path)
                if video_length <= 3:
                    start_time = 0
                else:
                    start_time = math.floor(random.uniform(0, video_length-3))
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                os.system(f"cd {image_path} | ffmpeg -loglevel quiet -ss {start_time} -t {duration} -i {video_path} -vf fps={frame_rate} {image_path}%d.jpg")
            except Exception as e:
                with open('error.log', 'a') as f:
                    f.write(f"{video_name} error\n")
                print(f"{video_name} error\n")
        except:
            with open('error.log', 'a') as f:
                f.write(f"{video_name} skipped\n")

def process_video_split(video_path, dataset_path):
    """
    動画全体から24フレームずつ切り取り、複数のフォルダに保存する
    """
    video_name = video_path.split('/')[-1]
    video_name = video_name.split('.')[:-1]
    video_name = '.'.join(video_name)
    print(video_path)
    path = video_path.split('/')[4:-1]
    path = '/'.join(path)

    base_path = f'{dataset_path}/frames/'+path+'/'

    print(f"Processing {video_name}...", end='\r')

    try:
        frame_rate = 8
        frames_per_clip = 24
        duration_per_clip = frames_per_clip / frame_rate  # 3秒

        video_length = get_video_length(video_path)
        num_clips = math.floor(video_length / duration_per_clip)

        if num_clips == 0:
            # 動画が短すぎる場合は全体を1つのクリップとして保存
            num_clips = 1

        for clip_idx in range(num_clips):
            start_time = clip_idx * duration_per_clip
            image_path = f'{base_path}{video_name}_clip_{clip_idx:04d}/'

            # すでに存在する場合はスキップ
            if os.path.exists(image_path) and len(os.listdir(image_path)) > 0:
                continue

            os.makedirs(image_path, exist_ok=True)

            # ffmpegコマンドで指定位置から24フレーム抽出
            cmd = f"ffmpeg -loglevel quiet -ss {start_time} -t {duration_per_clip} -i {video_path} -vf fps={frame_rate} {image_path}%d.jpg"
            os.system(cmd)

        print(f"{video_name}: {num_clips} clips extracted")

    except Exception as e:
        with open('error.log', 'a') as f:
            f.write(f"{video_name} error: {str(e)}\n")
        print(f"{video_name} error: {str(e)}")

import argparse

if __name__ == '__main__':

    random.seed(42)

    parser = argparse.ArgumentParser(description='Specify the dataset path.')
    parser.add_argument('--dataset-path', type=str, default='datasets',
                        help='Path to the dataset directory (default: datasets)')
    parser.add_argument('--split-mode', action='store_true',
                        help='Split video into multiple 24-frame clips instead of extracting a single random clip')
    args = parser.parse_args()
    dataset_path = args.dataset_path

    video_paths = glob(f"{dataset_path}/video/**", recursive=True)
    video_paths = [vp for vp in video_paths if vp.endswith(('.mp4', '.avi', '.mov', '.mkv', '.gif'))]

    print(f"Find {len(video_paths)} videos!")

    # 処理モードを選択
    if args.split_mode:
        print("Mode: Split video into multiple 24-frame clips")
        process_func = process_video_split
    else:
        print("Mode: Extract single random 24-frame clip")
        process_func = process_video

    args_list = [(vp, dataset_path) for vp in video_paths]

    num_processes = max(1, multiprocessing.cpu_count() // 2)
    print(f"Using {num_processes} processes")
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.starmap(process_func, args_list)




