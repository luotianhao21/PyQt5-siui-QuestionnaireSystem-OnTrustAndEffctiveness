# 问卷子窗口
from siui.components import SiLabel, SiLongPressButton, SiPushButton, SiScrollArea, SiMasonryContainer, SiLineEditWithDeletionButton
from siui.core import SiColor, SiGlobal, GlobalFont, Si
from siui.components.spinbox.spinbox import SiDoubleSpinBox, SiIntSpinBox
from siui.templates.application.components.dialog.modal import SiModalDialog
from siui.components.titled_widget_group import SiTitledWidgetGroup
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
from siui.components.button import (
    SiRadioButtonRefactor
)
from siui.components.page.child_page import SiChildPage
from siui.components.option_card import SiOptionCardPlane
from siui.gui import SiFont

from PyQt5.QtCore import Qt, QRect, pyqtSignal


import sys
import os
def get_scripts_path():
    # 获取父级目录下scripts文件夹的路径
    scripts_path = os.path.abspath(__file__)
    # 倒退5次路径，得到scripts文件夹的父级路径
    for i in range(5):
        scripts_path = os.path.dirname(scripts_path)
    scripts_path = os.path.join(scripts_path, "scripts")
    return scripts_path
scripts_path = get_scripts_path()
if scripts_path not in sys.path:
    sys.path.append(scripts_path) # 导入数据库和获取问题数据的py

from scripts.questions import Questions
from scripts.database import Database

class GroupTitle(SiLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedHeight(26)

        # 标题文字
        self.title_label = SiLabel(self)
        self.title_label.setFont(SiFont.tokenized(GlobalFont.M_BOLD))
        self.title_label.setFixedHeight(26)
        self.title_label.setAlignment(Qt.AlignBottom)
        self.title_label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)

        # 标题高光，显示在文字下方
        self.title_highlight = SiLabel(self)
        self.title_highlight.lower()
        self.title_highlight.setFixedStyleSheet("border-radius: 4px")

        # 标题指示器，显示在文字左侧
        self.title_indicator = SiLabel(self)
        self.title_indicator.resize(5, 18)
        self.title_indicator.setFixedStyleSheet("border-radius: 2px")

    def reloadStyleSheet(self):
        super().reloadStyleSheet()

        self.setStyleSheet("background-color: transparent")
        self.title_label.setStyleSheet("color: {}".format(SiGlobal.siui.colors["TEXT_A"]))
        self.title_indicator.setStyleSheet("background-color: {}".format(SiGlobal.siui.colors["TITLE_INDICATOR"]))
        self.title_highlight.setStyleSheet("background-color: {}".format(SiGlobal.siui.colors["TITLE_HIGHLIGHT"]))

    def setText(self, text: str):
        self.title_label.setText(text)
        self.adjustSize()

    def adjustSize(self):
        self.resize(self.title_label.width() + 12 + 4, self.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.title_indicator.move(0, 4)
        self.title_label.move(12, 0)
        self.title_highlight.setGeometry(12, 12, self.title_label.width() + 4, 13)

class QuestionCard(SiOptionCardPlane):

    checked = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.question_id = kwargs.get("question_id", 1)     # 序号
        self.dimension = kwargs.get("dimension", "")        # 维度
        self.type = kwargs.get("type", [])                  # 类型
        self.by = kwargs.get("by", 1)                      # 依赖于哪道题
        self.by_answer = kwargs.get("by_answer", "")        # 依赖于该题的哪个答案
        self.question = kwargs.get("question", "")          # 问题
        self.options = kwargs.get("options", [])            # 选项
        self.score = kwargs.get("score", [])                # 分值

        self.input_widgets: list[SiRadioButtonRefactor | SiIntSpinBox | SiLineEditWithDeletionButton] = [] # 输入控件

        self.create_wdigets()
        self.body().addPlaceholder(16)

        self.setMinimumWidth(400)
        self.setMaximumWidth(600)
        self.setMinimumHeight(150)

        self.body().setSpacing(4)

        self.setTitle(f"{self.question_id}. {self.question}")

        self.body().adjustSize()
        self.adjustSize()

    def create_wdigets(self):
        if "only_check" in self.type:
            # 单选题
            for option in self.options:
                # 单选框
                check_box = SiRadioButtonRefactor(self)
                check_box.setText(option)
                check_box.adjustSize()
                self.body().addWidget(check_box)
                self.input_widgets.append(check_box)
                check_box.clicked.connect(self.on_checked)
            # self.input_widgets[0].setChecked(True)
        elif "input" in self.type:
            # 输入题
            if self.question_id == 2:
                # 年龄
                line_edit = SiIntSpinBox(self)
            else:
                line_edit = SiLineEditWithDeletionButton(self)
            line_edit.resize(256, 32)
            self.body().addWidget(line_edit)
            self.input_widgets.append(line_edit)

    def get_answer(self) -> str:
        if "only_check" in self.type:
            # 单选题
            for btn in self.input_widgets:
                if btn.isChecked():
                    return btn.text()
            return "" # 未选择选项
        if "input" in self.type:
            if type(self.input_widgets[0]) == SiIntSpinBox:
                # 年龄
                return str(self.input_widgets[0].value())
            if type(self.input_widgets[0]) == SiLineEditWithDeletionButton:
                # 输入题
                return self.input_widgets[0].lineEdit().text()
            
    def set_answer(self, answer: str):
        if "only_check" in self.type:
            # 单选题
            for btn in self.input_widgets:
                if btn.text() == answer:
                    btn.setChecked(True)
                    break
        elif "input" in self.type:
            if type(self.input_widgets[0]) == SiIntSpinBox:
                # 年龄
                self.input_widgets[0].setValue(int(answer))
            if type(self.input_widgets[0]) == SiLineEditWithDeletionButton:
                # 输入题
                self.input_widgets[0].lineEdit().setText(answer)
        
    def on_checked(self):
        self.checked.emit(self.get_answer())
        

class QuestionnaireWindow(SiChildPage):

    sumbited = pyqtSignal(list) # 点击提交按钮触发的信号

    def __init__(self, _data: list[str] = []):
        super().__init__()

        self.data = _data # 传入的数据
        self.questions = Questions() # 实例化问题类
        self.database = Database() # 实例化数据库类

        self.view().setMinimumWidth(600)
        self.view().setMinimumHeight(800)

        self.content().setTitle("编辑问卷")

        self.scroll_container = SiTitledWidgetGroup(self)
        self.container_v = SiDenseVContainer(self)

        self.container_v.moveTo(int((1060-850) / 2), 0)

        self.dimensions = ["信息", "知", "信", "行", "口腔情况"]
        self.dimensions_key = ["info", "knowledge", "attitude", "behavior", "health_status"]
        self.question_cards: list[QuestionCard] = []
        last_dimension = ""

        for i, data in enumerate(self.questions.getDatas()):
            data = self._init_data(data)
            if data["dimension"] != last_dimension:
                last_dimension = data["dimension"]
                title_label = GroupTitle(self)
                title_label.setText(self.dimensions[self.dimensions_key.index(last_dimension)])
                self.container_v.addWidget(title_label)
            question_card = QuestionCard(self,
                                         question_id=data["id"],
                                         dimension=data["dimension"],
                                         type=data["type"],
                                         by=data["by"],
                                         by_answer=data["by_answer"],
                                         question=data["question"],
                                         options=data["options"],
                                         score=data["score"])
            self.question_cards.append(question_card)
            if "by" in data["type"]:
                # 当该题目依赖于其它题目时
                by_widget = self.question_cards[int(data["by"])-1]
                def __on_checked(answer, by_widget: QuestionCard, question_card: QuestionCard):
                    if answer == question_card.by_answer:
                        question_card.setVisible(True)
                    else:
                        question_card.setVisible(False)
                        """
                        if type(question_card.input_widgets[0]) == SiIntSpinBox:
                            # 年龄
                            question_card.input_widgets[0].setValue(0)
                        if type(question_card.input_widgets[0]) == SiLineEditWithDeletionButton:
                            # 输入题
                            question_card.input_widgets[0].lineEdit().setText("")
                        """ # 隐藏输入框

                by_widget.checked.connect(lambda answer, by_widget=by_widget, question_card=question_card: __on_checked(answer, by_widget, question_card))
                if by_widget.get_answer() == data["by_answer"]:
                    question_card.setVisible(True)
                else:
                    question_card.setVisible(False)
            
            self.container_v.addWidget(question_card)
        
        self.container_v.resized.connect(lambda _: self.scroll_container.adjustSize())
        self.scroll_container.addWidget(self.container_v)
        self.scroll_container.addPlaceholder(32)
        self.container_v.adjustSize()
        self.content().setAttachment(self.scroll_container)

        self.sumbit_btn = SiLongPressButton(self)
        self.sumbit_btn.attachment().setText("提交")
        self.sumbit_btn.longPressed.connect(self.on_long_press)

        self.cancle_btn = SiPushButton(self) # 取消按钮
        self.cancle_btn.attachment().setText("取消")
        self.cancle_btn.clicked.connect(self.close_winodw)

        self.panel().addWidget(self.sumbit_btn, "right")
        self.panel().addWidget(self.cancle_btn, "right")
        
        SiGlobal.siui.reloadStyleSheetRecursively(self)

        if self.data:
            self.set_data(self.data) # 设置问卷数据

    def _init_data(self, data: dict):
        """
        格式化数据
        """
        id = 1
        dimension = ""
        type = []
        by = 1
        by_answer = ""
        question = ""
        options = []
        score = []

        for key in ["id", "dimension", "type", "by", "by_answer", "question", "options", "score"]:
            if key in data:
                if key == "id":
                    id = data[key]
                elif key == "dimension":
                    dimension = data[key]
                elif key == "type":
                    type = data[key]
                elif key == "by":
                    by = data[key]
                elif key == "by_answer":
                    by_answer = data[key]
                elif key == "question":
                    question = data[key]
                elif key == "options":
                    options = data[key]
                elif key == "score":
                    score = data[key]

        return {
            "id": id,
            "dimension": dimension,
            "type": type,
            "by": by,
            "by_answer": by_answer,
            "question": question,
            "options": options,
            "score": score
        }
    
    def get_data(self) -> list[str]:
        """
        获取问卷数据
        """
        data: list[str] = []
        for question_card in self.question_cards:
            answer = question_card.get_answer()
            if "by" in question_card.type:
                # 依赖于其它题目
                if self.question_cards[int(question_card.by)-1].get_answer() != question_card.by_answer:
                    answer = "" # 依赖于其它题目，但答案不正确，不记录
            data.append(answer)
        return data
    
    def set_data(self, data: list[str]):
        """
        设置问卷数据
        params:
            data: list[str] 问卷数据，从数据库中获取，要去除头2项：序号和时间
        """
        # 截取问卷数据
        # print(data)
        data = data[2:]
        for i, question_card in enumerate(self.question_cards):
            if i < len(data):
                question_card.set_answer(data[i])
                if "by" in question_card.type:
                    # 依赖于其它题目
                    by_widget = self.question_cards[int(question_card.by)-1]
                    if by_widget.get_answer() == question_card.by_answer:
                        question_card.setVisible(True)
    
    def close_winodw(self):
        self.close()
        self.closeParentLayer()

    def on_long_press(self):
        data = self.get_data()
        self.sumbited.emit(data)
        self.close_winodw() # 长按关闭窗口