##******************************************************************
##　ラズパイ用アレイセンサ評価ソフト　通信用モジュール
##
##　ファイル名：com_sensor.py
##　作成日：2021/12/8
##
##　Ver.1.00			2021/12/8
##******************************************************************

##******************************************************************
##　外部ライブラリimport
##******************************************************************
from smbus2 import SMBus,i2c_msg
import time
import numpy as np
import datetime


##******************************************************************
##　global変数初期化
##******************************************************************
display_data = [0,0,0,0,0]
g_type = 0
    
##******************************************************************
##　定数
##******************************************************************
I2C_ADDR = 0x0A

##　各コマンド
START_CMD = 0x02
TAMB_CMD = 0x03
FPS_CMD = 0xF7
EP_CMD = 0xF2

##******************************************************************
##
##　関数名：ttar_measure()
##　引数：無し
##　戻値：temp      ターゲット温度データ
##
##　ターゲット温度を読出し、温度データに変換
##　センサタイプ(画素数)によって読出しサイズを切替
##
##******************************************************************
def ttar_measure():
    ##  global　変数宣言
    global g_type
    
    ##----------------------------------
    ##  センサタイプに応じて変数を初期化
    ##----------------------------------
    ##  32x32タイプ
    if g_type == 1:
        readbuffer = [0]*2048
        reso = 1024
        temp = [0]*1024
    ##  8x8タイプ
    else:
        readbuffer = [0]*128
        reso = 64
        temp = [0]*64
       
    ##  smbus(I2C)の通信コマンドを準備
    with SMBus(1) as bus:
        write = i2c_msg.write(I2C_ADDR, [START_CMD])
        read = i2c_msg.read(I2C_ADDR , reso*2+1)
        
        ##  ターゲット温度読出
        try:
            bus.i2c_rdwr(write,read)
            readbuffer = list(read)
            bus.close()  
        
        ##  エラー時の例外処理
        except:
            bus.close()
            print(datetime.datetime.now(), end="\t")
            print("To_I2C_ERR")
        
        ##  ℃へ変換
        for i in range(0,reso):
            temp[i] = ((readbuffer[i*2]) + (readbuffer[i*2+1] << 8 )) / 10.0
                
    return temp

##******************************************************************
##
##　関数名：tamb_measure()
##　引数：無し
##　戻値：tamb      周囲温度データ
##
##　ターゲット温度を読出し、温度データに変換
##　センサタイプ(画素数)から読出しサイズを切替
##
##******************************************************************
    
def tamb_measure():
    ##  変数を初期化
    tamb_buffer = [0]*2
    tamb = [0]
    ##  smbus(I2C)の通信コマンドを準備
    with SMBus(1) as bus:
        write = i2c_msg.write(I2C_ADDR , [TAMB_CMD])
        read = i2c_msg.read(I2C_ADDR , 2)

        ##  周囲温度読出
        try:
            bus.i2c_rdwr(write,read)
            tamb_buffer = list(read)
            bus.close()

        ##  エラー時の例外処理
        except:
            bus.close()
            print(datetime.datetime.now(), end="\t")
            print("Ta_I2C_ERR")

        ##  ℃へ変換
        tamb[0] = ((tamb_buffer[0]) + (tamb_buffer[1] << 8 )) / 10.0
    
    return tamb

##******************************************************************
##
##　関数名：measure()
##　引数：g_type
##　戻値：temp_data      現在時刻＋周囲温度＋ターゲット温度データ
##
##　ttar_measure()の実行
##　tamb_measure()の実行
##　現在時刻の取得
##　display_data     表示用データ(平均温度、周囲温度、最高画素温度、最低画素温度、温度ムラ)の作成
##　temp_data        現在時刻＋周囲温度＋ターゲット温度データの作成
##
##******************************************************************

def measure(array_type):
    ##  global　変数宣言
    global dispay_data
    global g_type

    g_type = array_type
    ttar = ttar_measure()
    tamb = tamb_measure()

    date_data = datetime.datetime.now()                             ##  現在時刻を格納
    temp_data = [date_data.strftime('%Y/%m/%d %H:%M:%S.%f')]        ##  温度データの先頭に変換した時刻を格納
    
    temp_data.extend(tamb)                                          ##  周囲温度を格納
    temp_data.extend(ttar)                                          ##  ターゲット温度を格納
    
    ##----------------------------------
    ##  表示用データ格納
    ##----------------------------------
    display_data[0] = round(sum(ttar)/len(ttar),1)                  ##  平均温度
    display_data[1] = tamb[0]                                       ##  周囲温度
    display_data[2] = max(ttar)                                     ##  最高画素温度
    display_data[3] = min(ttar)                                     ##  最低画素温度
    display_data[4] = round(max(ttar) - min(ttar),1)                ##  温度ムラ
    
    return temp_data

      
##******************************************************************
##
##　関数名：fps_write()
##　引数：w_fps     FPS設定値(書込み用)
##　戻値：r_fps    FPS設定値(読出し用)
##
##  センサタイプを確認し、32x32タイプは16Hz設定(非対応)を行わない
##  センサ情報が無い場合、sen_info()を実行しセンサ情報を取得
##　引数で指定されたFPS設定値をセンサーへ書込み
##　センサーFPS設定値の読出し
##
##******************************************************************

def fps_write(set_fps):
    ##  global　変数宣言
    global g_type

    with SMBus(1) as bus:
               
        ##  センサステータスを読出
        write = i2c_msg.write(I2C_ADDR, [FPS_CMD])
        read = i2c_msg.read(I2C_ADDR, 1)
        bus.i2c_rdwr(write, read)
        r_status = list(read)
        r_status = r_status[0]
        
        ##  32x32タイプの時、16Hzの設定要求を無視して終了する
        if g_type == 1:
            if set_fps == 16:
                print("32x32タイプは16Hzに設定出来ません")
                if r_status & 0b111 == 0b11:
                    r_fps = 8
                elif r_status & 0b111 == 0b10:
                    r_fps = 4
                elif r_status & 0b111 == 0b1:
                    r_fps = 2
                else:
                    r_fps = 1                  
                    
                return r_fps

            else:
                pass
        else:
            pass
        
        if set_fps == 16:
            w_fps = 0b100
            
        elif set_fps == 8:
            w_fps = 0b11
            
        elif set_fps == 4:
            w_fps = 0b10
            
        elif set_fps == 2:
            w_fps = 0b1
            
        else:
            w_fps = 0b0
        
        
        w_status = r_status & 0b11111000                                    ##  ステータスからFPS以外の部分の取出
        w_data = w_status | w_fps                                           ##  ステータスと新しいFPS設定値を結合
        
        ##  センサステータスを書込
        bus.write_i2c_block_data(I2C_ADDR, FPS_CMD, [w_data])
        ##  待機時間
        time.sleep(0.05)
        

        ##  再度センサステータスを読出
        write = i2c_msg.write(I2C_ADDR, [FPS_CMD])
        read = i2c_msg.read(I2C_ADDR, 1)
        bus.i2c_rdwr(write, read)
        status = list(read)
        bus.close()

        status = status[0]
        r_fps = (status & 0b111)                                           ##  ステータスからFPS設定値を取出
        
        ##  10進数設定値に変換

        if(r_fps==0x4):
            r_fps = 16
            
        elif(r_fps==3):
            r_fps = 8
            
        elif(r_fps==2):
            r_fps = 4
            
        elif(r_fps==1):
            r_fps = 2
            
        elif(r_fps==0):
            r_fps = 1

    return r_fps
        
##******************************************************************
##
##　関数名：epsilon_write()
##　引数：w_epsilon     放射率設定値(書込み用)
##　戻値：r_epsilon     放射率設定値(読出し用)
##
##　引数で指定された放射率設定値をセンサーへ書込み
##　センサー放射率設定値の読出し
##
##******************************************************************

def epsilon_write(w_epsilon):
    
    global r_epsilon
    
    ##　放射率設定値を2バイト値へ変換
    ep_setting = [w_epsilon & 0xFF, w_epsilon  >>8]

    with SMBus(1) as bus:
        ##　放射率設定値を書込
        bus.write_i2c_block_data(I2C_ADDR, EP_CMD, ep_setting)
        ##  待機時間
        time.sleep(0.05)
        
        ##　放射率設定値を読出
        write = i2c_msg.write(I2C_ADDR,[EP_CMD])
        read = i2c_msg.read(I2C_ADDR,2)
        bus.i2c_rdwr(write,read)
        status = list(read)
        bus.close()
        
        r_epsilon =((status[0])) + (status[1] << 8 )                        ##  ステータスから放射率設定値を取出
       
    return r_epsilon
        
################################################