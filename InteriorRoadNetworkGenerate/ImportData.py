
import pandas as pd
from DatabaseOperation import MySQLdatabse
import LoadData
from basic import LoadFileFromPath

if __name__=="__main__":
    #import trace data into database
    try:
        db=MySQLdatabse(name="mydatabase")
        dir=r"E:\data\moto\755AE\014417"
        attrPath=r'E:\data\configuration\dataRule_new.txt'
        attrInfo=LoadFileFromPath(attrPath,type="txt",delimeter="\t")
        LoadDataFac=LoadData.LoadTraceDataFromLocalFileFactory(dir=dir,attrInfo=attrInfo)
        traceDataDF=LoadDataFac.getTraceData()
        traceDataDF.to_sql("trajectory",db.engine,index=False,if_exists="append")
    except Exception,e:
        print e.message
