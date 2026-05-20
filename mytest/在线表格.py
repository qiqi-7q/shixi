from flask import Flask, render_template_string

app = Flask(__name__)

# Luckysheet 开源在线表格编辑器（完全本地运行）
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Python本地在线表格</title>
    <!-- 加载CDN资源，国内可正常访问 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/luckysheet@3.0.0/dist/css/luckysheet.css">
    <script src="https://cdn.jsdelivr.net/npm/luckysheet@3.0.0/dist/luckysheet.umd.js"></script>
</head>
<body style="margin:0;">
    <div id="luckysheet" style="width:100vw;height:100vh;"></div>
    <script>
        luckysheet.create({
            container: 'luckysheet',
            lang: 'zh-cn', // 中文界面
            allowUpdate: true, // 允许编辑
            showtoolbar: true, // 显示工具栏
            showsheetbar: true // 显示工作表栏
        });
    </script>
</body>
</html>
"""

@app.route('/index')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    print("="*50)
    print("✅ 本地在线表格已启动！")
    print("📍 本地访问地址：http://127.0.0.1:5000")
    print("📍 局域网访问地址：把 127.0.0.1 换成你的电脑IP（比如 192.168.1.100:5000）")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=False)