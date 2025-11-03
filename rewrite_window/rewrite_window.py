# 用于重写根窗口的部分函数
# 例如：侧边拖动调节大小
import typing
from PyQt5 import QtGui, QtCore
from siui.templates.application.application import SiliconApplication

class RewriteWindow:
    def __init__(self, app: (SiliconApplication)):
        super().__init__()
        self.app = app

        # 判断窗口侧边的像素范围
        self.side_pixel = 2
        self.is_changing_size = False

        # 重写窗口的鼠标事件
        #self.app.layerMain().mouseMoveEvent = self.mouseMoveEvent
        #self.app.layerMain().mouseReleaseEvent = self.mouseReleaseEvent

    def mouseMoveEvent(self, event: typing.Optional[QtGui.QMouseEvent]):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            # 判断鼠标是否在窗口的侧边
            if event.pos().x() <= self.side_pixel or event.pos().x() >= self.app.layerMain().width() - self.side_pixel:
                self.is_changing_size = True
                self.app.layerMain().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeHorCursor))
                # 计算窗口的新尺寸
                now_size = self.app.layerMain().size()
                # 鼠标移动的距离
                move_distance = event.pos().x() - self.side_pixel
                if event.pos().x() <= self.side_pixel:
                    new_width = now_size.width() - move_distance
                    if new_width >= 100:
                        self.app.resize(new_width, now_size.height())
                else:
                    new_width = now_size.width() + move_distance
                    if new_width >= 100:
                        self.app.resize(new_width, now_size.height())
            elif event.pos().y() <= self.side_pixel or event.pos().y() >= self.app.layerMain().height() - self.side_pixel:
                self.is_changing_size = True
                self.app.layerMain().setMouseTracking(True) # 鼠标跟踪
                # 计算窗口的新尺寸
                now_size = self.app.layerMain().size()
                # 鼠标移动的距离
                move_distance = event.pos().y() - self.side_pixel
                if event.pos().y() <= self.side_pixel:
                    new_height = now_size.height() - move_distance
                    if new_height >= 100:
                        self.app.resize(now_size.width(), new_height)
                else:
                    new_height = now_size.height() + move_distance
                    if new_height >= 100:
                        self.app.resize(now_size.width(), new_height)

    def mouseReleaseEvent(self, event: typing.Optional[QtGui.QMouseEvent]):
        if self.is_changing_size:
            self.is_changing_size = False
            self.app.layerMain().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            self.app.layerMain().setMouseTracking(False) # 鼠标不跟踪