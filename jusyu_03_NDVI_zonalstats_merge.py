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
#�t�H���_�����̃t�@�C���̂�
def getFileList(path):
    file_list = []
    filenames = os.listdir(path)
    for file in sorted(filenames):
        file_list.append(os.path.join(path, file))
    return file_list
#==================================================

if __name__ == '__main__':

    #--- �����J�n����
    Start_Time = datetime.datetime.now()
    print "�J�n���ԁF",Start_Time.strftime("%Y-%m-%d %H:%M:%S")
    #---
    arcpy.CheckOutExtension("spatial")
    root=Tkinter.Tk()
    root.withdraw()
    
    #========NDVI�摜���쐬���āA�̈敪��shp�t�@�C���Ƀ]�[�����v����    
    
    HOME_PATH = tkFileDialog.askdirectory(title=u"��������摜�������Ă���t�H���_�A�A�E�g�v�b�g�f�[�^��ۑ�����t�H���_�̈�K�w��̃t�H���_��I��")
        
    #�]�[�����v����̈敪��shp�t�@�C���������Ă���t�H���_
    SEG_PATH = HOME_PATH + "\\" + "02_image_segmentation" + "\\" + "01_shp"         
    #NDVI���쐬���錳�̉摜�������Ă���t�H���_   
    TIFF_PATH = HOME_PATH + "\\" + "01_clip_image" + "\\" + "01_tiff_split"
    #NDVI�t�H���_
    NDVI_PATH = HOME_PATH + "\\" + "03_ndvi"
    #NDVI�摜�t�H���_
    NDVI_IMAGE_PATH = NDVI_PATH + "\\" + "01_image"
    #�\�[�����v�����̒��Ԑ������̃e�[�u�����i�[�����t�H���_
    TABLE_PATH = NDVI_PATH + "\\" + "02_table"
    #temp�t�@�C�������Ƃ��t�H���_
    TEMP_PATH = NDVI_PATH + "\\" + "03_temp"
    
    
    #----�t�H���_���Ȃ���΍쐬����
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
            
    #----NDVI�摜�̍쐬                         
    #INPUT_PATH �ɂ���S�Ẵt�@�C�����擾����
    all_file_list = getFileList(TIFF_PATH)
    
    #�摜���X�g�ŌJ��Ԃ����� 
    for fname in all_file_list:
        basename, ext = os.path.splitext( os.path.basename(fname) ) 
        if ext == ".tif":
            #NDVI�摜�̖��O��ݒ� 
            ndvi = NDVI_IMAGE_PATH + "\\" + basename + "_NDVI" + ".tif"
            if os.path.exists(ndvi) == False:
                
                #NDVI�v�Z
                NIR = arcpy.Raster(fname + "\Band_4")
                Red = arcpy.Raster(fname + "\Band_3")
                Num = arcpy.sa.Float(NIR - Red)
                Denom = arcpy.sa.Float(NIR + Red)
                NDVI = arcpy.sa.Divide(Num, Denom)                         
                NDVI_16bit = arcpy.sa.Float(((NDVI +1)* 255)/2)
                NDVI_16bit.save(ndvi)             
                print ndvi
    #----
    
            #----�]�[�����v
            #�]�[�����v����shp�t�@�C���̐ݒ�            
            seg_shp = SEG_PATH + "\\" + basename + ".shp"
            #���Ԑ������̃e�[�u���̃t�@�C�����w��
            seg_dbf = TABLE_PATH + "\\" + basename + ".dbf"
            
            if os.path.exists(seg_dbf) == False:                
                #�]�[�����v���e�[�u���ɏo�� (Zonal Statistics as Table)���ςƕW���΍�
                arcpy.gp.ZonalStatisticsAsTable_sa(seg_shp, "shapeID", ndvi, seg_dbf, "DATA", "MEAN_STD")     
                print seg_dbf
                                
                #�t�B�[���h���̐���
                arcpy.AddField_management(seg_dbf,"mean_ndvi","DOUBLE",10,3)
                arcpy.AddField_management(seg_dbf,"std_ndvi","DOUBLE",10,3)
                arcpy.CalculateField_management(seg_dbf, "mean_ndvi" , "[MEAN]")
                arcpy.CalculateField_management(seg_dbf, "std_ndvi" , "[STD]")
                arcpy.DeleteField_management(seg_dbf, "MEAN")
                arcpy.DeleteField_management(seg_dbf, "STD")
                arcpy.DeleteField_management(seg_dbf, "AREA")
                arcpy.DeleteField_management(seg_dbf, "COUNT")      
                                         
                #�e�[�u����shp�Ɍ�������
                arcpy.JoinField_management(seg_shp, "shapeID", seg_dbf, "shapeID", ["mean_ndvi","std_ndvi"])     
                print seg_shp
            #----
    
    #�}�s���Ƃɂ킩��Ă���̈敪����shp�t�@�C�����摜���ƂɃ}�[�W���Ĉ�ɂ���
    
    #�}�[�W����shp�t�@�C���iNoData�ӏ������ρj���i�[����t�H���_
    OUTPUT_SEG_PATH = HOME_PATH + "\\" + "04_shp_merged"
    #�}�[�W����shp�t�@�C���iNoData�����O�j
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
        #�}�[�W��shp�t�@�C���̖��O�ݒ�
        seg_merged_b = shp_merged_with_nd + "\\" + file_name + ".shp"
        seg_merged = str(OUTPUT_SEG_PATH).replace("/", "\\") + "\\" + file_name + ".shp"
        #�܂��}�[�W���Ă��Ȃ���΃}�[�W
        if os.path.exists(seg_merged) == False:
            #�����摜�t�@�C����������shp�t�@�C���̃��X�g���쐬
            FIND_SEG = SEG_PATH + "\\" + file_name + "*" + ".shp"
            seg_list = glob.glob(FIND_SEG)
            #shp���X�g�̃t�@�C�����}�[�W
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
    
    #--- �����I������
    End_Time = datetime.datetime.now()
    elapsed_time = End_Time - Start_Time
    print ""
    print "�������ԁF",(End_Time - Start_Time)
    print "�I�����ԁF",End_Time.strftime("%Y-%m-%d %H:%M:%S")

#--- End of Main ---