# coding:cp932
#! C:\Python27\ArcGIS10.3\python.exe 

'''
Created on 2016/06/24

@author: 006022
'''

import arcpy
from arcpy import env
import random
import datetime
import os
import zipfile
import glob
import arcpy
import datetime # datetimeモジュールのインポート
import arcpy
import os
import sys
import math
from arcpy.sa import *
import numpy
import arcpy, string
from arcpy import env
import glob
import shutil
import csv
import Tkinter
import tkMessageBox
import tkFileDialog
    
def unzip(filename, path):
    with zipfile.ZipFile(filename, 'r') as zip_file:
        zip_file.extractall(path)

#==================================================
#CSVからリストを作成
def CSVtoLIST(CSV):
    f = open(CSV, "r")
    for line in f:
        LIST = line.split(",")        
    #end for
    f.close()
    return LIST
#==================================================
#==================================================
#フォルダ直下のファイルのみ
def getFileList(path):
    file_list = []
    filenames = os.listdir(path)
    for file in sorted(filenames):
        file_list.append(os.path.join(path, file))
    return file_list
#==================================================
if __name__ == '__main__':
   

    #--- 処理開始時間
    Start_Time = datetime.datetime.now()
    print "開始時間：",Start_Time.strftime("%Y-%m-%d %H:%M:%S")
    #---
    
    root=Tkinter.Tk()
    root.withdraw()
    
    input_image_x = tkFileDialog.askopenfilename(title=u"図郭ごとに分割する画像を選択")
    input_image = str(input_image_x).replace("/", "\\")
    clip_feature = tkFileDialog.askopenfilename(title=u"分割に使用する図郭を選択　（画像範囲で切り出したものを使用する）")
    output_path_x = tkFileDialog.askdirectory(title=u"アウトプットデータを保存するフォルダを選択")
    output_path = str(output_path_x).replace("/", "\\")
    clip_feature_shp = str(clip_feature).replace("/", "\\")
    clip_feature_lyr = str(clip_feature_shp).replace(".shp", ".lyr")
    arcpy.MakeFeatureLayer_management(clip_feature, clip_feature_lyr)  
    rows = arcpy.SearchCursor(clip_feature_lyr) 
    for row in rows:
        name = row.getValue("NAME")
        image_zukaku = output_path + "\\" + name + ".tif"
        print image_zukaku
        selection = "\"" + "NAME\"" + " = " + "\'" + str(name) + "\'"
        arcpy.SelectLayerByAttribute_management(clip_feature_lyr, "NEW_SELECTION", selection)
        arcpy.Clip_management(input_image, "#", image_zukaku, clip_feature_lyr, "0", "ClippingGeometry")
  

    #--- 処理終了時間
    End_Time = datetime.datetime.now()
    elapsed_time = End_Time - Start_Time
    print ""
    print "処理時間：",(End_Time - Start_Time)
    print "終了時間：",End_Time.strftime("%Y-%m-%d %H:%M:%S")