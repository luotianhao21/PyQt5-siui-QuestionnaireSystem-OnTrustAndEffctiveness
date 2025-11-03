import icons
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5 import QtGui
import siui
from siui.core import SiColor, SiGlobal, GlobalFont, Si
from siui.templates.application.application import SiliconApplication
from siui.templates.application.components.layer.layer_main.layer_main import LayerMain
from siui.components.button import SiPushButtonRefactor
from siui.gui import SiFont
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel,
    SiLineEdit,
    SiLongPressButton,
    SiPushButton,
    SiSimpleButton,
    SiSwitch,
)
import typing
siui.core.globals.SiGlobal.siui.loadIcons(
    icons.IconDictionary(color=SiGlobal.siui.colors.fromToken(SiColor.SVG_NORMAL)).icons
)
import fonts

class TopBar:
    def __init__(self, app: (SiliconApplication)):
        super().__init__() # 调用父类构造函数

        self.app = app
        self.layer_main = self.app.layerMain()
        self.drag_start_position = QtCore.QPoint()
        self.app_min_button_color = "#8892EC"
        self.app_max_button_color = "#98F5E1"
        self.app_close_button_color = "#EC88AE"
        self.top_bar_btn_size = 64
        
        # 设置窗口TopBar
        self.layer_main.app_title.setText("Questionnaire System")
        self.layer_main.app_title.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        self.layer_main.app_title.setMinimumWidth(300) # 设置最小宽度
        self.layer_main.app_title.setFont(SiFont.tokenized(GlobalFont.M_BOLD)) # 设置字体
        self.layer_main.app_title.setFixedHeight(32) # 固定高度
        self.layer_main.app_icon.load("./img/avatar1.png")
        self.layer_main.app_icon.moveTo(11, 16)
        self.layer_main.app_icon.setFixedSize(38, 38)
        
        # 重写self.layer_main.layerMain().container_title的鼠标事件
        self.layer_main.container_title.mouseDoubleClickEvent = self.toggleMaximized # 双击标题栏最大化/还原窗口
        self.layer_main.container_title.mousePressEvent = self.mousePressEvent
        self.layer_main.container_title.mouseMoveEvent = self.mouseMoveEvent
        self.layer_main.container_title.mouseReleaseEvent = self.mouseReleaseEvent

        # 设置TopBar的三个按钮
        # 最小化按钮
        self.app_min_button = SiSimpleButton(self.app)
        self.app_min_button.setToolTip("最小化")
        self.app_min_button.resize(self.top_bar_btn_size, self.top_bar_btn_size)
        # 最大化按钮
        self.app_max_button = SiSimpleButton(self.app)
        self.app_max_button.setToolTip("最大化")
        self.app_max_button.resize(self.top_bar_btn_size, self.top_bar_btn_size)
        # 关闭按钮
        self.app_close_button = SiSimpleButton(self.app)
        self.app_close_button.setToolTip("关闭")
        self.app_close_button.resize(self.top_bar_btn_size, self.top_bar_btn_size)
        # 按钮图标
        self.app_min_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_line_horizontal_1_filled", self.app_min_button_color))
        self.app_max_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_maximize_filled", self.app_max_button_color))
        self.app_close_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_dismiss_filled", self.app_close_button_color))
        # 按钮位置
        #self.layer_main.container_title.addPlaceholder(0, "right")
        self.layer_main.container_title.addWidget(self.app_close_button, "right")
        #self.layer_main.container_title.addPlaceholder(0, "right")
        self.layer_main.container_title.addWidget(self.app_max_button, "right")
        #self.layer_main.container_title.addPlaceholder(0, "right")
        self.layer_main.container_title.addWidget(self.app_min_button, "right")
        # 绑定按钮事件
        self.app_min_button.clicked.connect(self.app.showMinimized)
        self.app_max_button.clicked.connect(self.toggleMaximized)
        self.app_close_button.clicked.connect(self.app.close)

    def toggleMaximized(self, event: typing.Optional[QtGui.QMouseEvent]):
        # 判断双击的按键是否为左键
        try:
            if not event.button() == Qt.MouseButton.LeftButton:
                return
        except:
            event = event
        if self.app.isMaximized():
            self.app.showNormal()
            self.app_max_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_maximize_filled", self.app_max_button_color))
        else:
            self.app.showMaximized()
            self.app_max_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_minimize_filled", self.app_max_button_color))

    def mousePressEvent(self, event: typing.Optional[QtGui.QMouseEvent]):
        # 鼠标左键按下时记录鼠标位置
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPos() - self.app.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: typing.Optional[QtGui.QMouseEvent]):
        # 鼠标左键按下后移动窗口
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.app.isMaximized():
                # 当窗口最大化时，鼠标移动窗口后缩小窗口
                # 记录鼠标位置
                position = event.globalPos() - self.app.frameGeometry().topLeft()
                max_size = self.app.screen().size()
                self.app.showNormal() # 还原窗口
                # 按照比例计算常规窗口的位置
                normal_window_position = QtCore.QPoint(
                    int(event.globalPos().x() - position.x() * self.app.width() / max_size.width()),
                    int(event.globalPos().y() - position.y() * self.app.height() / max_size.height())
                )
                self.app_max_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_arrow_maximize_filled"))
                # 移动窗口到位置
                self.app.move(normal_window_position)
                self.drag_start_position = event.globalPos() - self.app.frameGeometry().topLeft()
                event.accept()
            else:
                self.app.move(event.globalPos() - self.drag_start_position)
                event.accept()

    def mouseReleaseEvent(self, event: typing.Optional[QtGui.QMouseEvent]):
        # 鼠标左键释放时恢复窗口
        if event.button() == Qt.MouseButton.LeftButton:
            event.accept()