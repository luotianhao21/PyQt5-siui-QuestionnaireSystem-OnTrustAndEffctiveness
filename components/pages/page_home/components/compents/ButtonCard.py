from PyQt5.QtWidgets import QSizePolicy, QBoxLayout
from PyQt5.QtCore import QPoint, QPointF, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor

from siui.core import SiGlobal
from siui.components.option_card import SiOptionCardPlane
from siui.components.widgets import (
    SiDenseVContainer,
    SiSimpleButton,
)

from .MyTable import MyTable
from ..child_window.filter_window import K2FilterDimensionChildWindow
from .table_managers.ButtonCardK2Table import ButtonCardK2Table

from components.pages.page_home.components.compents.sidebar_message.SideBarMessage import SideBarMessage
from scripts.database import Database, QuestionnaireScores, QuestionnaireFilterData
from scripts.questions import Questions

class ButtonCard(SiOptionCardPlane):

    # 卡方检验

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = Database() # 数据库管理类
        self.questions = Questions() # 问卷管理类
        self.sidebarMsg = SideBarMessage()  # 侧边栏消息

        self.dimensions_filter_data = self.database.getDefaultK2DimensionFilters() # 第二~第四维度["知识维度", "信念维度", "行为维度"]

        self.setFixedSize(800, 500)  # 设置固定大小 1175
        self.setTitle("卡方检验")  # 设置标题

        # Header筛选按钮
        self.filter_btn = SiSimpleButton(self)
        self.filter_btn.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_filter_add_regular"))
        self.filter_btn.resize(32, 32)
        self.filter_btn.setHint("设置参与分析的维度（知识、信念、行为）")
        self.filter_btn.clicked.connect(self.show_filter_window)

        self.header().addWidget(self.filter_btn, "right")

        # Body部分

        self.table = MyTable(self)
        self.table.resize(800 - 32 - 20, 400)
        self.table.setManager(ButtonCardK2Table(self.table))
        self.table.init_Rows()

        self.body().addWidget(self.table)

    def clear(self):
        self.table.setVisible(False)
        self.body().removeWidget(self.table)

        # 初始化表格
        self.table = MyTable(self)
        self.table.resize(800 - 32 - 20, 400)
        self.table.setManager(ButtonCardK2Table(self.table))
        self.table.init_Rows()

    def on_filter_applied(self, filter_data: list):
        if not filter_data is None:
            try:
                self.dimensions_filter_data = filter_data
            except Exception as e:
                print("on_filter_result 报错:", e)
                self.sidebarMsg.sendMessage(
                    title="数据错误",
                    text=str(e).replace("\n", ""),
                    msg_type="error",
                    fold_after=4
                )

    def show_filter_window(self):
        '''
        显示筛选窗口
        '''
        child_window = K2FilterDimensionChildWindow(self)
        if not self.dimensions_filter_data is None:
            child_window.setInitData(self.dimensions_filter_data)
        child_window.dataConfirmed.connect(self.on_filter_applied)
        SiGlobal.siui.windows["MAIN_WINDOW"].layerChildPage().setChildPage(child_window)