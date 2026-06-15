#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub发布脚本
用于创建和管理GitHub Releases
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd):
    """执行shell命令"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return None

def create_git_tag(tag_name):
    """创建git标签"""
    print(f"创建标签: {tag_name}")
    result = run_command(f"git tag -a {tag_name} -m 'Release {tag_name}'")
    if result is None:
        return False
    return True

def push_git_tag(tag_name):
    """推送git标签到远程"""
    print(f"推送标签: {tag_name}")
    result = run_command(f"git push origin {tag_name}")
    if result is None:
        return False
    return True

def create_release(tag_name, release_notes):
    """创建GitHub Release"""
    print(f"创建GitHub Release: {tag_name}")
    
    # 使用GitHub CLI创建Release
    cmd = f'gh release create {tag_name} --title "Release {tag_name}" --notes "{release_notes}"'
    result = run_command(cmd)
    
    if result is None:
        # 如果GitHub CLI不可用，使用curl API
        print("GitHub CLI不可用，尝试使用API...")
        return create_release_api(tag_name, release_notes)
    
    return True

def create_release_api(tag_name, release_notes):
    """使用GitHub API创建Release"""
    import json
    
    # 获取GitHub令牌
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("错误: 未设置GITHUB_TOKEN环境变量")
        return False
    
    # 构建API请求
    repo = os.environ.get('GITHUB_REPOSITORY', 'your-username/your-repo')
    url = f"https://api.github.com/repos/{repo}/releases"
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'tag_name': tag_name,
        'name': f'Release {tag_name}',
        'body': release_notes,
        'draft': False,
        'prerelease': False
    }
    
    # 发送请求
    import requests
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"成功创建Release: {tag_name}")
        return True
    else:
        print(f"创建Release失败: {response.status_code} - {response.text}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python release.py <tag_name> [release_notes]")
        sys.exit(1)
    
    tag_name = sys.argv[1]
    release_notes = sys.argv[2] if len(sys.argv) > 2 else f"Release {tag_name}\n\n自动构建版本\n\n构建时间: {datetime.now().isoformat()}"
    
    print(f"开始发布流程...")
    print(f"标签: {tag_name}")
    print(f"发布说明: {release_notes}")
    
    # 创建标签
    if not create_git_tag(tag_name):
        print("创建标签失败")
        sys.exit(1)
    
    # 推送标签
    if not push_git_tag(tag_name):
        print("推送标签失败")
        sys.exit(1)
    
    # 创建Release
    if not create_release(tag_name, release_notes):
        print("创建Release失败")
        sys.exit(1)
    
    print("发布流程完成！")

if __name__ == "__main__":
    main()