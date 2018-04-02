#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import os

import zipfile
from PIL import Image
import math
import operator
from functools import reduce
import shutil
import re
import subprocess

from library import pHash


def get_full_name(file_path,suffix):

    file_list = []
    for dirpath, dirnames, filenames in os.walk(file_path):
        for file in filenames:
            temp = os.path.splitext(file)[1]
            if suffix == temp:
                fullpath=os.path.join(dirpath,file)
                file_list.append(fullpath)

    return file_list


def extract_nested_zip(zippedFile, toFolder):

    with zipfile.ZipFile(zippedFile, 'r') as zfile:
        zfile.extractall(path=toFolder)
    os.remove(zippedFile)
    for dirpath, dirnames, filenames in os.walk(toFolder):
        for fn in filenames:
            unzip = ''
            suffix = os.path.splitext(fn)[1]
            # unzip file
            try:
                if suffix == '.png' or suffix == '.jpg':
                    continue

                if suffix == '.zip':
                    unzip_fn = os.path.join(dirpath, fn)

                if suffix <> '.zip' and suffix <> '.xml':
                    new_name = os.path.join(dirpath,fn + '.zip')
                    orig_name = os.path.join(dirpath, fn)
                    os.rename(orig_name, new_name)
                    unzip_fn = new_name

                if unzip_fn <> '':
                    print unzip_fn
                    temp = os.path.basename(unzip_fn)
                    dpath = os.path.join(dirpath,os.path.splitext(temp)[0])
                    extract_nested_zip(unzip_fn,dpath)
            except Exception,ex:
                pass


def get_new_name(img_file, compare_result,count,flag):


    category = [['W-EX','Z'],['2.5','3.0'],['480P', '720P', '1080P', '1440P']]
    folder_list = []
    for ct in category:
        for index, value in enumerate(ct):
            if img_file.find(value) != -1:
                folder_list.append(ct[index])

    folder = '_'.join(folder_list)

    new_name = ''.join([str(count),'_',folder,'_',flag,'_',str(compare_result),'_',os.path.basename(img_file)])

    return new_name


def compare_image(orig_img, dest_img, count, new_path):

    # img1=Image.open(orig_img)
    # img2=Image.open(dest_img)
    #
    # h1=img1.histogram()
    # h2=img2.histogram()
    #
    # '''
    # sqrt:计算平方根，reduce函数：前一次调用的结果和sequence的下一个元素传递给operator.add
    # operator.add(x,y)对应表达式：x+y
    # 这个函数是方差的数学公式：S^2= ∑(X-Y) ^2 / (n-1)
    # '''
    # #result的值越大，说明两者的差别越大；如果result=0,则说明两张图一模一样
    # try:
    #     result = math.sqrt(reduce(operator.add,  list(map(lambda a,b: (a-b)**2, h1, h2)))/len(h1) )
    #     print('compare result:' + str(int(result)))
    # except Exception,ex:
    #     pass
    #     result = 'null'

    cmd = 'compare -metric AE -fuzz 20% {0} {1} similar.png'.format(orig_img, dest_img)
    try:
        ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ret.wait()
        value = ret.stdout.readline()
    except Exception,ex:
        value = ''


    # copy original file
    name=get_new_name(orig_img,value,count,'O')
    dest =os.path.join(new_path, name)
    shutil.copyfile(orig_img, dest)

    # copy another file
    name=get_new_name(dest_img,value,count,'D')
    dest =os.path.join(new_path, name)
    try:
        shutil.copyfile(dest_img, dest)
    except Exception,ex:
        pass

def find_image(relative_path,find_basename, file_path):

    FOUND = False
    for dirpath, dirnames, filenames in os.walk(file_path):
        for fn in filenames:
            full_path = os.path.join(dirpath,fn)
            if fn == find_basename and full_path.find(relative_path) != -1:
                FOUND = True
                break
        if FOUND:
            break
    if FOUND:
        return full_path
    else:
        return ''

def walk_through_images(orig_path, dest_path, compare_path):

     count = 0
     for dirpath, dirnames, filenames in os.walk(orig_path):
        for fn in filenames:
            suffix = os.path.splitext(fn)[1]
            if suffix == '.png':
                full_path = os.path.join(dirpath, fn)
                print 'original_path:' + full_path
                rel_path = dirpath.replace(orig_path,'')
                res = find_image(rel_path, fn, dest_path)
                print 'destination_path:' + res

                if res != '':
                    count += 1
                    compare_image(full_path,res, count, compare_path)


if __name__ == '__main__':

    orig = r'E:\temp1\big_1.zip'
    dest = r'E:\temp2\big_2.zip'
    compare_path = r'E:\img_compare4'

    file_list = []
    file_list.append(orig)
    file_list.append(dest)

    # unzip file
    for zippedFile in file_list:
        toFolder = os.path.dirname(zippedFile)
        extract_nested_zip(zippedFile, toFolder)

    # compare file
    orig_path = os.path.dirname(orig)
    dest_path = os.path.dirname(dest)
    walk_through_images(orig_path, dest_path, compare_path)