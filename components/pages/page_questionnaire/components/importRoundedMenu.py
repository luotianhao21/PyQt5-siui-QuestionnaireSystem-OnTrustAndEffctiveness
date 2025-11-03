from contextlib import contextmanager

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QAction, QActionGroup, QWidget, QFileDialog

from siui.components.combobox_ import ComboboxItemWidget
from siui.components.menu_ import SiRoundedMenu
from siui.core import SiGlobal
from siui.templates.application.application import SiliconApplication

from scripts.questions import Questions
from scripts.database import Database, ImportSignals

from components.pages.page_home.components.compents.sidebar_message.SideBarMessage import SideBarMessage

class ImportRoundedMenu(SiRoundedMenu):

    imported = pyqtSignal()

    @contextmanager
    def useMenu(self, menu: SiRoundedMenu):
        '''
        用于临时使用某个菜单，并在完成后恢复原菜单
        '''
        yield menu

    def __init__(self, parent: QWidget):

        super().__init__(parent)

        self.database = Database()
        self.sidebar = SideBarMessage()

        self.main_menu = SiRoundedMenu(parent)

        self.import_from_csv = QAction(self.main_menu)
        self.import_from_csv.setText('从 <strong>CSV</strong> 文件导入')
        self.import_from_csv.setIcon(SiGlobal.siui.iconpack.toIcon('ic_fluent_code_filled'))

        self.main_menu.addAction(self.import_from_csv)

        self.import_from_csv.triggered.connect(lambda _: self.import_from_csv_file())

    def import_from_csv_file(self):
        '''
        从 CSV 文件导入数据
        '''
        # 弹出文件选择窗口
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择 CSV 文件", 
            "", 
            "CSV 文件 (*.csv);;所有文件 (*)"
        )
        if file_path:
            # print(f"用户选择的文件路径: {file_path}")
            # 在这里处理文件导入逻辑
            try:
                signals: ImportSignals = self.database.importQuestionnairesFromCSV(parent=self, file_path=file_path)
                signals.finish.connect(self.imported_fun)
            except Exception as e:
                print(f"导入失败: {e}")
                self.sidebar.sendMessage(
                    title="导入失败", 
                    text=f"{e}", 
                    msg_type="error",
                    icon=SiGlobal.siui.iconpack.get('ic_fluent_error_circle_filled')
                )

    def import_from_excel_file(self):
        '''
        从 Excel 文件导入数据
        '''
        # 弹出文件选择窗口
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择 Excel 文件", 
            "", 
            "Excel 文件 (*.xls *.xlsx);;所有文件 (*)"
        )
        if file_path:
            # print(f"用户选择的文件路径: {file_path}")
            # 在这里处理文件导入逻辑
            try:
                signals: ImportSignals = self.database.importQuestionnairesFromExcel(parent=self, file_path=file_path)
                signals.finish.connect(self.imported_fun)
            except Exception as e:
                print(f"导入失败: {e}")
                self.sidebar.sendMessage(
                    title="导入失败", 
                    text=f"{e}", 
                    msg_type="error",
                    icon=SiGlobal.siui.iconpack.get('ic_fluent_error_circle_filled')
                )

    def imported_fun(self, *args, **kwargs):
        '''
        导入完成后的回调函数
        '''
        self.sidebar.sendMessage(
            title="导入成功", 
            text="问卷数据已成功导入数据库！", 
            msg_type="success",
            icon=SiGlobal.siui.iconpack.get('ic_fluent_checkmark_circle_filled'),
            fold_after=4
        )
        self.imported.emit()
