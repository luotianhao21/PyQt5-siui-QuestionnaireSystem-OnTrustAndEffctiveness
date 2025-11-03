from PyQt5.QtWidgets import QSizePolicy, QBoxLayout
from PyQt5.QtCore import QPoint, QPointF, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor


from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiSimpleButton,
)

from .MyCapsuleButton import MyCapsuleButton

from ..data.questiontrust import QuestionTrust # 问卷可信度数据类
from ..manager.table_manager import NavigationBarTableManager
from ..compents.MyTable import MyTable

class NavigationBarWidget(SiDenseVContainer):
    # 每个导航项对应的组件，self为一个垂直布局容器
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSpacing(8)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setFixedSize(540, 400)
        self.setAdjustWidgetsSize(True)

        self.container = SiDenseVContainer(self)
        self.setFixedSize(540, 400)

        self.table_managed = MyTable(self)
        self.table_managed.setFixedSize(480, 300)
        self.table_managed.setManager(NavigationBarTableManager(self.table_managed))
        # 添加列
        self.table_managed.addColumn("问题序号", 80, 40, Qt.AlignmentFlag.AlignVCenter)
        self.table_managed.addColumn("校正项总计相关性(CITC)", 180, 40, Qt.AlignmentFlag.AlignVCenter)
        self.table_managed.addColumn("项已删除的α系数", 160, 40, Qt.AlignmentFlag.AlignVCenter)
        self.table_managed.init_Rows() # 初始化第一行

        # 添加一个胶囊按钮，显示维度的Cronbach's Alpha系数
        self.cronbach_alpha_btn = MyCapsuleButton(self)
        self.cronbach_alpha_btn.setFixedHeight(40)
        self.cronbach_alpha_btn.setColorWhen(0, 0.6, QColor("#FF684D"))
        self.cronbach_alpha_btn.setColorWhen(0.6, 0.7, QColor("#FFC266"))
        self.cronbach_alpha_btn.setColorWhen(0.7, 0.8, QColor("#76EAFF"))
        self.cronbach_alpha_btn.setColorWhen(0.8, 1, QColor("#61FC61"))
        self.cronbach_alpha_btn.setText("Cronbach Alpha")
        self.cronbach_alpha_btn.setValue(0) # 设置数值
        self.cronbach_alpha_btn.setToolTip("该维度的Cronbach's Alpha系数\n  >0.8        说明信度高\n  0.7~0.8   说明信度较好\n  0.6~0.7   说明信度可接受\n  <0.6        说明信度不佳")

        self.container.addWidget(self.table_managed)
        self.container.addWidget(self.cronbach_alpha_btn)
        self.addWidget(self.container)
        self.addPlaceholder(16)

    def updateTable(self, trust_data: QuestionTrust):
        '''
        更新表格数据
        @param trust_data: 题目信度分析管理类
        '''
        # 直接从self中删除table_managed和cronbach_alpha_btn，然后重新添加
        self.table_managed.setVisible(False)
        self.container.removeWidget(self.table_managed)
        self.container.removeWidget(self.cronbach_alpha_btn)
        # 创建新表格
        self.table_managed = MyTable(self)
        self.table_managed.setFixedSize(480, 300)
        self.table_managed.setManager(NavigationBarTableManager(self.table_managed))
        # 添加列
        self.table_managed.addColumn("问题序号", 80, 40, Qt.AlignmentFlag.AlignVCenter)
        self.table_managed.addColumn("校正项总计相关性(CITC)", 180, 40, Qt.AlignmentFlag.AlignVCenter)
        self.table_managed.addColumn("项已删除的α系数", 160, 40, Qt.AlignmentFlag.AlignVCenter)
        self.table_managed.init_Rows() # 初始化第一行
        # 填充数据
        for i, data in enumerate(trust_data.getTrustDatas().trust_datas):
            self.table_managed.addRow(data=[str(data.id), str(data.CITC), str(data.alpha_without_item)])
        
        # 添加到布局中
        self.container.addWidget(self.table_managed)
        self.addWidget(self.container)
        self.table_managed.show()
        self.table_managed.reloadStyleSheet()
        self.addPlaceholder(16)
        self.container.addWidget(self.cronbach_alpha_btn)
        # 设置Cronbach's Alpha数值
        self.cronbach_alpha_btn.setValue(round(trust_data.getTrustDatas().original_alpha, 6))
        self.cronbach_alpha_btn.adjustSize() # 调整大小以适应内容

    def clear(self):
        '''
        清空表格
        '''
        # 直接从self中删除table_managed和cronbach_alpha_btn，然后重新添加
        self.table_managed.setVisible(False)
        self.container.removeWidget(self.table_managed)
        self.container.removeWidget(self.cronbach_alpha_btn)
        # 创建新表格
        self.table_managed = MyTable(self)
        self.table_managed.setFixedSize(480, 300)
        self.table_managed.setManager(NavigationBarTableManager(self.table_managed))
        # 添加列
        self.table_managed.addColumn("问题序号", 80, 40, Qt.AlignmentFlag.AlignVCenter)
        self.table_managed.addColumn("校正项总计相关性(CITC)", 180, 40, Qt.AlignmentFlag.AlignVCenter)
        self.table_managed.addColumn("项已删除的α系数", 160, 40, Qt.AlignmentFlag.AlignVCenter)
        self.table_managed.init_Rows() # 初始化第一行
        # 添加到布局中
        self.container.addWidget(self.table_managed)
        self.addWidget(self.container)
        self.table_managed.show()
        self.table_managed.reloadStyleSheet()
        self.addPlaceholder(16)
        self.container.addWidget(self.cronbach_alpha_btn)
        # 设置Cronbach's Alpha数值
        self.cronbach_alpha_btn.setValue(0)
        self.cronbach_alpha_btn.adjustSize() # 调整大小以适应内容