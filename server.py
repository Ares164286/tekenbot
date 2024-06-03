from flask import Flask, request, jsonify
from threading import Thread
import logging

# Flask アプリケーションのインスタンスを作成
app = Flask(__name__)

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route('/')
def home():
    try:
        # クライアントがアクセスしてきた際にそのURLを返すエンドポイント
        url = request.base_url
        return jsonify(message=f'このページのURLは {url} です')
    except Exception as e:
        app.logger.error(f"Error in home endpoint: {e}")
        return jsonify(error="An error occurred"), 500

def run():
    try:
        # アプリケーションを指定のホストとポートで実行
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        app.logger.error(f"Error running server: {e}")

def keep_alive():
    try:
        # サーバーを別スレッドで実行し、メインスレッドがブロックされないようにする
        server = Thread(target=run)
        server.start()
    except Exception as e:
        app.logger.error(f"Error starting keep_alive: {e}")

# エラーハンドラー
@app.errorhandler(404)
def not_found(error):
    return jsonify(error="Not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(error="Internal server error"), 500
