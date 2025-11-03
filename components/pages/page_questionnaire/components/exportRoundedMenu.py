from contextlib import contextmanager

from PyQt5.QtWidgets import QAction, QActionGroup, QWidget

from siui.components.combobox_ import ComboboxItemWidget
from siui.components.menu_ import SiRoundedMenu
from siui.core import SiGlobal

class ExportRoundedMenu(SiRoundedMenu):

    def __init__(self, parent: QWidget):
        self.main_menu = SiRoundedMenu(parent)

        self.export_to_excel = QAction(self.main_menu)
        self.export_to_excel.setText('导出为 <strong>Excel</strong> 文件')
        self.export_to_excel.setIcon(SiGlobal.siui.iconpack.toIcon('ic_fluent_table_filled'))

        self.export_to_csv = QAction(self.main_menu)
        self.export_to_csv.setText('导出为 <strong>CSV</strong> 文件')
        self.export_to_csv.setIcon(SiGlobal.siui.iconpack.toIcon('ic_fluent_code_filled'))

        self.main_menu.addAction(self.export_to_excel)
        self.main_menu.addAction(self.export_to_csv)

    @contextmanager
    def useMenu(self, menu: SiRoundedMenu):
        """
        用于临时使用某个菜单，并在完成后恢复原菜单
        """
        yield menu