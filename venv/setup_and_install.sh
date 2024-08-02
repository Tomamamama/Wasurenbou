#!/bin/bash

# 仮想環境の作成
python -m venv venv

# 仮想環境をアクティブにする
source venv/bin/activate

# パッケージのインストール
pip install -r requirements.txt