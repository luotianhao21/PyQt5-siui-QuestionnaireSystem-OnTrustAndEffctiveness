import os
import sys
import json
import sqlite3
import pandas as pd
from PyQt5.QtCore import pyqtSignal, QObject, QThread, Qt
from PyQt5.QtWidgets import QApplication

from questions import Questions

_questions = Questions()

from siui.core import SiGlobal, SiColor
from siui.templates.application.application import SiliconApplication
from siui.templates.application.components.dialog.modal import SiModalDialog
from siui.components import (
    SiLabel,
    SiProgressBar,
    SiCircularProgressBar
)
from siui.components.widgets.container import (
    SiDenseHContainer,
    SiDenseVContainer
)

# 信号类：用于线程间通信
class ImportSignals(QObject):
    update_progress = pyqtSignal(float)  # 更新进度信号
    finish = pyqtSignal()                # 导入完成信号
    error = pyqtSignal(str)              # 错误提示信号

# 导入工作线程：处理数据逻辑（不操作UI）
class ImportWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, file_path, signals):
        super().__init__()
        self.file_path = file_path
        self.signals = signals
        self.database = Database()  # 线程内创建数据库连接

    def run(self):
        try:
            questions = Questions()
            # 读取文件
            # 获取文件类型是CSV还是Excel
            file_type = os.path.splitext(self.file_path)[1]
            if file_type == ".csv":
                df = pd.read_csv(self.file_path)
            elif file_type in [".xls", ".xlsx"]:
                df = pd.read_excel(self.file_path)
            titles = df.columns.tolist()

            # 获取关键列索引
            gender_index = titles.index(next(filter(lambda x: "性别" in x, titles)))
            age_index = titles.index(next(filter(lambda x: "年龄" in x, titles)))
            clear_index = titles.index(next(filter(lambda x: "清洗数据" in x, titles)))
            grade_index = titles.index(next(filter(lambda x: "年级" in x, titles)))
            questions_num = questions.getQuestionNum()

            # 处理数据
            questionnaire_data = df.values[1:].tolist()
            for i, data in enumerate(questionnaire_data):
                if "无效" in data[clear_index]:
                    continue
                

                # 数据清洗
                data = self.database.import_without_abcd(data[gender_index:gender_index + questions_num])
                data[1] = data[1].replace("\t", "")
                
                # 尝试转换成整数
                try:
                    int(data[1])
                except ValueError:
                    # 根据年级进行推测
                    grade_dict = {
                        "大一": 18,
                        "大二": 19,
                        "大三": 20,
                        "大四": 21,
                        "研究生及以上": 22
                    }
                    data[1] = str(grade_dict.get(data[4], 19)) # 默认年龄为19

                self.database.add_questionnaire_data(data)

                # 发送进度信号
                progress = float((i + 1) / len(questionnaire_data))
                self.signals.update_progress.emit(progress)

            self.signals.finish.emit()  # 导入完成
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.finished.emit()  # 工作线程结束

# 进度条窗口
class ChildWindowProgressBar(SiModalDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(300)
        self.setWindowModality(Qt.ApplicationModal)  # 应用级模态

        self.icon_.setDisabled(True)

        # 布局容器
        self.container_h = SiDenseHContainer(self)
        
        # 提示标签
        self.label = SiLabel(self.container_h)
        self.label.setStyleSheet(f"color: {self.getColor(SiColor.TEXT_E)}")
        self.label.setText(
            f'<span style="color: {self.getColor(SiColor.TEXT_B)}">正在导入问卷数据...</span>'
        )
        self.label.adjustSize()

        # 环形进度条
        self.progress_bar = SiCircularProgressBar(self.container_h)
        self.progress_bar.resize(32, 32)
        self.progress_bar.setValue(0.0)

        # 组装布局
        self.container_h.addWidget(self.label)
        self.container_h.addWidget(self.progress_bar)
        self.container_h.adjustSize()

        self.contentContainer().addWidget(self.container_h)
        self.contentContainer().adjustSize()

        # 隐藏按钮容器
        self.buttonContainer().setFixedHeight(0)
        self.buttonContainer().hide()

        SiGlobal.siui.reloadStyleSheetRecursively(self)
        self.adjustSize()

    def closeEvent(self, event):
        # 关闭时清除模态遮罩中对当前对话框的引用
        window: SiliconApplication = SiGlobal.siui.windows.get("MAIN_WINDOW")
        window.layerModalDialog().closeLayer()
        super().closeEvent(event)

# 问卷筛选数据类
class QuestionnaireFilterData:
    def __init__(self):
        self.sex = []
        self.age = []
        self.university = []
        self.nation = []

    def copy(self, data):
        self.sex = data.sex.copy()
        self.age = data.age.copy()
        self.university = data.university.copy()
        self.nation = data.nation.copy()

    def print(self):
        print("=========当前问卷筛选条件=============")
        print("性别：", self.sex)
        print("年龄：", self.age)
        print("大学：", self.university)
        print("民族：", self.nation)
        print("=====================================")

# 问卷分数处理类
class QuestionnaireScores:
    def __init__(self, id: int, scores: list[int | str]):
        self.id = id
        self.scores = scores

    def getScores(self) -> list[int]:
        """获取所有题目分数列表"""
        return self.scores
    
    def getScoreByNumbert(self, numbert: int | str) -> int:
        """获取某题目分数"""
        return self.scores[int(numbert) - 8]

    def getDimensionScores(self, dimension: str) -> list[int]:
        """获取某维度分数列表"""
        dimension_questions = _questions.getDimensionQuestions(dimension)
        return [self.getScoreByNumbert(q["id"]) for q in dimension_questions]

    def getDimensionScoresSum(self, dimension: str) -> int:
        """获取某维度分数总和"""
        return sum(self.getDimensionScores(dimension))
    
    def getIDsScores(self, ids: list[int | str]) -> list[int]:
        """获取指定题目ID的分数列表"""
        return [self.getScoreByNumbert(i) for i in ids]

    def getDimensionAndIDsScores(self, dimension: str, ids: list[int | str]) -> list[int]:
        """获取某维度中指定题目ID的分数列表"""
        dimension_questions = _questions.getDimensionQuestions(dimension)
        ids = [str(i) for i in ids]
        return [self.getScoreByNumbert(q["id"]) for q in dimension_questions if str(q["id"]) in ids]
    
    def getDimensionAllscore(self, dimension: str) -> int:
        """获取某维度所有题目分数总和"""
        return sum(self.getDimensionScores(dimension))

    def isDimensionPassed(self, dimension: str) -> bool | None:
        """判断该维度是否及格"""
        if not dimension in ["knowledge", "attitude", "behavior"]:
            return None
        pass_scores = {
            "knowledge": 6,
            "attitude": 5,
            "behavior": 24
        }
        if self.getDimensionScoresSum(dimension) >= pass_scores[dimension]:
            return True
        else:
            return False

    def getHealthStatusStatus(self) -> str | None:
        """获取健康状态维度的分数情况"""
        total_score = self.getDimensionScoresSum("health_status")
        if total_score < 6:
            return "不合格"
        elif total_score <= 8:
            return "合格"
        else:
            return "优秀"

# 数据库操作类（线程安全版）
class Database:
    def __init__(self):
        self.questions = Questions()
        self.data_name = "questionnaire_data.db"
        self._init_table()  # 初始化表结构
        self.import_thread = None
        self.import_worker = None

    def _get_conn(self):
        """获取线程独立的数据库连接"""
        conn = sqlite3.connect(self.data_name)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_table(self):
        """初始化数据表（仅在主线程调用）"""
        questions = self.questions.getDatas()
        self.question_fields_with_type = [f"q_{q['id']} TEXT" for q in questions]
        self.question_fields = [f"q_{q['id']}" for q in questions]

        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            sql = f"""CREATE TABLE IF NOT EXISTS questionnaire_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                {', '.join(self.question_fields_with_type)}
            )"""
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print(f"初始化表失败: {e}")
        finally:
            conn.close()

    def update_id(self):
        """重新编号ID"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM questionnaire_data ORDER BY id")
            ids = [row[0] for row in cursor.fetchall()]
            for i, old_id in enumerate(ids):
                cursor.execute("UPDATE questionnaire_data SET id = ? WHERE id = ?", (i + 1, old_id))
            conn.commit()
        except Exception as e:
            print(f"更新ID失败: {e}")
        finally:
            conn.close()

    def add_questionnaire_data(self, data: list):
        """新增问卷数据"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            sql = f"INSERT INTO questionnaire_data ({', '.join(self.question_fields)}) VALUES ({', '.join(['?'] * len(self.question_fields))})"
            cursor.execute(sql, data)
            conn.commit()
            self.update_id()
        except Exception as e:
            print(f"添加数据失败: {e}")
        finally:
            conn.close()

    def get_questionnaire_data(self, id: int) -> list:
        """获取单条问卷数据"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            sql = f"SELECT id, time, {', '.join(self.question_fields)} FROM questionnaire_data WHERE id = ?"
            cursor.execute(sql, (id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"获取数据失败: {e}")
            return []
        finally:
            conn.close()

    def get_all_questionnaire_data(self) -> list[list]:
        """获取所有问卷数据"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            self.update_id()
            sql = f"SELECT id, time, {', '.join(self.question_fields)} FROM questionnaire_data"
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"获取所有数据失败: {e}")
            return []
        finally:
            conn.close()

    def delete_questionnaire_data(self, id: int):
        """删除单条数据"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM questionnaire_data WHERE id = ?", (id,))
            conn.commit()
            self.update_id()
        except Exception as e:
            print(f"删除数据失败: {e}")
        finally:
            conn.close()

    def delete_questionnaire_datas(self, ids: list[int]):
        """删除多条数据"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            placeholders = ", ".join(["?"] * len(ids))
            cursor.execute(f"DELETE FROM questionnaire_data WHERE id IN ({placeholders})", ids)
            conn.commit()
            self.update_id()
        except Exception as e:
            print(f"批量删除失败: {e}")
        finally:
            conn.close()

    def getAllAges(self) -> list[str]:
        """获取所有年龄"""
        ages = []
        for data in self.get_all_questionnaire_data():
            age = data[3]  # 年龄字段索引
            try:
                age = int(age)
            except:
                continue
            if age not in ages:
                ages.append(age)
        return sorted(ages, key=lambda x: int(x))

    def getAllUniversities(self) -> list[str]:
        """获取所有大学"""
        unis = []
        for data in self.get_all_questionnaire_data():
            uni = data[4]  # 大学字段索引
            if uni == "其他":
                uni = data[5]  # 其他大学字段索引
            if uni not in unis:
                unis.append(uni)
        return unis

    def getAllNations(self) -> list[str]:
        """获取所有民族"""
        nations = []
        for data in self.get_all_questionnaire_data():
            nation = data[7]  # 民族字段索引
            if nation == "其他":
                nation = data[8]  # 其他民族字段索引
            if nation not in nations:
                nations.append(nation)
        return nations

    def getQuestionDataByFilters(self, filters: QuestionnaireFilterData) -> list[list]:
        """按筛选条件获取数据"""
        filtered = []
        for data in self.get_all_questionnaire_data():
            sex = data[2]
            age = int(data[3])
            university = data[4] if data[4] != "其他" else data[5]
            nation = data[7] if data[7] != "其他" else data[8]

            if (sex in filters.sex and
                age in filters.age and
                university in filters.university and
                nation in filters.nation):
                filtered.append(data)
        return filtered

    def getDefaultQuestionnaireFilterData(self) -> QuestionnaireFilterData:
        """获取默认筛选条件"""
        filters = QuestionnaireFilterData()
        filters.sex = ["男", "女"]
        filters.age = self.getAllAges()
        filters.university = self.getAllUniversities()
        filters.nation = self.getAllNations()
        return filters

    def getQuestionnairesScores(self, id: int) -> QuestionnaireScores:
        """获取问卷分数"""
        data = self.get_questionnaire_data(id)
        scores = []
        for q in self.questions.getDatas():
            if "score" in q:
                try:
                    answer_index = q["options"].index(data[q["id"] - 1 + 2])
                    scores.append(q["score"][answer_index])
                except:
                    scores.append(0)
        return QuestionnaireScores(id, scores)

    def getDefaultK2DimensionFilters(self) -> list[str]:
        """获取卡方时筛选的三个维度条件（英文）"""
        return ["knowledge", "attitude", "behavior"]

    def import_without_abcd(self, data: list[str]) -> list[str]:
        """移除选项中的ABCD前缀"""
        abcd = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i, val in enumerate(data):
            if isinstance(val, str) and len(val) >= 2 and val[0] in abcd:
                data[i] = val[2:]
        return data

    def importQuestionnairesFromCSV(self, parent, file_path: str) -> ImportSignals:
        """从CSV导入问卷数据（线程安全版）"""
        # 创建进度窗口（不变）
        progress_bar = ChildWindowProgressBar(parent)
        window = SiGlobal.siui.windows.get("MAIN_WINDOW")
        if window and hasattr(window, "layerModalDialog"):
            window.layerModalDialog().setDialog(progress_bar)

        # 信号与槽连接（不变）
        signals = ImportSignals()
        signals.update_progress.connect(progress_bar.progress_bar.setValue)
        signals.finish.connect(progress_bar.close)
        signals.error.connect(lambda msg: self._show_error(msg, progress_bar))

        # 修改：使用类属性存储线程和工作对象，避免局部变量被回收
        self.import_thread = QThread()
        self.import_worker = ImportWorker(file_path, signals)
        self.import_worker.moveToThread(self.import_thread)
        
        # 信号连接（不变）
        self.import_thread.started.connect(self.import_worker.run)
        self.import_worker.finished.connect(self.import_thread.quit)
        self.import_worker.finished.connect(self.import_worker.deleteLater)
        # 线程结束后清除引用（关键：避免内存泄漏）
        self.import_thread.finished.connect(lambda: setattr(self, "import_thread", None))
        self.import_thread.finished.connect(lambda: setattr(self, "import_worker", None))

        self.import_thread.start()
        progress_bar.show()

        return signals
    
    def importQuestionnairesFromExcel(self, parent, file_path: str) -> ImportSignals:
        """从Excel导入问卷数据（线程安全版）"""
        # 创建进度窗口（不变）
        progress_bar = ChildWindowProgressBar(parent)
        window = SiGlobal.siui.windows.get("MAIN_WINDOW")
        if window and hasattr(window, "layerModalDialog"):
            window.layerModalDialog().setDialog(progress_bar)

        # 信号与槽连接（不变）
        signals = ImportSignals()
        signals.update_progress.connect(progress_bar.progress_bar.setValue)
        signals.finish.connect(progress_bar.close)
        signals.error.connect(lambda msg: self._show_error(msg, progress_bar))

        # 修改：使用类属性存储线程和工作对象，避免局部变量被回收
        self.import_thread = QThread()
        self.import_worker = ImportWorker(file_path, signals)
        self.import_worker.moveToThread(self.import_thread)
        
        # 信号连接（不变）
        self.import_thread.started.connect(self.import_worker.run)
        self.import_worker.finished.connect(self.import_thread.quit)
        self.import_worker.finished.connect(self.import_worker.deleteLater)
        # 线程结束后清除引用（关键：避免内存泄漏）
        self.import_thread.finished.connect(lambda: setattr(self, "import_thread", None))
        self.import_thread.finished.connect(lambda: setattr(self, "import_worker", None))

        self.import_thread.start()
        progress_bar.show()

        return signals

    def _show_error(self, msg, progress_bar):
        """显示错误信息并关闭进度窗口"""
        print(f"导入错误: {msg}")
        progress_bar.close()

    def close(self):
        """关闭数据库连接（此处无需操作，连接已在每次操作后关闭）"""
        pass