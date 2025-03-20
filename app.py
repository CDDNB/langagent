import json
import os
import sys
from flask import Flask, request, jsonify, send_file, url_for, send_from_directory
from flask_cors import CORS
import mimetypes
import base64
from pdf_loader import process_document

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 创建上传和图片目录
UPLOAD_FOLDER = 'uploads'
IMAGE_FOLDER = 'images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# 支持的文件类型
ALLOWED_EXTENSIONS = {
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'doc': 'application/msword',
    'pdf': 'application/pdf',
    'txt': 'text/plain'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello_world():
   return 'Hello World'

@app.route('/upload', methods=['POST'])
def upload_file():
    print("\n=== 开始处理新的文件上传请求 ===")
    if "file" not in request.files:
        print("❌ 错误：未检测到上传文件")
        return jsonify({"error": "未上传文件"}), 400

    file = request.files["file"]
    print(f"📁 接收到文件：{file.filename}")
    
    # 检查文件类型
    if not allowed_file(file.filename):
        print(f"❌ 错误：不支持的文件类型 - {file.filename}")
        return jsonify({"error": "不支持的文件类型。支持的类型：docx, doc, pdf, txt"}), 400

    # 获取文件扩展名
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    
    # 保存文件
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(input_path)
    except Exception as e:
        return jsonify({"error": f"文件保存失败：{str(e)}"}), 500

    try:
        print("🔄 开始处理文档...")
        result = process_document(input_path)
        print("✅ 文档处理完成")
        
        # 获取思维导图图片的URL
        image_path = result['mindmap']['image_path']
        image_url = f"/images/{os.path.basename(image_path)}"
        print(f"🖼️ 思维导图已生成：{os.path.basename(image_path)}")
        
        # 返回处理结果
        return jsonify({
            "mindmap": {
                "mermaid_code": result['mindmap']['mermaid_code'],
                "image_url": image_url
            },
            "translation": result['translation'],
            "reading_comprehension": result['reading_comprehension'],
            "vocabulary": result['vocabulary'],
            "file_type": file_ext,
            "original_filename": file.filename
        })
    except Exception as e:
        print(f"❌ 处理失败：{str(e)}")
        return jsonify({"error": f"处理失败：{str(e)}"}), 500

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/generate-markdown', methods=['POST'])
def generate_markdown():
    print("\n=== 开始生成 Markdown 文件 ===")
    try:
        data = request.json
        print(f"📝 正在处理文件：{data.get('original_filename', 'document')}")
        
        # 创建Markdown内容
        md_content = f"# {data.get('filename', '文档分析')}\n\n"
        
        # 添加思维导图
        if 'mindmap' in data:
            md_content += "## 思维导图\n\n"
            if 'image_url' in data['mindmap']:
                md_content += f"![思维导图]({request.host_url.rstrip('/')}{data['mindmap']['image_url']})\n\n"
            if 'mermaid_code' in data['mindmap']:
                md_content += f"```mermaid\n{data['mindmap']['mermaid_code']}\n```\n\n"
        
        # 添加翻译
        if 'translation' in data:
            md_content += f"## 翻译\n\n{data['translation']}\n\n"
        
        # 添加阅读理解
        if 'reading_comprehension' in data:
            md_content += f"## 阅读理解\n\n{data['reading_comprehension']}\n\n"
        
        # 添加词汇表
        if 'vocabulary' in data:
            md_content += f"## 词汇表\n\n{data['vocabulary']}\n\n"
        
        # 保存Markdown文件
        filename = f"{data.get('original_filename', 'document').split('.')[0]}.md"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Markdown 文件已生成：{filename}")
        return jsonify({
            "success": True,
            "download_url": f"/download/{filename}"
        })
    except Exception as e:
        print(f"❌ 生成 Markdown 失败：{str(e)}")
        return jsonify({"error": f"生成Markdown失败：{str(e)}"}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        # 验证文件扩展名
        if not ('.' in filename and filename.rsplit('.', 1)[1].lower() == 'md'):
            return jsonify({"error": "只能下载 Markdown 文件"}), 400
        
        # 检查文件是否存在
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "文件不存在"}), 404
            
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"下载失败：{str(e)}"}), 500

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=9000)
