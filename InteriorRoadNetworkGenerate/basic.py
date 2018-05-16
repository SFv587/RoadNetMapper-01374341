# -*- coding: utf-8 -*
from enum import Enum
from math import radians,sin,cos,asin,sqrt
import pandas as pd
import pyproj
from math import pi,acos,sin
import os

class ProjectTrans(object):
    @staticmethod
    def WGS84ToXian80(lon,lat):
        WGS84 = pyproj.Proj(init="epsg:4326")  # geodetic coordinate sys
        XianPrj = pyproj.Proj(init="epsg:2333")  # projected coordinate sys
        x1, y1 = WGS84(lon, lat)
        x2, y2 = pyproj.transform(WGS84,XianPrj, x1, y1, radians=True)
        return x2,y2

    @staticmethod
    def Xian80ToWGS84(x,y):
        WGS84 = pyproj.Proj(init="epsg:4326")  # geodetic coordinate sys
        XianPrj = pyproj.Proj(init="epsg:2333")  # projected coordinate sys
        x1, y1 = XianPrj(x, y)
        #x1,y1=x,y
        x2, y2 = pyproj.transform(XianPrj, WGS84, x1, y1, radians=True)
        return x2, y2

class PointMotionType(Enum):
    Stay=0
    Move=1

class Point(object):
    def __init__(self,**args):
        '''
        Initialized point to move state
        '''
        self.ID=None
        self.groupid=None
        self.lng=None
        self.lat=None
        self.x=None
        self.y=None
        self.z=None
        self.x_adj=None
        self.y_adj=None
        self.tm=None
        self.TripID=None
        self.be=None
        self.Characteristic=False
        self.isOutlier=False
        self.prevPoint=None
        self.nextPoint=None
        self.baseDirection=None
        self.direction2next=None
        self.motionType=PointMotionType.Move
        self.TimeInterval=None
        self.DistInterval=None
        self.speed=None
        coorInd=0
        if args.has_key("ID"):
            self.ID=args["ID"]
        if args.has_key("TimeInterval"):
            self.TimeInterval=args["TimeInterval"]
        if args.has_key("DistanceInterval"):
            self.DistInterval=args["DistanceInterval"]
        if args.has_key("x"):
            self.x=args["x"]
            coorInd+=4
        if args.has_key("y"):
            self.y=args["y"]
            coorInd += 4
        if args.has_key("tm"):
            self.tm=args["tm"]
        if args.has_key("TripID"):
            self.TripID=args["TripID"]
        if args.has_key("motionType"):
            self.motionType=PointMotionType(args["motionType"])
        if args.has_key("be"):
            self.be=args["be"]
        if args.has_key("zx"):
            self.lng=args["zx"]
            coorInd += 1
        if args.has_key("zy"):
            self.lat=args["zy"]
            coorInd += 1
        if coorInd==2:
            if (self.x is None) or (self.y is None):
                self.x,self.y=ProjectTrans.WGS84ToXian80(self.lng,self.lat)
        elif coorInd==8:
            if (self.lng is None) or (self.lat is None):
                self.lng,self.lat=ProjectTrans.Xian80ToWGS84(self.x,self.y)
        else:
            pass
        if (self.DistInterval is not None) and (self.TimeInterval is not None):
            self.speed=self.DistInterval/self.TimeInterval

    def __eq__(self, other):
        if self.x is None:
            return self.lng==other.lng and self.lat==other.lat
        else:
            return self.x==other.x and self.y==other.y

    def fetchAttribute(self,name):
        if name.lower()=="groupid":
            return self.groupid
        if name.lower()=="motintype":
            return self.motionType

    def distanceToPoint(self,otherPoint):
        # degree to radian
        lon1, lat1, lon2, lat2 = map(radians, [self.lng, self.lat,otherPoint.lng,otherPoint.lat])
        # haversine equation
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6378137
        # average radius of the Earth，unit-km
        return c * r

    def setType(self,motype):
        if type(motype)==PointMotionType:
            self.motionType=motype
        else:
            raise ValueError

class Segment(object):
    def __init__(self,**args):
        self.pointList = []
        self.ID = None
        self.order=None
        self.length=0
        self.startPoint=None
        self.lastPoint=None
        if args.has_key("point"):
            self.pointList.append(args["point"])
        if args.has_key("pointLst"):
            self.pointList.extend(args["pointLst"])
        if len(self.pointList)!=0:
            self.length = len(self.pointList)
            self.startPoint = self.pointList[0]
            self.lastPoint=self.pointList[len(self.pointList)-1]

    def setAttri(self,**args):
        if args.has_key("ID"):
            self.ID=args["ID"]
        elif args.has_key("order"):
            self.order=args["order"]
        else:
            raise ValueError

    def insertPoint(self,po):
        if self.length==0:
            self.pointList=[]
        if isinstance(po,Point):
            self.pointList.append(po)
        else:
            self.pointList.extend(po)
        self.length=len(self.pointList)
        self.lastPoint=po

    def mergeSeg(self,otherSeg):
        if self.pointList is None:
            raise ValueError
        self.pointList.extend(otherSeg.pointList)
        self.length = len(self.pointList)
        return self

class Triangle(object):
    def __init__(self,x,y,z):
        pass

class Person(object):
    def __init__(self):
        self.ID=0
        self.traceDF=None
        self.moveSegs=[]    #segments in motion
        self.trace=Segment()  #space time gps point series

    def __init__(self,dataframe):
        if dataframe is None:
            print "none dataframe"
            raise ValueError
        if len(dataframe)==0:
            print "empty dataframe"
            raise ValueError
        self.ID=dataframe["un"][0]
        #initialize
        for i in range(len(dataframe)):
            po=Point(dataframe["zx"][i],dataframe["zy"][i],dataframe["tm"][i])
            self.trace.insertPoint(po)

def CacLineCoff(x1,y1,x2,y2):
    # return Analysis formula
    # Ax+By+C=0
    Cof = [None, None, None]
    Cof[0] = y2-y1
    Cof[1] = x1-x2
    Cof[2] = x2*y1-x1*y2
    return Cof

def CacVecFeatures(vec1,vec2):
    '''
    :param p1: first point
    :param p2: second point
    :param p3: third point
    :return:composed of direction(radians) and distance differece  between vec(p1,p2) and vec(p2,p3)
    '''
    disDiff=None
    dirDiff=None
    len1=sqrt(vec1[0]*vec1[0]+vec1[1]*vec1[1])
    len2=sqrt(vec2[0]*vec2[0]+vec2[1]*vec2[1])
    if len1==0 or len2==0:
        print 1
    val=(vec1[0] * vec2[0] + vec1[1] * vec2[1])/(len1*len2)
    if val>1:
        val=1
    if val<-1:
        val=-1
    dirDiff=acos(val)
    dirDiff_degree=dirDiff*180/pi
    disDiff=len2*sin(dirDiff)
    return dirDiff_degree,disDiff

def LoadFileFromPath(filepath,DataTypeDF=None,type="csv",delimeter=","):
    if DataTypeDF is None:
        if type=="csv":
            return pd.read_csv(filepath)
        elif type=="txt":
            return pd.read_table(filepath,delimiter=delimeter)
    else:
        Header=[]
        #Type=[]
        colInd=[]
        for i in range(len(DataTypeDF)):
            Header.append(DataTypeDF["name"][i])
            colInd.append(DataTypeDF['ID'][i]-1)
            # if "varchar" in str(DataTypeDF["type"][i]).lower():
            #     Type.append("string")
            # elif str(DataTypeDF["type"][i]).lower() == "double":
            #     Type.append("float64")
            # elif str(DataTypeDF["type"][i]).lower() == "float":
            #     Type.append("float")
            # elif "int" in str(DataTypeDF["type"][i]).lower():
            #     Type.append("int64")
            # else:
            #     raw_input("unkown type")
        try:
            temp = pd.read_csv(filepath, sep=',', header=None)
            temp=temp.ix[:,colInd]
            temp.columns = Header
        except Exception,e:
            print filepath
            raise ValueError

        return temp

def LoadFileFromDir(filedir, filter="csv"):
    files = os.listdir(filedir)
    targetFiles = []
    for file in files:
        filepath = os.path.join(filedir, file)
        str = file[-3:]
        if os.path.isdir(filepath) and file!="points":
            getfiles = LoadFileFromDir(filepath)
            getfiles.sort()
            targetFiles.extend(getfiles)
        else:
            if str == filter:
                targetFiles.append(filepath)
    return targetFiles

def ReadColumInfoFromDataframe(dataframe):
    attrInfo=pd.DataFrame(columns=["name","type"])
    ind=0
    for col,type in zip(dataframe.columns,dataframe.dtypes):
        attrInfo.loc[ind,"name"]=str(col)
        attrInfo.loc[ind,"type"]=str(type)
        ind+=1
    return attrInfo


if __name__=="__main__":
    from basic import Point, PointMotionType
    from LoadData import LoadTraceDataFromMysqlDBFactory
    from math import sqrt

    loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase', tblname="trajectory",
                                             whereClause="IsOutlier=0 order by un,tm")
    traceDF = loader.getTraceData()
    for i in range(len(traceDF)):
    # for i,j in zip(range(len(traceDF)-1),range(1,len(traceDF))):
        po = Point(zx=traceDF["zx"][i], zy=traceDF["zy"][i], ID=traceDF["UID"][i], tm=traceDF["tm"])
        # p2=Point(zx=traceDF["zx"][j], zy=traceDF["zy"][j], ID=traceDF["UID"][j], tm=traceDF["tm"])
        # dis= po.distanceToPoint(p2)
        # dist=sqrt((po.x-p2.x)*(po.x-p2.x)+(po.y-p2.y)*(po.y-p2.y))
        # if dis-dist<5:
        #     print "Y"
        # else:
        #     raw_input("N")
        sql="update trajectory set x=%f,y=%f where UID=%d" %(po.x,po.y,po.ID)
        loader.database.UpdateTable(sql)

