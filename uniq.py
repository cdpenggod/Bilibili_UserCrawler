# -*-coding:utf8-*-

import pandas as pd
import codecs
import csv


def uniq():
	df=pd.read_csv('bilibiliData.csv',header=0,names=['mid','姓名','性别','rank','face','spacesta','生日','签名','等级','官方验证类型','官方验证描述','vip类型','vip状态','toutu','toutuID','coins','关注数','粉丝数'])
	df=df.drop_duplicates(['mid'])
	csvfile = open('bilibiliData.csv','wb')
	csvfile.write(codecs.BOM_UTF8)
	df.to_csv('bilibiliData.csv',index=False)
	print("去重完成")



uniq()
