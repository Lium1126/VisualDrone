# VisualDrone
This app provide operation for drone with GUI

# DEMO


# Requirement
 
- python3
- pyparrot 1.5.3
 
# Installation

## pyparrotのインストール

  [https://pyparrot.readthedocs.io/en/latest/installation.html](pyparrot installation)から引用
  
  1. 依存パッケージのインストール

    1. `untangle`パッケージをインストール

      xmlデータを`parrot SDK`用にパースするパッケージ

      ```bash
      pip install untangle
      ```

    2. `zeroconf`パッケージをインストール

      Wifi接続用パッケージ

      ```bash
      pip install zeroconf
      ```

    3. `pybluez`をインストール

      python版BLE接続用パッケージ(Linuxのみ・カメラ接続不可)

      ```bash
      sudo apt-get install bluetooth
      sudo apt-get install bluez
      sudo apt-get install python-bluez
      ```

    4. `bluepy`をインストール

      もう一つのBLE接続用パッケージ(先述の`pybluez`と両方必要

      ```bash
      sudo apt-get install python-pip libglib2.0-dev
      sudo pip install bluepy
      sudo apt-get update
      ```

  2. `pyparrot`のインストール

    1. ソースからインストール
      
      ```bash
      git clone https://github.com/amymcgovern/pyparrot
      cd pyparrot
      ```
    
    2. pipを使ってインストール
      
      ```bash
      pip install pyparrot
      ```
 
# Usage
 
DEMOの実行方法など、"hoge"の基本的な使い方を説明する
 
```bash
git clone https://github.com/Lium1126/VisualDrone
python3 VisualDrone2.py
```

# Author
 
* Yoshiya Suzuki
* Hamamatu Technical High School
* 2019 - 2021
