from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor

from siui.components.widgets import (
    SiSimpleButton,
)
from siui.components.option_card import SiOptionCardPlane
from siui.core import SiGlobal

import threading

from .sidebar_message.SideBarMessage import SideBarMessage

from .MyCapsuleButton import MyCapsuleButton
from .MyTable import MyTable

from ..data.effectiveness import Effectiveness, EffectivenessDatas
from ..child_window.filter_window import FilterChildWindowQuestionNumber
from ..manager.table_manager import TableManager

from scripts.database import Database, QuestionnaireScores, QuestionnaireFilterData
from scripts.questions import Questions

class RightTopCard(SiOptionCardPlane):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = Database() # 数据库管理类
        self.questions = Questions() # 问卷管理类
        self.sidebarMsg = SideBarMessage() # 侧边栏消息

        self.questionnaire_filter_data: QuestionnaireFilterData = self.database.getDefaultQuestionnaireFilterData() # 问卷筛选条件
        self.question_number_filter_data: list[int] = self.questions.getDimensionQuestionsIDs("knowledge") + self.questions.getDimensionQuestionsIDs("attitude") + self.questions.getDimensionQuestionsIDs("behavior") + self.questions.getDimensionQuestionsIDs("health_status") # 题目题号筛选数据

        # 用于持有当前正在运行的 Effectiveness 实例，防止被回收导致线程提前销毁
        self._current_effectiveness = None

        self.setFixedSize(620, 540+180+16) # 设置固定大小
        self.setTitle("效度分析") # 设置标题

        # Header筛选按钮
        self.filter_btn = SiSimpleButton(self)
        self.filter_btn.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_filter_add_regular"))
        self.filter_btn.resize(32, 32)
        self.filter_btn.setHint("设置参与分析的题目")
        self.filter_btn.clicked.connect(self.show_filter_window)

        self.refilter_btn = SiSimpleButton(self)
        self.refilter_btn.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_filter_sync_filled"))
        self.refilter_btn.resize(32, 32)
        self.refilter_btn.setHint("重置筛选")
        self.refilter_btn.clicked.connect(self.initFilters)

        self.header().addWidget(self.refilter_btn, "right")
        self.header().addWidget(self.filter_btn, "right")

        self.table_managed = MyTable(self)
        self.table_managed.resize(600-32, 500)
        self.table_managed.setManager(TableManager(self.table_managed))
        # 添加列
        self.table_managed.addColumn("问题序号", 60, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("", 40, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("因子 1", 64, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("因子 2", 64, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("因子 3", 64, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("因子 4", 64, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("", 40, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("共同度", 40, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.init_Rows()

        # self.table_managed.addRow(data=["#1", "", "0.6", "0.5", "0.4", "0.3", "", "0.2"])

        self.kmo_btn = MyCapsuleButton(self)        # KMO值
        self.bartlett_btn = MyCapsuleButton(self)   # Bartlett值
        self.p_btn = MyCapsuleButton(self)          # p值

        # KMO值
        self.kmo_btn.setText(" KMO ")
        self.kmo_btn.setFixedSize(160, 40)
        self.kmo_btn.setColorWhen(0.8, 1, QColor("#61FC61"))
        self.kmo_btn.setColorWhen(0.7, 0.8, QColor("#76EAFF"))
        self.kmo_btn.setColorWhen(0.6, 0.7, QColor("#FFC266"))
        self.kmo_btn.setColorWhen(0, 0.6, QColor("#FF684D"))
        self.kmo_btn.setValue(0) # 设置数值
        self.kmo_btn.setToolTip("KMO值：\n  >0.8       非常适合提取信息（非常好）\n  0.7~0.8  适合提取信息（较好）\n  0.6~0.7  比较适合提取信息（一般）\n  <0.6       不适合提取信息（差）")

        # Bartlett值
        self.bartlett_btn.setText("Bartlett 球形值")
        self.bartlett_btn.setFixedSize(240, 40)
        self.bartlett_btn.setThemeColor(QColor("#76EAFF"))
        self.bartlett_btn.setValue(0) # 设置数值
        self.bartlett_btn.setToolTip("Bartlett 球形值（近似卡方）：\n  对应P值小于0.05即可说明适合进行因子分析")

        # p值
        self.p_btn.setText(" p值   ")
        self.p_btn.setFixedSize(160, 40)
        self.p_btn.setColorWhen(0.05, 1, QColor("#61FC61"))
        self.p_btn.setColorWhen(0.05, float('inf'), QColor("#FFC266"))
        self.p_btn.setValue(0) # 设置数值
        self.p_btn.setToolTip("p值：\n  小于0.05说明有效度")

        self.body().setAdjustWidgetsSize(True)
        self.body().addWidget(self.table_managed)
        self.body().addWidget(self.kmo_btn)
        self.body().addWidget(self.bartlett_btn)
        self.body().addWidget(self.p_btn)
        self.body().adjustSize()

    def clear(self):
        '''
        清空页面数据
        '''
        # 删除原有UI
        try:
            self.table_managed.setVisible(False)
            # 删除上一个addPlaceholder
            self.body().removeWidget(self.table_managed)
            self.body().removeWidget(self.kmo_btn)
            self.body().removeWidget(self.bartlett_btn)
            self.body().removeWidget(self.p_btn)
        except:
            pass

        # 重新添加UI
        self.table_managed = MyTable(self)
        self.table_managed.resize(600-32, 500)
        self.table_managed.setManager(TableManager(self.table_managed))
        # 添加列
        self.table_managed.addColumn("问题序号", 60, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("", 40, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("因子 1", 64, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("因子 2", 64, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("因子 3", 64, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("因子 4", 64, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("", 40, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("共同度", 40, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.init_Rows()

        self.kmo_btn.setValue("nan")
        self.bartlett_btn.setValue("nan")
        self.p_btn.setValue("nan")

        self.body().addWidget(self.table_managed)
        self.table_managed.show()
        self.table_managed.reloadStyleSheet()
        self.body().addWidget(self.kmo_btn)
        self.body().addWidget(self.bartlett_btn)
        self.body().addWidget(self.p_btn)
        self.body().adjustSize()

    def update(self, effectiveness_datas: EffectivenessDatas, questions: list[str] | None=None):
        '''
        更新页面数据

        @param effectiveness_datas: 效度分析结果
        @param questions: 题目列表
        '''

        dimensions = effectiveness_datas.dimensions
        factors = [data.factors for data in effectiveness_datas.effectiveness_datas]
        common_factors = [data.commonness for data in effectiveness_datas.effectiveness_datas]
        kmo = effectiveness_datas.kmo
        bartlett = effectiveness_datas.bartlett
        p = effectiveness_datas.p

        if questions is None or dimensions is None or factors is None or common_factors is None:
            self.clear()
            return None

        # 删除原有UI
        self.table_managed.setVisible(False)
        self.body().removeWidget(self.table_managed)
        self.body().removeWidget(self.kmo_btn)
        self.body().removeWidget(self.bartlett_btn)
        self.body().removeWidget(self.p_btn)
        try:
            old_table = getattr(self, "table_managed", None)
            if old_table is not None:
                self.body().removeWidget(old_table)
                old_table.setParent(None)
                old_table.deleteLater()
        except Exception:
            pass
        try:
            for w in (self.kmo_btn, self.bartlett_btn, self.p_btn):
                self.body().removeWidget(w)
        except Exception:
            pass

        # 重新添加UI
        self.table_managed = MyTable(self)
        self.table_managed.resize(600-32, 500)
        table_manager = TableManager(self.table_managed)
        table_manager.setDimensionsNum(len(dimensions)) # 设置维度数量
        self.table_managed.setManager(table_manager)

        # 计算每个因子UI的长度
        factor_width: int = 64 # 256 // len(dimensions)
        data_name_dict = {
            "knowledge": "知识",
            "attitude": "态度",
            "behavior": "行为",
            "health_status": "健康状况"
        }
        # 添加列
        self.table_managed.addColumn("问题序号", 60, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("", 40, 40, Qt.AlignLeft | Qt.AlignVCenter)
        for i in range(len(dimensions)):
            name = data_name_dict.get(dimensions[i], f"因子 {str(i+1)}")
            self.table_managed.addColumn(name, factor_width, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("", 40, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.addColumn("共同度", 40, 40, Qt.AlignLeft | Qt.AlignVCenter)
        self.table_managed.init_Rows()

        # 填充数据
        for i, question in enumerate(questions):
            row_data = [question, "", *[f"{float(j):.3f}" for j in factors[i]], "", f"{float(common_factors[i]):.3f}"]
            self.table_managed.addRow(data=row_data)

        self.sidebarMsg.sendMessage(
            title="效度分析",
            text="效度分析完成",
            msg_type="success",
            fold_after=4
        )

        self.kmo_btn.setValue(float(f"{kmo:.5f}"))
        self.bartlett_btn.setValue(float(f"{bartlett:.5f}"))
        self.p_btn.setValue(float(f"{p:.5f}"))
        self.body().addWidget(self.table_managed)
        self.table_managed.show()
        self.table_managed.reloadStyleSheet()
        self.body().addWidget(self.kmo_btn)
        self.body().addWidget(self.bartlett_btn)
        self.body().addWidget(self.p_btn)
        self.body().adjustSize()

    def updateTable(self):
        '''
        更新表格，重新计算效度分析
        '''
        # 处理筛选
        # 经过筛选条件的问卷
        filtered_data: list[list] | None = self.database.getQuestionDataByFilters(self.questionnaire_filter_data)
        filtered_data_scores_list: list[QuestionnaireScores] = []
        if not len(filtered_data) == 0:
            for data in filtered_data:
                scores: QuestionnaireScores = self.database.getQuestionnairesScores(int(data[0]))
                filtered_data_scores_list.append(scores)
        else:
            self.clear()
            return None

        scores_list: list[list[int]] = []
        for scores in filtered_data_scores_list:
            scores_list.append(scores.getIDsScores(self.question_number_filter_data)) # 根据题目ID列表获取分数列表

        if not self.question_number_filter_data or len(self.question_number_filter_data) == 0:
            self.sidebarMsg.sendMessage(
                title="筛选为空",
                text="未选择任何题目，请先选择题目再进行效度分析。",
                msg_type="warning",
                fold_after=3
            )
            self.clear()
            return

        if not scores_list or all(len(s) == 0 for s in scores_list):
            self.sidebarMsg.sendMessage(
                title="数据不足",
                text="没有可用的题目分数进行效度分析。",
                msg_type="warning",
                fold_after=3
            )
            self.clear()
            return

        # 保存 Effectiveness 实例到 self，避免在分析进行时被垃圾回收
        # 如果已有正在运行的实例，先尝试停止然后替换
        if getattr(self, "_current_effectiveness", None) is not None:
            try:
                self._current_effectiveness.stopEffectiveness()
            except Exception:
                pass
            self._current_effectiveness = None

        effectiveness = Effectiveness(self.question_number_filter_data, scores_list)
        self._current_effectiveness = effectiveness

        # 结束/出错时的清理函数
        def _clear_and_handle_error(wm=None):
            # 清理持有的 Effectiveness 引用
            try:
                self._current_effectiveness = None
            except Exception:
                pass
            # 如果是错误信号，可显示侧边栏消息
            if wm is not None:
                self.sidebarMsg.sendMessage(
                    title="效度分析错误",
                    text=str(getattr(wm, "message", wm)).replace("\n", ""),
                    msg_type="error",
                    fold_after=4
                )

        # 成功时更新 UI 并清理引用
        def _on_finish(effectiveness_datas: EffectivenessDatas):
            try:
                # questions 传入题号列表（保持原来行为）
                self.update(effectiveness_datas, self.question_number_filter_data)
            finally:
                _clear_and_handle_error()

        effectiveness.signals.finish.connect(_on_finish)
        effectiveness.signals.error.connect(_clear_and_handle_error)

        # 启动异步分析
        effectiveness.getEffectivenessDatas()

    def show_filter_window(self):
        '''
        显示筛选窗口
        '''
        child_window = FilterChildWindowQuestionNumber(self)
        if not self.question_number_filter_data is None:
            question_number_filter_data_str = [str(i) for i in self.question_number_filter_data]
            child_window.setInitData(question_number_filter_data_str) # 设置初始数据
        child_window.dataConfirmed.connect(self.on_filter_result) # 用pyqtSignal进行反馈
        SiGlobal.siui.windows["MAIN_WINDOW"].layerChildPage().setChildPage(child_window)

    def on_uplevel_filter_updated(self, data: QuestionnaireFilterData):
        '''
        当上一级筛选条件更新时调用
        '''
        if not data is None:
            self.questionnaire_filter_data = data
            self.updateTable()

    def on_filter_result(self, data: list[str]):
        '''
        处理筛选结果
        '''
        if not data is None:
            # 将字符串int化
            try:
                data = [int(i) for i in data]
                self.question_number_filter_data = data
                self.updateTable()
            except Exception as e:
                print("on_filter_result 报错:", e)
                self.sidebarMsg.sendMessage(
                    title="数据错误",
                    text=str(e).replace("\n", ""), 
                    msg_type="error",
                    fold_after=4
                )

    def initFilters(self, _: int):
        '''
        初始化筛选条件
        @para _: 无用参数
        '''
        self.question_number_filter_data = self.questions.getDimensionQuestionsIDs("knowledge") + self.questions.getDimensionQuestionsIDs("attitude") + self.questions.getDimensionQuestionsIDs("behavior") + self.questions.getDimensionQuestionsIDs("health_status")
        self.updateTable()