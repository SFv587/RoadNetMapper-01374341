import LoadFile

if __name__=="__main__":
    try:
        shpfilePath=r"E:\data\moto_trackdata_4city_shp\755\000159_20171127_20171203.shp"
        shapeFac=LoadFile.LoadTraceDataFromShapefileFactory(args=(shpfilePath))
        #trace data order by person,time,motiontype
        OnetraceDF=shapeFac.getTraceData()
        #trace segment  stop cluster detection
    except Exception,e:
        print e.message