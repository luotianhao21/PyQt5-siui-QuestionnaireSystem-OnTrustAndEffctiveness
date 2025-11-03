import sys
import os
import json

# 退回父级目录
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Datas:
    def __init__(self, datas: list = []):
        self.datas = datas

    def addData(self, data: dict):
        self.datas.append(data)

    def getDatas(self) -> list[dict]:
        '''
        获取所有数据
        '''
        return self.datas
    
    def getQuestions(self) -> list:
        '''
        获取所有题目数据
        '''
        questions = []
        for data in self.datas:
            questions.append(data["question"])
        return questions
    
    def getQuestionNum(self) -> int:
        '''
        获取题目数量
        '''
        return len(self.datas)
    
    def getDataById(self, id: int) -> dict:
        '''
        根据id获取数据
        '''
        for data in self.datas:
            if data["id"] == id:
                return data
        return {}

class Dimensions:
    def __init__(self, datas: list):
        self.datas = datas

        self.info = Datas([])          # 基础信息
        self.knowledge = Datas([])     # 知
        self.attitude = Datas([])      # 信
        self.behavior = Datas([])      # 行
        self.health_status = Datas([]) # 健康状态

        self.unknown_dimensions = Datas([]) # 未知维度

        for data in self.datas:
            if data["dimension"] == "info":
                self.info.addData(data)
            elif data["dimension"] == "knowledge":
                self.knowledge.addData(data)
            elif data["dimension"] == "attitude":
                self.attitude.addData(data)
            elif data["dimension"] == "behavior":
                self.behavior.addData(data)
            elif data["dimension"] == "health_status":
                self.health_status.addData(data)
            else:
                self.unknown_dimensions.addData(data)

class Questions:
    def __init__(self):
        self.questions_json_file = os.path.join(parent_dir, 'json', 'questions.json')
        # 读取json文件
        try:
            with open(self.questions_json_file, 'r', encoding='utf-8') as f:
                self.datas = Datas(json.load(f)["questions"])
            # 进行题目的维度化
            self.dimensions = Dimensions(self.datas.getDatas())
        except FileNotFoundError:
            print('questions.json文件不存在！')
            self.datas = Datas()

    def getDatas(self) -> list[dict]:
        '''
        获取所有数据：
        - 序号 "id"
        - 维度 "dimension"
        - 类型 "type"
        - 依赖 "by" # 依赖于哪个题目 [有或无]
        - 依赖答案 "by_answer" # 依赖于题目的答案 [有或无]
        - 问题 "question"
        - 选项 "options" [有或无]
        - 分数 "score" [有或无]
        '''
        return self.datas.getDatas()

    def getQuestions(self) -> list[str]:
        '''
        获取所有题目文字
        '''
        questions_str = []
        for data in self.datas.getDatas():
            questions_str.append(data["question"])
        return questions_str
    
    def getQuestionNum(self) -> int:
        '''
        获取题目数量
        '''
        return self.datas.getQuestionNum()
    
    def getQuestionHasScore(self) -> list[int]:
        '''
        获取所有有分数的题目的id
        '''
        questions_has_score = []
        for data in self.datas.getDatas():
            if 'score' in data.keys():
                questions_has_score.append(data["id"])
        return questions_has_score
    
    def getDimensionQuestions(self, dimension: str) -> list:
        '''
        获取某维度的所有题目
        '''
        if dimension == "info":
            return self.dimensions.info.getDatas()
        elif dimension == "knowledge":
            return self.dimensions.knowledge.getDatas()
        elif dimension == "attitude":
            return self.dimensions.attitude.getDatas()
        elif dimension == "behavior":
            return self.dimensions.behavior.getDatas()
        elif dimension == "health_status":
            return self.dimensions.health_status.getDatas()
        else:
            return self.dimensions.unknown_dimensions.getDatas()

    def getDimensions(self) -> Dimensions:
        '''
        获取题目的维度化数据
        - info 基础信息
        - knowledge 知
        - attitude 信
        - behavior 行
        - health_status 健康状态
        - unknown_dimensions 未知维度
        '''
        return self.dimensions
    
    def getDimensionQuestionsIDs(self, dimension: str) -> list[int]:
        '''
        获取某维度的所有题目ID
        '''
        dimension_questions = self.getDimensionQuestions(dimension)
        question_ids: list[int] = []
        for question in dimension_questions:
            question_ids.append(int(question["id"]))
        return question_ids
    
    def getQuestionDimension(self, id: int) -> str:
        '''
        获取题目的维度
        '''
        for data in self.datas.getDatas():
            if data["id"] == id:
                return data["dimension"]
        return ""
    
    def getDataById(self, id: int) -> dict:
        '''
        根据id获取数据
        '''
        return self.datas.getDataById(id)
    
    def getDimensionByID(self, id: int) -> str:
        '''
        根据id获取题目的维度
        '''
        for data in self.datas.getDatas():
            if data["id"] == id:
                return data["dimension"]
        return ""
    
    def getByQuestions(self, question_id: int) -> list:
        '''
        获取所有依赖于某题目的题目
        '''
        by_questions = []
        for data in self.datas.getDatas():
            if data["by"] == question_id:
                by_questions.append(data)
        return by_questions
    
    def getQuestionByID(self, id: int) -> int:
        '''
        获取该题目依赖题目的ID
        '''
        try:
            for data in self.datas.getDatas():
                if data["id"] == id:
                    return data["by"]
        except KeyError:
            return -1
    
    def getQuestionByAnswer(self, id: int) -> str:
        '''
        获取该题目的依赖答案
        '''
        try:
            for data in self.datas.getDatas():
                if data["id"] == id:
                    return data["by_answer"]
        except KeyError:
            return ""
    
    def getQuestionScore(self, id: int) -> list:
        '''
        获取该题目的分数列表
        '''
        try:
            for data in self.datas.getDatas():
                if data["id"] == id:
                    return data["score"]
        except KeyError:
            return []
        
    def getAnswerScore(self, id: int, answer: str) -> int:
        '''
        获取答案对应的分数
        '''
        data = self.getDataById(id)
        try:
            if data:
                if answer in data["options"]:
                    return data["score"][data["options"].index(answer)]
            else:
                return 0
        except KeyError:
            return 0