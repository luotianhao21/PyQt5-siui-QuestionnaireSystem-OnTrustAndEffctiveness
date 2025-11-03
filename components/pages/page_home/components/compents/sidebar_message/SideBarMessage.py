from siui.core import SiGlobal
from siui.templates.application.application import SiliconApplication

class SideBarMessage:
    def __init__(self):
        # 定义主窗口
        self.window: SiliconApplication = SiGlobal.siui.windows["MAIN_WINDOW"]

    def sendMessage(self, 
                    title: str | None=None, 
                    text: str="", 
                    msg_type: int | str=0, 
                    icon: bytes | None=None, 
                    fold_after: float | None=None
                    ) -> None:
        '''
        发送侧边栏消息

        @param title: 标题
        @param text: 内容
        @param msg_type: 消息类型，0-normal，1-success，2-info，3-warning，4-error
        @param icon: 图标
        @param fold_after: 自动折叠时间，单位：秒，默认不自动折叠
        '''

        if type(msg_type) != int:
            msg_type = {"normal": 0, "success": 1, "info": 2, "warning": 3, "error": 4}.get(msg_type, 0)

        if not fold_after is None:
            # 将折叠时间单位转化为毫秒
            fold_after *= 1000
            fold_after = int(fold_after)

        # 发送侧边栏消息
        self.window.LayerRightMessageSidebar().send(
            text=text,
            msg_type=msg_type,
            fold_after=fold_after,
            **({"title": title} if not title is None else {}),
            **({"icon": icon} if not icon is None else {})
        )