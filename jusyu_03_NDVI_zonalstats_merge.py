# coding:cp932
'''
Created on 2016/06/24

@author: 006022
'''
import os
import datetime
import arcpy, string

from arcpy import env
from arcpy.sa import*
import shutil
import Tkinter
import tkMessageBox
import tkFileDialog
import glob

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
    arcpy.CheckOutExtension("spatial")
    root=Tkinter.Tk()
    root.withdraw()
    
    #========NDVI画像を作成して、領域分割shpファイルにゾーン統計する    
    
    HOME_PATH = tkFileDialog.askdirectory(title=u"処理する画像が入っているフォルダ、アウトプットデータを保存するフォルダの一階層上のフォルダを選択")
        
    #ゾーン統計する領域分割shpファイルが入っているフォルダ
    SEG_PATH = HOME_PATH + "\\" + "02_image_segmentation" + "\\" + "01_shp"         
    #NDVIを作成する元の画像が入っているフォルダ   
    TIFF_PATH = HOME_PATH + "\\" + "01_clip_image" + "\\" + "01_tiff_split"
    #NDVIフォルダ
    NDVI_PATH = HOME_PATH + "\\" + "03_ndvi"
    #NDVI画像フォルダ
    NDVI_IMAGE_PATH = NDVI_PATH + "\\" + "01_image"
    #ソーン統計処理の中間生成物のテーブルが格納されるフォルダ
    TABLE_PATH = NDVI_PATH + "\\" + "02_table"
    #tempファイルを入れとくフォルダ
    TEMP_PATH = NDVI_PATH + "\\" + "03_temp"
    
    
    #----フォルダがなければ作成する
    if os.path.exists(NDVI_PATH) == False:
        os.mkdir(NDVI_PATH)
    if os.path.exists(NDVI_IMAGE_PATH) == False:
        os.mkdir(NDVI_IMAGE_PATH)
    if os.path.exists(TABLE_PATH) == False:
        os.mkdir(TABLE_PATH)
    if os.path.exists(TEMP_PATH) == False:
        os.mkdir(TEMP_PATH)
        
    #----
    
    arcpy.env.workspace = TEMP_PATH
            
    #----NDVI画像の作成                         
    #INPUT_PATH にある全てのファイルを取得する
    all_file_list = getFileList(TIFF_PATH)
    
    #画像リストで繰り返し処理 
    for fname in all_file_list:
        basename, ext = os.path.splitext( os.path.basename(fname) ) 
        if ext == ".tif":
            #NDVI画像の名前を設定 
            ndvi = NDVI_IMAGE_PATH + "\\" + basename + "_NDVI" + ".tif"
            if os.path.exists(ndvi) == False:
                
                #NDVI計算
                NIR = arcpy.Raster(fname + "\Band_4")
                Red = arcpy.Raster(fname + "\Band_3")
                Num = arcpy.sa.Float(NIR - Red)
                Denom = arcpy.sa.Float(NIR + Red)
                NDVI = arcpy.sa.Divide(Num, Denom)                         
                NDVI_16bit = arcpy.sa.Float(((NDVI +1)* 255)/2)
                NDVI_16bit.save(ndvi)             
                print ndvi
    #----
    
            #----ゾーン統計
            #ゾーン統計するshpファイルの設定            
            seg_shp = SEG_PATH + "\\" + basename + ".shp"
            #中間生成物のテーブルのファイル名指定
            seg_dbf = TABLE_PATH + "\\" + basename + ".dbf"
            
            if os.path.exists(seg_dbf) == False:                
                #ゾーン統計をテーブルに出力 (Zonal Statistics as Table)平均と標準偏差
                arcpy.gp.ZonalStatisticsAsTable_sa(seg_shp, "shapeID", ndvi, seg_dbf, "DATA", "MEAN_STD")     
                print seg_dbf
                                
                #フィールド名の整理
                arcpy.AddField_management(seg_dbf,"mean_ndvi","DOUBLE",10,3)
                arcpy.AddField_management(seg_dbf,"std_ndvi","DOUBLE",10,3)
                arcpy.CalculateField_management(seg_dbf, "mean_ndvi" , "[MEAN]")
                arcpy.CalculateField_management(seg_dbf, "std_ndvi" , "[STD]")
                arcpy.DeleteField_management(seg_dbf, "MEAN")
                arcpy.DeleteField_management(seg_dbf, "STD")
                arcpy.DeleteField_management(seg_dbf, "AREA")
                arcpy.DeleteField_management(seg_dbf, "COUNT")      
                                         
                #テーブルをshpに結合する
                arcpy.JoinField_management(seg_shp, "shapeID", seg_dbf, "shapeID", ["mean_ndvi","std_ndvi"])     
                print seg_shp
            #----
    
    #図郭ごとにわかれている領域分割後shpファイルを画像ごとにマージして一つにする
    
    #マージしたshpファイル（NoData箇所除去済）を格納するフォルダ
    OUTPUT_SEG_PATH = HOME_PATH + "\\" + "04_shp_merged"
    #マージしたshpファイル（NoData除去前）
    shp_merged_with_nd = str(OUTPUT_SEG_PATH).replace("/", "\\")  + "\\" + "old"
        
    if os.path.exists(OUTPUT_SEG_PATH) == False:
        os.mkdir(OUTPUT_SEG_PATH)
    if os.path.exists(shp_merged_with_nd) == False:
        os.mkdir(shp_merged_with_nd)
   
    #=====
    FIND_SHP = SEG_PATH + "\\" + "*" + ".shp"
    shp_list = glob.glob(FIND_SHP)
    for shp in shp_list:
        shp_basename = os.path.basename(shp)
        word_count = len(shp_basename)
        end = word_count - 8
        file_name = shp_basename[0:end]
        #マージ後shpファイルの名前設定
        seg_merged_b = shp_merged_with_nd + "\\" + file_name + ".shp"
        seg_merged = str(OUTPUT_SEG_PATH).replace("/", "\\") + "\\" + file_name + ".shp"
        #まだマージしていなければマージ
        if os.path.exists(seg_merged) == False:
            #同じ画像ファイルから作ったshpファイルのリストを作成
            FIND_SEG = SEG_PATH + "\\" + file_name + "*" + ".shp"
            seg_list = glob.glob(FIND_SEG)
            #shpリストのファイルをマージ
            arcpy.Merge_management(seg_list, seg_merged_b)   
            seg_merged_lyr = shp_merged_with_nd + "\\" + file_name + "_merged.lyr"
            arcpy.MakeFeatureLayer_management(seg_merged_b, seg_merged_lyr)
            selection_1 = "\"" + "mean1\"" + " > " + "0"
            selection_2 = "\"" + "mean2\"" + " > " + "0"
            selection_3 = "\"" + "mean3\"" + " > " + "0"
            selection_4 = "\"" + "mean4\"" + " > " + "0" 
            arcpy.SelectLayerByAttribute_management(seg_merged_lyr, "NEW_SELECTION", selection_1)
            arcpy.SelectLayerByAttribute_management(seg_merged_lyr, "SUBSET_SELECTION", selection_2)
            arcpy.SelectLayerByAttribute_management(seg_merged_lyr, "SUBSET_SELECTION", selection_3)
            arcpy.SelectLayerByAttribute_management(seg_merged_lyr, "SUBSET_SELECTION", selection_4)
            arcpy.CopyFeatures_management(seg_merged_lyr, seg_merged)
            print seg_merged 
    
    #--- 処理終了時間
    End_Time = datetime.datetime.now()
    elapsed_time = End_Time - Start_Time
    print ""
    print "処理時間：",(End_Time - Start_Time)
    print "終了時間：",End_Time.strftime("%Y-%m-%d %H:%M:%S")

#--- End of Main ---