import icons
import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QDesktopWidget
from PyQt5.QtGui import QIcon
import siui
from siui.core import SiColor, SiGlobal
from siui.templates.application.application import SiliconApplication
from siui.templates.application.components.page_view.page_view import PageView, PageButton

siui.core.globals.SiGlobal.siui.loadIcons(
    icons.IconDictionary(color=SiGlobal.siui.colors.fromToken(SiColor.SVG_NORMAL)).icons
)

# 导入窗口重写
from rewrite_window import RewriteWindow

# 导入组件
import components

class MySiliconApp(SiliconApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        screen_geo = QDesktopWidget().screenGeometry()  # 获取屏幕尺寸
        self.setMinimumSize(1024, 380)
        self.resize(1366, 916)
        self.move((screen_geo.width() - self.width()) // 2, (screen_geo.height() - self.height()) // 2)

        # 设置窗口
        self.setWindowTitle('PyQt Silicon - UI 首选')
        self.setWindowIcon(QIcon('./img/avatar1.png'))
        # 窗口无边框化
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setContentsMargins(0, 0, 0, 0)
        # 重写窗口
        #self.rewrite_window = RewriteWindow(self) # 报错弃用

        # 导入TopBar
        self.top_bar = components.TopBar(self)

        self.layerMain().page_view.page_navigator.container.addPlaceholder(8)
        self.layerMain().page_view.page_navigator.container.setSpacing(8)

        # 添加页面
        self.home_page = components.PageHome(self)
        self.layerMain().addPage(self.home_page,
                                icon=SiGlobal.siui.iconpack.get("ic_fluent_home_filled"),
                                hint="主页",
                                side="top"
                                )
        
        self.questionnaire_page = components.PageQuestionnaire(self)
        self.layerMain().addPage(self.questionnaire_page,
                                icon=SiGlobal.siui.iconpack.get("ic_fluent_text_bullet_list_square_filled"),
                                hint="问卷管理",
                                side="top"
                                )

        self.need_change = False

        self.questionnaire_page.questionnaire_list_card.databaseChanged.connect(self._data_changed)
        homepage_btn: PageButton = self.layerMain().page_view.page_navigator.buttons[0]
        homepage_btn.activated.connect(self._on_to_home_page)
        # self.questionnaire_page.questionnaire_list_card.databaseChanged.connect(lambda _: self.home_page.data_widgets.left_bottom_card.updateTable())
        # self.questionnaire_page.questionnaire_list_card.databaseChanged.connect(lambda _: self.home_page.data_widgets.right_top_card.updateTable())

        self.layerMain().setPage(0) # 显示主页
        SiGlobal.siui.reloadAllWindowsStyleSheet()

    def _data_changed(self, _):
        self.need_change = True
        self.home_page.data_widgets.left_top_card.on_database_changed(0)

    def _on_to_home_page(self):
        if self.need_change:
            self.need_change = False
            self.home_page.data_widgets.left_top_card.__emit__()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MySiliconApp()
    window.show()

    wait_time = 500 # 延时执行加载任务
    while wait_time > 0:
        app.processEvents()
        wait_time -= 1

    window.home_page.data_widgets.left_bottom_card.updateTable() # 更新左下卡片
    window.home_page.data_widgets.right_top_card.updateTable() # 更新右上卡片
    window.home_page.data_widgets.button_card.updateTabel() # 更新底部卡片

    sys.exit(app.exec_())