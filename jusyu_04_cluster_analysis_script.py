# coding:cp932
#! C:\Python27\ArcGIS10.3\python.exe 

'''
Created on 2016/06/24

@author: 006022
'''

import random
import datetime
import os
import glob
import sys
import math
import numpy
import shutil
import Tkinter
import tkMessageBox
import tkFileDialog    

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
    
    algorythm = str(lines[0]).replace("\n","")
    cluster = str(lines[1]).replace("\n","")
    data_set = str(lines[2]).replace("\n","")
    ID = str(lines[3]).replace("\n","")
    iter_max = str(lines[4]).replace("\n","")
    input_path = str(lines[5]).replace("\n","").replace("\\", "/")
    output_path = str(lines[6]).replace("\n","").replace("\\", "/")
    
    
    
    key_word = algorythm[0]
    ylim = "1,255"
    cex_axis = "1.5"
    cex_main = "1.5"
    cluster_analysis_path = output_path + "\\" + "05_cluster_analysis"
    csv_path_v = cluster_analysis_path + "\\" + "01_csv"
    csv_path = csv_path_v.replace("\\", "/")
    plot_path_v = cluster_analysis_path + "\\" + "02_boxplot"
    plot_path = plot_path_v.replace("\\", "/")
    script_txt = cluster_analysis_path + "\\" + "R_script.txt"
    
    if os.path.exists(cluster_analysis_path) == False:
        os.mkdir(cluster_analysis_path)
    if os.path.exists(csv_path_v) == False:
        os.mkdir(csv_path_v)
    if os.path.exists(plot_path_v) == False:
        os.mkdir(plot_path_v)
    
    FIND_dbf = input_path + "\\" + "*" + ".dbf"
    dbf_list = glob.glob(FIND_dbf)
    
    f = open(script_txt,'w')
    f.write("library(foreign)" + "\n")
    for input_file in dbf_list:
        basename, ext = os.path.splitext( os.path.basename(input_file) )
        f.write("setwd(\"" + input_path + "\")" + "\n" + 
                "data <- read.dbf(\"" + input_path + "/" + basename + ".dbf\")" + "\n" + 
                "test <- data[,c(" + data_set + ")]" + "\n")
        
        ans = "ans_" + basename
        group = "group_" + basename
        f.write(ans + "<- kmeans(test, centers=" + str(cluster) + ", iter.max=" + iter_max + ", algorithm=" + "\"" + algorythm + "\")" + "\n" + 
                basename + "<- " + ans + "$cluster" + "\n" + 
                "shapeID <- data[," + ID + "]" + "\n" +
                "result <- data.frame(ID = shapeID, group = " + basename + ")" + "\n" + 
                "setwd(\"" + csv_path + "\")" + "\n" + 
                "write.csv(result,\"" + basename + ".csv\")" + "\n" +
                "group_test<- cbind(test, " + basename + ")" + "\n" + 
                "bygroup <- split(group_test, group_test$" + basename + ")" + "\n" + 
                "setwd(\"" + plot_path + "\")" + "\n")
        
        for i in range(1, int(cluster)+1):
            text1 = "png(\"" + basename + "_" + key_word + str(cluster) + "_" + str(i) + ".png\", width=400, height=350)"
            text2 = "par(mfrow=c(1,1))"
            plotdata = "bygroup$'" + str(i) + "'$mean3, bygroup$'" + str(i) + "'$mean2, bygroup$'" + str(i) + "'$mean1, bygroup$'" + str(i) + "'$mean4, bygroup$'" + str(i) + "'$mean_ndvi"
            names = "names = c(\"R\" , \"G\", \"B\", \"NIR\", \"NDVI\")"
            main = "main=\"" + basename + " " + str(cluster) + "分類　" + "グループ" + str(i) + "\"" 
            text3 = "boxplot(" + plotdata + "," + names + "," + main + "," + "ylim=c(" + ylim + ")" + "," + "cex.axis=" + cex_axis + "," + "cex.main=" + cex_main + "," + "range=0" + ")"
            
            f.write(text1 + "\n" + text2 + "\n" + text3 + "\n" + "dev.off()" + "\n")
    f.close()
      
    
    #--- 処理終了時間
    End_Time = datetime.datetime.now()
    elapsed_time = End_Time - Start_Time
    print ""
    print "処理時間：",(End_Time - Start_Time)
    print "終了時間：",End_Time.strftime("%Y-%m-%d %H:%M:%S")