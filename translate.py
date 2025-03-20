class DocumentTranslator:
    def __init__(self, client):
        """初始化文档翻译器"""
        self.client = client

    '''
    def translate_text(self, text):
        """调用阿里翻译 API 进行翻译"""
        messages = [
            {"role": "user", "content": f"{text}"}
        ]
        translation_options = {
            "source_lang": "German",
            "target_lang": "Chinese"
        }
        response = self.client.chat.completions.create(
            model="qwen-mt-turbo",
            messages=messages,
            extra_body={
                "translation_options": translation_options
            }
        )
        return response.choices[0].message.content

    def generate_markdown(self, paragraphs):
        """德文和中文交替生成 Markdown"""
        md_content = []
        for para in paragraphs:
            md_content.append(para)  # 添加德语
            md_content.append(self.translate_text(para))  
            md_content.append("")  # 换行
        return self.double_check("\n".join(md_content))
    '''
    
    def translate_text(self, text):
        """调用 Qwen-Plus API 二次校对"""
        prompt = f"""
        原文与翻译的对照如下：\n
        {text}
        请按照文章自然段落，一段德语一段中文的格式输出，段落之间换行。严格保持德语内容不变，不要包含额外的说明。\n
        """
        try:
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {'role':'system', 'content': '你是一位德语翻译专家，请将用户给出的德语文章翻译成流畅通顺的中文。请使用更现代的中文表达风格。也就是说，可以修改词汇、语法、句子结构等，不必严格翻译，要让翻译的内容更像人，甚至更口语化，而不是像机器一样死板。如果遇到新鲜事物或者网络热词，要将德语表达替换成中文社区和中文互联网的习惯表达，地名、人名也要保持事实性准确。最重要的是，翻译后的中文要像说人话！！！'},
                    {'role': 'user', 'content': prompt}
                    ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"关键词提取模块请求失败: {str(e)}"
