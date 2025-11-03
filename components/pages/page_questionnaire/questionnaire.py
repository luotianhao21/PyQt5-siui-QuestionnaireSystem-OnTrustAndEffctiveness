from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint, QPointF
from PyQt5.QtGui import QLinearGradient, QPainter

from siui.components.page import SiPage
from siui.components import SiPixLabel
from siui.components.widgets.expands import SiHoverExpandWidget
from siui.components.option_card import SiOptionCardLinear, SiOptionCardPlane
from siui.templates.application.application import SiliconApplication
from siui.components.titled_widget_group import SiTitledWidgetGroup
from siui.core import GlobalFont, Si, SiColor, SiGlobal
from siui.components.slider import SiSliderH
from siui.gui import SiFont
from siui.components.widgets.table import SiTableView
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel,
    SiLineEdit,
    SiLongPressButton,
    SiPushButton,
    SiSimpleButton,
    SiSwitch,
    SiToggleButton
)
from siui.components.widgets.abstracts.table import ABCSiTabelManager, SiRow
from siui.components.button import (
    SiFlatButton,
    SiLongPressButtonRefactor,
    SiPushButtonRefactor,
    SiCheckBox,
    SiToggleButtonRefactor
)
from siui.components.widgets.abstracts.table import ABCSiTable
from siui.components import SiLabel, SiMasonryContainer, SiScrollArea, SiWidget

from components.pages.page_questionnaire.components.questionnaire_window import QuestionnaireWindow
from scripts.questions import Questions
from scripts.database import Database

from components.pages.page_questionnaire.components.importRoundedMenu import ImportRoundedMenu
from components.pages.page_questionnaire.components.exportRoundedMenu import ExportRoundedMenu

class MyTable(SiTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.questions = Questions()
        self.database = Database()

        self.setContainer

        self.is_writed = False # 是否已经写入数据
        self.data_lists = []
        self.check_boxes_list = []

    def init_Rows(self):
        # 添加完列后调用，初始化第一行
        self.is_writed = False
        _new_row = []
        for i in range(0, len(self.columnNames())):
            _new_row.append("")
        self.addRow(widgets=None, data=_new_row, is_init=True) # type: ignore

    def addRow(self, widgets: list = None, data: list = None, is_init: bool = False): # type: ignore
        # 重写以达到初始化时为空
        self.data_lists.append(data)
        super().addRow(widgets, data)
        if not is_init and not self.is_writed:
            self.is_writed = True
            self.deleteRow(0)

    def deleteRow(self, row_index: int):
        '''
        删除指定行
        '''
        # 直接清空
        for row_ in self.rows_[:]:
            self.container_.removeWidget(row_)
            self.rows_.remove(row_)
        # 删除self.data_lists中第row_index的数据
        self.data_lists.pop(row_index)
        if len(self.data_lists) == 0:
            self.init_Rows()
        else:
            for data in self.data_lists:
                super().addRow(data=data)

    def clear(self):
        '''
        清空表格
        '''
        for row_ in self.rows_[:]:
            self.container_.removeWidget(row_)
            self.rows_.remove(row_)
        self.data_lists = []
        self.init_Rows()

    def getCheckedRowIndexes(self) -> list[int]:
        '''
        获取选中的行引索
        '''
        checked_rows = []
        for i, row in enumerate(self.check_boxes_list):
            if row.isChecked():
                checked_rows.append(i)
        return checked_rows

    def set_check_boxes_weight(self, weight_list: list[SiCheckBox]):
        self.check_boxes_list = weight_list

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scroll_area.setGeometry(self.padding, 48, event.size().width() - self.padding, event.size().height() - 48 - 1)

class RecodeSiLongPressButtonRefactor(SiLongPressButtonRefactor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _drawButtonRect(self, painter: QPainter, rect: QRect) -> None:
        # 确保p在0-1之间
        p = min(self._progress, 1)
        p = max(p, 0)
        if p - 0.0001 < 0:
            p = 0.0001
        gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
        gradient.setColorAt(p - 0.0001, self.style_data.progress_color)
        gradient.setColorAt(p, self.style_data.button_color)
        painter.setBrush(gradient)
        painter.drawPath(self._drawButtonPath(rect))

class QuestionnaireTableManager(ABCSiTabelManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.questions = Questions()
        self.database = Database()
        self.all_check_btn = None

        self.check_box_widgets: list[SiCheckBox] = []
        self.is_checked = []
        self.update_table_func: callable = None

    def set_update_table_func(self, func: callable):
        self.update_table_func = func

    def _value_read_parser(self, row_index, col_index):
        return self.parent().getRowWidget(row_index)[col_index].text()

    def _value_write_parser(self, row_index, col_index, value):
        # 重写该方法以实现对表格数据的写入
        weight = self.parent().getRowWidget(row_index)[col_index] # 获取该单元格的控件

        if not col_index in [0, 6]:
            weight.setTextColor(self.parent().getColor(SiColor.TEXT_B))
            weight.setText(str(value)) # 设置文本
        else:
            if self.parent().is_writed:
                if col_index == 6:
                    weight.setText("编辑") # 设置文本
                    weight.clicked.connect(lambda: self._on_row_edit_clicked(row_index)) # 编辑按钮被点击
            else:
                weight.setTextColor(self.parent().getColor(SiColor.TEXT_B))
                weight.setText("") # 设置文本

    def _widget_creator(self, col_index):
        if col_index in [0, 6] and self.parent().is_writed: # 按钮列
            if col_index == 0:
                button = SiCheckBox(self.parent())
                button.resize(98, 32)
                button.setText("选择")
                button.setChecked(False)
                self.check_box_widgets.append(button)
                self.parent().set_check_boxes_weight(self.check_box_widgets)
            if col_index == 6:
                button = SiPushButtonRefactor(self.parent())
                button.resize(70, 32)
            return button
        else:
            label = SiLabel(self.parent())
            label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
            return label

    def on_header_created(self, header: SiRow):
        for i, name in enumerate(self.parent().column_names):
            if i == 0:
                # 全选框
                self.all_check_btn = SiFlatButton(self.parent())
                self.all_check_btn.resize(36, 36)
                self.all_check_btn.setSvgIcon(SiGlobal.siui.iconpack.get("ic_fluent_select_all_on_regular"))
                self.all_check_btn.setToolTip("全选")
                self.all_check_btn.clicked.connect(self._on_all_check_clicked)
                header.container().addWidget(self.all_check_btn)
            else:
                new_label = SiLabel(self.parent())
                new_label.setFont(SiFont.tokenized(GlobalFont.S_BOLD))
                new_label.setTextColor(self.parent().getColor(SiColor.TEXT_B))
                new_label.setText(name)
                new_label.adjustSize()
                header.container().addWidget(new_label)

        header.container().arrangeWidgets()

    def _on_all_check_clicked(self):
        # 全选按钮被点击
        is_all_checked = True # 是否全部的复选框都被选中
        for check_btn in self.check_box_widgets:
            if not check_btn.isChecked():
                # 当有一个未选中时
                is_all_checked = False
                check_btn.setChecked(True)
        
        if is_all_checked:
            for check_btn in self.check_box_widgets:
                # 当全部都是选中状态时再按下全选按钮，则全部取消选中
                check_btn.setChecked(False)

    def _on_row_edit_clicked(self, row_index):
        # 编辑按钮被点击
        # 弹出编辑框
        data = self.database.get_questionnaire_data(row_index + 1)
        child_window = QuestionnaireWindow(_data=data)
        SiGlobal.siui.windows["MAIN_WINDOW"].layerChildPage().setChildPage(child_window)
        child_window.sumbited.connect(lambda data, i=row_index+1: self._on_child_window_sumbited(i, data))

    def _on_child_window_sumbited(self, i: int, data: list[str]):
        # 子窗口提交后更新数据库
        self.database.update_questionnaire_data(i, data)
        # 更新表格
        self.update_table_func()

class QuestionnaireListCard(SiOptionCardPlane):

    databaseChanged = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 数据库
        self.database = Database()
        self.questions = Questions()

        self.setTitle("问卷列表")
        self.setSpacing(32)
        self.resize(850, 640 + 100)

        self.footer().setFixedHeight(64)
        self.footer().setSpacing(24)
        self.footer().setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.questionnaire_list = []

        self.questionnaire_table = MyTable(self)
        self.questionnaire_table.resize(768, 500 + 100)
        self.questionnaire_table_manager = QuestionnaireTableManager(self.questionnaire_table)
        self.questionnaire_table_manager.set_update_table_func(self.updateTable)
        self.questionnaire_table.setManager(self.questionnaire_table_manager)
        self.questionnaire_table.addColumn("", 100, 40, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) # 复选框按钮列
        self.questionnaire_table.addColumn("性别", 64, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("年龄", 64, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("大学", 148, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("年级", 64, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("民族", 64, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("", 98, 40, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter) # 编辑按钮列
        
        self.questionnaire_table.init_Rows()

        # self.questionnaire_table.addRow(data=["", "男", "20", "清华大学", "大一", "汉族", ""]) # 测试数据
        # self.questionnaire_table.addRow(data=["", "男", "20", "清华大学", "大一", "汉族", ""]) # 测试数据

        self.add_questionnaire_btn = SiPushButtonRefactor(self)
        self.add_questionnaire_btn.setSvgIcon(SiGlobal.siui.iconpack.get("ic_fluent_add_filled"))
        self.add_questionnaire_btn.setText("添加问卷")
        self.add_questionnaire_btn.setToolTip("点击添加问卷")
        self.add_questionnaire_btn.clicked.connect(self._on_add_questionnaire_clicked)

        self.del_questionnaire_btn = RecodeSiLongPressButtonRefactor(self)
        self.del_questionnaire_btn.setSvgIcon(SiGlobal.siui.iconpack.get("ic_fluent_delete_filled"))
        self.del_questionnaire_btn.setText("删除问卷")
        self.del_questionnaire_btn.setToolTip("长按删除已选择的问卷<br><strong>注意：删除后不可恢复</strong>")
        self.del_questionnaire_btn.longPressed.connect(self._on_del_questionnaire_longPressed)

        self.import_btn = SiPushButtonRefactor(self)
        self.import_btn.setSvgIcon(SiGlobal.siui.iconpack.get("ic_fluent_arrow_import_filled"))
        self.import_btn.setText("导入问卷数据")
        self.import_menu = ImportRoundedMenu(self.import_btn)
        self.import_btn.clicked.connect(
            lambda: self.import_menu.main_menu.popup(self.import_btn.mapToGlobal(QPoint(0, self.import_btn.height())))
        )
        self.import_menu.imported.connect(self.updateTable)

        self.export_btn = SiPushButtonRefactor(self)
        self.export_btn.setSvgIcon(SiGlobal.siui.iconpack.get("ic_fluent_arrow_export_filled"))
        self.export_btn.setText("导出问卷数据")
        self.export_menu = ExportRoundedMenu(self.export_btn)
        self.export_btn.clicked.connect(
            lambda: self.export_menu.main_menu.popup(self.export_btn.mapToGlobal(QPoint(0, self.export_btn.height())))
        )

        self.footer().addWidget(self.add_questionnaire_btn)
        self.footer().addWidget(self.del_questionnaire_btn)
        self.footer().addPlaceholder(32, "right")
        self.footer().addWidget(self.export_btn, "right")
        self.footer().addPlaceholder(10, "right")
        self.footer().addWidget(self.import_btn, "right")

        self.body().addWidget(self.questionnaire_table)
        self.body().adjustSize()
        self.adjustSize()

        self.updateTable() # 读取数据库并显示

    def updateTable(self):
        # 读取数据库
        data_list = self.database.get_all_questionnaire_data()
        self.questionnaire_table.setVisible(False)
        self.body().removeWidget(self.questionnaire_table)

        self.questionnaire_table = MyTable(self)
        self.questionnaire_table.resize(768, 500 + 100)
        self.questionnaire_table_manager = QuestionnaireTableManager(self.questionnaire_table)
        self.questionnaire_table_manager.set_update_table_func(self.updateTable)
        self.questionnaire_table.setManager(self.questionnaire_table_manager)
        self.questionnaire_table.addColumn("", 100, 40, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) # 复选框按钮列
        self.questionnaire_table.addColumn("性别", 64, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("年龄", 64, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("大学", 148, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("年级", 64, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("民族", 64, 40, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.questionnaire_table.addColumn("", 98, 40, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter) # 编辑按钮列
        
        self.questionnaire_table.init_Rows()
        
        for data in data_list:
            sex = data[2] if data[2] else "未知"
            age = data[3] if data[3] else "未知"
            university = data[4] if data[4] else "未知"
            if university == "其他学校":
                university = data[5] if data[5] else "未知"
            grade = data[6] if data[6] else "未知"
            nation = data[7] if data[7] else "未知"
            if nation == "其他":
                nation = data[8] if data[8] else "未知"
            _data = ["", sex, age, university, grade, nation, ""]
            # print(_data) # 测试数据
            self.questionnaire_table.addRow(data=_data)
        
        self.body().addWidget(self.questionnaire_table)
        self.questionnaire_table.show()
        self.questionnaire_table.reloadStyleSheet()
        self.databaseChanged.emit(0)

    def _on_add_questionnaire_clicked(self):
        # 添加问卷按钮被点击
        child_window = QuestionnaireWindow()
        SiGlobal.siui.windows["MAIN_WINDOW"].layerChildPage().setChildPage(child_window)
        child_window.sumbited.connect(self._on_add_questionnaire_sumbit)
    
    def _on_add_questionnaire_sumbit(self, data: list):
        self.database.add_questionnaire_data(data)
        self.updateTable()
        self.databaseChanged.emit(0)

    def _on_del_questionnaire_longPressed(self):
        # 删除问卷按钮被点击
        checked_rows = self.questionnaire_table.getCheckedRowIndexes()
        # 将全部i都+1，因为数据库的索引是从1开始的
        checked_rows = [i + 1 for i in checked_rows]
        self.database.delete_questionnaire_datas(checked_rows)
        self.updateTable()
        self.databaseChanged.emit(0)

class PageQuestionnaire(SiPage):
    def __init__(self, *args, **kwargs):
        super().__init__()

        # 整个滚动区域
        self.scroll_container = SiTitledWidgetGroup(self)

        # 下方区域标签
        self.body_area = SiLabel(self)
        self.body_area.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.body_area.resized.connect(lambda _: self.scroll_container.adjustSize())

        # 下面的 titledWidgetGroups
        self.titled_widget_group = SiTitledWidgetGroup(self.body_area)
        self.titled_widget_group.setSiliconWidgetFlag(Si.EnableAnimationSignals)
        self.titled_widget_group.resized.connect(lambda size: self.body_area.setFixedHeight(size[1] + 80))
        self.titled_widget_group.move(64, 32)
        self.titled_widget_group.setSpacing(16)

        # 问卷列表
        self.container_h = SiDenseHContainer(self)
        self.questionnaire_list_card = QuestionnaireListCard(self)
        self.titled_widget_group.addTitle("问卷的编辑与导入导出")
        self.container_h.addWidget(self.questionnaire_list_card)
        self.questionnaire_list_card.resized.connect(lambda _: self.container_h.adjustSize())

        self.titled_widget_group.addWidget(self.container_h)
        self.container_h.resized.connect(lambda _: self.titled_widget_group.adjustSize())

        self.scroll_container.addWidget(self.body_area)

        # 添加到页面
        self.setAttachment(self.scroll_container)