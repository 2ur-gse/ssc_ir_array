##******************************************************************
##　ラズパイ用アレイセンサ評価ソフト　メインGUI
##
##  ※ラズパイはI2Cクロックが不安定になることがあるので、
##  　200～300kHz設定を推奨
##
##　ファイル名：main.py
##　作成日：2021/12/8
##
##　Ver.1.00			2021/12/8
##******************************************************************

##******************************************************************
##　外部ライブラリimport
##******************************************************************

import tkinter as tk
import time
import datetime as dt
import pathlib
import csv
import datetime
import threading as th
import copy

##  cv2使用前に以下をインストールすること
##  sudo pip3 install opencv-python==4.1.0.25
##  sudo apt-get install libatlas-base-dev
##  sudo apt-get install libjasper-dev
##  sudo apt-get install qt4-dev-tools qt4-doc qt4-qtconfig libqt4-test
import cv2 as cv

##******************************************************************
##　モジュールimport
##******************************************************************

import com_sensor
import temp_img

##******************************************************************
##　global変数初期化
##******************************************************************

g_start_stop = 0                                                    ##  スタート状態フラグ
g_elapsed_time = "00:00:00"                                         ##  経過時間
g_frame_count = 0                                                   ##　カウントアップフレーム数
g_old_data = []                                                     ##  比較用前フレーム温度
g_log_mode = 0                                                      ##  ログモード設定フラグ
g_set_fps = 2
g_set_epsilon = 1000
g_array_type = 0

##******************************************************************
##
##　関数名：fps_button()
##　引数：set_fps
##　戻値：無し
##
##　FPS設定ボタンを押したときに実行される関数
##  FPS書込み関数の実行と画面へ設定値の表示を行う
##
##******************************************************************

def fps_button(set_fps):
    ##  global　変数宣言
    global g_set_fps
    
    g_set_fps = com_sensor.fps_write(set_fps)
    
    ##  時間と設定値を表示
    print(datetime.datetime.now(), end="\t")
    print("FPS: " + str(g_set_fps) + "Hz")

    label13["text"] = "FPS:" + str(g_set_fps) + "Hz"

    return
    
##******************************************************************
##
##　関数名：epsilon_button()
##　引数：set_epsilon
##　戻値：無し
##
##  放射率設定ボタンを押したときに実行される関数
##　放射率書込み関数の実行と画面へ設定値の表示を行う
##
##******************************************************************

def epsilon_button(set_epsilon):
    ##  global　変数宣言
    global g_set_epsilon
    
    g_set_epsilon = com_sensor.epsilon_write(set_epsilon)
    
    ##  時間と設定値を表示
    print(datetime.datetime.now(), end="\t")
    print("e: ", g_set_epsilon/1000)

    label14["text"] = "e:" + str(g_set_epsilon/1000)
    
    return

##******************************************************************
##
##　関数名：kensa_start()
##　引数：無し
##　戻値：無し
##
##　スタートボタン実行時に1度実行される関数
##　com_sensor.sen_info()を実行し、センサー情報を読み取る
##　ログの要否を判断し、CSVファイルを作成
##　kensa_loop()の実行
##
##******************************************************************
def kensa_start():
    ##  global　変数宣言
    global g_start_stop
    global g_start_time
    global g_time_delta
    global file_path
    global g_frame_count
    global g_bln
    global g_log_mode
    global g_set_fps
    global g_set_epsilon
    global g_array_type
    
    if g_start_stop == 1:
        return
    
    else:
        pass
    
    g_start_stop = 1                                                ##  スタート状態を有効にセット
    time_delta = 0                                                  ##  経過時間をリセット
    g_frame_count = 0                                               ##  フレームカウントをリセット


    g_array_type = type_val.get()                                   ##  アレイタイプを取得
    
    ##  取得したアレイタイプに応じて名称をセット
    if g_array_type == 0:
        array_type = "8x8"
    
    else:
        array_type = "32x32"
    

    ##  ログモード有効時はCSV書込み用データを準備
    if g_bln.get():
        g_log_mode = 1
        
        ##  ヘッダーを作成
        header = ","+","+","+","+","
   
        
        ##　アレイタイプに応じてヘッダーの画素数を設定
        if g_array_type == 1:
            for k in range(0,1024):
                header += str(k) + ","
        
        elif g_array_type == 0:
            for k in range(0,64):
                header += str(k) + ","

        else:
            pass
         
        header += "\n"


        ##--------------------------------
        ##  ログ用CSVファイルを新規作成
        ##--------------------------------
        now = dt.datetime.now()                                         ##  現在時刻を取得
        ##  YYYYMMDD-hhmmss形式に時刻を変換変換
        ##  アレイタイプ毎にフォルダを指定
        ##  アレイタイプと現在時刻からファイル名を作成
        file_path = "/home/pi/Documents/test_data/"+ array_type + "/" \
                    + array_type +f'_{now:%Y%m%d-%H%M%S}.csv'
       
        f =  open(file_path, 'a')                                       ##  CSVを新規作成し開く
        f.write(str(header))                                            ##  CSV書込
        f.close()
        
        label12["text"] = str(file_path)                                ##  保存先フォルダとファイル名を表示する
    
    ##  ログモードが無効時
    else:
        g_log_mode = 0
        
        label12["text"] = " "                                           ##  保存先フォルダとファイル名表示をクリアする
    
    
    
    g_set_fps = com_sensor.fps_write(g_set_fps)                         ##  FPSを設定
    label13["text"] = "FPS:" + str(g_set_fps) + "Hz"                    ##  FPS設定値を表示
    
    g_set_epsilon = com_sensor.epsilon_write(g_set_epsilon)             ##  放射率を設定
    label14["text"] = "e:" + str(g_set_epsilon/1000)                    ##  放射率設定値を表示 

    g_start_time = time.time()                                          ##  開始時間を格納する

    ##  時間とスタートを表示
    print(dt.datetime.now()   , end="\t")
    print("START")
    
    ##  kensa_loopをスタートする
    kensa_loop()
    
    return

##******************************************************************
##
##　関数名：kensa_stop()
##　引数：無し
##　戻値：無し
##
##　ストップボタン実行時に1度実行される関数
##　熱画像のウィンドウをクローズし、kensa_loop()を停止する
##
##******************************************************************

def kensa_stop():
    ##  global　変数宣言
    global g_start_stop
    
    if g_start_stop == 1:
        cv.destroyAllWindows()                                              ##  熱画像のウィンドウをクローズする
        g_start_stop = 0

        ##  時間とストップを表示
        print(dt.datetime.now()   , end="\t")
        print("STOP")

    else:
        pass
    
    return
    
##******************************************************************
##
##　関数名：kensa_loop()
##　引数：無し
##　戻値：無し
##
##　kensa_start()実行後に繰り返し実行される関数
##　com_sensor.measure()を実行し、アレイセンサから温度データを取り出す
##　前フレームデータとの比較、重複時はデータの破棄
##　経過時間、温度表示の更新
##　CSVファイルの出力
##　熱画像を表示する為のtemp_img.temp_img()へ温度データを渡し、実行
##　指定時間後にkensa_loop()の再起呼び出し
##
##******************************************************************
def kensa_loop():
    ##  global　変数宣言
    global g_start_stop
    global g_elapsed_time
    global file_path
    global g_frame_count
    global g_log_mode
    global g_array_type
    global g_old_data
    global g_set_fps
    
    if g_start_stop == 1:                                         ##  スタート有効状態
        
        time_now = time.time()                                      ##　現在時刻取得
        time_delta = time_now - g_start_time                        ##　経過時間算出
        
        ##  経過時間を時間、分、秒毎に分割
        elapsed_hour = int(time_delta // 3600)
        elapsed_minute = int((time_delta % 3600) // 60)
        elapsed_second = int((time_delta % 3600 % 60) )

        ##  hh:mm:ss形式に文字列で変換
        g_elapsed_time = (str(elapsed_hour).zfill(2) + ":" \
                        + str(elapsed_minute).zfill(2) + ":" \
                        + str(elapsed_second).zfill(2))
        ##  I2Cで温度データを取り込み              
        data_array = com_sensor.measure(g_array_type)
        
        ##  経過時間の表示を更新
        label1["text"] = str(g_elapsed_time)
        
        ##  0:8ピクセルの温度を前フレームと比較
        if data_array[2:10] == g_old_data[0:8]:
            time.sleep(0.04)
            pass                                                    ##  重複時は何もしない
        
        ##  重複しない時の処理
        else:                                                       
            g_frame_count += 1                                      ##  フレーム数をカウントアップ
            
            ##  ログモードが有効時はCSV書込み用データを作成
            if g_log_mode == 1:
                csv_data = copy.copy(data_array)                    ##  取り込んだ温度データ(時間、Ta、To)を格納
                csv_data[1:1] = [g_frame_count]                     ##  フレームカウント数を1列目に挿入
                csv_data[2:2] = ["Ta:"]                             ##  文字列"Ta:"を2列目に挿入
                csv_data[4:4] = ["Pixel:"]                          ##  文字列"Pixel:"を2列目に挿入
                
                ##  準備した書込み用データをCSVの末尾に追記する
                with open(file_path,'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(csv_data)
             
            else:
                pass                                                ##  ログモード無効時は何もしない

            g_old_data = data_array[2:10]                           ##  現在の温度データを過去の比較用データに格納
            
            label2["text"] = str(g_frame_count)                     ##  フレームカウント数の表示を更新
            label3["text"] = str(com_sensor.display_data[0])        ##  平均温度表示を更新
            label4["text"] = str(com_sensor.display_data[1])        ##  周囲温度表示を更新
            label5["text"] = str(com_sensor.display_data[2])        ##  最高温度表示を更新
            label6["text"] = str(com_sensor.display_data[3])        ##  最低温度表示を更新
            label7["text"] = str(com_sensor.display_data[4])        ##  最高-最低(温度ムラ)を表示を更新
            
            
            ##--------------------------------
            ##  温度レンジ設定値を取得
            ##--------------------------------
            max_val = scale_max.get()                               ##  MAXトラックバー
            min_val = scale_min.get()                               ##  MINトラックバー
            
            
            temp_array = [g_array_type]                             ##  センサタイプをリストに格納
            
            temp_array.extend(data_array[2:])                       ##  ターゲット温度のみをリストに追加格納
            
            ##--------------------------------
            ##  スレッド2で温度表示を実行
            ##--------------------------------
            th2 =  th.Thread(target=temp_img.temp_img(temp_array, max_val, min_val))
            th2.start()
            
            
        root.after(2, kensa_loop)                                  ##  指定msec後に再起呼出
        
    else:
        pass                 

    return

##******************************************************************
##　メイン
##******************************************************************

##--------------------------------
##	フォントプリセット
##--------------------------------
font_set0 = ("IPAexゴシック Regular", "16", "normal")
font_set1 = ("IPAexゴシック Regular", "24", "normal")
font_set2 = ("IPAexゴシック Regular", "30", "normal")
font_set3 = ("IPAexゴシック Regular", "14", "normal")
font_set4 = ("IPAexゴシック Regular", "11", "normal")

##--------------------------------
##	widthプリセット
##--------------------------------
w_set0 = 9
w_set1 = 1
w_set2 = 20
w_set3 = 3
w_set4 = 0

##--------------------------------
##	メインウィンドウ
##--------------------------------
root = tk.Tk()                                                      ##  tkinterGUIを準備
root. title("IR Array Tester")                                      ##  GUIタイトル

##--------------------------------
##	経過時間表示部
##--------------------------------
tk.Label(root, text="経過時間",anchor="w",padx=5, pady=5,font=font_set2,)\
.grid(rowspan=2, columnspan=4, row=0, column=0)

tk.Label(root, text=":",anchor="w",padx=1, pady=5,font=font_set2,)\
.grid(rowspan=2, columnspan=1, row=0, column=4)

label1 = tk.Label(root, text="00:00:00",anchor="w",pady=20,font=font_set2,)
label1.grid(rowspan=2, columnspan=4, row=0, column=5)

##--------------------------------
##	フレームカウント表示部
##--------------------------------
tk.Label(root, text="フレーム数", padx=5, pady=5,font=font_set1,)\
.grid(rowspan=2, columnspan=4, row=2, column=0)

tk.Label(root, text=":", padx=1, pady=5,font=font_set2,)\
.grid(rowspan=2, columnspan=1, row=2, column=4)

label2 = tk.Label(root, text="0", pady=20,font=font_set2,)
label2.grid(rowspan=2, columnspan=4, row=2, column=5)

##--------------------------------
##	平均温度表示部
##--------------------------------
tk.Label(root, text="TtarAvg", padx = w_set0, pady=10,font=font_set0)\
.grid(rowspan=1, columnspan=1, row=4, column=0 ,sticky="E")

tk.Label(root, text=":", padx= w_set1, pady=10, font=font_set0)\
.grid(rowspan=1, columnspan=1, row=4, column=1)

label3 = tk.Label(root, text= " ", padx=w_set2, pady=10,font=font_set0)
label3.grid(rowspan=1, columnspan=1, row=4, column=2)

tk.Label(root, text= "℃", padx= w_set3, pady=10,font=font_set0)\
.grid(rowspan=1, columnspan=1, row=4, column=3)

##--------------------------------
##	周囲温度表示部
##--------------------------------
tk.Label(root, text="Tamb", padx = w_set0, pady=11,font=font_set0)\
                       .grid(rowspan=1, columnspan=1, row=4, column=5 ,sticky="E")
tk.Label(root, text=":", padx= w_set1, pady=10,font=font_set0)\
                        .grid(rowspan=1, columnspan=1, row=4, column=6)

label4 = tk.Label(root, text=" ", padx=w_set2, pady=10,font=font_set0)
label4.grid(rowspan=1, columnspan=1, row=4, column=7)

tk.Label(root, text="℃",padx= w_set3, pady=10,font=font_set0)\
                       .grid(rowspan=1, columnspan=1, row=4, column=8)

##--------------------------------
##	最高温度表示部
##--------------------------------
tk.Label(root, text="Tmax", padx= w_set0, pady=10,font=font_set0)\
                        .grid(rowspan=1, columnspan=1, row=5, column=0 ,sticky="E")
tk.Label(root, text=":", padx= w_set1, pady=10,font=font_set0)\
                        .grid(rowspan=1, columnspan=1, row=5, column=1)

label5 = tk.Label(root, text=" ", padx = w_set2, pady=10,font=font_set0)
label5.grid(rowspan=1, columnspan=1, row=5, column=2)

tk.Label(root, text= "℃", padx= w_set3, pady=10,font=font_set0)\
                        .grid(rowspan=1, columnspan=1, row=5, column=3)

##--------------------------------
##	最低温度表示部
##--------------------------------
tk.Label(root, text="Tmin", padx= w_set0, pady=10,font=font_set0)\
                       .grid(rowspan=1, columnspan=1, row=5, column=5 ,sticky="E")
tk.Label(root, text=":", padx= w_set1, pady=10,font=font_set0)\
                       .grid(rowspan=1, columnspan=1, row=5, column=6)

label6 = tk.Label(root, text=" ", padx= w_set2, pady=10, font=font_set0)
label6.grid(rowspan=1, columnspan=1, row=5, column=7)

tk.Label(root, text="℃", padx= w_set3, pady=10,font=font_set0)\
                       .grid(rowspan=1, columnspan=1, row=5, column=8)

##--------------------------------
##	温度ムラ(最高-最低)表示部
##--------------------------------
tk.Label(root, text="Tmax-min", padx= w_set0, pady=10,font=font_set0)\
                       .grid(rowspan=1, columnspan=2, row=6, column=4 ,sticky="E")
tk.Label(root, text=":", padx= w_set1, pady=10,font=font_set0)\
                       .grid(rowspan=1, columnspan=1, row=6, column=6)

label7 = tk.Label(root, text=" ", padx= w_set2, pady=10,font=font_set0)
label7.grid(rowspan=1, columnspan=1, row=6, column=7)

tk.Label(root, text="℃", padx= w_set3, pady=10,font=font_set0)\
                       .grid(rowspan=1, columnspan=1, row=6, column=8)


label13 = tk.Label(root, text=" ", pady=10, font=font_set4,)
label13.grid(rowspan=1, columnspan=1, row=6, column=0, sticky="W")

label14 = tk.Label(root, text=" ", pady=10, font=font_set4,)
label14.grid(rowspan=1, columnspan=2, row=6, column=1, sticky="W")


tk.Label(root, text=" ", pady=12, font=font_set4,).grid(rowspan=1, columnspan=1, row=8, column=0, sticky="E")
tk.Label(root, text=" ", pady=12, font=font_set4,).grid(rowspan=1, columnspan=1, row=9, column=0, sticky="E")
tk.Label(root, text=" ", pady=12, font=font_set4,).grid(rowspan=1, columnspan=1, row=10, column=0, sticky="E")


##########################################################
##--------------------------------
##	メインボタン
##--------------------------------
##　スタート
tk.Button(root, text="START", padx=30, pady=15,font=font_set1, command=lambda :kensa_start())\
                    .grid(rowspan=2, columnspan=2, row=0,column=12)
##　ストップ
tk.Button(root, text="STOP", padx=37, pady=15,font=font_set1, command=lambda :kensa_stop())\
                    .grid(rowspan=2, columnspan=2, row=2,column=12)

##--------------------------------
##	放射率設定ボタン
##--------------------------------
tk.Label(root, text="-e-", padx=20, pady=1, font=font_set0,).grid(row=4, column=13, sticky="S")
tk.Button(root, text=u'1.00', padx=10, pady=4, font=font_set0,command=lambda:epsilon_button(1000))\
                    .grid(rowspan=1, columnspan=2, row=5,column=13)
tk.Button(root, text=u'0.98', padx=10, pady=4, font=font_set0,command=lambda:epsilon_button(980))\
                    .grid(rowspan=1, columnspan=2, row=6,column=13)
tk.Button(root, text=u'0.95', padx=10, pady=4, font=font_set0,command=lambda:epsilon_button(950))\
                    .grid(rowspan=1, columnspan=2, row=7,column=13)
tk.Button(root, text=u'0.90', padx=10, pady=4, font=font_set0,command=lambda:epsilon_button(900))\
                    .grid(rowspan=1, columnspan=2, row=8,column=13)
tk.Button(root, text=u'0.80', padx=10, pady=4, font=font_set0,command=lambda:epsilon_button(800))\
                    .grid(rowspan=1, columnspan=2, row=9,column=13)

##--------------------------------
##	FPS設定ボタン
##--------------------------------
tk.Label(root, text="       -FPS-", padx=16, pady=1, font=font_set0,).grid(row=4, column=11, sticky="S")
tk.Button(root, text=u'16Hz', padx=14, pady=4, font=font_set0,command=lambda:fps_button(16))\
                    .grid(rowspan=1, columnspan=2, row=5,column=11)
tk.Button(root, text=u'8Hz', padx=20, pady=4, font=font_set0,command=lambda:fps_button(8))\
                    .grid(rowspan=1, columnspan=2, row=6,column=11)
tk.Button(root, text=u'4Hz', padx=20, pady=4, font=font_set0,command=lambda:fps_button(4))\
                    .grid(rowspan=1, columnspan=2, row=7,column=11)
tk.Button(root, text=u'2Hz', padx=20, pady=4, font=font_set0,command=lambda:fps_button(2))\
                    .grid(rowspan=1, columnspan=2, row=8,column=11)
tk.Button(root, text=u'1Hz', padx=20, pady=4, font=font_set0,command=lambda:fps_button(1))\
                    .grid(rowspan=1, columnspan=2, row=9,column=11)

##--------------------------------
##	温度レンジ設定トラックバー
##--------------------------------
##　MAX
tk.Label(root, text="MAX", padx=20, pady=10, font=font_set0,).grid(row=8, column=0, )
scale_max = tk.Scale(root, orient=tk.HORIZONTAL, from_=0, to=250, length=400, width=20)
scale_max.grid(rowspan=1, columnspan=9, row=8,column=1)
scale_max.set(35)                                                   ##  初期値は35℃にセット
##　MIN
tk.Label(root, text="MIN", padx=20, pady=8, font=font_set0,).grid(rowspan=2, row=9, column=0, )
scale_min = tk.Scale(root, orient=tk.HORIZONTAL, from_=0, to=250, length=400, width=20, tickinterval=50)
scale_min.grid(rowspan=2, columnspan=9, row=9,column=1)
scale_min.set(15)                                                   ##  初期値は15℃にセット

##--------------------------------
##	ログ出力設定チェックボックス
##--------------------------------
##　チェックボックス
g_bln = tk.BooleanVar()
g_bln.set(False)                                                     ##  初期設定
c_button0 = tk.Checkbutton(root, variable=g_bln, text="Record", padx=10, pady=5, font=font_set4, width=0)
c_button0.grid(rowspan=1, columnspan=2, row=11,column=0, sticky="W")
##　出力ファイル名表示部
label12 = tk.Label(root, text=" ", padx=w_set0, pady=10, font=font_set4,)
label12.grid(rowspan=1, columnspan=12, row=11, column=1, sticky="W")

##--------------------------------
##	アレイセンサタイプ選択ボタン
##--------------------------------
tk.Label(root, text="Type:", font=font_set0).grid(row=7, column=0)

type_val = tk.IntVar()
type_val.set(0)                                                     ##  初期設定

##  8x8
type_btn1 = tk.Radiobutton(root, value=0, variable=type_val, text="8x8", font=font_set0,)
type_btn1.grid(rowspan=1, columnspan=2,row=7, column=1, )
##  32x32
type_btn2 = tk.Radiobutton(root, value=1, variable=type_val, text="32x32", font=font_set0,)
type_btn2.grid(rowspan=1, columnspan=2,row=7, column=5, )


th1 =  th.Thread(target=root.mainloop())
th1.start()