#-*- coding:utf-8 -*-
from basic import Segment
from LoadData import LoadTraceDataFromMysqlDBFactory

if __name__=="__main__":
    #import motion,isoutlier labelled raw trajectory data containning id,tm property
    loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase', tblname="trajectory",
                                             whereClause="IsOutlier=0 order by un,tm")
    database=loader.database
    traceDF = loader.getTraceData()
    if traceDF is None or len(traceDF)==0:
        raise ValueError
    curTripID=database.QureyTable("select max(TripID) as TripID from trajectory")["TripID"][0]
    if curTripID==-1:
        curTripID=1
    elif curTripID>1:
        curTripID+=1
    else:
        print ValueError
    curUN=traceDF["un"][0]
    curSegList=[]
    lastIndex=traceDF.index[0]
    #Threshold
    TimeThres=60
    DisThres=100
    PointLenThres=3

    for i in range(len(traceDF.index)):
        ind=traceDF.index[i]
        if traceDF["un"][ind]==curUN and traceDF["TimeInterval"][ind]<=TimeThres \
                and traceDF["DistanceInterval"][ind]<=DisThres and traceDF["motion"][ind]==1:
            curSegList.append(traceDF["UID"][ind])
        if traceDF["un"][ind]!=curUN or traceDF["TimeInterval"][ind]>TimeThres \
                or i==traceDF.index[-1] or traceDF["DistanceInterval"][ind]>DisThres or traceDF["motion"][ind]==0:
            if len(curSegList)>=PointLenThres:
                for ID in curSegList:
                    sql="update trajectory set TripID=%d where UID=%d" %(curTripID,ID)
                    loader.database.UpdateTable(sql)
                #upgrade TripID
                curTripID+=1
            if traceDF["TimeInterval"][ind]<=TimeThres and traceDF["DistanceInterval"][ind]<=DisThres \
                    and traceDF["motion"][ind]==1:
                i=i-1
            curSegList=[]
            curUN=traceDF["un"][i]






