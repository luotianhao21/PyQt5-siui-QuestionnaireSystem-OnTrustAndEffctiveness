from PyQt5.QtWidgets import QSizePolicy, QBoxLayout
from PyQt5.QtCore import pyqtSignal

from siui.components.container import SiDenseContainer
from siui.components.option_card import SiOptionCardPlane
from siui.components.progress_bar import SiProgressBar # 进度条
from siui.components.widgets import (
    SiSimpleButton,
)
from siui.components.button import (
    SiCapsuleButton # 胶囊按钮
)
from siui.core import SiGlobal

from .MyCapsuleButton import MyCapsuleButton
from ..child_window.filter_window import FilterChildWindowQuestionnaire
from ..child_window.filter_window import QuestionnaireFilterData as FilterWindowQuestionnaireFilterData

from scripts.database import Database, QuestionnaireFilterData

class LeftTopCard(SiOptionCardPlane):

    filter_updated: pyqtSignal = pyqtSignal(QuestionnaireFilterData) # 当筛选条件更新时继续向上传递信号
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = Database() # 数据库管理类

        self.filters_saved: QuestionnaireFilterData | None = self.database.getDefaultQuestionnaireFilterData() # 保存的筛选条件

        self.setFixedSize(540, 180) # 设置固定大小
        self.header().setSpacing(8)
        self.body().setSpacing(8)
        self.setTitle("问卷数量统计及筛选") # 设置标题

        # Header筛选按钮
        self.filter_btn = SiSimpleButton(self)
        self.filter_btn.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_filter_add_regular"))
        self.filter_btn.resize(32, 32)
        self.filter_btn.setHint("筛选问卷<strong>（该筛选将应用于信度与效度分析）</strong>")
        self.filter_btn.clicked.connect(self.show_filter_window)

        self.refilter_btn = SiSimpleButton(self)
        self.refilter_btn.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_filter_sync_filled"))
        self.refilter_btn.resize(32, 32)
        self.refilter_btn.setHint("重置筛选")
        self.refilter_btn.clicked.connect(lambda _: self.on_database_changed(0))

        self.header().addWidget(self.refilter_btn, "right")
        self.header().addWidget(self.filter_btn, "right")

        # Body部分
        self.btn_liner_container = SiDenseContainer(self)
        self.btn_liner_container.layout().setDirection(QBoxLayout.LeftToRight)
        self.btn_liner_container.layout().setSpacing(120)
        self.btn_liner_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.btn_liner_container.setFixedHeight(36)

        self.capsule_button_1 = MyCapsuleButton(self)
        self.capsule_button_1.setText("全部问卷")
        self.capsule_button_1.setValue(0) # 设置数值
        self.capsule_button_1.setToolTip("数据库中已经存在的问卷总数")
        self.capsule_button_1.adjustSize()

        self.capsule_button_2 = MyCapsuleButton(self)
        self.capsule_button_2.setText("已筛选问卷")
        self.capsule_button_2.setValue(0) # 设置数值
        self.capsule_button_2.setToolTip("经过筛选条件后剩余的问卷数")
        self.capsule_button_2.setThemeColor(SiCapsuleButton.Theme.Yellow)
        self.capsule_button_2.adjustSize()

        self.btn_liner_container.addWidget(self.capsule_button_1)
        self.btn_liner_container.addWidget(self.capsule_button_2)

        self.progress_bar = SiProgressBar(self)
        self.progress_bar.setFixedSize(420, 20)
        self.progress_bar.setValue(1) # 设置进度条值
        self.progress_bar.setHint("已筛选问卷 0/0 (100%)") # 设置进度条格式

        self.body().addWidget(self.btn_liner_container)
        self.body().addPlaceholder(2)
        self.body().addWidget(self.progress_bar)
        self.body().adjustSize()

        self.updateFilterData() # 更新筛选条件得到的结果

    def show_filter_window(self):
        '''
        显示筛选窗口
        '''
        child_window = FilterChildWindowQuestionnaire(self)
        if not self.filters_saved is None:
            child_window.setInitData(self.filters_saved)
        child_window.dataConfirmed.connect(self.on_filter_result)
        SiGlobal.siui.windows["MAIN_WINDOW"].layerChildPage().setChildPage(child_window)

    def on_filter_result(self, data: FilterWindowQuestionnaireFilterData):
        '''
        处理筛选结果
        '''
        # data.print()
        # 重新创建一个QuestionnaireFilterData对象，避免类型错误
        new_data: QuestionnaireFilterData = QuestionnaireFilterData()
        new_data.copy(data) # 复制数据

        self.filters_saved = new_data
        self.updateFilterData()

    def initFilters(self):
        '''
        初始化筛选条件
        '''
        self.filters_saved = self.database.getDefaultQuestionnaireFilterData()

    def updateFilterData(self):
        '''
        更新筛选条件得到的结果（用于外部删除数据后调用）
        '''
        # 获取问卷总数
        total_num = len(self.database.get_all_questionnaire_data())
        # 获取筛选的问卷数
        filtered_num = len(self.database.getQuestionDataByFilters(self.filters_saved))
        # 更新按钮数值
        self.capsule_button_1.setValue(total_num)
        self.capsule_button_2.setValue(filtered_num)
        self.capsule_button_1.adjustSize()
        self.capsule_button_2.adjustSize()

        # 更新进度条
        filtered_baifen = round(filtered_num/total_num*100, 2) if total_num > 0 else 0
        self.progress_bar.setHint(f"已筛选问卷 {filtered_num}/{total_num} ({filtered_baifen}%)")
        self.progress_bar.setValue(filtered_baifen) # 设置进度条值
        self.body().adjustSize()

    def on_database_changed(self, _: int):
        '''
        数据库改变时调用
        @para _: 无用参数
        '''
        self.initFilters()
        self.updateFilterData()

    def __emit__(self):
        # 做一个滞留，当页面还留在问卷管理[1]时不向上传递，当切回到主页[0]时向上传递
        self.filter_updated.emit(self.filters_saved)  # 向上传递信号