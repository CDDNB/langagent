import json
import os
import sys
from flask import Flask, request, jsonify, send_file, url_for
#import tencentcloud.common.credential as credential
#import qcloud_cos  # 腾讯云 COS 存储
#from qcloud_cos import CosConfig
#from qcloud_cos import CosS3Client
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用 CORS


@app.route('/')
def hello_world():
   return 'Hello World'

@app.route('/upload', methods=['POST'])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "未上传文件"}), 400

    file = request.files["file"]
    input_path = f"{file.filename}"
    output_md_path = input_path.replace(".docx", ".md")
    file.save(input_path)
    # 调用 pdf2md 脚本
    #os.system(f"python3 pdf_loader.py {input_path} {output_md_path}")

    # 生成下载链接
    download_url = f"http://localhost:9000/download/{output_md_path}"
    return jsonify({"download_url": download_url})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=9000)
