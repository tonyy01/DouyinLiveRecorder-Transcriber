#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
测试转录功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from src.transcriber import Transcriber


def test_transcriber_init():
    """测试转录器初始化"""
    print("测试转录器初始化...")
    transcriber = Transcriber(model_name="base", language="zh", output_format="srt")
    print(f"  模型: {transcriber.model_name}")
    print(f"  语言: {transcriber.language}")
    print(f"  输出格式: {transcriber.output_format}")
    print(f"  设备: {transcriber.device}")
    print("✓ 转录器初始化成功\n")


def test_whisper_check():
    """测试 Whisper 是否可用"""
    print("检查 Whisper 是否已安装...")
    transcriber = Transcriber()
    is_installed = transcriber._check_whisper_installed()
    if is_installed:
        print("✓ Whisper 已安装并可用\n")
    else:
        print("✗ Whisper 未安装或不可用")
        print("  请运行: pip install openai-whisper\n")
    return is_installed


def test_transcribe_sample():
    """测试转录示例视频（如果存在）"""
    print("查找测试视频文件...")
    
    # 在 downloads 目录下查找视频文件
    downloads_dir = script_dir / "downloads"
    if not downloads_dir.exists():
        print("  downloads 目录不存在，跳过实际转录测试\n")
        return
    
    # 查找第一个视频文件
    video_extensions = ['.mp4', '.ts', '.flv', '.mkv']
    video_file = None
    
    for ext in video_extensions:
        files = list(downloads_dir.rglob(f'*{ext}'))
        if files:
            video_file = files[0]
            break
    
    if not video_file:
        print("  未找到测试视频文件，跳过实际转录测试\n")
        return
    
    print(f"  找到测试视频: {video_file.name}")
    print("  开始转录（这可能需要一些时间）...")
    
    transcriber = Transcriber(model_name="base", language="zh", output_format="srt")
    output_file = transcriber.transcribe_video(str(video_file))
    
    if output_file and os.path.exists(output_file):
        print(f"✓ 转录成功: {output_file}")
        # 显示转录文件的前几行
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
            print("  转录内容预览:")
            for line in lines:
                print(f"    {line.rstrip()}")
    else:
        print("✗ 转录失败")


def main():
    """主测试函数"""
    print("=" * 60)
    print("转录功能测试")
    print("=" * 60 + "\n")
    
    test_transcriber_init()
    
    whisper_available = test_whisper_check()
    
    if whisper_available:
        # 只有在 Whisper 可用时才进行实际转录测试
        # test_transcribe_sample()  # 注释掉以避免长时间运行
        print("提示: 取消注释 test_transcribe_sample() 以测试实际转录")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
