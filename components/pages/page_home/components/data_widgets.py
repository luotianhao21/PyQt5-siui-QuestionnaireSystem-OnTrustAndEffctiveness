from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
)

from .compents.LeftTopCard import LeftTopCard
from .compents.LeftBottomCard import LeftBottomCard
from .compents.RightTopCard import RightTopCard
from .compents.ButtonCard import ButtonCard

class DataWidgets(SiDenseVContainer):
    # 当前数据显示
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # 父类初始化

        self.setAdjustWidgetsSize(True) # 设置是否在垂直上自适应子组件大小
        self.setSpacing(8) # 间距
        '''
        # 使用嵌套布局3x2
        # 左上显示当前问卷数量，以及筛选后数量与总数的占比进度条，该卡片左上角有筛选按钮
        # 左中显示筛选后各分数的折线图
        # 右显示筛选后各选项的信度和效度分数表格
        '''

        self.top_container_h = SiDenseHContainer(self) # 顶部水平布局

        self.left_container_v = SiDenseVContainer(self) # 左侧垂直布局
        self.right_container_v = SiDenseVContainer(self) # 右侧垂直布局

        self.left_top_card = LeftTopCard(self) # 左上卡片
        self.left_bottom_card = LeftBottomCard(self) # 左下卡片
        self.right_top_card = RightTopCard(self) # 右卡片
        self.button_card = ButtonCard(self)

        self.left_top_card.filter_updated.connect(self.left_bottom_card.on_uplevel_filter_updated)
        self.left_top_card.filter_updated.connect(self.right_top_card.on_uplevel_filter_updated)
        self.left_top_card.filter_updated.connect(self.button_card.on_uplevel_filter_updated)

        self.left_container_v.addWidget(self.left_top_card)
        self.left_container_v.addWidget(self.left_bottom_card)
        self.right_container_v.addWidget(self.right_top_card)

        self.top_container_h.addWidget(self.left_container_v)
        self.top_container_h.addWidget(self.right_container_v)

        self.addWidget(self.top_container_h)
        self.addWidget(self.button_card)

    def resizeEvent(self, event):
        super().resizeEvent(event)