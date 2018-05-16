# -*- coding:utf:8 -*-

import shapefile
import os
import csv
import pandas as pd
import xlrd
import re
from basic import LoadFileFromDir

class shapefileOperation(object):
    def __init__(self,**args):
        pass

    def dataframeType2ArcpyShapefileType(input_field):
        if str(input_field).lower()=="int":
            return "Long"
        if str(input_field).lower()=="float" or str(input_field).lower()=="double":
            return "double"
        if str(input_field).lower()=="varchar(64)":
            return "String"

    @staticmethod
    def RemoveShapeFiles(filepath):
        nameWithoutSuffix=filepath.split('.')[0]
        dir=os.path.dirname(filepath)
        SuffixLst=["shp","dbf","prj","shx",".shp.xml"]
        for suffix in SuffixLst:
            path='.'.join([nameWithoutSuffix,suffix])
            if os.path.exists(path):
                os.remove(path)

    @staticmethod
    def CreateShapeFile(filepath,attrInfo,dataframe):
        #print dataframe.dtypes
        try:
            if os.path.exists(filepath):
                shapefileOperation.RemoveShapeFiles(filepath)
            w = shapefile.Writer()
            w.autoBalance = 1
            w = shapefile.Writer(shapeType=shapefile.POINT)
            for i in range(len(attrInfo)):
                if "varchar" in str(attrInfo["type"][i]).lower():
                    pattern=re.compile(r'\d+')
                    res=pattern.findall(str(attrInfo["type"][i]).lower())
                    if len(res)==0:
                        w.field(attrInfo["name"][i],'C',size=10)
                    else:
                        w.field(attrInfo["name"][i], 'C', size=int(res[0])+1)
                elif str(attrInfo["type"][i]).lower()=="int64":
                    w.field(attrInfo["name"][i], 'C', 11)
                elif "int" in str(attrInfo["type"][i]).lower():
                    pattern = re.compile(r'\d+')
                    res = pattern.findall(str(attrInfo["type"][i]).lower())
                    if len(res) == 0:
                        w.field(attrInfo["name"][i], 'C', 8)
                    else:
                        w.field(attrInfo["name"][i], 'C', int(res[0]) + 1)
                elif str(attrInfo["type"][i]).lower()=="float" :
                    w.field(attrInfo["name"][i],'F',decimal=8)
                elif str(attrInfo["type"][i]).lower()=="double" or str(attrInfo["type"][i]).lower()=="float64":
                    w.field(attrInfo["name"][i],'F',decimal=16)
                elif str(attrInfo["type"][i]).lower()=="object":
                    w.field(attrInfo["name"][i],'C',size=10)
                else:
                    raw_input("unkown type ,you must take a look personally!")
            for i in dataframe.index:
                newRow=[]
                w.point(dataframe["zx"][i],dataframe["zy"][i])
                for attr in dataframe.columns:
                    newRow.append(dataframe[attr][i])
                w.record(*newRow)
            w.save(filepath)
        except Exception,e:
            print e.message

    @staticmethod
    def CreateLineFromPoint(filepath,dataframe):
        try:
            if os.path.exists(filepath):
                shapefileOperation.RemoveShapeFiles(filepath)
            w = shapefile.Writer()
            w.autoBalance = 1
            w = shapefile.Writer(shapeType=shapefile.POLYLINE)
            w.field("TripID", 'C', 10)
            w.field("Length",'F',decimal=8)
            curTripID=None
            curPointList=[]
            for i in range(len(dataframe)):
                thisTripID=dataframe["TripID"][i]
                if curTripID is None:
                    curTripID=thisTripID
                if thisTripID==curTripID:
                    curPointList.append([dataframe["zx"][i],dataframe["zy"][i]])
                if thisTripID!=curTripID or i==len(dataframe)-1:
                    if len(curPointList)>=2:
                        w.line(parts=[curPointList])
                        length=0
                        points=[Point(zx=x[0],zy=x[1]) for x in curPointList]
                        for p0,p1 in zip(range(len(points)-1),range(1,len(points))):
                            dis=points[p0].distanceToPoint(points[p1])
                            length+=dis
                        length = float("%.8f" %length)
                        w.record(curTripID,length)
                    else:
                        print curTripID
                        raise ValueError
                    curTripID=thisTripID
                    curPointList=[]
                    curPointList.append([dataframe["zx"][i],dataframe["zy"][i]])
            w.save(filepath)
        except Exception,e:
            print e.message

    def File2ShapeFile(self,fileLst,attriInfo):
        '''input
                1. filepath list -fileLst [path1,path2,... ]
                2. file record structure dataframe- attriInfo [ID,name,tags]
           output
                1.shapefiles( merge same Courier traj divided by days to a shapefile)
                   1003/20170611.csv, 1003/20170612.csv , 1003/20170613.csv , 1003/20170614.csv -> 1003_11-14.shp
        '''
        curDir=os.path.dirname(fileLst[0])
        courierID = curDir.split('\\')[-1]
        start = None
        end = None
        Header=[]
        Type=[]
        for i in range(len(attrInfo)):
            Header.append(attrInfo["name"][i])
            if "varchar" in str(attrInfo["type"][i]).lower():
                Type.append("string")
            elif str(attrInfo["type"][i]).lower()=="double":
                Type.append("float64")
            elif str(attrInfo["type"][i]).lower()=="float":
                Type.append("float")
            elif "int" in str(attrInfo["type"][i]).lower():
                Type.append("int64")
            else:
                raw_input("unkown type")
        curDataframe = pd.DataFrame(columns=Header)
        #print curDataframe.dtypes
        for i in range(len(fileLst)):
            if os.path.dirname(fileLst[i])==curDir:
                try:
                    if os.path.exists(fileLst[i]):
                        name=os.path.basename(fileLst[i])
                        curDate=name.split('.')[0].split('_')[1]
                        if (start is None) or (end is None):
                            start=curDate
                            end=curDate
                        if int(start)>int(curDate):
                            start=curDate
                        if int(end)<int(curDate):
                            end=curDate
                        temp=pd.read_csv(fileLst[i],sep=',',header=None)
                        temp.columns=Header
                        if len(curDataframe)==0:
                            curDataframe=temp
                        else:
                            curDataframe=curDataframe.append(temp,ignore_index=True)
                except IOError:
                    print "read file error lineXX"
            if (os.path.dirname(fileLst[i])!=curDir) or (i==len(fileLst)-1):
                #DataFrame to shapefile
                outputDir=r"E:\data\moto_trackdata_4city_shp\755"
                filename="%s_%s_%s.shp" %(courierID,start,end)
                outputFilePath = os.path.join(outputDir, filename)
                #curDataframe.sort_index(by="tm")
                shapefileOperation.CreateShapeFile(outputFilePath,attrInfo,curDataframe)
                #reset variables
                curDir = os.path.dirname(fileLst[i])
                courierID=curDir.split('\\')[-1]
                start=None
                end=None
                curDataframe = pd.DataFrame(Header)

if __name__=="__main__":
    from basic import LoadFileFromPath,ReadColumInfoFromDataframe
    from basic import Point,PointMotionType,Segment
    from LoadData import LoadTraceDataFromMysqlDBFactory
    from DatabaseOperation import MySQLdatabse
    from LoadData import LoadTraceDataFromShapefileFactory
    cls=shapefileOperation()
    # fileLst=LoadFileFromDir(r"E:\data\moto_trackdata_4city\755\000159")
    # attrInfo=LoadFileFromPath(r"E:\data\dataRule.txt",type="txt",delimeter="\t")
    # cls.File2ShapeFile(fileLst,attrInfo)
    # print len(fileLst)
    # loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase', tblname="trajectory",
    #                                          whereClause="IsOutlier=0 order by un,tm")
    # traceDF = loader.getTraceData()
    #
    # seg = Segment()
    # IsBreak=False
    # segID=1
    # for i in range(len(traceDF)):
    #     po = Point(zx=traceDF["zx"][i], zy=traceDF["zy"][i], ID=traceDF["UID"][i], tm=traceDF["tm"][i])
    #     if traceDF["motion"][i] == 0:
    #         po.setType(PointMotionType.Stay)
    #     if po.motionType == PointMotionType.Move:
    #         if seg.length == 0:
    #             seg = Segment(point=po)
    #         else:
    #             if po.tm-seg.lastPoint.tm>60:
    #                 IsBreak=True
    #             else:
    #                 seg.insertPoint(po)
    #     if po.motionType == PointMotionType.Stay or i == len(traceDF) - 1 or IsBreak:
    #         if seg.length >= 3:
    #             for po in seg.pointList:
    #                 sql = "update trajectory set TripID=%d where UID=%d" % (segID, po.ID)
    #                 loader.database.UpdateTable(sql)
    #             segID += 1
    #         seg=Segment()
    #         if po.motionType==PointMotionType.Move:
    #             seg=Segment(point=po)
    loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase', tblname="trajectory",
                                             whereClause="TripID>-1 order by un,tm")
    traceDF = loader.getTraceData()
    attrInfo=ReadColumInfoFromDataframe(traceDF)
    cls.CreateShapeFile(r"E:\tempprogram\InteriorRoadNetworkGenerate\data\shapefile\raw_traj.shp",attrInfo,traceDF)

    cls.CreateLineFromPoint(r"E:\tempprogram\InteriorRoadNetworkGenerate\data\shapefile\raw_traj_line.shp",traceDF)

    loader = LoadTraceDataFromShapefileFactory(path=r"E:\tempprogram\InteriorRoadNetworkGenerate\data\shapefile\raw_traj_line.shp")
    df = loader.getTraceData()
    db = MySQLdatabse(name="mydatabase")
    df.to_sql("tripInfo", db.engine, index=False, if_exists="append")