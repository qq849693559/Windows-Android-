#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python应用程序示例
支持Windows和Android平台
"""

import sys
import platform
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("跨平台Python应用")
        self.setGeometry(100, 100, 400, 300)
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 显示平台信息
        platform_label = QLabel(f"当前平台: {platform.system()}")
        platform_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(platform_label)
        
        # 显示Python版本
        python_label = QLabel(f"Python版本: {sys.version}")
        python_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(python_label)
        
        # 添加按钮
        button = QPushButton("点击我")
        button.clicked.connect(self.on_button_click)
        layout.addWidget(button)
        
        # 设置布局
        central_widget.setLayout(layout)
        
    def on_button_click(self):
        self.setWindowTitle("按钮被点击了！")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()