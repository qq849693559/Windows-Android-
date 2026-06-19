#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安卓音乐播放器
支持Windows和Android平台的音乐播放应用
"""

import sys
import os
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QListWidget,
                           QSlider, QFileDialog, QStatusBar, QToolBar, QAction)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QIcon, QPixmap

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("音乐播放器")
        self.setGeometry(100, 100, 600, 400)
        
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
        
        # 工具栏
        self.create_toolbar()
        
        # 播放控制区域
        control_layout = QHBoxLayout()
        
        # 播放/暂停按钮
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(50, 50)
        self.play_button.clicked.connect(self.toggle_playback)
        control_layout.addWidget(self.play_button)
        
        # 上一曲按钮
        self.prev_button = QPushButton("⏮")
        self.prev_button.setFixedSize(50, 50)
        self.prev_button.clicked.connect(self.play_previous)
        control_layout.addWidget(self.prev_button)
        
        # 下一曲按钮
        self.next_button = QPushButton("⏭")
        self.next_button.setFixedSize(50, 50)
        self.next_button.clicked.connect(self.play_next)
        control_layout.addWidget(self.next_button)
        
        # 进度条
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self.set_position)
        control_layout.addWidget(self.progress_slider)
        
        # 时间显示
        self.time_label = QLabel("00:00 / 00:00")
        control_layout.addWidget(self.time_label)
        
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
        
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 打开文件动作
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.add_files)
        toolbar.addAction(open_action)
        
        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
        
    def add_files(self):
        if platform.system() == "Windows":
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
            file_dialog.setNameFilter("音频文件 (*.mp3 *.wav *.ogg *.m4a)")
            
            if file_dialog.exec():
                files = file_dialog.selectedFiles()
                for file in files:
                    self.add_to_playlist(file)
        else:
            # Android平台使用简化版本
            files = QFileDialog.getOpenFileNames(
                self, "选择音乐文件", "", "音频文件 (*.mp3 *.wav *.ogg *.m4a)"
            )
            if files[0]:
                for file in files[0]:
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
            self.status_bar.showMessage(f"正在播放: {os.path.basename(file_path)}")
            
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
            current_time = position // 1000
            total_time = duration // 1000
            self.time_label.setText(f"{self.format_time(current_time)} / {self.format_time(total_time)}")
            
    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)
        total_time = duration // 1000
        self.time_label.setText(f"00:00 / {self.format_time(total_time)}")
        
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
        
    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def show_about(self):
        about_text = """
        音乐播放器 v1.0
        
        一个简单的跨平台音乐播放器
        支持Windows和Android平台
        
        功能特性：
        - 播放多种音频格式
        - 播放列表管理
        - 进度控制
        - 音量调节
        - 循环播放
        """
        QMessageBox.about(self, "关于", about_text)

def main():
    app = QApplication(sys.argv)
    
    # 设置应用图标（如果有）
    app.setApplicationName("音乐播放器")
    app.setOrganizationName("MusicPlayer")
    
    # 创建并显示主窗口
    player = MusicPlayer()
    player.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()