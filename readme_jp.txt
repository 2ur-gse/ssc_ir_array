※※※※※※※※※※※※※※※※※※※※※※※※※※※

初心者が作成しておりますので問題点等多々あるかと思いますが、
こちらに関しましては技術的なサポート・フォローは致しかねます。
あくまで参考情報として御活用ください

※※※※※※※※※※※※※※※※※※※※※※※※※※※

〇動作確認
ラズパイ３B＋
ラズパイ４

〇使い方
①ラズパイのI2Cを有効にする

②sudo nano /boot/config.txtでコンフィグ画面を表示する
③末尾に　dtparam=i2c_baudrate=250000　追記(I2C速度設定)
④さらに　core_freq=250　追記(ラズパイのクロック速度変動対策)
⑤CTRL+o、Enterで確定する

⑥I2C用ライブラリをインストールする
sudo pip3 install smbus2

⑦OpenCVをインストールする
##ラズパイをアップデートして再起動
sudo apt update
sudo apt autoremove
sudo apt upgrade -y
sudo reboot

#依存関係をインストール
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
#本題
sudo apt-get install python3-opencv

⑧CSV出力フォルダを準備する
home/pi/Documents/test_data/8x8
home/pi/Documents/test_data/32x32

⑨4つのpythonファイルをラズパイの適当な同一フォルダに保存
⑩main.pyを起動する