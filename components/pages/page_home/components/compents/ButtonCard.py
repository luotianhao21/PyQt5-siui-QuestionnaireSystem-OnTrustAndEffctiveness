from PyQt5.QtWidgets import QSizePolicy, QBoxLayout
from PyQt5.QtCore import QPoint, QPointF, Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QColor

from siui.core import SiGlobal
from siui.components.option_card import SiOptionCardPlane
from siui.components.widgets import (
    SiDenseVContainer,
    SiSimpleButton,
)

from .MyTable import MyTable
from .MyCapsuleButton import MyCapsuleButton
from ..child_window.filter_window import K2FilterDimensionChildWindow
from ..data.K2DataClass import K2DataSignal, K2DataWorker, K2Data, K2ReturnData
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

        self._current_k2 = None

        self.questionnaire_filter_data: QuestionnaireFilterData = self.database.getDefaultQuestionnaireFilterData() # 问卷筛选条件

        self.dimensions_filter_data = self.database.getDefaultK2DimensionFilters() # 第二~第四维度["知识维度", "信念维度", "行为维度"]

        self.setFixedSize(800, 620)  # 设置固定大小 1175
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
        self.table.addColumn("口腔状况   \\   知信行", 160, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.addColumn("合格", 180, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.addColumn("不合格", 180, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.addColumn("合计", 120, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.init_Rows()

        self.k2_btn = MyCapsuleButton(self) # 卡方
        self.df_btn = MyCapsuleButton(self) # 自由度
        self.p_value = MyCapsuleButton(self) # p值(a)

        self.k2_btn.setText(" 卡方值 χ² ")
        self.k2_btn.setValue("nan")
        self.k2_btn.setToolTip(f"卡方检验：\n"
                               f"   自由度 1：α=0.05 时，临界值为 3.841\n"
                               f"   自由度 2：α=0.01 时，临界值为 9.210\n"
                               f"   自由度 5：α=0.10 时，临界值为 9.236")
        self.k2_btn.adjustSize()

        self.df_btn.setText(" 自由度 df ")
        self.df_btn.setValue("nan")
        self.df_btn.setToolTip(f"df = (rows-1) * (columns-1)")
        self.df_btn.adjustSize()

        self.p_value.setText(" p值（α=） ")
        self.p_value.setValue("nan")
        self.p_value.adjustSize()

        self.body().addWidget(self.table)
        self.body().addWidget(self.k2_btn)
        self.body().addWidget(self.df_btn)
        self.body().addWidget(self.p_value)
        self.body().adjustSize()

    def clear(self):
        self.table.setVisible(False)
        self.body().removeWidget(self.table)
        self.body().removeWidget(self.k2_btn)
        self.body().removeWidget(self.df_btn)
        self.body().removeWidget(self.p_value)

        # 初始化表格
        self.table = MyTable(self)
        self.table.resize(800 - 32 - 20, 400)
        self.table.setManager(ButtonCardK2Table(self.table))
        self.table.addColumn("口腔状况   \\   知信行", 160, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.addColumn("合格", 180, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.addColumn("不合格", 180, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.addColumn("合计", 120, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.init_Rows()

        self.k2_btn.setValue("nan")
        self.df_btn.setValue("nan")
        self.p_value.setValue("nan")

        self.k2_btn.adjustSize()
        self.df_btn.adjustSize()
        self.p_value.adjustSize()

        self.body().addWidget(self.table)
        self.table.show()
        self.table.reloadStyleSheet()
        self.body().addWidget(self.k2_btn)
        self.body().addWidget(self.df_btn)
        self.body().addWidget(self.p_value)
        self.body().adjustSize()

    def update(self, k2data: K2ReturnData):
        """
        更新页面
        """
        self.table.setVisible(False)
        self.body().removeWidget(self.table)
        self.body().removeWidget(self.k2_btn)
        self.body().removeWidget(self.df_btn)
        self.body().removeWidget(self.p_value)

        # 初始化表格
        self.table = MyTable(self)
        self.table.resize(800 - 32 - 20, 400)
        self.table.setManager(ButtonCardK2Table(self.table))
        self.table.addColumn("口腔状况   \\   知信行", 160, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.addColumn("合格", 180, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.addColumn("不合格", 180, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.addColumn("合计", 120, 40, Qt.AlignCenter | Qt.AlignVCenter)
        self.table.init_Rows()

        _3_dimensions_status = ["优秀", "良好", "不及格", "合计"]
        try:
            for i, row in enumerate(k2data.getShowTable()):
                # 在row最前面加_3_dimensions_status[i]
                row_copy = [_3_dimensions_status[i], *[str(j) for j in row]]
                self.table.addRow(data=row_copy)
        except Exception as e:
            self.sidebarMsg.sendMessage(
                title="卡方检验",
                text=str(e),
                msg_type="error",
            )
            return
        self.sidebarMsg.sendMessage(
            title="卡方检验",
            text="卡方检验成功",
            msg_type="success",
            fold_after=4
        )

        self.k2_btn.setValue(k2data.chi2)
        self.df_btn.setValue(k2data.df)
        self.p_value.setValue(round(k2data.p_value, 4))

        self.k2_btn.adjustSize()
        self.df_btn.adjustSize()
        self.p_value.adjustSize()

        self.body().addWidget(self.table)
        self.table.show()
        self.table.reloadStyleSheet()
        self.body().addWidget(self.k2_btn)
        self.body().addWidget(self.df_btn)
        self.body().addWidget(self.p_value)
        self.body().adjustSize()

    def updateTabel(self):
        """
        更新表格
        """

        if not self.dimensions_filter_data or len(self.dimensions_filter_data) == 0:
            self.sidebarMsg.sendMessage(
                title="筛选为空",
                text="未选择任何题目，请先选择题目再进行效度分析。",
                msg_type="warning",
                fold_after=3
            )
            self.clear()
            return
        # 保存 K2Data 实例到 self，避免在分析进行时被垃圾回收
        # 如果已有正在运行的实例，先尝试停止然后替换
        if getattr(self, "_current_k2", None) is not None:
            try:
                self._current_k2.stopEffectiveness()
            except Exception:
                pass
            self._current_k2 = None
        k2= K2Data()
        self._current_k2 = k2
        def _clear_and_handle_error(wm=None):
            # 清理持有的 Effectiveness 引用
            try:
                self._current_k2 = None
            except Exception:
                pass
            # 如果是错误信号，可显示侧边栏消息
            if wm is not None:
                self.sidebarMsg.sendMessage(
                    title="卡方分析错误",
                    text=str(getattr(wm, "message", wm)).replace("\n", ""),
                    msg_type="error",
                    fold_after=4
                )
                self.clear()

        # 成功时更新 UI 并清理引用
        def _on_finish(k2data: K2ReturnData):
            try:
                self.update(k2data)
            finally:
                _clear_and_handle_error()

        k2.signals.finish.connect(_on_finish)
        k2.signals.error.connect(_clear_and_handle_error)

        # 启动异步
        k2.getK2(self.dimensions_filter_data, self.questionnaire_filter_data)

    def on_filter_applied(self, filter_data: list):
        if not filter_data is None:
            try:
                self.dimensions_filter_data = filter_data
                self.updateTabel()
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

    def on_uplevel_filter_updated(self, data: QuestionnaireFilterData):
        '''
        当上一级筛选条件更新时调用
        '''
        if not data is None:
            self.questionnaire_filter_data = data
            try:
                self.updateTabel()
            except Exception as e:
                print(e)