from basic import Point, PointMotionType
from LoadData import LoadTraceDataFromMysqlDBFactory
from SegByMotion import MotionSegmentMediator
import matplotlib.pyplot as plt

loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase', tblname="trajectory",
                                         whereClause="IsOutlier=0 order by un,tm")
traceDF = loader.getTraceData()
trace=[Point(zx=traceDF["zx"][i],zy=traceDF["zy"][i],tm=traceDF["tm"][i],ID=traceDF["UID"][i]) for i in traceDF.index]
TimeIntervalLst=[]
DistanceIntervalLst=[]
for i,j in zip(range(len(trace)-1),range(1,len(trace))):
    TI=int(trace[j].tm-trace[i].tm)
    dis=Point(zx=traceDF["zx"][j],zy=traceDF["zy"][j]).distanceToPoint(Point(zx=traceDF["zx"][i],zy=traceDF["zy"][i]))
    DistanceIntervalLst.append(dis)
    sql="update trajectory set DistanceInterval=%s,TimeInterval=%s where UID=%d" %(dis,TI,traceDF["UID"][j])
    loader.database.UpdateTable(sql)
    TimeIntervalLst.append(TI)
TimeIntervalLst1=[x for x in TimeIntervalLst if x<10]
DistanceIntervalLst1=[x for x in DistanceIntervalLst if x<100]
print len(TimeIntervalLst1)*1.0/len(TimeIntervalLst)
print len(DistanceIntervalLst1)*1.0/len(DistanceIntervalLst)
figure,axes=plt.subplots(2,2,figsize=(10,10))
axes[0,0].boxplot(TimeIntervalLst1)
axes[0,1].hist(TimeIntervalLst1)
axes[1,0].boxplot(DistanceIntervalLst1)
axes[1,1].hist(DistanceIntervalLst1)
plt.show()
