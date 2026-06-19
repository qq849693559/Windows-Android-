#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Android APK构建脚本
使用 PyQtDeploy + Gradle 构建 Android 音乐播放器 APK
"""

import sys
import os
import subprocess
import json
import shutil
import platform
from pathlib import Path


class AndroidAPKBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.config_file = self.project_root / "android-music-player.pdy"
        self.build_dir = self.project_root / "android_build"
        self.apk_output = self.project_root / "MusicPlayer.apk"

    def check_dependencies(self):
        """检查构建依赖，返回 (ok, warnings)"""
        print("=" * 50)
        print("检查构建依赖...")
        warnings = []

        # Python环境
        print(f"  Python: {sys.version.split()[0]}")

        # Java环境
        try:
            result = subprocess.run(
                ["java", "-version"], capture_output=True, text=True,
                timeout=10
            )
            ver_line = result.stderr.splitlines()[0] if result.stderr else "unknown"
            print(f"  Java: {ver_line}")
        except FileNotFoundError:
            print("  [ERROR] Java 未安装")
            return False, warnings

        # Android SDK
        sdk_root = os.environ.get("ANDROID_SDK_ROOT") or os.environ.get("ANDROID_HOME")
        if sdk_root and Path(sdk_root).exists():
            print(f"  Android SDK: {sdk_root}")
        else:
            warnings.append("ANDROID_SDK_ROOT 未设置，将无法使用 Gradle 编译 APK")

        # PyQt6
        try:
            import PyQt6
            print(f"  PyQt6: {PyQt6.QtCore.PYQT_VERSION_STR}")
        except ImportError:
            warnings.append("PyQt6 未安装")

        # PyQtDeploy
        try:
            import PyQtDeploy
            print("  PyQtDeploy: 已安装")
        except ImportError:
            print("  PyQtDeploy: 未安装，正在安装...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pyqtdeploy"],
                    check=True, capture_output=True
                )
                print("  PyQtDeploy: 安装完成")
            except subprocess.CalledProcessError:
                warnings.append("PyQtDeploy 安装失败")

        # Gradle
        try:
            result = subprocess.run(
                ["gradle", "--version"], capture_output=True, text=True,
                timeout=15
            )
            for line in result.stdout.splitlines():
                if "Gradle" in line and not line.startswith(" "):
                    print(f"  {line.strip()}")
                    break
        except FileNotFoundError:
            warnings.append("Gradle 未安装，将使用 Gradle Wrapper")

        return True, warnings

    def load_config(self):
        """加载项目配置"""
        if not self.config_file.exists():
            print(f"[ERROR] 配置文件不存在: {self.config_file}")
            return None

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            print(f"[ERROR] 配置文件格式错误: {e}")
            return None

    def create_android_project(self, config):
        """创建 Android 项目结构"""
        print("\n创建 Android 项目结构...")

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir, ignore_errors=True)
        self.build_dir.mkdir(parents=True)

        pkg = config.get("application_package", "com.example.musicplayer")
        app_name = config.get("application_name", "音乐播放器")
        version = config.get("version", "1.0.0")
        android_cfg = config.get("android", {})

        pkg_path = self.build_dir / "app" / "src" / "main" / "java"
        pkg_path = pkg_path / pkg.replace(".", "/")
        pkg_path.mkdir(parents=True, exist_ok=True)

        res_path = self.build_dir / "app" / "src" / "main" / "res"
        (res_path / "values").mkdir(parents=True, exist_ok=True)
        (res_path / "layout").mkdir(parents=True, exist_ok=True)
        (res_path / "mipmap-hdpi").mkdir(parents=True, exist_ok=True)

        # 生成占位应用图标（最小有效 PNG）
        self._generate_icon(res_path / "mipmap-hdpi" / "ic_launcher.png")

        # ---- Gradle 文件 ----
        self._write_settings_gradle(pkg, app_name)
        self._write_root_build_gradle()
        self._write_gradle_properties()
        self._write_app_build_gradle(pkg, version, android_cfg)

        # ---- AndroidManifest.xml ----
        self._write_manifest(pkg, app_name, version, android_cfg)

        # ---- Java 源码 ----
        self._write_main_activity(pkg_path, pkg, android_cfg)

        # ---- 资源文件 ----
        self._write_strings_xml(res_path, app_name)
        self._write_layout_xml(res_path)

        # ---- 复制 Python 源码 ----
        python_assets = self.build_dir / "app" / "src" / "main" / "assets" / "python"
        python_assets.mkdir(parents=True, exist_ok=True)
        src_py = self.project_root / "源码" / "music_player.py"
        if src_py.exists():
            shutil.copy2(src_py, python_assets / "main.py")
            print(f"  复制源码: {src_py} -> assets/python/main.py")

        print("  Android 项目结构创建完成")

        # ---- 使用 pyqtdeploy 生成嵌入层 ----
        self._run_pyqtdeploy_build(config)

        return True

    def _write_settings_gradle(self, pkg, app_name):
        content = f"""pluginManagement {{
    repositories {{
        google()
        mavenCentral()
        gradlePluginPortal()
    }}
}}

dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}

rootProject.name = "{app_name}"
include(":app")
"""
        (self.build_dir / "settings.gradle").write_text(content, encoding="utf-8")

    def _write_root_build_gradle(self):
        content = """plugins {
    id("com.android.application") version "8.2.0" apply false
}
"""
        (self.build_dir / "build.gradle").write_text(content, encoding="utf-8")

    def _write_gradle_properties(self):
        content = """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
"""
        (self.build_dir / "gradle.properties").write_text(content, encoding="utf-8")

    def _write_app_build_gradle(self, pkg, version, android_cfg):
        min_sdk = android_cfg.get("min_sdk_version", 21)
        target_sdk = android_cfg.get("target_sdk_version", 33)
        content = f"""plugins {{
    id("com.android.application")
}}

android {{
    namespace = "{pkg}"

    compileSdk = {target_sdk}

    defaultConfig {{
        applicationId = "{pkg}"
        minSdk = {min_sdk}
        targetSdk = {target_sdk}
        versionCode = 1
        versionName = "{version}"
    }}

    buildTypes {{
        release {{
            minifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }}
        debug {{
            debuggable = true
        }}
    }}

    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }}

    sourceSets {{
        getByName("main") {{
            assets {{
                srcDirs("src/main/assets")
            }}
        }}
    }}
}}

dependencies {{
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
}}
"""
        app_dir = self.build_dir / "app"
        app_dir.mkdir(parents=True, exist_ok=True)
        (app_dir / "build.gradle").write_text(content, encoding="utf-8")

    def _write_manifest(self, pkg, app_name, version, android_cfg):
        min_sdk = android_cfg.get("min_sdk_version", 21)
        target_sdk = android_cfg.get("target_sdk_version", 33)
        permissions = android_cfg.get("permissions", [])
        features = android_cfg.get("features", [])
        activity = android_cfg.get("activity_name", "MainActivity")

        perm_lines = "\n".join(
            f'    <uses-permission android:name="android.permission.{p}" />'
            for p in permissions
        )
        feat_lines = "\n".join(
            f'    <uses-feature android:name="{f}" />' for f in features
        )

        content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

{perm_lines}

{feat_lines}

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{app_name}"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.DarkActionBar">

        <activity
            android:name=".{activity}"
            android:exported="true"
            android:configChanges="orientation|screenSize|screenLayout|keyboardHidden"
            android:label="{app_name}">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>

</manifest>
"""
        manifest_dir = self.build_dir / "app" / "src" / "main"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        (manifest_dir / "AndroidManifest.xml").write_text(content, encoding="utf-8")

    def _write_main_activity(self, pkg_path, pkg, android_cfg):
        activity = android_cfg.get("activity_name", "MainActivity")
        content = f"""package {pkg};

import android.os.Bundle;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

/**
 * 音乐播放器主活动
 * Python 解释器将通过 JNI 在 native 层加载
 */
public class {activity} extends AppCompatActivity {{

    static {{
        try {{
            System.loadLibrary("python3.11");
        }} catch (UnsatisfiedLinkError e) {{
            // Python 库未找到，将在 onResume 中处理
        }}
    }}

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 检查 Python 环境
        if (isPythonAvailable()) {{
            Toast.makeText(this, "Python 环境已就绪", Toast.LENGTH_SHORT).show();
            startPythonApp();
        }} else {{
            Toast.makeText(this, "Python 环境未找到，请安装完整包", Toast.LENGTH_LONG).show();
        }}
    }}

    @Override
    protected void onResume() {{
        super.onResume();
    }}

    private boolean isPythonAvailable() {{
        try {{
            // 尝试调用 Python 初始化
            nativePythonInit(getAssets());
            return true;
        }} catch (Exception e) {{
            return false;
        }}
    }}

    private void startPythonApp() {{
        new Thread(() -> {{
            nativePythonMain(
                getFilesDir().getAbsolutePath(),
                getCacheDir().getAbsolutePath()
            );
        }}).start();
    }}

    // Native 方法 - 由 PyQtDeploy 生成的 C++ 代码提供实现
    private native void nativePythonInit(Object assetManager);
    private native void nativePythonMain(String filesDir, String cacheDir);
}}
"""
        (pkg_path / f"{activity}.java").write_text(content, encoding="utf-8")

    def _write_strings_xml(self, res_path, app_name):
        content = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{app_name}</string>
    <string name="title_activity_main">{app_name}</string>
</resources>
"""
        (res_path / "values" / "strings.xml").write_text(content, encoding="utf-8")

    def _write_layout_xml(self, res_path):
        content = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:gravity="center">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="音乐播放器"
        android:textSize="28sp"
        android:textStyle="bold"
        android:layout_marginBottom="24dp" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="正在加载 Python 运行环境..."
        android:textSize="14sp"
        android:textColor="#888888" />

</LinearLayout>
"""
        (res_path / "layout" / "activity_main.xml").write_text(content, encoding="utf-8")

    def _run_pyqtdeploy_build(self, config):
        """使用 PyQtDeploy 生成 Python 嵌入层"""
        print("\n尝试使用 PyQtDeploy 构建...")
        try:
            import PyQtDeploy
        except ImportError:
            print("  [SKIP] PyQtDeploy 未安装，跳过 Python 嵌入层生成")
            return

        # pyqtdeploy-build 需要 .pdy 配置文件
        pdy_file = self.config_file
        if not pdy_file.exists():
            print("  [SKIP] .pdy 配置文件不存在")
            return

        try:
            result = subprocess.run(
                [sys.executable, "-m", "PyQtDeploy", "build",
                 "--project", str(pdy_file),
                 "--output", str(self.build_dir)],
                capture_output=True, text=True,
                timeout=300,
                cwd=str(self.project_root)
            )
            if result.returncode == 0:
                print("  PyQtDeploy 构建成功")
            else:
                print(f"  PyQtDeploy 构建警告: {result.stderr[:200]}")
                print("  [INFO] 将继续使用 Gradle 构建基础 APK")
        except subprocess.TimeoutExpired:
            print("  [SKIP] PyQtDeploy 构建超时，继续 Gradle 构建")
        except Exception as e:
            print(f"  [INFO] PyQtDeploy 未就绪: {e}")

    def _write_local_properties(self):
        """生成 local.properties，指向 Android SDK"""
        sdk_root = os.environ.get("ANDROID_SDK_ROOT") or os.environ.get("ANDROID_HOME")
        if sdk_root:
            content = f"sdk.dir={sdk_root}\n"
            (self.build_dir / "local.properties").write_text(content, encoding="utf-8")
            print(f"  local.properties 已生成 -> sdk.dir={sdk_root}")
        else:
            print("  [WARNING] 未找到 ANDROID_SDK_ROOT 或 ANDROID_HOME 环境变量")

    def _generate_icon(self, output_path):
        """生成最小有效 PNG 图标（48x48 蓝色方块），无需任何图片库依赖"""
        import struct, zlib

        def chunk(chunk_type, data):
            c = chunk_type + data
            crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
            return struct.pack(">I", len(data)) + c + crc

        width, height = 48, 48
        # 生成蓝色像素行
        raw = b""
        for y in range(height):
            raw += b"\x00"  # filter byte
            for x in range(width):
                raw += b"\x1a\x6b\xd4\xff"  # RGBA 蓝色

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(raw))
        png += chunk(b"IEND", b"")

        output_path.write_bytes(png)
        print(f"  生成占位图标: {output_path.name}")

    def generate_gradle_wrapper(self):
        """生成 Gradle Wrapper"""
        wrapper_dir = self.build_dir / "gradle" / "wrapper"
        wrapper_dir.mkdir(parents=True, exist_ok=True)

        props = """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https://services.gradle.org/distributions/gradle-8.5-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""
        (wrapper_dir / "gradle-wrapper.properties").write_text(props, encoding="utf-8")

        # 使用系统 gradle 生成 wrapper
        try:
            subprocess.run(
                ["gradle", "wrapper", "--gradle-version", "8.5"],
                cwd=str(self.build_dir),
                capture_output=True,
                timeout=60
            )
            print("  Gradle Wrapper 已生成")
        except Exception:
            # 手动创建 gradlew 脚本
            self._create_gradlew_script()
            print("  Gradle Wrapper 已手动创建")

    def _create_gradlew_script(self):
        """手动创建 gradlew (Unix)"""
        script = """#!/bin/sh
GRADLE_OPTS="-Dorg.gradle.appname=gradle"
exec gradle "$@"
"""
        gradlew = self.build_dir / "gradlew"
        gradlew.write_text(script, encoding="utf-8")
        gradlew.chmod(0o755)

    def build_with_gradle(self):
        """使用 Gradle 编译 APK"""
        print("\n" + "=" * 50)
        print("使用 Gradle 编译 APK...")

        # 生成 local.properties，确保 Gradle 能找到 Android SDK
        self._write_local_properties()

        self.generate_gradle_wrapper()

        # 确定使用哪种 gradle 命令
        gradle_cmd = self._get_gradle_command()

        # 清理并构建
        print("\n清理旧构建...")
        result = subprocess.run(
            gradle_cmd + ["clean"],
            cwd=str(self.build_dir),
            capture_output=True, text=True,
            timeout=120
        )
        if result.returncode != 0:
            print(f"  清理警告: {result.stderr[-300:]}")

        print("\n开始编译 APK (debug)...")
        result = subprocess.run(
            gradle_cmd + ["assembleDebug"],
            cwd=str(self.build_dir),
            capture_output=True, text=True,
            timeout=600
        )

        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)

        if result.returncode == 0:
            # 查找生成的 APK
            apk_glob = list(self.build_dir.glob("app/build/outputs/apk/debug/*.apk"))
            if apk_glob:
                apk_path = apk_glob[0]
                shutil.copy2(apk_path, self.apk_output)
                import datetime
                size_mb = apk_path.stat().st_size / (1024 * 1024)
                print(f"\n[SUCCESS] APK 编译成功!")
                print(f"  输出文件: {self.apk_output}")
                print(f"  文件大小: {size_mb:.1f} MB")
                print(f"  构建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            else:
                print("\n[WARNING] Gradle 编译成功但未找到 APK 文件")
                return False
        else:
            stderr_tail = result.stderr[-1500:] if len(result.stderr) > 1500 else result.stderr
            print(f"\n[ERROR] Gradle 编译失败:")
            print(stderr_tail)
            return False

    def _get_gradle_command(self):
        """获取 Gradle 命令"""
        # 优先使用 gradlew
        gradlew = self.build_dir / "gradlew"
        if gradlew.exists():
            if platform.system() == "Windows":
                return [str(self.build_dir / "gradlew.bat")]
            return ["./gradlew"]

        # 回退到系统 gradle
        try:
            subprocess.run(["gradle", "--version"], capture_output=True, timeout=5)
            return ["gradle"]
        except Exception:
            return ["./gradlew"]

    def run(self):
        """运行构建流程"""
        print("Android APK 构建工具")
        print(f"项目目录: {self.project_root}")
        print(f"构建目录: {self.build_dir}")

        # 1. 检查依赖
        ok, warnings = self.check_dependencies()
        if warnings:
            print("\n构建警告:")
            for w in warnings:
                print(f"  - {w}")

        # 2. 加载配置
        config = self.load_config()
        if not config:
            print("[ERROR] 无法加载配置，构建终止")
            return False

        # 3. 创建 Android 项目
        if not self.create_android_project(config):
            print("[ERROR] 项目创建失败")
            return False

        # 4. Gradle 编译
        if not self.build_with_gradle():
            print("\n[WARNING] Gradle 编译出现问题，但项目结构已创建")
            print("  你可以在本地安装 Android SDK 后手动编译:")
            print(f"    cd {self.build_dir}")
            print(f"    gradle assembleDebug")
            return False

        print("\n" + "=" * 50)
        print("构建完成!")
        return True


def main():
    builder = AndroidAPKBuilder()
    success = builder.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
