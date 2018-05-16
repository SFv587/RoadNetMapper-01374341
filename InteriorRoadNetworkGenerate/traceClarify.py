#-*- coding:utf-8 -*-
from LoadData import LoadTraceDataFromMysqlDBFactory
from basic import Point,CacLineCoff
from rtree import index
from shapely.geometry import linestring
from math import acos

class ClarifyMethod(object):
    def __init__(self):
        self.M=1
        self.delta=10
        self.k=0.005
        self.ind=None                 #R tree index
        self.loop=20
        self.disThres=0.15            #unit:meter   0.15meters
        self.searchDisRange=0.000463  #unit:degree  equals 30 meters

    def cacAttractForce(self,segs):
        pass

    def cacSpringForce(self,segs):
        pass

    def cacPostMovePosition(self,attraForce,springForece):
        pass

    def executeClarify(self,points):
        idx = index.Index()
        for i,j in zip(range(len(tracePoints)-1),range(1,len(tracePoints))):
            idx.insert(tracePoints[i].ID,(min(tracePoints[i].x,tracePoints[j].x),
                                          min(tracePoints[i].y,tracePoints[j].y),
                                          max(tracePoints[i].x,tracePoints[j].x),
                                          max(tracePoints[i].y,tracePoints[j].y)))
            if i == 0:
                tracePoints[i] == tracePoints[i]
            else:
                tracePoints[i].prevPoint = tracePoints[i - 1]
            tracePoints[i].nextPoint = tracePoints[i + 1]
            if j == len(tracePoints) - 1:
                tracePoints[j].nextPoint = tracePoints[j]
            tracePoints[i].direction2next = CacLineCoff(tracePoints[i].prevPoint.x, tracePoints[i].prevPoint.y,
                                                        tracePoints[i].nextPoint.x, tracePoints[i].nextPoint.y)
            tracePoints[i].baseDirection = CacLineCoff(tracePoints[i].x, tracePoints[i].y,
                                                       tracePoints[i].nextPoint.x, tracePoints[i] .nextPoint.y)
        #start Loop
        loop=1
        newInd=index.Index()
        while loop<=20:
            #cac direction for each point
            for po in tracePoints:
                this_inclineAngle=po.direction2next[i]
                neighIDs=list(idx.intersection((po.x-self.searchDisRange,po.y-self.searchDisRange,
                                                po.x+self.searchDisRange,po.y+self.searchDisRange)))

                if len(neighIDs)!=0:
                    self.cacPostMovePosition()

if __name__=="__main__":
    try:
        loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase', tblname="trajectory",
                                                whereClause="TripID>0 order by un,tm")
        traceDF = loader.getTraceData()
        tracePoints=[Point(zx=traceDF["zx"][i],zy=traceDF["zy"][i],
                           TripID=traceDF["TripID"][i],ID=traceDF["UID"][i]) for i in traceDF.index]
        clarifyMethod=ClarifyMethod()
        clarifyMethod.executeClarify(tracePoints)
    except Exception,e:
        print e.message
