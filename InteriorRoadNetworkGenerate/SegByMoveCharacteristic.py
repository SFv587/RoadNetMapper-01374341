#-*- coding:utf-8 -*-
from basic import Segment,PointMotionType,Point,CacVecFeatures
from TraceFilter import ConsistentFilter,FilterFacotory
from math import acos,pi,sqrt,sin
'''trace in motion characteristic based segment method
   characteristic point detection (distance,direction difference)
   ref:Yang X, Tang L, Zhang X, et al. A Data Cleaning Method for Big Trace Data Using Movement Consistency[J]. Sensors, 2018, 18(3).
   ——4.2
'''

class CharacterSegmentMediator(object):
    def __init__(self):
        self.disThres=14
        self.dirThres=30  #unit degree

    def ExecuteSegMethod(self,trace):
        '''
        :param trace: raw trajectory
        :return: trace with consistence and characteristic parts
        '''
        resSeg=[]
        if trace is None:
            return [],[]
        if len(trace)==0:
            return [],[]
        if len(trace)<3:
            return trace,[]
        seg=Segment(point=trace[0])
        seg.insertPoint(trace[1])
        for startIndex in range(len(trace)-2):
            vec1=[trace[startIndex+1].x-trace[startIndex].x,trace[startIndex+1].y-trace[startIndex].y]
            vec2=[trace[startIndex+2].x-trace[startIndex+1].x,trace[startIndex+2].y-trace[startIndex+1].y]
            dirDiff,disDiff=CacVecFeatures(vec1,vec2)
            if self.CheckIfCharacteristicPoint(dirDiff,disDiff):
                seg.insertPoint(trace[startIndex + 2])
            else:
                trace[startIndex + 2].Characteristic = True
                if seg.length>=3:
                    resSeg.append(seg)
                #new round
                seg = Segment(point=trace[startIndex + 1])
                seg.insertPoint(trace[startIndex + 2])
            if startIndex+2==len(trace)-1:
                if seg.length >= 3:
                    resSeg.append(seg)
        return resSeg


    def CheckIfCharacteristicPoint(self,dirDiff,disDiff):
        if disDiff<self.disThres and dirDiff<self.dirThres:
            return True
        else:
            return False

if __name__=="__main__":
    from basic import Point, PointMotionType
    from LoadData import LoadTraceDataFromMysqlDBFactory
    from SegByMotion import MotionSegmentMediator

    loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase', tblname="trajectory",
                                             whereClause="IsOutlier=0 order by un,tm")
    traceDF = loader.getTraceData()
    trace=[Point(zx=traceDF["zx"][i],zy=traceDF["zy"][i],tm=traceDF["tm"][i],ID=traceDF["UID"][i]) for i in traceDF.index]
    MoveSegMed=MotionSegmentMediator(5)
    moveSegs=MoveSegMed.segTrace(trace)
    #label trip id
    for moveseg in moveSegs:
        for po in moveseg.pointList:
            sql="update mydatabase.trajectory set TripID=%d" %moveseg.ID
            loader.database.UpdateTable(sql)

    for moveseg in moveSegs:
        CharSegMed=CharacterSegmentMediator()
        segParts=CharSegMed.ExecuteSegMethod(moveseg.pointList)
        for part in segParts:
            filter = FilterFacotory.CreateConsistentFilter()
            if part.length>3:
                filter.ExeConsistentFilter(part.pointList, plotfig=True)
                for po in part.pointList:
                    if po.isOutlier == True:
                        sql = "update trajectory set IsConsistent=0 where UID=%d" % po.ID
                    else:
                        sql = "update trajectory set IsConsistent=1 where UID=%d" % po.ID
                    loader.database.UpdateTable(sql)
                    if po.Characteristic==True:
                        sql = "update trajectory set IsCharacteristic=1 where UID=%d" % po.ID
                    else:
                        sql = "update trajectory set IsCharacteristic=0 where UID=%d" % po.ID
                    loader.database.UpdateTable(sql)


