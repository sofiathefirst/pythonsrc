#!/usr/bin/env python
# -*- encoding: utf-8 -*- 
import  codecs, sys
import chardet

if __name__ == '__main__':
#     get_sn_wsn_rwr()
    a=float(sys.argv[1])
    m=int(sys.argv[2])

    print chardet.detect(sys.argv[3])

    str_uni = codecs.decode(sys.argv[3],"utf-8")
    print type(str_uni)
    uni2utf8= str_uni.encode("utf-8")
    print 'uni2utf8',chardet.detect(uni2utf8)
    uni2gb2312= str_uni.encode("gb18030")
    print uni2gb2312,chardet.detect(uni2gb2312)
    #str_utf8=codecs.decode(sys.argv[3], 'gb2312')#( "utf-8" )
    print a,m,sys.argv[3],type(sys.argv[2]),
