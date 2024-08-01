from flask import Flask, jsonify, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
import asyncio
from bleak import BleakScanner

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Bluetooth(db.Model):
    id #プライマリーキー
    user_name
    mac_address

# TODO: 1.ログイン、アーティクル関連を全て削除
#       2.supabaseとの接続を行う(上記のBluetoothのテーブル参照)
#       3.クライアントのルート、バックエンドのルートをそれぞれ二つにする
#       4.バックの中に書く処理は、bluetoothでの探索と探索に成功した場合にそのユーザー名とMACアドレスをDBへ書き込む(一つ目のルーティング)
#       5.もう一つのルーティングでユーザー名とアドレスの組合せ一覧を返す
#       6.それぞれのバックに対応するフロントを作成


# Bluetooth Signal Strength Detection
def calculate_distance(rssi, A=-50, n=2):
    return 10 ** ((A - rssi) / (10 * n))

async def get_bluetooth_signal_strength(target_device):
    devices = await BleakScanner.discover()
    device_signal_data = {}
    
    for device in devices:
        if device.address == target_device:
            try:
                signal_strength = device.rssi  # 信号強度（dBm）を取得
                distance = calculate_distance(signal_strength)  # 距離を計算
                device_signal_data[device.address] = {
                    'rssi': signal_strength,
                    'distance': distance
                }
            except Exception as e:
                device_signal_data[device.address] = str(e)
            break
    
    return device_signal_data

def fetch_signal_strengths(target_device):
    return asyncio.run(get_bluetooth_signal_strength(target_device))

@app.route('/bluetooth', methods=['GET'])
@login_required
def bluetooth_info():
    article_id = request.args.get('article_id')
    device_address = None
    if article_id:
        article = Article.query.get_or_404(article_id)
        device_address = article.content
    return render_template('bluetooth.html', device_address=device_address)

@app.route('/bluetooth_data', methods=['GET'])
@login_required
def bluetooth_data():
    device_address = request.args.get('device_address')
    signal_strengths = fetch_signal_strengths(device_address)
    return jsonify(signal_strengths)

@app.route('/articles')
@login_required
def articles():
    articles = Article.query.filter_by(user_id=current_user.id).all()
    return render_template('articles.html', articles=articles)

@app.route('/add_article', methods=['GET', 'POST'])
@login_required
def add_article():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        article = Article(title=title, content=content, user_id=current_user.id)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('articles'))
    return render_template('edit_article.html', article=None)

@app.route('/edit_article/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        db.session.commit()
        return redirect(url_for('articles'))
    return render_template('edit_article.html', article=article)

@app.route('/delete_article/<int:id>', methods=['POST'])
@login_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('articles'))

@app.route('/')
def root():
    return redirect(url_for('signup'))

if __name__ == '__main__':
    app.run(debug=True)