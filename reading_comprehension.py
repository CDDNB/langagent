class ReadingComprehension:
    def __init__(self, client):
        self.client = client

    def generate_questions(self, german_text):
        """调用 Qwen-Plus API 生成德语阅读理解题"""
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
                model="qwen-plus",
                messages=[
                    {'role': 'system', 'content': '你是一位经验丰富的德语教学老师，请根据用户给出的德语文章，用德语生成 5 道单项选择题，每道题目包含 4 个选项，并提供正确答案和中文答案解析。'},
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
        """调用 Qwen-Plus API 提取德语文章关键词"""
        prompt = f"""
        **文章内容**：
        {german_text}

        **要求与格式**：
        如果是单词，请提供：
        - **单词**：
        - **词性**：
        - **翻译**：
        - **所在原句**：（返回这个单词在文章中的完整句子）
        -(可选) **易混淆单词或常考搭配**：（如果非常重要，请列出，并提供简要解析）

        如果是词组，请提供：
        - **词组**：
        - **翻译**：
        - **所在原句**：（返回这个词组在文章中的完整句子）
        请不要包含额外的说明。
        """
        try:
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {'role':'system', 'content': '你是一位经验丰富的德语教学老师，请阅读用户给出的德语文章，选取其中值得学习的**单词或词组**，并给出词性、释义和其他解析，帮助德语学习者掌握重点词汇。'},
                    {'role': 'user', 'content': prompt}
                    ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"关键词提取模块请求失败: {str(e)}"