from graphviz import Digraph
import json

class MindMapGenerator:
    def __init__(self, text, client):
        self.text = text
        self.structure = None
        self.client = client

    def analyze_structure(self):
        """调用大模型进行结构分析"""
        prompt = f"""
        请分析以下德语文章的写作逻辑结构，用JSON格式返回层次化分析结果。
        要求：
        1. 包含3-5个主要部分
        2. 每个部分最多3个子点
        3. 使用中文标签
        4. 只返回JSON格式数据，不要包含其他说明文字
        5. 格式示例：
        {{
            "核心论点": "气候变化的影响",
            "分支": [
                {{
                    "主题": "极地冰川融化",
                    "子主题": ["数据统计", "生态影响"]
                }}
            ]
        }}

        文本内容：
        {self.text[:2000]}
        """

        response = self.client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        #print(content)
        # 尝试提取 JSON 部分
        try:
            if content.startswith('```json'):
                content = content.split('```json')[1].split('```')[0]
            self.structure = json.loads(content.strip())
            return self.structure
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            print(f"原始内容: {content}")
            raise

    def generate_mermaid(self):
        """生成Mermaid代码"""
        mm_code = "graph TD\n"
        main_node = f'A["{self.structure["核心论点"]}"]\n'
        mm_code += main_node

        for i, branch in enumerate(self.structure["分支"], start=1):
            node_id = chr(66 + i)  # B,C,D...
            mm_code += f'{node_id}["{branch["主题"]}"]\n'
            mm_code += f'A --> {node_id}\n'

            for j, sub in enumerate(branch["子主题"], start=1):
                sub_id = f"{node_id}{j}"
                mm_code += f'{sub_id}["{sub}"]\n'
                mm_code += f'{node_id} --> {sub_id}\n'

        return mm_code

    def export_image(self, format='png'):
        """导出可视化文件"""
        dot = Digraph()
        dot.node('A', self.structure["核心论点"])
        
        for i, branch in enumerate(self.structure["分支"]):
            branch_id = f'B{i}'
            dot.node(branch_id, branch["主题"])
            dot.edge('A', branch_id)
            
            for sub in branch["子主题"]:
                sub_id = f'{branch_id}_{sub[:2]}'
                dot.node(sub_id, sub)
                dot.edge(branch_id, sub_id)
        
        dot.render(f'mindmap', format=format, cleanup=True)
