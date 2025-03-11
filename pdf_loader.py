import fitz  # PyMuPDF 解析 PDF
import docx
from openai import OpenAI
import sys
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

def save_markdown(md_text, output_path):
    """保存 Markdown 文件"""
    with open(output_path, "a", encoding="utf-8") as f:
        f.write("\n---\n")  # 添加分隔符
        f.write(md_text)


def main(file_path, output_md_path):
    # 根据文件扩展名选择不同的提取方法
    file_ext = file_path.lower().split('.')[-1]
    if file_ext == 'pdf':
        paragraphs = extract_text_from_pdf(file_path)
    elif file_ext in ['doc', 'docx']:
        paragraphs = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_ext}")
    
    client = OpenAI(base_url=api_url, api_key=api_key)
    # 生成词汇表
    #save_markdown(word_extraction(client).extract_keywords('\n'.join(paragraphs)), output_md_path)
    #print(f"Markdown 文件已生成：{output_md_path}")
    #sys.exit(0)
    # 生成思维导图
    generator = MindMapGenerator('\n'.join(paragraphs), client)
    structure = generator.analyze_structure()
    generator.generate_mermaid()
    generator.export_image()

    # 生成翻译
    translator = DocumentTranslator(client)
    md_text = translator.generate_markdown(paragraphs)
    save_markdown(md_text, output_md_path)
    #translator.save_markdown(md_text, output_md_path)

    # 生成阅读理解题
    save_markdown(ReadingComprehension(client).generate_questions('\n'.join(paragraphs)), output_md_path)

    # 生成词汇表
    save_markdown(word_extraction(client).extract_keywords('\n'.join(paragraphs)), output_md_path)
    
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
