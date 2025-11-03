from PyQt5.QtCore import Qt, pyqtSignal, pyqtBoundSignal

from siui.components.page.child_page import SiChildPage
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
)
from siui.components.widgets import (
    SiCheckBox,
    SiDenseHContainer,
    SiDraggableLabel,
    SiIconLabel,
    SiLabel,
    SiLongPressButton,
    SiPixLabel,
    SiPushButton,
    SiRadioButton,
    SiSimpleButton,
    SiSwitch,
    SiToggleButton,
)
from siui.components.button import (
    SiFlatButton,
    SiLongPressButtonRefactor,
    SiProgressPushButton,
    SiPushButtonRefactor,
    SiRadioButtonRefactor,
    SiRadioButtonWithAvatar,
    SiRadioButtonWithDescription,
    SiSwitchRefactor,
    SiToggleButtonRefactor,
)
from siui.components import SiFlowContainer, SiMasonryContainer
from siui.components.option_card import SiOptionCardLinear, SiOptionCardPlane
from siui.components.widgets.navigation_bar import SiNavigationBarH, SiNavigationBarV
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.core import SiGlobal, Si, SiColor

import sys
import os
def get_scripts_path():
    # 获取父级目录下scripts文件夹的路径
    scripts_path = os.path.abspath(__file__)
    # 倒退6次路径，得到scripts文件夹的父级路径
    for i in range(6):
        scripts_path = os.path.dirname(scripts_path)
    scripts_path = os.path.join(scripts_path, "scripts")
    return scripts_path
scripts_path = get_scripts_path()
if scripts_path not in sys.path:
    sys.path.append(scripts_path) # 导入数据库和获取问题数据的py

from scripts.database import Database
from scripts.questions import Questions

class MyNavigationBarH(SiNavigationBarH):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root_container = None # 根容器
        self.item_widgets = [] # 每个导航对应的组件
        self.current_showing_widgets = [] # 当前显示的组件

    def setRootContainer(self, container):
        self.root_container = container

    def addItems(self, items: list):
        for item in items:
            self.addItem(item)

    def addItem(self, name: str, side="left"):
        super().addItem(name, side)
        self.item_widgets.append([]) # 为每个导航项添加一个空的组件列表

    def addItemWidget(self, index: int, widget):
        widget.setVisible(False) # 初始不可见
        if 0 <= index < len(self.item_widgets):
            self.item_widgets[index].append(widget)

    def setEnabledIndexOf(self, index: int):
        for widget in self.current_showing_widgets:
            # 先移除当前显示的组件
            self.root_container.removeWidget(widget)
            widget.setVisible(False)
            self.current_showing_widgets.remove(widget)
        for widget in self.item_widgets[index]:
            # 再添加新的组件
            self.root_container.addWidget(widget)
            widget.setVisible(True)
            self.current_showing_widgets.append(widget)
        self.setCurrentIndex(index) # 设置当前导航项

    def _on_button_clicked(self, index):
        if self.root_container is None:
            raise ValueError("根容器未设置，请使用 setRootContainer 方法设置")
        
        self.setEnabledIndexOf(index) # 设置当前导航项的组件显示

class FilterCard(SiOptionCardPlane):
    # 每个筛选内容的卡片
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        self.setFixedSize(840-65-65, 480)

        # 全选按钮
        self.select_all_btn = SiToggleButtonRefactor(self)
        self.select_all_btn.resize(96, 32)
        self.select_all_btn.setSvgIcon(SiGlobal.siui.iconpack.get("ic_fluent_select_all_on_filled"))
        self.select_all_btn.setText("全选")
        self.select_all_btn.adjustSize()
        self.select_all_btn.setChecked(True)
        self.select_all_btn.clicked.connect(self._select_all_btn)

        # 整个用瀑布流布局
        self.container_flow = SiFlowContainer(self)
        self.container_flow.resize(840-65-65-64, 470)

        self.filters: list[str] = []
        self.btns: list[(str, SiDraggableLabel, SiToggleButtonRefactor)] = [] # 按钮列表，每个筛选条件的按钮

        self.header().addWidget(self.select_all_btn)
        self.body().setAdjustWidgetsSize(True)
        self.body().addWidget(self.container_flow)
        self.adjustSize()

    def addFilter(self, name: str):
        '''
        添加一个筛选条件
        '''
        if name in self.filters:
            return
        self.filters.append(name)
        # 添加一个筛选条件
        label = SiDraggableLabel(self)
        btn = SiToggleButton(label)
        btn.attachment().setText(str(name))
        btn.colorGroup().assign(SiColor.BUTTON_OFF, "#3b373f")
        btn.colorGroup().assign(SiColor.BUTTON_ON, "#855198")
        btn.colorGroup().assign(SiColor.BUTTON_HOVER, "#40855198")
        btn.setChecked(True)
        btn.setFixedHeight(32)
        btn.adjustSize()
        btn.clicked.connect(lambda WTF=None, name=name, label=label, btn=btn: self._filter_btn(name, label, btn)) # 什么鬼，要用一个传参顶掉第一个，不然第一位永远是bool
        # btn.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # 使按钮忽略鼠标事件
        label.setTrack(False)
        label.button = btn
        label.setFixedSize(btn.size())
        self.container_flow.addWidget(label, ani=False)
        self.container_flow.regDraggableWidget(label)
        self.container_flow.adjustSize()
        self.btns.append([name, label, btn])
        self.adjustSize()

    def _get_all_filters(self) -> list[str]:
        '''
        获取所有筛选条件
        '''
        filters: list[str] = []

        for group in self.btns:
            filters.append(group[0])

        return filters

    def getFilters(self) -> list[str]:
        '''
        获取当前筛选条件
        '''
        return self.filters
    
    def setFilter(self, filter: str, state: bool):
        '''
        设置单个筛选的状态
        '''
        if filter not in self._get_all_filters():
            return
        
        if state:
            # state为True
            if not filter in self.filters:
                self.filters.append(filter)
                for group in self.btns:
                    if group[0] == filter:
                        group[2].setChecked(True)
        else:
            # state为False
            if filter in self.filters:
                self.filters.remove(filter)
                for group in self.btns:
                    if group[0] == filter:
                        group[2].setChecked(False)

    def setAllFilters(self, state: bool):
        '''
        设置所有筛选条件
        '''
        for filter in self._get_all_filters():
            self.setFilter(filter, state)
    
    def setDefaults(self, defaults: list[str]):
        '''
        设置默认筛选条件
        '''

        self.setAllFilters(False)
        
        for default in defaults:
            self.setFilter(default, True)

        # 全选按钮的状态
        if len(self.filters) == len(self._get_all_filters()):
            self.select_all_btn.setChecked(True)
        else:
            self.select_all_btn.setChecked(False)


    # 回调函数
    def _select_all_btn(self):
        '''
        选择按钮的回调函数
        '''
        # 获取当前全选按钮的状况
        all_select_btn_state = self.select_all_btn.isChecked()
        if all_select_btn_state:
            for group in self.btns:
                # 遍历按钮设置为选中状态
                group[2].setChecked(True)
                # 在筛选条件中获取当前按钮的筛选条件
                if not group[0] in self.filters:
                    self.filters.append(group[0])
        else:
            self.filters = [] # 清空筛选条件
            for group in self.btns:
                # 遍历按钮设置为未选中状态
                group[2].setChecked(False)

    def _filter_btn(self, name: str, label: SiDraggableLabel, btn: SiToggleButtonRefactor):
        '''
        筛选按钮的回调函数
        '''
        # 获取当前按钮的状况
        btn_state = btn.isChecked()
        if btn_state:
            # 遍历按钮设置，若都为选中状态，则设置全选按钮为选中状态
            is_all = True
            for group in self.btns:
                if not group[2].isChecked():
                    is_all = False
                    break
            if is_all:
                self.select_all_btn.setChecked(True)
            self.filters.append(name) # 若当前按钮选中，则添加筛选条件
        else:
            self.select_all_btn.setChecked(False) # 若当前按钮选中，则取消全选按钮的选中状态
            self.filters.remove(name) # 移除筛选条件
    
    # 外部绑定所有按钮的connect函数
    def allButtonsConnect(self, func):
        '''
        用于外部接入所有按钮按下后进行刷新筛选条件的函数
        '''
        self.select_all_btn.clicked.connect(func)
        for group in self.btns:
            group[2].clicked.connect(func)

class QuestionnaireFilterData:
    def __init__(self):
        self.sex = []
        self.age = []
        self.university = []
        self.nation = []

    def copy(self, data):
        self.sex = data.sex
        self.age = data.age
        self.university = data.university
        self.nation = data.nation

    def print(self):
        print("=========当前问卷筛选条件=============")
        print("性别：", self.sex)
        print("年龄：", self.age)
        print("大学：", self.university)
        print("民族：", self.nation)
        print("=====================================")

# 问卷数据筛选
class FilterChildWindowQuestionnaire(SiChildPage):

    dataConfirmed = pyqtSignal(QuestionnaireFilterData)

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        self.view().setMinimumWidth(800) # 设置最小宽度
        self.content().setTitle("设置问卷筛选条件")
        self.content().setPadding(64)

        self.database = Database()

        self.root_container = SiDenseVContainer(self)
        self.root_container.setFixedSize(840, 560)
        self.root_container.moveTo(65, 80)

        self.navigation_bar = MyNavigationBarH(self)
        self.navigation_bar.resize(840-65-65, 40)
        self.navigation_bar.addItems(["  性别  ", "  年龄  ", "  大学  ", "  民族  "])
        self.filter_names = ["性别", "年龄", "大学", "民族"]

        self.navigation_bar_items_container = SiDenseVContainer(self)
        self.navigation_bar_items_container.setFixedSize(840-65-65, 480)
        self.navigation_bar.setRootContainer(self.navigation_bar_items_container)

        self.sex_filter_card = FilterCard(self)
        self.sex_filter_card.setTitle("性别")
        self.sex_filter_card.addFilter("男")
        self.sex_filter_card.addFilter("女")
        self.sex_filter_card.adjustSize()

        self.age_filter_card = FilterCard(self)
        self.age_filter_card.setTitle("年龄")
        self.all_ages = self.database.getAllAges()
        for age in self.all_ages:
            self.age_filter_card.addFilter(age)
        self.age_filter_card.adjustSize()

        self.university_filter_card = FilterCard(self)
        self.university_filter_card.setTitle("大学")
        self.all_universities = self.database.getAllUniversities()
        for university in self.all_universities:
            self.university_filter_card.addFilter(university)
        self.university_filter_card.adjustSize()

        self.nation_filter_card = FilterCard(self)
        self.nation_filter_card.setTitle("民族")
        self.all_nations = self.database.getAllNations()
        for nation in self.all_nations:
            self.nation_filter_card.addFilter(nation)
        self.nation_filter_card.adjustSize()

        self.navigation_bar.addItemWidget(0, self.sex_filter_card)
        self.navigation_bar.addItemWidget(1, self.age_filter_card)
        self.navigation_bar.addItemWidget(2, self.university_filter_card)
        self.navigation_bar.addItemWidget(3, self.nation_filter_card)
        
        self.navigation_bar.setEnabledIndexOf(0)

        self.root_container.addWidget(self.navigation_bar)
        self.root_container.addWidget(self.navigation_bar_items_container)
        self.root_container.adjustSize()

        self.apply_btn = SiPushButtonRefactor(self)
        self.apply_btn.setText("应用")
        self.apply_btn.adjustSize()
        self.apply_btn.resize(self.apply_btn.size().width() + 40, self.apply_btn.size().height())
        # 给按钮绑定刷新筛选条件的函数
        self.apply_btn.clicked.connect(self._upload_filter_data)

        self.content().addWidget(self.root_container)
        self.content().adjustSize()
        self.panel().addWidget(self.apply_btn, "right")
        self.panel().adjustSize()
        SiGlobal.siui.reloadStyleSheetRecursively(self)

    def setInitData(self, data: QuestionnaireFilterData):
        '''
        设置初始筛选条件
        '''
        self.sex_filter_card.setDefaults(data.sex)
        self.age_filter_card.setDefaults(data.age)
        self.university_filter_card.setDefaults(data.university)
        self.nation_filter_card.setDefaults(data.nation)

    def _upload_filter_data(self):
        '''
        向上级函数传递筛选条件数据
        '''
        filter_data = QuestionnaireFilterData()
        filter_data.sex = self.sex_filter_card.getFilters()
        filter_data.age = self.age_filter_card.getFilters()
        filter_data.university = self.university_filter_card.getFilters()
        filter_data.nation = self.nation_filter_card.getFilters()

        self.dataConfirmed.emit(filter_data) # 向上级发送筛选条件数据
        self.close() # 关闭当前窗口
        self.closeParentLayer() # 关闭父窗口（背景暗化）

# 信度效度分析筛选题目号（只用于信度或效度中一个的筛选（局部筛选））
class FilterChildWindowQuestionNumber(SiChildPage):

    dataConfirmed = pyqtSignal(list)

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        self.question = Questions()
        self.database = Database()

        self.view().setMinimumWidth(800) # 设置最小宽度
        self.content().setTitle("选择参与数据分析的题目")
        self.content().setPadding(64)

        self.root_container = SiDenseVContainer(self)
        self.root_container.setFixedSize(840, 560)
        self.root_container.moveTo(65, 80)

        self.question_number_filter_card = FilterCard(self)
        self.question_number_filter_card.header().removeWidget(self.question_number_filter_card.title)
        self.question_number_filter_card.setFixedSize(self.question_number_filter_card.size().width(), 530)
        self.question_number_filter_card.adjustSize()

        self.all_question_numbers = self.question.getQuestionHasScore()
        for num in self.all_question_numbers:
            self.question_number_filter_card.addFilter(str(num))
        self.question_number_filter_card.adjustSize()

        self.root_container.addWidget(self.question_number_filter_card)
        self.root_container.adjustSize()

        self.apply_btn = SiPushButtonRefactor(self)
        self.apply_btn.setText("应用")
        self.apply_btn.adjustSize()
        self.apply_btn.resize(self.apply_btn.size().width() + 40, self.apply_btn.size().height())
        self.apply_btn.clicked.connect(self._upload_filter_data)

        self.content().addWidget(self.root_container)
        self.content().adjustSize()
        self.panel().addWidget(self.apply_btn, "right")
        self.panel().adjustSize()
        SiGlobal.siui.reloadStyleSheetRecursively(self)

    def setInitData(self, data: list[str]):
        '''
        设置初始筛选条件
        '''
        self.question_number_filter_card.setDefaults(data)

    def _upload_filter_data(self):
        '''
        向上级函数传递筛选条件数据
        '''
        filter_data = self.question_number_filter_card.getFilters()
        self.dataConfirmed.emit(filter_data) # 向上级发送筛选条件数据
        self.close() # 关闭当前窗口
        self.closeParentLayer() # 关闭父窗口（背景暗化）