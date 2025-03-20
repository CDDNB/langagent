class ReadingComprehension:
    def __init__(self, client):
        self.client = client

    def generate_questions(self, german_text):
        prompt = f"""
        **文章内容**：
        {german_text}

        **输出格式**：
        1. 题目
        - A. 选项1
        - B. 选项2
        - C. 选项3
        - D. 选项4
        **答案**：X
        **解析**：详细的中文解析

        请严格按照这个格式输出，不要包含额外的说明。
        """
        try:
            completion = self.client.chat.completions.create(
                model="qwen-max",
                messages=[
                    {'role': 'system', 'content': '你是一位教德语进阶课程的高级教师，请根据用户给出的德语文章，用德语生成 5 道德语B1/B2等级水平及以上的高质量、有思考的单项选择题，每道题目包含 4 个选项，并提供正确答案和中文答案解析。'},
                    {'role': 'user', 'content': prompt}
                    ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"阅读理解模块请求失败: {str(e)}"

class word_extraction:
    def __init__(self, client):
        self.client = client
    def extract_keywords(self, german_text):
        prompt = f"""
        **文章内容**：
        {german_text}

        **要求与格式**：
        如果是单词，请先将这个单词转换为原型，然后提供：
        - **单词**：（原型）
        - **词性**：（用字母简写表示，如n.， adj.， adv.， v.等。如果是名词，还需注明这个德语名词是阴性/阳性/中性）
        - **翻译**：
        - **原句**：（返回这个单词在文章中的完整句子）
        -(可选) **易混淆单词或常考搭配**：（如果非常重要，请列出，并提供简要解析）

        如果是俚语，请提供：
        - **俚语**：
        - **翻译**：
        - **原句**：（返回这个词组在文章中的完整句子）
        -（可选） **示例**：（再举一个使用该俚语的其他场景案例）

        请不要包含额外的说明。
        """
        try:
            completion = self.client.chat.completions.create(
                model="qwen-max",
                messages=[
                    {'role':'system', 'content': '你是一位教德语进阶课程的高级教师，请阅读用户给出的德语文章，选取其中值得学习的**单词**（二十个左右，视文章长度决定）和**固定搭配/俚语**（最多两三条，有的文章没有就不选），并给出词性、释义和所在原句，帮助德语学习者掌握重点词汇。请尽可能选择面向德语B1、B2级别以上的学习内容，避免过于简单'},
                    {'role': 'user', 'content': prompt}
                    ]
            )
            return self.double_check(completion.choices[0].message.content)
        except Exception as e:
            return f"关键词提取模块请求失败: {str(e)}"
        
    def double_check(self, text):
        """调用 Qwen-Plus API 二次校对"""
        prompt = f"""
        词汇表如下：\n
        {text}
        请严格按照原格式输出，不要包含额外的说明。\n
        """
        try:
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {'role':'system', 'content': '你是一位教德语进阶课程的高级教师，请检查授课所用的词汇表，删去其中过于冷门、学习意义极低或难度过于简单的词，保留格式不变'},
                    {'role': 'user', 'content': prompt}
                    ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"二次校对模块请求失败: {str(e)}"