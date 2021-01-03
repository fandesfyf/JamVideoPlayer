# JamVideoPlayer
A VideoPlayer
一个用pyqt库构建的视频播放器,支持几乎所有音视频甚至gif和图片的的播放显示，支持全屏播放、倍速播放、添加播放列表、切换播放模式(单曲、列表循环、播放一次等)、支持快进快退、亮度音量调节等功能；
# 配置

### 需要pyqt库
pip install PyQt5

### 需要注册多媒体解码器:
从LAVFilters-0.74.1-x64 文件夹以管理员命令运行install.bat文件，或者通过命令行自行注册.ax文件

### 默认(可选)需要ffmpeg套件
用于获取更详细的视频信息(如时长\帧率\分辨率等),自行搜索安装ffmpeg套件，并传入路径到ffmpegpath。该套件体积较大，仅用于视频信息的获取，如不需要或通过其他途径获取视频信息可以自行改写get_video_information函数。
传入参数：playlist是传入的列表类型播放路径，ffmpegpath为ffplayer所在目录
JamVideoWidget(playlist=['0.mp4', '1.mp4', '2.mp4', '3.mp4'],ffmpegpath=r'D:\python_work\Jamtools\bin')

# 效果展示

