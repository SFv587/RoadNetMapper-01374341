# -*- coding:utf-8 -*-
from scipy.spatial import Delaunay
import numpy as np
from rtree import index
import matplotlib.pyplot as plt
from basic import Segment
from sklearn import linear_model, datasets
import pandas as pd
from math import e,cos,acos,atan,pi,fabs,sqrt
from basic import Point
from LoadData import LoadTraceDataFromMysqlDBFactory

class FilterFacotory(object):
    def __init__(self):
        pass

    @staticmethod
    def CreateDelaunayFilter():
        return DelaunayFilter()

    @staticmethod
    def CreateConsistentFilter():
        return ConsistentFilter()

    @staticmethod
    def CreateDistinctFilter():
        return DistinctFilter()

class ConsistentFilter(object):
    def __init__(self):
        self.exepected_ita=3
        self.simiThres=self.DetermineSimiThresByExpectedAccuracy(self.exepected_ita)

    def DetermineSimiThresByExpectedAccuracy(self,ita):
        return e**(-0.263*ita)

    def CacVecSimilarity(self,dirDiff,disDiff):
        '''
        similarity model:sim=0.91*e(-disDiff)+0.09*e(-(1-cos(dirDiff)))
        the weight can be adjusted
        :param disDiff:distance
        :param dirDiff:direction
        :return: the similarity value between vector 1 and vector 2
        '''
        simi_Val=0.91*(e**(-disDiff))+0.09*(e**(-1+cos(dirDiff)))
        return simi_Val

    def Ransac(self,seg,plotfig=False):
        '''
        :param seg: gps point series
        :return: y=kx+b or x=b
        '''
        # Robustly fit linear model with RANSAC algorithm
        X = [item.x for item in seg]
        y = [item.y for item in seg]
        X = np.array(X).reshape(len(X),1)
        y = np.array(y).reshape(len(X),1)
        # Robustly fit linear model with RANSAC algorithm
        ransac = linear_model.RANSACRegressor()
        ransac.fit(X, y)
        inlier_mask = ransac.inlier_mask_
        outlier_mask = np.logical_not(inlier_mask)
        # Predict data of estimated models
        line_X = np.array([X.min(), X.max()])[:, np.newaxis]
        line_X=line_X.tolist()
        line_y_ransac = ransac.predict(line_X)
        line_y_ransac=line_y_ransac.tolist()
        #return Analysis formula
        Cof=[None,None,None]
        Cof[0]=line_y_ransac[1][0]-line_y_ransac[0][0]
        Cof[1]=line_X[0][0]-line_X[1][0]
        Cof[2]=line_X[1][0]*line_y_ransac[0][0]-line_X[0][0]*line_y_ransac[1][0]

        if Cof[0]==0 and Cof[1]==0:
            print "only 1 point in this trace segment"
            raise ValueError
        if plotfig:
            lw = 2
            plt.scatter(X[inlier_mask], y[inlier_mask], color='yellowgreen', marker='.',
                        label='Inliers')
            plt.scatter(X[outlier_mask], y[outlier_mask], color='gold', marker='.',
                        label='Outliers')
            plt.plot(line_X, line_y_ransac, color='cornflowerblue', linewidth=lw,
                     label='RANSAC regressor')
            plt.legend(loc='lower right')
            plt.xlabel("Input")
            plt.ylabel("Response")
            plt.show()
        return Cof

    def ExeConsistentFilter(self,seg,plotfig=False):
        '''trace in motion characteristic based segment method
           characteristic point detection (distance,direction difference)
           ref:Yang X, Tang L, Zhang X, et al. A Data Cleaning Method for Big Trace Data Using Movement Consistency[J]. Sensors, 2018, 18(3).
           ——4.2
           :param trace: raw trajectory
           :return: trace with consistence and characteristic parts
        '''
        Cof=self.Ransac(seg,plotfig=False)
        for i in range(0,len(seg)-1):
            dir,dis=self.CacFeature(seg[i],seg[i+1],Cof)
            simiVal=self.CacVecSimilarity(dir,dis)
            if simiVal<self.simiThres:
                seg[i].isOutlier=True

    def CacFeature(self,p0,p1,line_Cof):
        azimuth=None
        line_dir=None
        dis=None
        vec1=[line_Cof[1],-line_Cof[0]]
        vec2=[p1.x-p0.x,p1.y-p0.y]
        len1=sqrt(vec1[0]*vec1[0]+vec1[1]*vec1[1])
        len2=sqrt(vec2[0]*vec2[0]+vec2[1]*vec2[1])
        if len1==0 and len2==0:
            raw_input("error")
        if fabs(vec1[0]*vec2[0]+vec1[1]*vec2[1])/(len1*len2)>1:
            dir=0
        else:
            dir=acos(fabs(vec1[0]*vec2[0]+vec1[1]*vec2[1])/(len1*len2))
        dis=fabs(line_Cof[0]*p0.x+line_Cof[1]*p0.y+line_Cof[2])/sqrt(line_Cof[0]*line_Cof[0]+line_Cof[1]*line_Cof[1])
        return dir,dis

class DelaunayFilter(object):
    def __init__(self):
        self.confidence=0.05

    def ExeDelaunayFilter(self,thisgroup_trace,plotfig=False):
        #input point array Point0,Point1,Point2,...,Pointn   ref;basic-Point
        # get (x0,y0),(x1,y1),...type of trace data   ---plist
        plist = [[item.lng, item.lat] for item in thisgroup_trace]
        points = np.asarray(plist)
        tri = Delaunay(np.asarray(points))
        del points
        n_triangles = len(tri.simplices)
        # build r-tree index for the grouped data
        #to be done
        #filter
        idx = self.__BuildRTree(thisgroup_trace)
        if plotfig:
            self.plotData(tri,thisgroup_trace)

    def __BuildRTree(self,thisgroup_trace):
        idx = index.Index()
        for po in thisgroup_trace:
            idx.insert(id=po.ID, bounds=(po.x, po.y, po.x, po.y), obj=po.ID)

    def plotData(self,tri,trace):
        inlierTrace=[item for item in trace if item.isOutlier==False]
        outlierTrace=[item for item in trace if item.isOutlier==True]
        plt.triplot([item.x for item in trace],[item.y for item in trace],tri.simplices.copy())
        plt.plot([item.x for item in inlierTrace],[item.y for item in inlierTrace],'o')
        plt.plot([item.x for item in outlierTrace], [item.y for item in outlierTrace], '+')
        plt.show()

class DistinctFilter(object):
    def __init__(self):
        self.error=15

    def ExecuteNullPositionMarker(self,traceDF):
        if "IsOutlier" not in traceDF.columns:
            traceDF["IsOutlier"]=0
        if "zx" in traceDF.columns:
            traceDF["IsOutlier"][traceDF.zx==0]=1
        if "zy" in traceDF.columns:
            traceDF["IsOutlier"][traceDF.zy==0]=1
        if "x" in traceDF.columns:
            traceDF["IsOutlier"][traceDF.x==0]=1
        if "y" in traceDF.columns:
            traceDF["IsOutlier"][traceDF.x == 0] = 1

    def ExecuteOverRecordMarker(self,traceDF):
        ind=traceDF[traceDF.IsOutlier==0].index
        print len(ind)*1.0/len(traceDF)
        for i_ind,j_ind in zip(range(len(ind)-1),range(1,len(ind))):
            last=ind[i_ind-1]
            i=ind[i_ind]
            j=ind[j_ind]
            if j==len(ind)-1:
                break
            next=ind[j_ind+1]
            if traceDF["tm"][i]==traceDF["tm"][j]:
                po_last=Point(zx=traceDF["zx"][last],zy=traceDF["zy"][last])
                po_next=Point(zx=traceDF["zx"][next],zy=traceDF["zy"][next])
                po_i=Point(zx=traceDF["zx"][i],zy=traceDF["zy"][i])
                po_j=Point(zx=traceDF["zx"][j],zy=traceDF["zy"][j])
                dis1=po_last.distanceToPoint(po_i)+po_next.distanceToPoint(po_i)
                dis2=po_last.distanceToPoint(po_j)+po_next.distanceToPoint(po_j)
                if dis1>dis2:
                    traceDF["IsOutlier"][i]=1
                else:
                    traceDF["IsOutlier"][j]=1


    def ExecuteOutPositionMarker(self,traceDF):
        pass

class DelaunayFilterMediator():
    def __init__(self,confidence=0.05,deviationMultiplier=1):
        self.confidence=confidence
        self.deviationMultiplier=deviationMultiplier

    def SetTrace(self,trace,groupid_name='gid'):
        # input point array Point0,Point1,Point2,...,Pointn   ref;basic-Point
        groupidLst = list(set(map(lambda x: x.fetchAttribute(groupid_name), trace)))
        for groupid in groupidLst:
            # select data belongs to same group
            thisgroup_trace = [item for item in trace if item.fetchAttribute(groupid) == groupidLst]
            #Apply Delaunay filter
            filter=FilterFacotory.CreateDelaunayFilter()

if __name__=="__main__":
    try:
        loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase', tblname="trajectory",
                                                 whereClause="IsOutlier=0 order by un,tm")
        traceDF = loader.getTraceData()
        filter=FilterFacotory.CreateDistinctFilter()
        filter.ExecuteNullPositionMarker(traceDF)
        filter.ExecuteOverRecordMarker(traceDF)
        changedDF=traceDF[traceDF.IsOutlier==1]
        for i in changedDF.index:
            sql="update mydatabase.trajectory set IsOutlier=1 where UID=%d" %changedDF["UID"][i]
            loader.database.UpdateTable(sql)
    except Exception,e:
        print e.message



