from siui.components.page import SiPage
from siui.components import SiPixLabel
from siui.components.option_card import SiOptionCardLinear, SiOptionCardPlane
from siui.templates.application.application import SiliconApplication
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.core import GlobalFont, Si, SiColor, SiGlobal
from siui.components.slider import SiSliderH
from siui.gui import SiFont
from PyQt5.QtCore import Qt
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
from siui.components.progress_bar import SiProgressBar

from .components.themed_option_card import ThemedOptionCardPlane
from .components.data_widgets import DataWidgets

class PageHome(SiPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.app = app

        # 整个滚动区域
        self.scroll_container = SiTitledWidgetGroup(self)

        # 整个顶部
        self.head_area = SiLabel(self)
        self.head_area.setFixedHeight(450)

        # 创建背景底图和渐变
        self.background_image = SiPixLabel(self.head_area)
        self.background_image.setFixedSize(1366, 300)
        self.background_image.setBorderRadius(6)
        self.background_image.load("./img/homepage_background.png")

        self.background_fading_transition = SiLabel(self.head_area)
        self.background_fading_transition.setGeometry(0, 100, 0, 200)
        self.background_fading_transition.setStyleSheet(
            """
            background-color: qlineargradient(x1:0, y1:1, x2:0, y2:0, stop:0 {}, stop:1 {})
            """.format( SiGlobal.siui.colors["INTERFACE_BG_B"],
                        SiColor.trans(SiGlobal.siui.colors["INTERFACE_BG_B"], 0))
        )

        # 创建大标题和副标题
        self.title = SiLabel(self.head_area)
        self.title.setGeometry(64, 0, 500, 128)
        self.title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.title.setText("调查问卷 | 主页")
        self.title.setStyleSheet("color: {}".format(SiGlobal.siui.colors["TEXT_A"]))
        self.title.setFont(SiFont.tokenized(GlobalFont.XL_BOLD))

        self.subtitle = SiLabel(self.head_area)
        self.subtitle.setGeometry(64, 72, 500, 48)
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.subtitle.setText("一个基于PyQt-SiliconUI的调查问卷管理器，可快速计算多种指标")
        self.subtitle.setStyleSheet("color: {}".format(SiColor.trans(SiGlobal.siui.colors["TEXT_A"], 0.9)))
        self.subtitle.setFont(SiFont.tokenized(GlobalFont.S_DEMI_BOLD))

        # 创建一个水平容器
        self.container_for_cards = SiDenseHContainer(self.head_area)
        self.container_for_cards.move(0, 130)
        self.container_for_cards.setFixedHeight(310)
        self.container_for_cards.setAlignment(Qt.AlignCenter)
        self.container_for_cards.setSpacing(32)

        # 添加卡片
        self.option_card_project = ThemedOptionCardPlane(self)
        self.option_card_project.setTitle("SPSS 工具网站")
        self.option_card_project.setFixedSize(218, 270)
        self.option_card_project.setThemeColor("#4A70A1")
        self.option_card_project.setDescription(
            "点击下方链接即可进入SPSS 工具箱网站，里面有各种分数表格计算工具")
        self.option_card_project.setURL("https://spssau.com/index.html")

        self.option_card_example = ThemedOptionCardPlane(self)
        self.option_card_example.setTitle("PyQt-SiliconUI Gitee仓库")
        self.option_card_example.setFixedSize(300, 270)
        self.option_card_example.setThemeColor("#7573aa")
        self.option_card_example.setDescription(
            "点击下方链接进入该项目依赖的PyQt-SiliconUI的Gitee仓库，里面有丰富的示例代码")
        self.option_card_example.setURL("https://github.com/ChinaIceF/PyQt-SiliconUI")

        # 添加到水平容器
        self.container_for_cards.addPlaceholder(64 - 32)
        self.container_for_cards.addWidget(self.option_card_project)
        self.container_for_cards.addWidget(self.option_card_example)

        # 添加到滚动区域容器
        self.scroll_container.addWidget(self.head_area)

        # 下方区域标签
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())

        # 下面的 titledWidgetGroups
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1]))
        self.titled_widget_group.move(64, 0)

        self.data_widgets = DataWidgets(self)
        self.titled_widget_group.setSpacing(16)
        self.titled_widget_group.addTitle("问卷分析")
        self.titled_widget_group.addWidget(self.data_widgets)
        self.titled_widget_group.addPlaceholder(42)

        # 添加到滚动区域容器
        self.body_area.setFixedHeight(self.titled_widget_group.height())
        self.scroll_container.addWidget(self.body_area)

        # 添加到页面
        self.setAttachment(self.scroll_container)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        self.body_area.setFixedWidth(w)
        self.background_image.setFixedWidth(w)
        self.background_fading_transition.setFixedWidth(w)
        self.titled_widget_group.setFixedWidth(min(w - 128, 1300))