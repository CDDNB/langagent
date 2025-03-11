class DocumentTranslator:
    def __init__(self, client):
        """初始化文档翻译器"""
        self.client = client

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
        return "\n".join(md_content)
