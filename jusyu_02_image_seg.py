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
#�w��p�X���̃t�@�C����S�ĕԂ��֐�
def getFileList(path):
    file_list = []
    for (root, dirs, files) in os.walk(path):
        for file in files:
            file_list.append(os.path.join(root,file))
    return file_list
#============================

if __name__ == '__main__':

    #--- �����J�n����
    Start_Time = datetime.datetime.now()
    print "�J�n���ԁF",Start_Time.strftime("%Y-%m-%d %H:%M:%S")
    #---
    root=Tkinter.Tk()
    root.withdraw()
    fTyp_1=[('text', '*.txt')]
    
    parameter_file = tkFileDialog.askopenfilename(filetypes=fTyp_1, title=u"���ɂ���p�����[�^�t�@�C����I��")
    
    #�e�L�X�g�t�@�C���̓ǂݍ��݁i1�s���Ƀt�@�C���I�[�܂őS�ēǂށA���s�������܂܂��j
    f = open(parameter_file)
    lines = f.readlines()
    f.close()    
    output_path = str(lines[1]).replace("\n","")
    segmentation_path = output_path + "\\" + "02_image_segmentation"
    segmentation_shp_path = segmentation_path + "\\" + "01_shp"
    parameter_path = segmentation_path + "\\" + "02_parameter"
    batch_file = segmentation_path + "\\" + "image_seg.bat"
    
    #----�t�H���_���Ȃ���΍쐬����
    if os.path.exists(segmentation_path) == False:
        os.mkdir(segmentation_path)
    if os.path.exists(segmentation_shp_path) == False:
        os.mkdir(segmentation_shp_path)
    if os.path.exists(parameter_path) == False:
        os.mkdir(parameter_path)
    #----   
        
    #----�摜�t�H���_�ɂ���摜�̃��X�g������āA�J��Ԃ�����
    #INPUT_TIFF_Path �ɂ���S�Ẵt�@�C�����擾����
    input_image_path = str(lines[2]).replace("\n","")
    all_file_list = getFileList(input_image_path)
    
    #�p�����[�^����
    line1 = str(lines[0]).replace("\n","")
    line4 = str(lines[3]).replace("\n","")
    line5 = str(lines[4]).replace("\n","")
    line6 = str(lines[5]).replace("\n","")
    exe_file = str(lines[6]).replace("\n","")
    
    for fname in all_file_list:
                
        basename, ext = os.path.splitext(os.path.basename(fname))
        if ext == ".tif":
            
            #�t�H���_�A�t�@�C��������
            shp_file = segmentation_shp_path + "\\" + basename + ".shp"          
            text_file  = parameter_path  + "\\" + basename + ".txt"
            
            if os.path.exists(shp_file) == False:
                #�p�����[�^�[�t�@�C���̍쐬
                wfile2 = codecs.open(text_file, "w","cp932")
                wfile2.write(line1 + "\r\n")
                wfile2.write(shp_file + "\r\n" )
                wfile2.write(fname + "\r\n" )
                wfile2.write(line4 + "\r\n")
                wfile2.write(line5 + "\r\n")
                wfile2.write(line6 + "\r\n")
                wfile2.close()
                
                #�o�b�`�t�@�C���̍쐬                            
                wfile1 = codecs.open(batch_file, "a","cp932")
                EXEC_PATH_FILENAME = exe_file
                wfile1.write(EXEC_PATH_FILENAME + " " + text_file + "\r\n")
                wfile1.write("echo %time% %time%" + "\r\n")
                wfile1.close()
                
   
    #--- �����I������
    End_Time = datetime.datetime.now()
    elapsed_time = End_Time - Start_Time
    print ""
    print "�������ԁF",(End_Time - Start_Time)
    print "�I�����ԁF",End_Time.strftime("%Y-%m-%d %H:%M:%S")

#--- End of Main ---