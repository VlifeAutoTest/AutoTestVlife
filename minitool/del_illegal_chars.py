#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'xuxh'

import re
import os

if __name__ == '__main__':

    orig_file = r'/home/lang/jmeter/serverAPI.jtl'
    dest_file = r'/home/lang/jmeter/output.jtl'

    new_line1 = '<responseData class="java.lang.String">The response data contains illegal characters and therefore is not shown here</responseData>'
    new_line2 = '<queryString class="java.lang.String">data contains illegal characters and therefore is not shown here</queryString>'

    with open(orig_file,'rb') as rfile, open(dest_file,'wb') as wfile:

        #pattern = "[^<>&'\"\u0001-\uD7FF\uE000-\uFFFD\ud800\udc00-\udbff\udfff]"
        #pattern = "[^\x09\x0A\x0D\x20-\xD7FF\xE000-\xFFFD\x10000-x10FFFF]"
        #pattern = "[^\u0009\u000a\u000d\u0020-\ud7ff\ue000-\ufffd]|([\ud800-\udbff](?![\udc00-\udfff]))|((?<![\ud800-\udbff])[\udc00-\udfff])"
        #pattern = "[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]"
        find_str = ''
        for line in rfile:
            if find_str == '':
                if line.find('<responseData class="java.lang.String">')!=-1 and line.find('&#x0') != -1:
                    if line.find('</responseData>')!= -1:
                        wfile.write(new_line1)
                    else:
                        find_str = '</responseData>'
                        continue
                elif line.startswith('<queryString class="java.lang.String">')!=-1 and line.find('&#x0') != -1:
                    if line.find('</queryString>') != -1:
                        wfile.write(new_line2)
                    else:
                        find_str = '</queryString>'
                        continue
                else:
                    wfile.write(line)
            else:
                if line.find(find_str) == -1:
                    continue
                else:
                    if find_str == '</responseData>':
                       wfile.write(new_line1)
                    if find_str == '</queryString>':
                       wfile.write(new_line2)
                    find_str = ''

            #temp = re.sub(pattern, '', line)
            #wfile.write(temp)

    # delete orig_file
    os.remove(orig_file)
    # rename file
    os.rename(dest_file, orig_file)