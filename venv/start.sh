#!/bin/bash

# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 必要なパッケージをインストール
pip install -r requirements.txt

# Flaskアプリケーションを起動
python app.py