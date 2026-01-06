
import gradio as gr
import requests
import json

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/v1/extract"

def extract(file):
    """Function to call the FastAPI backend."""
    if file is None:
        return "Please upload a document.", ""

    try:
        files = {"file": (file.name, open(file.name, "rb"), "text/plain")}
        response = requests.post(API_URL, files=files, timeout=300)

        if response.status_code == 200:
            data = response.json()
            # Pretty-print the JSON output
            pretty_json = json.dumps(data["content"], indent=2, ensure_ascii=False)
            return f"✅ Extraction successful for {data["filename"]}", pretty_json
        else:
            return f"❌ Error: {response.status_code}", response.text

    except Exception as e:
        return "❌ An unexpected error occurred.", str(e)

# --- Gradio Interface ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🤖 工程规范文档结构化抽取智能体
        
        上传一个工程规范文档（如建筑规范、机械规格等），智能体将自动抽取其中的结构化约束。
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="上传文档 (Upload Document)")
            submit_button = gr.Button("开始抽取 (Start Extraction)", variant="primary")
        
        with gr.Column(scale=2):
            status_output = gr.Textbox(label="状态 (Status)", interactive=False)
            json_output = gr.JSON(label="抽取结果 (Extraction Result)")

    submit_button.click(
        fn=extract,
        inputs=[file_input],
        outputs=[status_output, json_output]
    )
    
    gr.Markdown(
        """
        ### 关于此智能体
        这是一个任务型、状态机驱动的智能体，专为高可靠性的结构化数据抽取而设计。其核心价值在于其架构模式，包括自我修复和严格的校验机制。
        
        [查看GitHub仓库](https://github.com/yanzhao77/spec-extraction-agent)
        """
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
