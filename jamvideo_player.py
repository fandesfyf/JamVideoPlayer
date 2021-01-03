import json
import os
import subprocess
import sys
import time

from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtWidgets import QPushButton, QGroupBox, QDoubleSpinBox, QSlider, QListWidget
# import jamresourse 为导入资源文件,如图标等,去除后将界面将很丑....
import jamresourse


class JQSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value_label = QLabel(self)
        # self.valueChanged.connect(self.update)
        self.value_label.setGeometry(0, 0, 30, 20)
        self.valueChanged.connect(self.v_show)
        self.value_label.setFont(QFont('微软雅黑', 9))
        self.value_label.setStyleSheet('color:rgb(255,2,100)')

    def v_show(self):
        self.setToolTip(str(self.value()))
        self.toolTipDuration()
        self.value_label.setText(str(self.value()))
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)


class JamVideoWidget(QWidget):
    def __init__(self, playlist=[], windowsname='Jamvideo', ffmpegpath='', parent=None,
                 autoclose=False):
        super().__init__(parent=parent)
        self.player = QMediaPlayer()
        self.video_widget = QVideoWidget(self)
        self.video_widget.setAspectRatioMode(-1)
        self.video_widget.setMouseTracking(True)
        self.video_widget.setFocusPolicy(Qt.NoFocus)
        self.duration_ts = self.playmode = self.t_brightness = 0
        self.t_volume = 100
        self.autoclose = autoclose
        self.single_press_pause = self.control_autohide = False
        self.acceptvideoformat = ['.mp4', '.mkv', '.flv', '.wmv', '.rmvb', '.mov', '.m4v', '.gif',
                                  '.avi', '.mp3', '.wav', '.flac', '.aac', '.real media', '.midi', '.ogg', '.amr',
                                  '.png']
        self.f_path = ffmpegpath
        if ffmpegpath=="":print("!! 未传入ffmpeg套件地址,将无法获取视频的详细信息,但仍可以播放...")
        self.control_groupbox = QGroupBox(self)
        self.time_label = QLabel(self.control_groupbox)
        self.sound_btn = QPushButton(self.control_groupbox)
        self.brightness_btn = QPushButton(self.control_groupbox)
        self.speed_slider = QDoubleSpinBox(self.control_groupbox)
        self.playQSlider = QSlider(self.control_groupbox)
        self.volume_slider = JQSlider(self.control_groupbox)
        self.brightness_slider = JQSlider(self.control_groupbox)
        self.previous_btn = QPushButton(self.control_groupbox)
        self.play_pause_btn = QPushButton(self.control_groupbox)
        self.next_btn = QPushButton(self.control_groupbox)
        self.forwardplay_btn = QPushButton(self.control_groupbox)
        self.backplay_btn = QPushButton(self.control_groupbox)
        self.mode_btn = QPushButton(self.control_groupbox)
        self.list_btn = QPushButton(self.control_groupbox)
        self.fullscreen_btn = QPushButton(self.control_groupbox)

        self.setWindowTitle(windowsname)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.list_widget = QListWidget(self)
        self.playerlist = QMediaPlaylist()
        self.playerlist.setPlaybackMode(QMediaPlaylist.Loop)
        self.pathlist = playlist
        if len(playlist) > 0:
            for name in playlist:
                self.playerlist.addMedia(QMediaContent(QUrl.fromLocalFile(name)))
                self.list_widget.addItem(os.path.split(name)[1])
            self.get_video_information(playlist[0])
        else:
            print('拖入文件播放')

        self.player.setPlaylist(self.playerlist)
        self.player.setVideoOutput(self.video_widget)  # 视频播放输出的widget，就是上面定义的
        self.player.play()  # 播放视频

        # print(self.player.state())
        self.setAcceptDrops(True)

        # self.h1_layout = QHBoxLayout()
        # self.h2_layout = QHBoxLayout()
        # self.all_v_layout = QVBoxLayout()
        self.widget_init()

    def widget_init(self):
        self.control_groupbox.show()
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setOrientation(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setOrientation(Qt.Horizontal)
        self.list_widget.hide()
        self.playQSlider.setOrientation(Qt.Horizontal)
        self.speed_slider.setRange(0, 5)
        self.speed_slider.setValue(1)
        self.speed_slider.setSingleStep(0.1)
        self.speed_slider.setPrefix('速度:')
        self.speed_slider.setToolTip('播放速度')
        self.speed_slider.setFocusPolicy(Qt.NoFocus)
        self.sound_btn.setIcon(QIcon(':/sound3.png'))
        self.sound_btn.setToolTip('音量(屏幕右侧滚动可快速调节)')
        self.sound_btn.setFocusPolicy(Qt.NoFocus)
        self.brightness_btn.setIcon(QIcon(':/bright.png'))
        self.brightness_btn.setToolTip('亮度(屏幕左侧滚动可快速调节)')
        self.brightness_btn.setFocusPolicy(Qt.NoFocus)
        self.previous_btn.setIcon(QIcon(':/lastplay.png'))
        self.previous_btn.setToolTip('上一个')
        self.previous_btn.setFocusPolicy(Qt.NoFocus)
        self.backplay_btn.setToolTip('后退5s(←键)')
        self.backplay_btn.setIcon(QIcon(':/backplay.png'))
        self.backplay_btn.setFocusPolicy(Qt.NoFocus)
        self.forwardplay_btn.setToolTip('前进5s(→键)')
        self.forwardplay_btn.setIcon(QIcon(':/forwardplay.png'))
        self.forwardplay_btn.setFocusPolicy(Qt.NoFocus)
        self.play_pause_btn.setStyleSheet('border-image: url(:/startplay.png);')
        self.next_btn.setIcon(QIcon(':/nextplay.png'))
        self.next_btn.setToolTip('下一个')
        self.next_btn.setFocusPolicy(Qt.NoFocus)
        self.mode_btn.setIcon(QIcon(':/loopplay.png'))
        self.mode_btn.setFocusPolicy(Qt.NoFocus)
        self.list_btn.setIcon(QIcon(':/playlist.png'))
        self.list_btn.setToolTip('播放列表')
        self.list_btn.setFocusPolicy(Qt.NoFocus)
        self.fullscreen_btn.setIcon(QIcon(':/full.png'))
        self.fullscreen_btn.setToolTip('全屏')
        self.fullscreen_btn.setFocusPolicy(Qt.NoFocus)
        # self.player.setPlaybackRate(0.5)
        self.resize_all()
        self.show()
        self.connect_all()
        self.setStyleSheet("""QSlider::groove:horizontal{ height: 12px;
                                                            left: 5px; 
                                                            right: 5px; 
                                                            border-image: url(:/slider1.png);
                                                          } 
                                            QSlider::handle:horizontal{ 
                                                            border-radius: 20px; 
                                                            width:  40px; 
                                                            height: 40px; 
                                                            margin-top: -10px; 
                                                            margin-left: -10px; 
                                                            margin-bottom: -20px; 
                                                            margin-right: -10px; 
                                                            border-image:url(:/sliderbtn.png);} 
                                            QSlider::sub-page:horizontal{border-image: url(:/slider0.png);}""")

    def connect_all(self):
        """信号连接"""
        self.volume_slider.valueChanged.connect(self.volume_slider_func)
        self.brightness_slider.valueChanged.connect(self.brightness_slider_func)
        self.playQSlider.sliderMoved.connect(self.update_position_func)
        self.speed_slider.valueChanged.connect(self.playspeed_change)
        self.sound_btn.clicked.connect(self.change_volume)
        self.brightness_btn.clicked.connect(self.change_brightness)
        self.previous_btn.clicked.connect(lambda: self.previous_play(False))
        self.play_pause_btn.clicked.connect(self.start_and_stop)
        # self.play_pause_btn.setShortcut( Qt.Key_Space)
        # self.play_pause_btn.setShortcutAutoRepeat(False,False)
        self.next_btn.clicked.connect(lambda: self.previous_play(True))
        self.mode_btn.clicked.connect(self.modechange)
        self.list_btn.clicked.connect(self.playlist_show)
        self.fullscreen_btn.clicked.connect(self.fullscreen_change)
        self.player.positionChanged.connect(self.get_position_func)
        self.playerlist.currentIndexChanged.connect(self.playlist_show_current)
        self.backplay_btn.clicked.connect(lambda: self.play_back_forward(False))
        # self.backplay_btn.setShortcut(Qt.Key_Left)
        self.forwardplay_btn.clicked.connect(lambda: self.play_back_forward(True))
        # self.forwardplay_btn.setShortcut(Qt.Key_Right)
        self.list_widget.doubleClicked.connect(self.list_play_func)

    def resize_all(self):
        """resize后调整所有控件"""
        self.video_widget.resize(self.width(), self.height() - 80)
        self.control_groupbox.setGeometry(0, self.height() - 80, self.width(), 80)
        self.playQSlider.setGeometry(0, 0, self.control_groupbox.width() - 138, 20)
        self.time_label.setGeometry(self.playQSlider.x() + self.playQSlider.width(), self.playQSlider.y(),
                                    self.width() - self.playQSlider.width(), 20)
        self.play_pause_btn.setGeometry(self.control_groupbox.width() // 2 - 25, 20, 50, 50)
        self.previous_btn.setGeometry(self.play_pause_btn.x() - 65,
                                      self.play_pause_btn.y() + 7, 35, 35)

        self.next_btn.setGeometry(self.play_pause_btn.x() + self.play_pause_btn.width() + 30,
                                  self.play_pause_btn.y() + 7, 35, 35)
        self.backplay_btn.setGeometry(self.previous_btn.x() - 65,
                                      self.previous_btn.y(), 35, 35)
        self.forwardplay_btn.setGeometry(self.next_btn.x() + self.next_btn.width() + 30,
                                         self.next_btn.y(), 35, 35)
        self.list_btn.setGeometry(self.control_groupbox.width() - 40, self.play_pause_btn.y(), 30, 30)
        self.fullscreen_btn.setGeometry(self.control_groupbox.width() - 40, self.list_btn.y() + self.list_btn.height(),
                                        30, 30)
        self.list_widget.setGeometry(self.control_groupbox.x() + self.control_groupbox.width() - 205,
                                     self.control_groupbox.y() - 205, 200, 200)
        self.sound_btn.setGeometry(self.forwardplay_btn.x() + 55, self.list_btn.y() - 10, 30, 30)
        self.volume_slider.move(self.sound_btn.x() + 35,
                                self.sound_btn.y() + 3)
        self.brightness_btn.setGeometry(self.sound_btn.x(), self.sound_btn.y() + 35, 30, 30)
        self.brightness_slider.move(self.brightness_btn.x() + 35,
                                    self.brightness_btn.y() + 3)
        self.speed_slider.setGeometry(self.list_btn.x() - 100, self.list_btn.y(), 100, 25)
        self.mode_btn.setGeometry(self.backplay_btn.x() - 80, self.backplay_btn.y(), 30, 30)

    def play_back_forward(self, forward=True):
        if forward:
            self.player.setPosition(self.player.position() + 5000)
        else:
            self.player.setPosition(self.player.position() - 5000)

    def playspeed_change(self, value):
        self.player.setPlaybackRate(value)
        print(self.player.playbackRate())

    def change_brightness(self):
        self.video_widget.setBrightness(0)
        self.brightness_slider.setValue(0)

    def change_volume(self):
        """点击了声音按钮"""
        if self.player.volume() != 0:
            self.t_volume = self.player.volume()
            self.player.setVolume(0)
            self.volume_slider.setValue(0)
        else:
            self.player.setVolume(self.t_volume)
            self.volume_slider.setValue(self.t_volume)

    def brightness_slider_func(self, value):
        """亮度显示改变"""
        self.video_widget.setBrightness(value)
        self.brightness_slider.setValue(value)

    def volume_slider_func(self, value):
        """声音显示改变"""
        self.player.setVolume(value)
        self.volume_slider.setValue(value)
        if value == 0:
            self.sound_btn.setIcon(QIcon(':/sound0.png'))
        elif value < 50:
            self.sound_btn.setIcon(QIcon(':/sound1.png'))
        elif value < 80:
            self.sound_btn.setIcon(QIcon(':/sound2.png'))
        else:
            self.sound_btn.setIcon(QIcon(':/sound3.png'))

    def modechange(self):  # 改变播放循环模式
        if self.playmode < 3:
            self.playmode += 1
            if self.playmode == 1:
                self.mode_btn.setToolTip('单曲循环')
                self.playerlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
                self.mode_btn.setIcon(QIcon(':/loopsingleplay.png'))
            elif self.playmode == 2:
                self.playerlist.setPlaybackMode(QMediaPlaylist.CurrentItemOnce)
                self.mode_btn.setToolTip('播放一次')
                self.mode_btn.setIcon(QIcon(':/singleplay.png'))
            else:
                self.playerlist.setPlaybackMode(QMediaPlaylist.Random)
                self.mode_btn.setToolTip('随机播放')
                self.mode_btn.setIcon(QIcon(':/randplay.png'))

        elif self.playmode == 3:
            self.playmode = 0
            self.playerlist.setPlaybackMode(QMediaPlaylist.Loop)
            self.mode_btn.setToolTip('列表循环')
            self.mode_btn.setIcon(QIcon(':/loopplay.png'))

    def get_time_func(self, d):
        """拉动滑块时的调节时间显示"""
        if d == 0:
            self.time_label.setText('--/--')
        else:
            self.time_label.setText(
                '{0}/{1}'.format(time.strftime("%H:%M:%S", time.gmtime(d / 1000)),
                                 time.strftime("%H:%M:%S", time.gmtime(self.duration_ts / 1000))))

    def update_position_func(self, v):
        """self.playQSlider.sliderMoved.connect(self.update_position_func)
        拖动进度条事件"""
        print(v, 0)
        self.player.setPosition(v)
        self.get_time_func(v)

    def get_position_func(self, p):
        """播放时进度条改变"""
        # print(p)
        self.time_label.setText('{0}/{1}'.format(time.strftime("%H:%M:%S", time.gmtime(p / 1000)),
                                                 time.strftime("%H:%M:%S", time.gmtime(self.duration_ts / 1000))))
        self.playQSlider.setValue(p)

    def list_play_func(self):
        """双击播放列表"""
        self.playerlist.setCurrentIndex(self.list_widget.currentRow())
        self.player.play()
        self.play_pause_btn.setStyleSheet('border-image: url(:/startplay.png);')

    def playlist_show_current(self, index):
        # print(index)
        self.list_widget.setCurrentRow(index)
        self.get_video_information(self.pathlist[self.playerlist.currentIndex()])

    def playlist_show(self):
        """显示播放列表"""
        if self.list_widget.isHidden():
            self.list_widget.show()
            print('show list')
        else:
            print('hide list')
            self.list_widget.hide()

    def previous_play(self, a=True):
        """按钮切换播放列表"""
        print(a)
        if a:
            if self.playerlist.currentIndex() == self.playerlist.mediaCount() - 1:
                self.playerlist.setCurrentIndex(0)
            elif self.playerlist.playbackMode() == QMediaPlaylist.Random:
                self.playerlist.next()
            else:
                self.playerlist.setCurrentIndex(self.playerlist.currentIndex() + 1)
        else:
            if self.playerlist.currentIndex() == 0:
                self.playerlist.setCurrentIndex(self.playerlist.mediaCount() - 1)
            elif self.playerlist.playbackMode() == QMediaPlaylist.Random:
                self.playerlist.previous()
            else:
                self.playerlist.setCurrentIndex(self.playerlist.currentIndex() - 1)
        print(self.pathlist[self.playerlist.currentIndex()], self.playerlist.currentIndex(), 'index')
        # self.get_video_information(self.pathlist[self.playerlist.currentIndex()])

    def start_and_stop(self):
        """播放/暂停"""
        if self.player.state() == 2:
            self.player.play()
            self.play_pause_btn.setStyleSheet('border-image: url(:/startplay.png);')
        elif self.player.state() == 1:
            self.player.pause()
            self.play_pause_btn.setStyleSheet('border-image: url(:/pauseplay.png);')

    def dragEnterEvent(self, e):
        """拖动事件"""
        file0 = e.mimeData().urls()[0].toLocalFile()
        if os.path.splitext(file0)[-1].lower() in self.acceptvideoformat:
            e.acceptProposedAction()

    def dropEvent(self, e):
        """接受拖动事件"""
        print(e.mimeData().urls())
        files = []
        for item in e.mimeData().urls():
            file0 = item.toLocalFile()
            files.append(file0)
        self.append_playlist(files)

    def append_playlist(self, files):
        print('getfiles:', files)
        try:
            for file0 in files:
                if os.path.splitext(file0)[-1].lower() in self.acceptvideoformat:
                    self.pathlist.append(file0)
                    self.playerlist.addMedia(QMediaContent(QUrl.fromLocalFile(file0)))
                    self.list_widget.addItem(os.path.split(file0)[1])
            self.get_video_information(self.pathlist[self.playerlist.mediaCount() - len(files)])
            self.playerlist.setCurrentIndex(self.playerlist.mediaCount() - len(files))
            self.player.play()
            # self.controller.controlerrun_start(file0)
            print('start', self.playerlist.mediaCount())
        except:
            print(sys.exc_info())
            self.get_video_information(self.pathlist[0])
            self.playerlist.setCurrentIndex(0)

    def showFullScreen(self):
        """全屏"""
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        super().showFullScreen()
        self.control_groupbox.hide()
        self.control_autohide = True
        self.video_widget.resize(self.width(), self.height())

    def showNormal(self):
        """退出全屏,显示正常窗口"""
        super().showNormal()
        self.control_groupbox.show()
        self.control_autohide = False
        try:
            del self.control_groupbox_hidetimer
        except:
            pass
        # self.video_widget.resize(self.width(), self.height() - 80)

    def mouseDoubleClickEvent(self, e):
        """双击动作"""
        super().mouseDoubleClickEvent(e)
        self.fullscreen_change()

    def fullscreen_change(self):
        if self.isFullScreen():
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.showNormal()
            self.fullscreen_btn.setIcon(QIcon(':/full.png'))
            # self.show()
            # self.setFullScreen(False)
        else:
            self.fullscreen_btn.setIcon(QIcon(':/exfull.png'))
            self.showFullScreen()

            # self.show()
            # self.video_widget.setFullScreen(True)

    def mouseMoveEvent(self, e):
        # super().mouseMoveEvent(e)
        if self.control_autohide:
            if e.y() < self.height() / 2:
                self.control_groupbox.hide()
            else:
                self.fullscreenshow_controlbox()

    def fullscreenshow_controlbox(self):
        if self.control_autohide:
            self.control_groupbox.show()
            self.control_groupbox_hidetimer = QTimer()
            self.control_groupbox_hidetimer.timeout.connect(self.control_groupbox_hidetimer.stop)
            self.control_groupbox_hidetimer.timeout.connect(self.control_groupbox.hide)
            self.control_groupbox_hidetimer.start(2000)

    def keyPressEvent(self, e):
        # super().keyPressEvent(e)
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_Space:
            self.start_and_stop()
        elif e.key() == Qt.Key_Down:
            self.volume_slider_func(self.player.volume() - 5)
        elif e.key() == Qt.Key_Up:
            self.volume_slider_func(self.player.volume() + 5)
        elif e.key() == Qt.Key_Left:
            self.play_back_forward(False)
        elif e.key() == Qt.Key_Right:
            self.play_back_forward(True)

    def wheelEvent(self, e):
        # super().wheelEvent(e)
        if self.isVisible():
            # print(e.x(), self.width() // 2)
            self.fullscreenshow_controlbox()
            angleDelta = e.angleDelta() / 8
            dy = angleDelta.y()
            if e.y() < self.height() * 4 / 5:
                if e.x() > self.width() // 2:
                    # self.setting_volume = True
                    # print(self.player.volume())
                    if dy > 0:
                        if self.player.volume() < 100:
                            self.volume_slider_func(self.player.volume() + 2)
                    else:
                        if self.player.volume() > 0:
                            self.volume_slider_func(self.player.volume() - 2)
                else:

                    if dy > 0:
                        self.brightness_slider_func(self.video_widget.brightness() + 2)
                    else:
                        self.brightness_slider_func(self.video_widget.brightness() - 2)
                self.update()

    def mouseReleaseEvent(self, e):
        # super().mouseReleaseEvent(e)
        if self.single_press_pause:
            if e.button() == Qt.LeftButton:
                if self.player.state() == 1:
                    self.player.pause()
                    print(self.player.state())
                else:
                    self.player.play()
                    print(self.player.state())

    def get_video_information(self, videoname):
        """获取视频信息"""
        try:
            self.info_finder = subprocess.Popen(
                '"' + self.f_path + r'\ffprobe" -print_format json -show_streams -loglevel quiet "' + str(
                    videoname) + '"',
                shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
            inf = self.info_finder.stdout.read()
            if len(inf)!=0:
                info = json.loads(inf, encoding='utf-8')
            else:
                raise Exception
        except:
            print("error: ffprobe 解析视频信息出错,请传入正确的ffmpeg路径到ffmpegpath参数,或使用其他方法获取视频详细信息\n", sys.exc_info())

        try:
            self.duration_ts = float(info['streams'][0]['duration']) * 1000
        except:
            print("error: 未获取到视频信息,视频时长已设置为9999")
            self.duration_ts = 99999
        print(self.duration_ts, 'duration_ts')
        try:
            if not self.isFullScreen():
                if info['streams'][0]['height'] > QApplication.desktop().height() * 4 / 5:
                    self.resize(info['streams'][0]['width'] * 4 / 5, info['streams'][0]['height'] * 4 / 5)
                else:
                    self.resize(info['streams'][0]['width'], info['streams'][0]['height'])
                self.move((QApplication.desktop().width() - self.width()) // 2,
                          (QApplication.desktop().height() - self.height()) // 2)
        except:
            pass
        self.playQSlider.setRange(0, self.duration_ts)
        print("总时长:",time.strftime("%H:%M:%S", time.gmtime(self.duration_ts / 1000)))
        self.time_label.setText('00:00:00/{0}'.format(time.strftime("%H:%M:%S", time.gmtime(self.duration_ts / 1000))))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.resize_all()

    def closeEvent(self, e):
        self.player.stop()
        # self.hide()
        # e.ignore()
        super(JamVideoWidget, self).closeEvent(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    videowidget = JamVideoWidget()
    # videowidget = JamVideoWidget(playlist=['0.mp4', '1.mp4', '2.mp4', '3.mp4'],ffmpegpath=r'D:\python_work\Jamtools\bin')#传入playlist参数为播放路径列表

    videowidget.show()
    sys.exit(app.exec_())
