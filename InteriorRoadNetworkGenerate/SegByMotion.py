# -*- coding:utf-8 -*-

from basic import Segment,PointMotionType,Point
'''
stop detection 
ref:Zhang F, Wilkie D, Zheng Y, et al. Sensing the pulse of urban refueling behavior[C]// 
ACM International Joint Conference on Pervasive and Ubiquitous Computing. ACM, 2013:13-22. 
——5.1 Fig(6)
'''

class MotionSegmentMediator(object):
    globalID=0

    def __init__(self,disThreshold):
        self.disThreshold=disThreshold

    def labelStayPoints(self,trace):
        '''input:
                        space-temporal(ordered by time) trace data of certain person
                        trace points like:  (x0,y0,tm0),(x1,y1,tm1),...,(xn,yn,tmn)
                   given:
                        disTreshold t to detect stop clusters, others as move points
                   detection method
                        ref:Zhang F, Wilkie D, Zheng Y, et al. Sensing the pulse of urban refueling behavior[C]//
                        ACM International Joint Conference on Pervasive and Ubiquitous Computing. ACM, 2013:13-22.
                         ——5.1 Fig(6)
                         label stay points in the given trace
                   return
                         None
                '''
        staysegsCnt = 0
        if trace is None:
            raise ValueError
        if len(trace) == 1:
            return trace
        for i in range(len(trace)):
            stayseg = Segment(point=trace[i])
            for j in range(i + 1, len(trace)):
                disToStart=stayseg.startPoint.distanceToPoint(trace[j])
                ditToLast=stayseg.lastPoint.distanceToPoint(trace[j])
                if (disToStart<= self.disThreshold) and (ditToLast<= self.disThreshold) and trace[j].speed<1:
                    stayseg.insertPoint(trace[j])
                if (disToStart > self.disThreshold) or (ditToLast > self.disThreshold) or (j == len(trace) - 1) \
                    or trace[j].speed>=1:
                    if stayseg.length >= 2:
                        # label stay points
                        staysegsCnt += 1
                        for po in stayseg.pointList:
                            po.setType(PointMotionType.Stay)
                    i = j
                    break

    def segTrace(self,trace):
        '''input:
                space-temporal(ordered by time) trace data of certain person
                trace points like:  (x0,y0,tm0),(x1,y1,tm1),...,(xn,yn,tmn)
           given:
                disTreshold t to detect stop clusters, others as move points
           detection method
                ref:Zhang F, Wilkie D, Zheng Y, et al. Sensing the pulse of urban refueling behavior[C]//
                ACM International Joint Conference on Pervasive and Ubiquitous Computing. ACM, 2013:13-22.
                 ——5.1 Fig(6)
           return
                 trace segments in motion divided by stops
                 [seg1,seg2,...segk], seg=[p0,p1]
        '''
        staysegsCnt=0
        staysegLst=[]
        if trace is None:
            raise ValueError
        if len(trace)==1:
            return trace
        for i in range(len(trace)):
            stayseg = Segment(point=trace[i])
            for j in range(i+1,len(trace)):
                if (stayseg.startPoint.distanceToPoint(trace[j])<=self.disThreshold and
                        stayseg.lastPoint.distanceToPoint(trace[j])<=self.disThreshold):
                    stayseg.insertPoint(trace[j])
                if (stayseg.startPoint.distanceToPoint(trace[j]) > self.disThreshold or
                        stayseg.lastPoint.distanceToPoint(trace[j]) > self.disThreshold or
                        j==len(trace)-1):
                    if stayseg.length>=2:
                        staysegLst.append(stayseg)
                        #label stay points
                        staysegsCnt+=1
                        for po in stayseg.pointList:
                            po.setType(PointMotionType.Stay)
                    i=j
                    break
        #conbine segs if the segs touch with each other
        if staysegsCnt==0:
            return trace
        resSegs=[]
        for i in range(len(trace)):
            if trace[i].motionType!=PointMotionType.Stay:
                moveSeg= Segment(point=trace[i])
                for j in range(i+1,len(trace)):
                    if trace[j].motionType!=PointMotionType.Stay:
                        moveSeg.insertPoint(trace[j])
                    if trace[j].motionType==PointMotionType.Stay or j==len(trace)-1:
                        if moveSeg.length>=3:
                            moveSeg.setAttri(ID=self.globalID)
                            resSegs.append(moveSeg)
                            self.globalID+=1
                        i=j
                        break
        return resSegs


if __name__=="__main__":
    from LoadData import LoadTraceDataFromMysqlDBFactory
    from basic import Point
    try:
        loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase', tblname="trajectory",
                                                whereClause="IsOutlier=0 order by un,tm")
        traceDF = loader.getTraceData()
        seg=[]
        for i in range(len(traceDF)):
            po=Point(zx=traceDF["zx"][i],zy=traceDF["zy"][i],tm=traceDF["tm"][i],
                     ID=traceDF["UID"][i],TimeInterval=traceDF["TimeInterval"][i],
                     DistanceInterval=traceDF["DistanceInterval"][i])
            seg.append(po)
        segCls=MotionSegmentMediator(5)
        segCls.labelStayPoints(seg)
        for po in seg:
            sql=""
            if po.motionType==PointMotionType.Move:
                sql="update trajectory set motion=1 where UID=%d" %po.ID
            elif po.motionType==PointMotionType.Stay:
                sql = "update trajectory set motion=0 where UID=%d" % po.ID
            loader.database.UpdateTable(sql)
    except Exception,e:
        print e.message

