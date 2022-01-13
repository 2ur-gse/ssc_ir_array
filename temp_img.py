##******************************************************************
##　ラズパイ用アレイセンサ評価ソフト　熱画像表示用モジュール
##
##　ファイル名：temp_img.py
##　作成日：2021/12/8
##
##　Ver.1.00			2021/12/8
##******************************************************************

##******************************************************************
##　外部ライブラリimport
##******************************************************************
import cv2 as cv
import numpy as np

##******************************************************************
##　モジュールimport
##******************************************************************
import cmr_map          ##8ビットカラーマップ


##******************************************************************
##
##　関数名：mapVal()
##　引数：val, inMin, inMax, outMin, outMax
##　戻値：(val - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
##
##　温度データを8bit(256段階)データに変換
##
##******************************************************************
def mapVal(val, inMin, inMax, outMin, outMax):
    return (val - inMin) * (outMax - outMin) / (inMax - inMin) + outMin


##******************************************************************
##
##　関数名：temp_img()
##　引数：temp_array,h_range, l_range   温度データ,最高レンジ、最低レンジ
##　戻値：無し
##
##　センサタイプ(画素数)により、表示サイズを切替
##　センサタイプ(画素数)により、表示方向を切替
##　入力温度レンジが異常時(最高<=最低)は最高>最低に値を修正する
##　温度からcmr_map.map(8ビットカラーマップ)を読出し、
##　最高レンジと最低レンジに合わせた色を選択する
##　
##******************************************************************
def temp_img(temp_array, h_range, l_range):
    
    ##  入力温度レンジが異常時(最高<=最低)は最高>最低に値を修正する
    if h_range <= l_range:
        l_range = h_range - 1
        
    else:
        pass                                                            ##  通常時はユーザー設定のまま反映
    
    
    ##  センサタイプに応じてサイズを設定
    if temp_array[0] == 1:
        rows = 32
        cellsize = 8

    else:
        rows = 8
        cellsize = 32
        
    
    ##  表示のための配列を作成
    img = np.full((cellsize*rows, cellsize*rows, 3), 128, dtype=np.uint8)

    pixels = np.array(temp_array[1:]).reshape(rows, rows).tolist()          ##  温度データだけを二次元アレイ型へ変換

    ##  32x32タイプは並び替え
    if temp_array[0] == 10:
        pixels = np.array(pixels).T.tolist()                            ##  90度回転
        pixels.reverse()                                                ##  反転
        
    else:
        pass
    
    ##--------------------------------
    ##  温度を256段階に変換し、熱画像化
    ##--------------------------------
    for x in range(rows):
        for y in range(rows):       
            val = mapVal(pixels[x][y], l_range, h_range, 0, 255)        ##  値を256範囲に変換する
            val = min(max(0, val), 255)                                 ##  値を256範囲に収める
    
            ##  カラーマップから温度に対応したカラーを選択し、イメージ化
            cv.rectangle(img, (x*cellsize, y*cellsize),\
                        (x*cellsize+cellsize, y*cellsize+cellsize),\
                        color = cmr_map.map[int(val)], thickness=-1)
    
    cv.namedWindow("HTPA",cv.WINDOW_KEEPRATIO)                          ##  ウィンドウサイズ変更可
    cv.imshow("HTPA",img)                                               ##  熱画像表示

    ##  Escキーが押されるまで待機
    ##  これが実行された段階でイメージが表示される
    if cv.waitKey(33) == 27:
        cv.destroyAllWindows()
        return