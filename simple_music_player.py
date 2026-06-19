#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版音乐播放器
支持Windows平台的基础音乐播放功能
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QListWidget,
                           QSlider, QFileDialog, QStatusBar)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class SimpleMusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("音乐播放器")
        self.setGeometry(100, 100, 500, 350)
        
        # 播放器组件
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # 播放列表
        self.playlist = []
        self.current_index = -1
        
        # 初始化UI
        self.init_ui()
        
        # 连接信号
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.playbackStateChanged.connect(self.update_playback_state)
        
    def init_ui(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 播放控制区域
        control_layout = QHBoxLayout()
        
        # 播放/暂停按钮
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(40, 40)
        self.play_button.clicked.connect(self.toggle_playback)
        control_layout.addWidget(self.play_button)
        
        # 上一曲按钮
        self.prev_button = QPushButton("⏮")
        self.prev_button.setFixedSize(40, 40)
        self.prev_button.clicked.connect(self.play_previous)
        control_layout.addWidget(self.prev_button)
        
        # 下一曲按钮
        self.next_button = QPushButton("⏭")
        self.next_button.setFixedSize(40, 40)
        self.next_button.clicked.connect(self.play_next)
        control_layout.addWidget(self.next_button)
        
        # 进度条
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self.set_position)
        control_layout.addWidget(self.progress_slider)
        
        main_layout.addLayout(control_layout)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_label = QLabel("音量:")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        main_layout.addLayout(volume_layout)
        
        # 当前播放信息
        self.now_playing_label = QLabel("当前播放: 无")
        self.now_playing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.now_playing_label)
        
        # 播放列表
        playlist_label = QLabel("播放列表:")
        main_layout.addWidget(playlist_label)
        
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected)
        main_layout.addWidget(self.playlist_widget)
        
        # 文件操作按钮
        file_layout = QHBoxLayout()
        
        self.add_button = QPushButton("添加文件")
        self.add_button.clicked.connect(self.add_files)
        file_layout.addWidget(self.add_button)
        
        self.clear_button = QPushButton("清空列表")
        self.clear_button.clicked.connect(self.clear_playlist)
        file_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(file_layout)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 设置布局
        central_widget.setLayout(main_layout)
        
    def add_files(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("音频文件 (*.mp3 *.wav *.ogg)")
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            for file in files:
                self.add_to_playlist(file)
                
    def add_to_playlist(self, file_path):
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            self.playlist_widget.addItem(file_name)
            self.playlist.append(file_path)
            self.status_bar.showMessage(f"已添加: {file_name}")
            
    def clear_playlist(self):
        self.playlist_widget.clear()
        self.playlist.clear()
        self.current_index = -1
        self.media_player.stop()
        self.status_bar.showMessage("播放列表已清空")
        
    def play_selected(self, item):
        index = self.playlist_widget.row(item)
        if 0 <= index < len(self.playlist):
            self.current_index = index
            self.play_current()
            
    def toggle_playback(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            if self.current_index >= 0:
                self.play_current()
            else:
                self.play_next()
                
    def play_current(self):
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.play()
            file_name = os.path.basename(file_path)
            self.now_playing_label.setText(f"当前播放: {file_name}")
            self.status_bar.showMessage(f"正在播放: {file_name}")
            
    def play_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.play_current()
        elif self.playlist:
            self.current_index = len(self.playlist) - 1
            self.play_current()
            
    def play_next(self):
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.play_current()
        elif self.playlist:
            self.current_index = 0
            self.play_current()
            
    def update_position(self, position):
        duration = self.media_player.duration()
        if duration > 0:
            self.progress_slider.setValue(int(position * 100 / duration))
            
    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)
        
    def update_playback_state(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setText("⏸")
        else:
            self.play_button.setText("▶")
            
    def set_position(self, position):
        duration = self.media_player.duration()
        if duration > 0:
            self.media_player.setPosition(int(position * duration / 100))
            
    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100.0)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("音乐播放器")
    
    player = SimpleMusicPlayer()
    player.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()