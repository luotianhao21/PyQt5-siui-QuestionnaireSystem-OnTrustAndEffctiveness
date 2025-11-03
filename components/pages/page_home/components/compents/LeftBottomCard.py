from PyQt5.QtWidgets import QSizePolicy, QBoxLayout
from PyQt5.QtCore import QPoint, QPointF, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor

from siui.core import SiGlobal
from siui.components.option_card import SiOptionCardPlane
from siui.components.widgets import (
    SiDenseVContainer,
    SiSimpleButton,
)

from .MyNavigationBarH import MyNavigationBarH
from .NavigationBarWidget import NavigationBarWidget
from .sidebar_message.SideBarMessage import SideBarMessage

from ..child_window.filter_window import FilterChildWindowQuestionNumber
from ..data.questiontrust import QuestionTrust 

from scripts.database import Database, QuestionnaireScores, QuestionnaireFilterData
from scripts.questions import Questions

class LeftBottomCard(SiOptionCardPlane):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = Database() # 数据库管理类
        self.questions = Questions() # 问卷管理类
        self.sidebarMsg = SideBarMessage() # 侧边栏消息

        self.questionnaire_filter_data: QuestionnaireFilterData = self.database.getDefaultQuestionnaireFilterData() # 问卷筛选条件
        self.question_number_filter_data: list[str] = self.questions.getDimensionQuestionsIDs("knowledge") + self.questions.getDimensionQuestionsIDs("attitude") + self.questions.getDimensionQuestionsIDs("behavior") + self.questions.getDimensionQuestionsIDs("health_status") # 题目题号筛选数据

        self.setFixedSize(540, 540) # 设置固定大小
        self.setTitle("信度分析") # 设置标题

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

        self.header().addWidget(self.refilter_btn, "right")
        self.header().addWidget(self.filter_btn, "right")

        self.v_container = SiDenseVContainer(self)
        self.v_container.setSpacing(8)
        self.v_container.setAdjustWidgetsSize(True)
        self.v_container.setFixedSize(540, 480)
        self.v_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # 顶边导航栏
        self.navigation_bar = MyNavigationBarH(self)
        self.navigation_bar.resize(480, 40)
        self.navigation_bar.addItems(["知信行三维度", "知识维度", "信念维度", "行为维度", "口腔健康"])

        # 每个导航项对应的组件
        # 知信行三维度
        self.kbb_three =  NavigationBarWidget(self)
        # 知识维度
        self.knowledge = NavigationBarWidget(self)
        # 信念维度
        self.belief = NavigationBarWidget(self)
        # 行为维度
        self.behavior = NavigationBarWidget(self)
        # 口腔健康维度
        self.oral_health = NavigationBarWidget(self)

        self.body().addWidget(self.navigation_bar)
        self.body().addPlaceholder(8)
        self.navigation_bar.setRootContainer(self.v_container) # 设置根容器为 v_container
        self.body().addWidget(self.v_container)
        self.navigation_bar.addItemWidget(0, self.kbb_three)
        self.navigation_bar.addItemWidget(1, self.knowledge)
        self.navigation_bar.addItemWidget(2, self.belief)
        self.navigation_bar.addItemWidget(3, self.behavior)
        self.navigation_bar.addItemWidget(4, self.oral_health)
        self.navigation_bar.setEnabledIndexOf(0)

    def show_filter_window(self):
        '''
        显示筛选窗口
        '''
        child_window = FilterChildWindowQuestionNumber(self)
        if not self.question_number_filter_data is None:
            # self.question_number_filter_data字符串化
            question_number_filter_data_str = [str(i) for i in self.question_number_filter_data]
            child_window.setInitData(question_number_filter_data_str) # 设置初始数据
        child_window.dataConfirmed.connect(self.on_filter_result)
        SiGlobal.siui.windows["MAIN_WINDOW"].layerChildPage().setChildPage(child_window)

    def updateTable(self) -> None:
        '''
        更新表格数据
        1. 计算各维度的Cronbach's Alpha系数
        2. 计算各维度的各题的CITC
        3. 计算各维度的各题的项已删除的α系数
        4. 显示结果
        '''
        # 处理筛选
        # 经过筛选条件的问卷
        filtered_data: list[list] | None = self.database.getQuestionDataByFilters(self.questionnaire_filter_data)
        filtered_data_scores_list: list[QuestionnaireScores] = []
        if not filtered_data is None:
            for data in filtered_data:
                scores: QuestionnaireScores = self.database.getQuestionnairesScores(int(data[0]))
                filtered_data_scores_list.append(scores)

        if len(filtered_data_scores_list) < 2:
            self.kbb_three.clear()
            self.knowledge.clear()
            self.belief.clear()
            self.behavior.clear()
            self.oral_health.clear()
            self.sidebarMsg.sendMessage(
                title="问卷数量不足",
                text="至少需要两个问卷",
                msg_type="error",
                fold_after=4
            )
            return None # 至少需要两个问卷

        # 为每个bar都定义其对应的题目分数列表并调用NavigationBarWidget中的更新表格函数进行计算并更新

        error_list: list[str] = [] # 错误提示列表

        # 知信行三维度
        # 获取知信行三维度的题目ID列表
        kbb_three_ids = self.questions.getDimensionQuestionsIDs("knowledge") + self.questions.getDimensionQuestionsIDs("attitude") + self.questions.getDimensionQuestionsIDs("behavior")
        # 将知信行三个维度与已经筛选的题目进行交集
        kbb_three_ids = list(set(kbb_three_ids) & set(self.question_number_filter_data))
        if len(kbb_three_ids) >= 3:
            # 将问卷分数列表进行处理
            kbb_three_scores_list: list[list[int]] = []
            for scores in filtered_data_scores_list:
                kbb_three_scores_list.append(scores.getIDsScores(kbb_three_ids)) # 根据题目ID列表获取分数列表
            # 创建知信行三维度的信度分析管理类
            kbb_three_trust = QuestionTrust(kbb_three_ids, kbb_three_scores_list)
            self.kbb_three.updateTable(kbb_three_trust)
        else:
            self.kbb_three.clear()
            error_list.append("知信行三维度")

        # 知识维度
        knowledge_ids = self.questions.getDimensionQuestionsIDs("knowledge")
        knowledge_ids = list(set(knowledge_ids) & set(self.question_number_filter_data))
        if len(knowledge_ids) >= 3:
            knowledge_scores_list: list[list[int]] = []
            for scores in filtered_data_scores_list:
                knowledge_scores_list.append(scores.getIDsScores(knowledge_ids)) # 根据题目ID列表获取分数列表
            knowledge_trust = QuestionTrust(knowledge_ids, knowledge_scores_list)
            self.knowledge.updateTable(knowledge_trust)
        else:
            self.knowledge.clear()
            error_list.append("知识维度")

        # 信念维度
        attitude_ids = self.questions.getDimensionQuestionsIDs("attitude")
        attitude_ids = list(set(attitude_ids) & set(self.question_number_filter_data))
        if len(attitude_ids) >= 3:
            attitude_scores_list: list[list[int]] = []
            for scores in filtered_data_scores_list:
                attitude_scores_list.append(scores.getIDsScores(attitude_ids)) # 根据题目ID列表获取分数列表
            attitude_trust = QuestionTrust(attitude_ids, attitude_scores_list)
            self.belief.updateTable(attitude_trust)
        else:
            self.belief.clear()
            error_list.append("信念维度")

        # 行为维度
        behavior_ids = self.questions.getDimensionQuestionsIDs("behavior")
        behavior_ids = list(set(behavior_ids) & set(self.question_number_filter_data))
        if len(behavior_ids) >= 3:
            behavior_scores_list: list[list[int]] = []
            for scores in filtered_data_scores_list:
                behavior_scores_list.append(scores.getIDsScores(behavior_ids)) # 根据题目ID列表获取分数列表
            behavior_trust = QuestionTrust(behavior_ids, behavior_scores_list)
            self.behavior.updateTable(behavior_trust)
        else:
            self.behavior.clear()
            error_list.append("行为维度")

        # 口腔健康维度
        health_status_ids = self.questions.getDimensionQuestionsIDs("health_status")
        health_status_ids = list(set(health_status_ids) & set(self.question_number_filter_data))
        if len(health_status_ids) >= 3:
            health_status_scores_list: list[list[int]] = []
            for scores in filtered_data_scores_list:
                health_status_scores_list.append(scores.getIDsScores(health_status_ids)) # 根据题目ID列表获取分数列表
            health_status_trust = QuestionTrust(health_status_ids, health_status_scores_list)
            self.oral_health.updateTable(health_status_trust)
        else:
            self.oral_health.clear()
            error_list.append("口腔健康维度")

        if len(error_list) > 0:
            self.sidebarMsg.sendMessage(
                title="题目数量不足",
                text=f"至少需要三个题目，以下维度题目数量不足：{', '.join(error_list)}",
                msg_type="error",
                fold_after=4
            )

        self.sidebarMsg.sendMessage(
            title="信度分析",
            text="信度分析完成",
            msg_type="success",
            fold_after=4
        )

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
        # print(data)
        if not data is None:
            # 将字符串int化
            try:
                data = [int(i) for i in data]
                self.question_number_filter_data = data
                self.updateTable()
            except Exception as e:
                print("on_filter_result 报错:", e)