import fitz  # PyMuPDF 解析 PDF
import docx
from openai import OpenAI
import sys
import os
import json
from translate import DocumentTranslator
from mindmap import MindMapGenerator
from reading_comprehension import ReadingComprehension, word_extraction

api_key = 'sk-de619016f861434aa6a70d34eed13085'
api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

def extract_text_from_docx(docx_path):
    """从 Word 文件中提取文本，保留标题格式"""
    doc = docx.Document(docx_path)
    paragraphs = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        paragraphs.append(text)  # 普通正文段落

    return paragraphs

def extract_text_from_pdf(pdf_path):
    """从 PDF 提取文本，并按段落分割"""
    doc = fitz.open(pdf_path)
    paragraphs = []
    temp_paragraph = ""

    for page in doc:
        text = page.get_text("text")
        for line in text.split("\n"):
            if line.strip():
                temp_paragraph += " " + line.strip()
            else:
                if temp_paragraph:
                    paragraphs.append(temp_paragraph.strip())
                    temp_paragraph = ""

    if temp_paragraph:
        paragraphs.append(temp_paragraph.strip())

    return paragraphs

def extract_text_from_txt(txt_path):
    """从 TXT 文件中提取文本，按空行分段"""
    paragraphs = []
    temp_paragraph = ""
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                temp_paragraph += " " + line
            else:
                if temp_paragraph:
                    paragraphs.append(temp_paragraph.strip())
                    temp_paragraph = ""
    
    if temp_paragraph:
        paragraphs.append(temp_paragraph.strip())
    
    return paragraphs

def process_document(file_path):
    """处理文档并返回各个模块的结果"""
    print(f"\n📄 开始处理文档：{os.path.basename(file_path)}")
    
    # 根据文件扩展名选择不同的提取方法
    file_ext = file_path.lower().split('.')[-1]
    print(f"📑 文件类型：{file_ext}")
    
    if file_ext == 'pdf':
        print("⚙️ 正在提取 PDF 文本...")
        paragraphs = extract_text_from_pdf(file_path)
    elif file_ext in ['doc', 'docx']:
        print("⚙️ 正在提取 Word 文本...")
        paragraphs = extract_text_from_docx(file_path)
    elif file_ext == 'txt':
        print("⚙️ 正在提取 TXT 文本...")
        paragraphs = extract_text_from_txt(file_path)
    else:
        print(f"❌ 不支持的文件类型: {file_ext}")
        raise ValueError(f"不支持的文件类型: {file_ext}")
    
    print(f"✅ 文本提取完成，共 {len(paragraphs)} 个段落")
    
    client = OpenAI(base_url=api_url, api_key=api_key)
    full_text = '\n'.join(paragraphs)
    
    print("\n🔄 开始生成思维导图...")
    generator = MindMapGenerator(full_text, client)
    structure = generator.analyze_structure()
    mermaid_code = generator.generate_mermaid()
    mindmap_image_path = generator.export_image()
    print("✅ 思维导图生成完成")
    
    '''
    print("\n🔄 开始生成翻译...")
    translator = DocumentTranslator(client)
    translation = translator.translate_text(full_text)
    print("✅ 翻译生成完成")
    
    print("\n🔄 开始生成阅读理解题...")
    reading_comprehension = ReadingComprehension(client).generate_questions(full_text)
    print("✅ 阅读理解题生成完成")
    
    print("\n🔄 开始生成词汇表...")
    vocabulary = word_extraction(client).extract_keywords(full_text)
    print("✅ 词汇表生成完成")
    
    # 返回所有结果
    result = {
        "mindmap": {
            "mermaid_code": mermaid_code,
            "image_path": mindmap_image_path
        },
        "translation": translation,
        "reading_comprehension": reading_comprehension,
        "vocabulary": vocabulary
    }
    '''
    result = {
        "mindmap": {
            "mermaid_code": mermaid_code,
            "image_path": mindmap_image_path
        },
        "translation": "translation",
        "reading_comprehension": "reading_comprehension",
        "vocabulary": "vocabulary"
    }
    print("\n🎉 文档处理全部完成！")
    return result

# 如果直接运行此脚本，则保持原有功能
def save_markdown(md_text, output_path):
    """保存 Markdown 文件"""
    with open(output_path, "a", encoding="utf-8") as f:
        f.write("\n---\n")  # 添加分隔符
        f.write(md_text)

def main(file_path, output_md_path):
    result = process_document(file_path)
    
    # 清空输出文件
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("")
    
    # 保存思维导图
    save_markdown(f"## 思维导图\n\n![思维导图]({result['mindmap']['image_path']})\n\n```mermaid\n{result['mindmap']['mermaid_code']}\n```", output_md_path)
    
    # 保存翻译
    save_markdown(result["translation"], output_md_path)
    
    # 保存阅读理解题
    save_markdown(result["reading_comprehension"], output_md_path)
    
    # 保存词汇表
    save_markdown(result["vocabulary"], output_md_path)
    
    print(f"Markdown 文件已生成：{output_md_path}")

# 运行代码
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python pdf_loader.py <输入文件> <输出文件>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_md = sys.argv[2]
    print(input_file)
    print(output_md)
    main(input_file, output_md)
