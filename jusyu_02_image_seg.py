# coding:cp932
#! C:\Python27\ArcGIS10.3\python.exe 

'''
Created on 2016/04/21

@author: 001603
'''
import datetime
import os
import codecs
import sys
import Tkinter
import tkMessageBox
import tkFileDialog



#============================
#指定パス内のファイルを全て返す関数
def getFileList(path):
    file_list = []
    for (root, dirs, files) in os.walk(path):
        for file in files:
            file_list.append(os.path.join(root,file))
    return file_list
#============================

if __name__ == '__main__':

    #--- 処理開始時間
    Start_Time = datetime.datetime.now()
    print "開始時間：",Start_Time.strftime("%Y-%m-%d %H:%M:%S")
    #---
    root=Tkinter.Tk()
    root.withdraw()
    fTyp_1=[('text', '*.txt')]
    
    parameter_file = tkFileDialog.askopenfilename(filetypes=fTyp_1, title=u"元にするパラメータファイルを選択")
    
    #テキストファイルの読み込み（1行毎にファイル終端まで全て読む、改行文字も含まれる）
    f = open(parameter_file)
    lines = f.readlines()
    f.close()    
    output_path = str(lines[1]).replace("\n","")
    segmentation_path = output_path + "\\" + "02_image_segmentation"
    segmentation_shp_path = segmentation_path + "\\" + "01_shp"
    parameter_path = segmentation_path + "\\" + "02_parameter"
    batch_file = segmentation_path + "\\" + "image_seg.bat"
    
    #----フォルダがなければ作成する
    if os.path.exists(segmentation_path) == False:
        os.mkdir(segmentation_path)
    if os.path.exists(segmentation_shp_path) == False:
        os.mkdir(segmentation_shp_path)
    if os.path.exists(parameter_path) == False:
        os.mkdir(parameter_path)
    #----   
        
    #----画像フォルダにある画像のリストを作って、繰り返し処理
    #INPUT_TIFF_Path にある全てのファイルを取得する
    input_image_path = str(lines[2]).replace("\n","")
    all_file_list = getFileList(input_image_path)
    
    #パラメータ準備
    line1 = str(lines[0]).replace("\n","")
    line4 = str(lines[3]).replace("\n","")
    line5 = str(lines[4]).replace("\n","")
    line6 = str(lines[5]).replace("\n","")
    exe_file = str(lines[6]).replace("\n","")
    
    for fname in all_file_list:
                
        basename, ext = os.path.splitext(os.path.basename(fname))
        if ext == ".tif":
            
            #フォルダ、ファイル名準備
            shp_file = segmentation_shp_path + "\\" + basename + ".shp"          
            text_file  = parameter_path  + "\\" + basename + ".txt"
            
            if os.path.exists(shp_file) == False:
                #パラメーターファイルの作成
                wfile2 = codecs.open(text_file, "w","cp932")
                wfile2.write(line1 + "\r\n")
                wfile2.write(shp_file + "\r\n" )
                wfile2.write(fname + "\r\n" )
                wfile2.write(line4 + "\r\n")
                wfile2.write(line5 + "\r\n")
                wfile2.write(line6 + "\r\n")
                wfile2.close()
                
                #バッチファイルの作成                            
                wfile1 = codecs.open(batch_file, "a","cp932")
                EXEC_PATH_FILENAME = exe_file
                wfile1.write(EXEC_PATH_FILENAME + " " + text_file + "\r\n")
                wfile1.write("echo %time% %time%" + "\r\n")
                wfile1.close()
                
   
    #--- 処理終了時間
    End_Time = datetime.datetime.now()
    elapsed_time = End_Time - Start_Time
    print ""
    print "処理時間：",(End_Time - Start_Time)
    print "終了時間：",End_Time.strftime("%Y-%m-%d %H:%M:%S")

#--- End of Main ---