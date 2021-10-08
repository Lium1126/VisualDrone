#インポート======================================================================
import tkinter as tk
import math
from tkinter import *
from tkinter import ttk
from pyparrot.Minidrone import Mambo
try:
    from bluepy.btle import Scanner, DefaultDelegate
    BLEAvailable = True
except:
    BLEAvailable = False

#定義===========================================================================
#クラス--------------------------------------------------------------------
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)
#-------------------------------------------------------------------------

#定数----------------------------------------------------------------------
MAX_POINT_NUM = 30
COORDINATE_ORIGIN = 230 # 原点のx,y座標の値
PITCH = 27.78           # 初期値は50cm進むピッチ(sizeによって変更)
#-------------------------------------------------------------------------

#グローバル変数宣言----------------------------------------------------------
coordinate_x = [0]
coordinate_y = [0]
point_num = 1
mamboAddr = "e0:14:76:24:3d:d2"
mambo = Mambo(mamboAddr, use_wifi=False)
size = 3                # 実際のマップの1辺の長さ[m]
#-------------------------------------------------------------------------

#手続きの定義---------------------------------------------------------------
#マップ内でクリックを検出した---------------------------------
def map_click(event):
    global point_num
    
    # クリックされたところに円を描画し、座標を配列に追加
    if(point_num <= MAX_POINT_NUM): # ポイントの個数が最大値に達していない
        point_num += 1
        tag_name = "CircleAndLine%d" % point_num
        map_canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill = "black", width = 0, tags = tag_name)
        map_canvas.create_line(coordinate_x[point_num - 2] + COORDINATE_ORIGIN, coordinate_y[point_num - 2] + COORDINATE_ORIGIN, event.x, event.y, tags = tag_name)
        
        coordinate_x.append(event.x - COORDINATE_ORIGIN)
        coordinate_y.append(event.y - COORDINATE_ORIGIN)

    return
#--------------------------------------------------------

#ドローン飛行を実行する-------------------------------------
def flyDrone(self):
    self["text"] = "実行中..."

    global point_num
    global PITCH

    print("Trying to connect")
    success = mambo.connect(num_retries = 3)
    print("Connected: %s" % success)

    if(success and point_num > 1):
        print("Sleeping")
        mambo.smart_sleep(2)
        mambo.ask_for_state_update()
        mambo.smart_sleep(2)
        # 離陸
        print("Takeing off!")
        mambo.safe_takeoff(5)
        
        #now :現在着目している点
        #next:nowの次の点
        degree = 90.0 #スタート時は正面方向を向いているので90°で初期化
        i = 1
        while(i < point_num):
            '''-------------------------------------
            距離計算と角度計算に用いる情報を求める
            diff_x:2点間のx成分の差分
            diff_y:2点間のy成分の差分
            '''
            diff_x =  coordinate_x[i] - coordinate_x[i - 1]
            diff_y = -(coordinate_y[i] - coordinate_y[i - 1]) # 通常の平面と大小関係が逆なのでマイナスをつける
            #---------------------------------------

            '''-------------------------------------
            2点間の距離を計算する
            dist:2点間の距離
            '''
            dist = math.sqrt((diff_x ** 2 ) + (diff_y ** 2))
            #---------------------------------------
            
            '''-------------------------------------
            2点間の角度を計算する
            degree:nowから見たnextへの角度
            '''
            if(diff_x == 0 and diff_y > 0):
                temp_degree = 90.0
            elif(diff_x == 0 and diff_y < 0):
                temp_degree = 270
            else:
                temp_degree = round((math.degrees(math.atan2(diff_y, diff_x)) + 360) % 360) # 0 <= temp_degree < 360
                
            turn = (temp_degree - degree + 360) % 360 # turn:turn_degrees()に渡す引数
            if(turn > 180):
                turn = 180 - (turn - 180)
            else:
                turn = -turn
            #--------------------------------------
            
            # Mamboを飛行させる----------------------
            # 旋回方向の正負が座標平面と逆なのでturn()にはマイナスを渡す -> 変数turnで考慮済み
            # 旋回する角度の計算
            print("Flying [turn:%d distance:%f pitch:%f]" % (turn, dist, PITCH * (dist / 75.0)))
            mambo.turn_degrees(turn)
            mambo.fly_direct(roll = 0, pitch = PITCH * (dist / 75.0), yaw = 0, vertical_movement = 0, duration = 1)
            mambo.smart_sleep(1)
            #--------------------------------------
            
            now = next
            degree = temp_degree
            i += 1
            #endfor

        # ドローンを停止する-------------------------
        print("Landing...")
        mambo.safe_land(5)
        mambo.smart_sleep(5)
        
        print("Disconnect")
        mambo.disconnect()
        #----------------------------------------

        # ボタンに表示される文字列を元に戻す
        self["text"] = "実行"

    return
#-------------------------------------------------------

#最後にクリックされた点を削除する----------------------------
def deleteLastPoint(self):
    global point_num
    if(point_num > 1): # クリックした点が存在する
        del coordinate_x[point_num - 1]
        del coordinate_y[point_num - 1]
        tag_name = "CircleAndLine%d" % point_num
        map_canvas.delete(tag_name)
        point_num -= 1

    return
#-------------------------------------------------------

#全ての点を削除する----------------------------------------
def deleteAllPoint(self):
    global point_num
    while(point_num > 1): # クリックした点が存在する間
        del coordinate_x[point_num - 1]
        del coordinate_y[point_num - 1]
        tag_name = "CircleAndLine%d" % point_num
        map_canvas.delete(tag_name)
        point_num -= 1

    return
#-------------------------------------------------------

#マップのサイズ比変更を適用する------------------------------
def setSize(self):
    global size
    global PITCH
    
    # sizeを取得(1 <= size <= 5)
    size = sizeTextBox.get()
    size = float(size)
    if(size > 5.0):
        size = 5
    elif(size < 1.0):
        size = 1
    else:
        size = round(size)

    # sizeが影響を及ぼす変数を更新
    # PITCH=50:90[cm] = x:1マスの実際の大きさ[cm] より
    PITCH = ((size * 100 / 6.0) * 50) / 90
    
    # テキストボックス内を正しい内容に変更
    sizeTextBox.delete(0, tk.END)
    sizeTextBox.insert(0, size)

    print("set map size %d(pitch: %f)" % (size, PITCH))
    return
#-------------------------------------------------------

#接続可能なMamboを検知する---------------------------------
def searchMambo(self):
    self["text"] = "探索中..."
    
    # Mamboを探す
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(10.0)
    droneNum = 0
    mamboData = []
    
    for dev in devices:
        for (adtype, desc, value) in dev.getScanData():
            if (desc == "Complete Local Name"):
                if ("Mambo" in value): # Mamboを見つけた
                    droneNum += 1
                    # content = "%s(%s)" % (value, dev.addr)
                    content = dev.addr
                    mamboData.append(content)
                    print("FOUND A MAMBO!")
                    print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
                    print("  %s = %s" % (desc, value))
                    
    openSubWindow(mamboData, droneNum)
    self["text"] = "ドローンを探す"
#-----------------------------------------------------

#接続確認ウィンドウの表示---------------------------------
def openSubWindow(mamboData, droneNum):
    # Mamboの情報を表示するサブウィンドウの初期化
    findMessage = tk.Tk()
    findMessage.title("Visual Drone")
    findMessage.geometry("400x120")
    findMessage.resizable(0, 0)
    find_canvas = tk.Canvas(findMessage, width = 400, height = 120)
    find_canvas.place(x = 0, y = 0)

    if(droneNum != 0):
        # 表示したMamboに接続するか問う
        findLabel1 = tk.Label(find_canvas, text = "ドローンを発見しました。")
        findLabel1.place(x = 7, y = 10)
        findLabel2 = tk.Label(find_canvas, text = "接続するドローンを選択してください。")
        findLabel2.place(x = 8, y = 32)

        # 発見したドローンをコンボボックスで表示
        selectDrone = ttk.Combobox(findMessage, state = 'readonly')
        selectDrone.place(x = 7, y = 54)
        selectDrone["values"] = mamboData
        selectDrone.current(0)
        
        # 接続およびキャンセルボタン
        connectDrone = tk.Button(findMessage, text = "接続", compound = TOP, command = lambda : connectMambo(selectDrone.get(), findMessage))
        connectDrone.place(x = 230, y = 83)
        connectCancel = tk.Button(findMessage, text = "キャンセル", compound = TOP, command = lambda : findMessage.destroy())
        connectCancel.place(x = 290, y = 83)

    else:
        # 1台もMAMBOが発見できなかった場合
        findLable1 = tk.Label(find_canvas, text = "ドローンを発見できませんでした。")
        findLable1.place(x = 7, y = 10)

        # サブウィンドウを閉じるボタン
        connectCancel = tk.Button(findMessage, text = "OK", compound = TOP, command = lambda : findMessage.destroy())
        connectCancel.place(x = 335, y = 83)

    return
#-----------------------------------------------------

#接続先のMamboを変更する---------------------------------
def connectMambo(devAddr, subWindow):
    global mamboAddr
    global mambo
    
    mamboAddr = devAddr
    mambo = Mambo(mamboAddr, use_wifi=False)

    print("Change:Target of connect = %s" % devAddr)
    subWindow.destroy()
#-----------------------------------------------------

#プログラム本体==================================================================
#メイン-------------------------------------------------------------------
#ウィンドウを作る-----------------------------
root = tk.Tk()
root.title("Visual Drone")
root.geometry("800x566")
root.resizable(0, 0)

# 背景用Canvasを作る
bg_canvas = tk.Canvas(root, width = 800, height = 566, bg = "#0c2550")
bg_canvas.place(x = 0, y = 0)
#-------------------------------------------

#画像(マップ)表示-----------------------------
# マップ用Canvasを作る
map_canvas = tk.Canvas(root, width = 460, height = 460, bg = "white")
map_canvas.place(x = 30, y = 27)

# 画像表示
maps = tk.PhotoImage(file = "map.png")
map_canvas.create_image(0, 0, image = maps, anchor=tk.NW)
#------------------------------------------

#各ボタンを配置------------------------------
# ボタンを配置
Icon_search = PhotoImage(file = "Icon_search.png")
searchDrone = tk.Button(root, image = Icon_search, text = "ドローンを探す", compound = TOP, command = lambda : searchMambo(searchDrone))
searchDrone.place(x = 510, y = 10)

Icon_takeoff = PhotoImage(file = "Icon_takeoff.png")
takeOff = tk.Button(root, image = Icon_takeoff, text = "実行", compound = TOP, command = lambda : flyDrone(takeOff))
takeOff.place(x = 510, y = 150)

Icon_undo = PhotoImage(file = "Icon_undo.png")
unDo = tk.Button(root, image = Icon_undo, text = "取り消し", compound = TOP, command = lambda : deleteLastPoint(unDo))
unDo.place(x = 510, y = 290)

Icon_clear = PhotoImage(file = "Icon_clear.png")
clearPoint = tk.Button(root, image = Icon_clear, text = "全消去", compound = TOP, command = lambda: deleteAllPoint(clearPoint))
clearPoint.place(x = 510, y = 430)
#-----------------------------------------

# マップとリアルのサイズ比を調整する箇所のUI-----
# キャンバスの作成
map_size_canvas = tk.Canvas(root, width = 460, height = 50, bg = "white")
map_size_canvas.place(x = 30, y = 489)
# 直線を引く
map_size_canvas.create_line(3, 3, 3, 27)
map_size_canvas.create_line(457, 3, 457, 27)
map_size_canvas.create_line(3, 15, 200, 15)
map_size_canvas.create_line(260, 15, 457, 15)
# テキストボックス周りの表示
sizeLabel = tk.Label(text = 'メートル', bg = "white")
sizeLabel.place(x = 250, y = 495)
sizeTextBox = tk.Entry(width = 3)
sizeTextBox.place(x = 228, y = 495)
sizeTextBox.insert(0, size)
# 適用ボタンの配置
sizeEnter = tk.Button(map_size_canvas, text = "適用", compound = TOP, command = lambda: setSize(sizeTextBox))
sizeEnter.place(x = 400, y = 25)
#-----------------------------------------

# マップクリック時のイベントを設定する
map_canvas.bind("<Button-1>", map_click)

root.mainloop()
