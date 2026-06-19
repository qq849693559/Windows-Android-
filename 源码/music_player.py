import sys
import requests
import json
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                             QTextEdit, QComboBox, QProgressBar, QMessageBox,
                             QFileDialog, QHeaderView, QCheckBox, QSlider)
from PyQt6.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# 配置文件路径
CONFIG_FILE = "download_config.json"

# 酷狗音乐API
KUGOU_SEARCH_API = "http://mobilecdn.kugou.com"
KUGOU_PLAY_API = "http://m.kugou.com"

# 网易云音乐官方API
NETEASE_SEARCH_API = "https://music.163.com/api/search/get/web"
NETEASE_DOWNLOAD_API = "http://music.163.com/song/media/outer/url?id={}.mp3"

def kugou_search(keyword, page=1, pagesize=100):
    """酷狗音乐搜索"""
    try:
        url = f"{KUGOU_SEARCH_API}/api/v3/search/song"
        params = {
            "keyword": keyword,
            "page": page,
            "pagesize": pagesize,
            "showtype": "1"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                return data.get("data", {}).get("info", [])
        return []
    except Exception as e:
        print(f"酷狗搜索失败: {str(e)}")
        return []

def kugou_get_song_url(hash_value, album_id):
    """获取酷狗音乐播放URL"""
    try:
        url = f"{KUGOU_PLAY_API}/app/i/getSongInfo.php"
        params = {
            "cmd": "playInfo",
            "hash": hash_value,
            "from": "mkugou"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                return data.get("url", "")
        return ""
    except Exception as e:
        print(f"获取酷狗播放URL失败: {str(e)}")
        return ""

def netease_search(keyword, page=1, pagesize=100):
    """网易云音乐搜索"""
    try:
        params = {
            "s": keyword,
            "type": 1,  # 1: 单曲
            "offset": (page - 1) * pagesize,
            "limit": pagesize
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "http://music.163.com/"
        }
        response = requests.get(NETEASE_SEARCH_API, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "songs" in data["result"]:
                return data["result"]["songs"]
        return []
    except Exception as e:
        print(f"网易云搜索失败: {str(e)}")
        return []

def netease_get_song_url(song_id):
    """获取网易云音乐播放URL"""
    try:
        url = NETEASE_DOWNLOAD_API.format(song_id)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "http://music.163.com/"
        }
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
        if response.status_code == 302:
            return response.headers.get('Location', '')
        elif response.status_code == 200:
            return url
        return ""
    except Exception as e:
        print(f"获取网易云播放URL失败: {str(e)}")
        return ""

def netease_get_lyrics(song_id):
    """获取网易云音乐歌词，返回 [(时间ms, 歌词文本), ...] 列表"""
    try:
        url = f"http://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=-1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "http://music.163.com/"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "lrc" in data and "lyric" in data["lrc"]:
                lrc_text = data["lrc"]["lyric"]
                # 解析LRC格式
                lyrics_data = parse_lrc(lrc_text)
                return lyrics_data
            return []
        return []
    except Exception as e:
        print(f"获取网易云歌词失败: {str(e)}")
        return []

def kugou_get_lyrics(hash_value):
    """获取酷狗音乐歌词"""
    try:
        url = f"http://krcs.kugou.com/search?ver=1&man=yes&client=mob&keyword=&hash={hash_value}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # 简化的歌词获取，实际可能需要更复杂的解析
            return "酷狗歌词获取功能待完善"
        return "暂无歌词"
    except Exception as e:
        print(f"获取酷狗歌词失败: {str(e)}")
        return f"加载歌词失败: {str(e)}"

def parse_lrc(lrc_text):
    """解析LRC格式歌词，返回 [(时间ms, 歌词文本), ...] 列表"""
    import re
    lyrics_data = []
    lines = lrc_text.strip().split('\n')
    
    # 匹配时间标签和歌词内容
    time_pattern = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)')
    
    for line in lines:
        match = time_pattern.match(line)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            milliseconds = int(match.group(3))
            total_ms = minutes * 60 * 1000 + seconds * 1000 + milliseconds
            lyrics = match.group(4).strip()
            if lyrics:  # 只添加有内容的歌词行
                time_str = f"{minutes:02d}:{seconds:02d}"
                lyrics_data.append((total_ms, f"[{time_str}] {lyrics}"))
        elif line.strip() and not line.startswith('['):
            # 纯文本歌词行（无时间戳）
            lyrics_data.append((0, line.strip()))
    
    # 按时间排序
    lyrics_data.sort(key=lambda x: x[0])
    return lyrics_data

class SearchThread(QThread):
    search_finished = pyqtSignal(list)
    search_error = pyqtSignal(str)
    
    def __init__(self, keyword, platform):
        super().__init__()
        self.keyword = keyword
        self.platform = platform
    
    def run(self):
        try:
            if self.platform == "酷狗音乐":
                # 使用酷狗音乐API
                kugou_results = kugou_search(self.keyword)
                # 转换为统一格式
                results = []
                for song in kugou_results:
                    # 检查是否为VIP歌曲（根据版权标识）
                    is_vip = song.get("copyright", 0) != 0 or song.get("hash", "").startswith("VIP")
                    results.append({
                        "id": song.get("hash", ""),
                        "name": song.get("songname", ""),
                        "artist": song.get("singername", ""),
                        "album": song.get("album_name", ""),
                        "platform": "kugou",
                        "album_id": song.get("album_id", ""),
                        "is_vip": is_vip
                    })
                self.search_finished.emit(results)
            elif self.platform == "网易云音乐":
                # 使用网易云音乐官方API
                netease_results = netease_search(self.keyword)
                # 转换为统一格式
                results = []
                for song in netease_results:
                    artists = song.get("artists", [])
                    artist_name = ", ".join([a.get("name", "") for a in artists])
                    # 检查是否为VIP歌曲（根据fee字段：0=免费，1=VIP，4=需购买）
                    is_vip = song.get("fee", 0) in [1, 4]
                    results.append({
                        "id": song.get("id", ""),
                        "name": song.get("name", ""),
                        "artist": artist_name,
                        "album": song.get("album", {}).get("name", ""),
                        "platform": "netease",
                        "is_vip": is_vip
                    })
                self.search_finished.emit(results)
        except Exception as e:
            self.search_error.emit(f"搜索出错: {str(e)}")

class LinkTestThread(QThread):
    link_test_finished = pyqtSignal(int, bool)  # 行索引, 是否有效
    
    def __init__(self, row_index, song):
        super().__init__()
        self.row_index = row_index
        self.song = song
    
    def run(self):
        try:
            song_id = self.song.get('id')
            platform = self.song.get('platform')
            
            # 酷狗音乐单独测试
            if platform == "kugou":
                album_id = self.song.get('album_id', '')
                music_url = kugou_get_song_url(song_id, album_id)
                if music_url and music_url.startswith('http'):
                    self.link_test_finished.emit(self.row_index, True)
                else:
                    self.link_test_finished.emit(self.row_index, False)
                return
            
            # 网易云音乐使用官方API测试
            if platform == "netease":
                music_url = netease_get_song_url(song_id)
                if music_url and music_url.startswith('http'):
                    self.link_test_finished.emit(self.row_index, True)
                else:
                    self.link_test_finished.emit(self.row_index, False)
                return
            
            self.link_test_finished.emit(self.row_index, False)
        except Exception as e:
            self.link_test_finished.emit(self.row_index, False)

class DownloadThread(QThread):
    download_progress = pyqtSignal(int)  # 进度百分比
    download_finished = pyqtSignal(int, int, list)  # 成功数量，失败数量，失败歌曲序号列表
    download_error = pyqtSignal(str)
    
    def __init__(self, songs, save_dir):
        super().__init__()
        self.songs = songs
        self.save_dir = save_dir
    
    def run(self):
        total = len(self.songs)
        success_count = 0
        failed_count = 0
        failed_indices = []
        
        for i, song in enumerate(self.songs):
            try:
                song_id = song.get('id')
                platform = song.get('platform')
                
                # 酷狗音乐单独处理
                if platform == "kugou":
                    album_id = song.get('album_id', '')
                    music_url = kugou_get_song_url(song_id, album_id)
                # 网易云音乐使用官方API
                elif platform == "netease":
                    music_url = netease_get_song_url(song_id)
                else:
                    music_url = None
                
                if music_url:
                    filename = f"{song.get('name', 'song')} - {song.get('artist', 'unknown')}.mp3"
                    # 清理文件名中的非法字符
                    filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
                    save_path = f"{self.save_dir}\\{filename}"
                    
                    music_response = requests.get(music_url, stream=True, timeout=30)
                    with open(save_path, 'wb') as f:
                        for chunk in music_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    success_count += 1
                else:
                    failed_count += 1
                    failed_indices.append(i + 1)
            except Exception as e:
                failed_count += 1
                failed_indices.append(i + 1)
            
            progress = int(((i + 1) / total) * 100)
            self.download_progress.emit(progress)
            
            # 间隔1秒再下载下一首
            if i < total - 1:
                time.sleep(1)
        
        self.download_finished.emit(success_count, failed_count, failed_indices)

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.search_results = []
        self.current_song = None
        self.search_thread = None
        self.download_thread = None
        self.link_test_threads = []
        self.download_path = self.load_config()
        
        # 歌词相关
        self.lyrics_list = []  # 存储解析后的歌词列表 [(时间ms, 歌词文本), ...]
        self.current_lyric_index = -1  # 当前高亮的歌词索引
        
        # 进度条相关
        self.is_slider_pressed = False
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("TuneHub 音乐播放器")
        self.setGeometry(100, 100, 1200, 800)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 顶部信息栏
        top_layout = QHBoxLayout()
        self.now_playing_label = QLabel("当前播放: 无")
        top_layout.addWidget(self.now_playing_label)
        main_layout.addLayout(top_layout)
        
        # 搜索标签页
        self.create_search_tab(main_layout)
        
        # 播放控制区域
        self.create_player_controls(main_layout)
        
        # 歌词显示区域
        self.create_lyrics_area(main_layout)
        
        # 下载进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def create_search_tab(self, layout):
        # 搜索输入区域
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入歌曲名称...")
        self.search_input.returnPressed.connect(self.on_search)
        search_input_layout.addWidget(self.search_input)
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["网易云音乐", "酷狗音乐"])
        search_input_layout.addWidget(self.platform_combo)
        
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.on_search)
        search_input_layout.addWidget(search_btn)
        
        layout.addLayout(search_input_layout)
        
        # 批量操作区域
        batch_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("全选")
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)
        batch_layout.addWidget(self.select_all_checkbox)
        
        self.path_label = QLabel(f"下载路径: {self.download_path if self.download_path else '未设置'}")
        batch_layout.addWidget(self.path_label)
        
        select_path_btn = QPushButton("选择路径")
        select_path_btn.clicked.connect(self.select_download_path)
        batch_layout.addWidget(select_path_btn)
        
        batch_download_btn = QPushButton("批量下载")
        batch_download_btn.clicked.connect(self.batch_download)
        batch_layout.addWidget(batch_download_btn)
        
        layout.addLayout(batch_layout)
        
        self.search_table = QTableWidget()
        self.search_table.setColumnCount(8)
        self.search_table.setHorizontalHeaderLabels(["选择", "歌曲ID", "歌名", "歌手", "专辑", "平台", "试听", "下载"])
        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.search_table)
    
    def create_player_controls(self, layout):
        player_layout = QHBoxLayout()
        self.play_btn = QPushButton("播放")
        self.play_btn.clicked.connect(self.toggle_play)
        player_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_play)
        player_layout.addWidget(self.stop_btn)
        
        layout.addLayout(player_layout)
        
        # 添加播放进度条
        progress_layout = QHBoxLayout()
        self.time_label = QLabel("00:00 / 00:00")
        progress_layout.addWidget(self.time_label)
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderPressed.connect(self.on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.on_slider_released)
        self.progress_slider.sliderMoved.connect(self.on_slider_moved)
        progress_layout.addWidget(self.progress_slider)
        
        layout.addLayout(progress_layout)
    
    def create_lyrics_area(self, layout):
        lyrics_label = QLabel("歌词:")
        layout.addWidget(lyrics_label)
        self.lyrics_text = QTextEdit()
        self.lyrics_text.setReadOnly(True)
        self.lyrics_text.setMaximumHeight(200)
        layout.addWidget(self.lyrics_text)
    
    def on_search(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索关键词")
            return
        
        platform = self.platform_combo.currentText()
        
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.terminate()
        
        self.search_thread = SearchThread(keyword, platform)
        self.search_thread.search_finished.connect(self.display_search_results)
        self.search_thread.search_error.connect(self.on_search_error)
        self.search_thread.start()
    
    def on_search_error(self, error_msg):
        QMessageBox.warning(self, "错误", error_msg)
    
    def start_link_tests(self, results):
        # 清理旧的测试线程
        for thread in self.link_test_threads:
            if thread.isRunning():
                thread.terminate()
        self.link_test_threads.clear()
        
        # 为每首歌启动测试线程
        for row, song in enumerate(results):
            test_thread = LinkTestThread(row, song.copy())
            test_thread.link_test_finished.connect(self.update_play_button_color)
            test_thread.start()
            self.link_test_threads.append(test_thread)
    
    def update_play_button_color(self, row_index, is_valid):
        play_btn = self.search_table.cellWidget(row_index, 6)
        if play_btn:
            if is_valid:
                play_btn.setText("试听")
                play_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            else:
                play_btn.setText("无效")
                play_btn.setStyleSheet("background-color: #f44336; color: white;")
    
    def on_select_all_changed(self, state):
        for row in range(self.search_table.rowCount()):
            checkbox = self.search_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(state == Qt.CheckState.Checked.value)
    
    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('download_path', '')
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
        return ''
    
    def save_config(self):
        try:
            config = {'download_path': self.download_path}
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
    
    def select_download_path(self):
        file_dialog = QFileDialog()
        path = file_dialog.getExistingDirectory(self, "选择下载路径")
        
        if path:
            self.download_path = path
            self.path_label.setText(f"下载路径: {self.download_path}")
            self.save_config()
    
    def batch_download(self):
        selected_songs = []
        for row in range(self.search_table.rowCount()):
            checkbox = self.search_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                song = checkbox.property('song_data')
                if song:
                    selected_songs.append(song)
        
        if not selected_songs:
            QMessageBox.warning(self, "提示", "请先选择要下载的歌曲")
            return
        
        # 如果有正在下载的线程，先终止
        if self.download_thread and self.download_thread.isRunning():
            reply = QMessageBox.question(self, "提示", 
                "有正在进行的下载任务，是否取消并开始新下载？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.download_thread.terminate()
                self.download_thread.wait()
            else:
                return
        
        # 选择保存目录
        save_dir = self.download_path
        if not save_dir:
            file_dialog = QFileDialog()
            save_dir = file_dialog.getExistingDirectory(self, "选择保存目录")
            if not save_dir:
                return
        else:
            reply = QMessageBox.question(self, "确认下载", 
                f"将下载到: {save_dir}\n是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                file_dialog = QFileDialog()
                save_dir = file_dialog.getExistingDirectory(self, "选择保存目录")
                if not save_dir:
                    return
        
        # 启动下载线程
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.download_thread = DownloadThread(selected_songs, save_dir)
        self.download_thread.download_progress.connect(self.update_download_progress)
        self.download_thread.download_finished.connect(self.on_download_finished)
        self.download_thread.download_error.connect(self.on_download_error)
        self.download_thread.start()
    
    def update_download_progress(self, progress):
        self.progress_bar.setValue(progress)
    
    def on_download_finished(self, success_count, failed_count, failed_indices):
        self.progress_bar.setVisible(False)
        message = f"成功下载: {success_count} 首\n下载失败: {failed_count} 首"
        if failed_indices:
            message += f"\n失败歌曲序号: {', '.join(map(str, failed_indices))}"
        QMessageBox.information(self, "批量下载完成", message)
    
    def on_download_error(self, error_msg):
        self.progress_bar.setVisible(False)
        QMessageBox.warning(self, "错误", error_msg)
    
    def display_search_results(self, results):
        self.search_results = results
        self.search_table.setRowCount(len(results))
        
        platform_name_map = {
            'netease': '网易云音乐',
            'qq': 'QQ音乐',
            'kuwo': '酷我音乐',
            'kugou': '酷狗音乐'
        }
        
        for row, song in enumerate(results):
            # 复选框
            checkbox = QCheckBox()
            checkbox.setProperty('song_data', song)
            self.search_table.setCellWidget(row, 0, checkbox)
            
            self.search_table.setItem(row, 1, QTableWidgetItem(str(song.get('id', ''))))
            
            # 歌名，如果是VIP歌曲则添加VIP标识
            song_name = song.get('name', '')
            if song.get('is_vip', False):
                song_name += " [VIP]"
                # 设置VIP歌曲名称为金色
            name_item = QTableWidgetItem(song_name)
            if song.get('is_vip', False):
                name_item.setForeground(QColor("#FFD700"))  # 金色
            self.search_table.setItem(row, 2, name_item)
            
            self.search_table.setItem(row, 3, QTableWidgetItem(song.get('artist', '')))
            self.search_table.setItem(row, 4, QTableWidgetItem(song.get('album', '')))
            platform = song.get('platform', '')
            platform_name = platform_name_map.get(platform, platform)
            self.search_table.setItem(row, 5, QTableWidgetItem(platform_name))
            
            song_copy = song.copy()
            play_btn = QPushButton("测试中...")
            play_btn.clicked.connect(lambda checked, s=song_copy: self.play_song(s))
            self.search_table.setCellWidget(row, 6, play_btn)
            
            download_btn = QPushButton("下载")
            download_btn.clicked.connect(lambda checked, s=song_copy: self.download_song(s))
            self.search_table.setCellWidget(row, 7, download_btn)
        
        # 启动链接测试
        self.start_link_tests(results)
    
    def play_song(self, song):
        self.current_song = song
        song_id = song.get('id')
        platform = song.get('platform')
        
        # 酷狗音乐单独处理
        if platform == "kugou":
            self.now_playing_label.setText(f"当前播放: 准备中... (酷狗)")
            self.try_play_kugou(song)
            return
        
        # 网易云音乐使用官方API
        if platform == "netease":
            self.now_playing_label.setText(f"当前播放: 准备中... (网易云)")
            self.try_play_netease(song_id)
            return
        
        QMessageBox.warning(self, "错误", "不支持的平台")
    
    def try_play_kugou(self, song):
        try:
            song_id = song.get('id')
            album_id = song.get('album_id', '')
            
            music_url = kugou_get_song_url(song_id, album_id)
            
            if music_url and music_url.startswith('http'):
                # 验证URL有效性
                self.player.setSource(QUrl(music_url))
                self.player.play()
                self.now_playing_label.setText(f"当前播放: {song.get('name')} - {song.get('artist')} (酷狗)")
                self.play_btn.setText("暂停")
                # 启动进度更新定时器
                self.progress_timer.start(100)
            else:
                QMessageBox.warning(self, "错误", "酷狗音乐播放失败，请尝试其他歌曲")
                self.now_playing_label.setText("当前播放: 无")
                self.play_btn.setText("播放")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"酷狗音乐播放出错: {str(e)}")
            self.now_playing_label.setText("当前播放: 无")
            self.play_btn.setText("播放")

    def try_play_netease(self, song_id):
        """使用网易云音乐官方API播放"""
        try:
            music_url = netease_get_song_url(song_id)
            
            if music_url and music_url.startswith('http'):
                # 验证URL有效性
                self.player.setSource(QUrl(music_url))
                self.player.play()
                self.now_playing_label.setText(f"当前播放: {self.current_song.get('name')} - {self.current_song.get('artist')} (网易云)")
                self.play_btn.setText("暂停")
                self.load_lyrics(self.current_song)
                # 启动进度更新定时器
                self.progress_timer.start(100)
            else:
                QMessageBox.warning(self, "错误", "网易云音乐播放失败，请尝试其他歌曲")
                self.now_playing_label.setText("当前播放: 无")
                self.play_btn.setText("播放")
                self.progress_timer.stop()
                self.progress_slider.setValue(0)
                self.time_label.setText("00:00 / 00:00")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"网易云音乐播放出错: {str(e)}")
            self.now_playing_label.setText("当前播放: 无")
            self.play_btn.setText("播放")
            self.progress_timer.stop()
            self.progress_slider.setValue(0)
            self.time_label.setText("00:00 / 00:00")
    
    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("播放")
        else:
            self.player.play()
            self.play_btn.setText("暂停")
    
    def update_progress(self):
        if not self.is_slider_pressed:
            position = self.player.position()
            duration = self.player.duration()
            
            if duration > 0:
                progress = int((position / duration) * 1000)
                self.progress_slider.setValue(progress)
                
                # 更新歌词高亮
                self.update_lyrics_highlight(position)
            
            current_time = self.format_time(position)
            total_time = self.format_time(duration)
            self.time_label.setText(f"{current_time} / {total_time}")
    
    def update_lyrics_highlight(self, current_position):
        """更新歌词高亮"""
        if not self.lyrics_list:
            return
        
        # 找到当前时间对应的歌词索引
        new_index = -1
        for i, (time_ms, _) in enumerate(self.lyrics_list):
            if time_ms <= current_position:
                new_index = i
            else:
                break
        
        # 如果歌词索引变化，更新显示
        if new_index != self.current_lyric_index:
            self.current_lyric_index = new_index
            
            # 重新显示歌词，高亮当前行
            lyrics_html = ""
            for i, (_, lyric_text) in enumerate(self.lyrics_list):
                if i == new_index:
                    lyrics_html += f'<p style="color: #ff6b6b; font-size: 18px; font-weight: bold;">{lyric_text}</p>'
                elif i == new_index + 1:
                    lyrics_html += f'<p style="color: #888888;">{lyric_text}</p>'
                elif i == new_index + 2:
                    lyrics_html += f'<p style="color: #aaaaaa;">{lyric_text}</p>'
                else:
                    lyrics_html += f'<p style="color: #666666;">{lyric_text}</p>'
            
            self.lyrics_text.setHtml(lyrics_html)
            
            # 滚动到当前歌词
            if new_index >= 0:
                cursor = self.lyrics_text.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                for _ in range(new_index):
                    cursor.movePosition(cursor.MoveOperation.Down)
                self.lyrics_text.setTextCursor(cursor)
    
    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def on_slider_pressed(self):
        self.is_slider_pressed = True
    
    def on_slider_released(self):
        self.is_slider_pressed = False
        position = self.progress_slider.value()
        duration = self.player.duration()
        if duration > 0:
            new_position = int((position / 1000) * duration)
            self.player.setPosition(new_position)
    
    def on_slider_moved(self, value):
        duration = self.player.duration()
        if duration > 0:
            new_position = int((value / 1000) * duration)
            current_time = self.format_time(new_position)
            total_time = self.format_time(duration)
            self.time_label.setText(f"{current_time} / {total_time}")
    
    def stop_play(self):
        self.player.stop()
        self.play_btn.setText("播放")
        self.now_playing_label.setText("当前播放: 无")
        self.progress_timer.stop()
        self.progress_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")
    
    def download_song(self, song):
        try:
            song_id = song.get('id')
            platform = song.get('platform')
            
            # 酷狗音乐单独处理
            if platform == "kugou":
                album_id = song.get('album_id', '')
                music_url = kugou_get_song_url(song_id, album_id)
            # 网易云音乐使用官方API
            elif platform == "netease":
                music_url = netease_get_song_url(song_id)
            else:
                url = f"{BASE_URL}/api/?source={platform}&id={song_id}&type=url&br=320k"
                response = requests.get(url, timeout=10, allow_redirects=False)
                if response.status_code == 302:
                    music_url = response.headers.get('Location')
                else:
                    music_url = None
            
            if music_url:
                filename = f"{song.get('name', 'song')} - {song.get('artist', 'unknown')}.mp3"
                # 清理文件名中的非法字符
                filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
                
                # 如果有保存的路径，直接使用
                if self.download_path:
                    save_path = f"{self.download_path}\\{filename}"
                else:
                    # 没有保存路径时才弹出选择对话框
                    file_dialog = QFileDialog()
                    save_path, _ = file_dialog.getSaveFileName(self, "保存音乐", filename, "MP3 Files (*.mp3)")
                    if not save_path:
                        return
                
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                
                music_response = requests.get(music_url, stream=True)
                total_size = int(music_response.headers.get('content-length', 0))
                
                with open(save_path, 'wb') as f:
                    downloaded = 0
                    for chunk in music_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress_bar.setValue(progress)
                
                self.progress_bar.setVisible(False)
                QMessageBox.information(self, "成功", "下载完成！")
            else:
                QMessageBox.warning(self, "错误", "无法获取音乐链接")
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.warning(self, "错误", f"下载失败: {str(e)}")
    
    def load_lyrics(self, song):
        try:
            song_id = song.get('id')
            platform = song.get('platform')
            
            self.lyrics_list = []  # 清空之前的歌词
            self.current_lyric_index = -1
            
            # 网易云音乐使用官方API获取歌词
            if platform == "netease":
                self.lyrics_list = netease_get_lyrics(song_id)
            # 酷狗音乐使用官方API获取歌词
            elif platform == "kugou":
                self.lyrics_list = kugou_get_lyrics(song_id)
            else:
                self.lyrics_text.setText("不支持歌词获取的平台")
                return
            
            # 显示歌词
            if self.lyrics_list:
                lyrics_text = "\n".join([item[1] for item in self.lyrics_list])
                self.lyrics_text.setText(lyrics_text)
            else:
                self.lyrics_text.setText("暂无歌词")
        except Exception as e:
            self.lyrics_text.setText(f"加载歌词失败: {str(e)}")


def main():
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()