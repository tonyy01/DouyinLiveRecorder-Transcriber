# -*- encoding: utf-8 -*-

"""
Author: AI Assistant
Date: 2025-02-01
Function: Transcribe recorded video files using Whisper
"""

import os
import subprocess
import threading
from pathlib import Path
from typing import Optional
from src.utils import logger


class Transcriber:
    """视频转录器，使用 Whisper 将录制的视频转录为文本"""
    
    def __init__(self, model_name: str = "base", language: Optional[str] = None,
                 output_format: str = "srt", device: str = "auto"):
        """
        初始化转录器
        
        Args:
            model_name: Whisper 模型名称 (tiny, base, small, medium, large)
            language: 目标语言代码 (zh, en 等)，None 为自动检测
            output_format: 输出格式 (srt, txt, vtt, json)
            device: 使用的设备 (auto, cpu, cuda)
        """
        self.model_name = model_name
        self.language = language
        self.output_format = output_format
        self.device = device
        self._check_whisper_installed()
    
    def _check_whisper_installed(self) -> bool:
        """检查 Whisper 是否已安装"""
        try:
            result = subprocess.run(
                ["whisper", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Whisper 未安装或不可用。请运行: pip install openai-whisper")
            return False
    
    def transcribe_video(self, video_path: str, output_dir: Optional[str] = None,
                        delete_audio_temp: bool = True) -> Optional[str]:
        """
        转录视频文件
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录，None 则使用视频所在目录
            delete_audio_temp: 是否删除临时提取的音频文件
            
        Returns:
            转录文件路径，失败返回 None
        """
        if not os.path.exists(video_path):
            logger.error(f"视频文件不存在: {video_path}")
            return None
        
        if not self._check_whisper_installed():
            logger.error("Whisper 未安装，无法进行转录")
            return None
        
        try:
            # 设置输出目录
            if output_dir is None:
                output_dir = os.path.dirname(video_path)
            
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建 Whisper 命令
            whisper_command = [
                "whisper",
                video_path,
                "--model", self.model_name,
                "--output_dir", output_dir,
                "--output_format", self.output_format,
            ]
            
            # 添加语言参数
            if self.language:
                whisper_command.extend(["--language", self.language])
            
            # 添加设备参数
            if self.device != "auto":
                whisper_command.extend(["--device", self.device])
            
            logger.info(f"开始转录视频: {os.path.basename(video_path)}")
            logger.debug(f"Whisper 命令: {' '.join(whisper_command)}")
            
            # 执行转录
            result = subprocess.run(
                whisper_command,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            if result.returncode == 0:
                # 生成输出文件路径
                video_basename = os.path.splitext(os.path.basename(video_path))[0]
                output_file = os.path.join(output_dir, f"{video_basename}.{self.output_format}")
                
                if os.path.exists(output_file):
                    logger.info(f"转录完成: {output_file}")
                    return output_file
                else:
                    logger.error(f"转录文件未生成: {output_file}")
                    return None
            else:
                logger.error(f"转录失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"转录超时: {video_path}")
            return None
        except Exception as e:
            logger.error(f"转录过程发生错误: {e}")
            return None
    
    def transcribe_async(self, video_path: str, output_dir: Optional[str] = None,
                        callback=None) -> threading.Thread:
        """
        异步转录视频文件
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            callback: 完成后的回调函数，接收转录文件路径作为参数
            
        Returns:
            转录线程对象
        """
        def _transcribe_wrapper():
            result = self.transcribe_video(video_path, output_dir)
            if callback:
                callback(result)
        
        thread = threading.Thread(target=_transcribe_wrapper)
        thread.daemon = True
        thread.start()
        return thread


def transcribe_file(video_path: str, model_name: str = "base",
                   language: Optional[str] = None, output_format: str = "srt",
                   output_dir: Optional[str] = None, device: str = "auto") -> Optional[str]:
    """
    便捷函数：转录单个视频文件
    
    Args:
        video_path: 视频文件路径
        model_name: Whisper 模型名称
        language: 目标语言代码
        output_format: 输出格式
        output_dir: 输出目录
        device: 使用的设备
        
    Returns:
        转录文件路径，失败返回 None
    """
    transcriber = Transcriber(model_name, language, output_format, device)
    return transcriber.transcribe_video(video_path, output_dir)
