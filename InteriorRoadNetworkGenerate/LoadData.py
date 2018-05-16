import pandas as pd
import shapefile
from DatabaseOperation import DataBase,MySQLdatabse
import os
from basic import LoadFileFromDir,LoadFileFromPath

class LoadTraceDataFactory(object):
    def __init__(self,**args):
        self.TraceDataframe=None
        pass

    def __LoadFile__(self,**args):
        pass

    def getTraceData(self):
        if self.TraceDataframe is None:
            self.__LoadFile__()
        return self.TraceDataframe

class LoadTraceDataFromShapefileFactory(LoadTraceDataFactory):
    def __init__(self,**args):
        LoadTraceDataFactory.__init__(self)
        self.filepath=args["path"]

    def __LoadFile__(self):
        try:
            sf=shapefile.Reader(self.filepath)
            fieldObjList = sf.fields
            # Create an empty list that will be populated with field names
            fieldNameList = []
            # For each field in the object list, add the field name to the
            #  name list.  If the field is required, exclude it, to prevent errors
            for field in fieldObjList:
                if not field[0]=='DeletionFlag':
                    fieldNameList.append(field[0])
            records=sf.records()
            self.TraceDataframe = pd.DataFrame(records,columns=fieldNameList)
        except Exception,e:
            print e.message

class LoadTraceDataFromMysqlDBFactory(LoadTraceDataFactory):
    def __init__(self,**args):
        LoadTraceDataFactory.__init__(self)
        self.database=MySQLdatabse(name=args["dbname"])
        self.table = args["tblname"]
        self.sql=self.compileSQL(**args)

    def compileSQL(self,**args):
        column = "*"
        if args.has_key("column"):
            column = ','.join(args["column"])
        whereClause = ""
        if args.has_key("whereClause"):
            whereClause = "where " + args["whereClause"]
        if args.has_key("tblname"):
            self.table=args["tblname"]
        return "select %s from %s.%s %s" % (column, self.database.name, self.table, whereClause)

    def __LoadFile__(self):
        try:
            self.TraceDataframe=self.database.QureyTable(self.sql)
        except Exception,e:
            print e.message

class LoadTraceDataFromLocalFileFactory(LoadTraceDataFactory):
    def __init__(self,**args):
        LoadTraceDataFactory.__init__(self)
        self.filePath=[]
        if args.has_key("attrInfo"):
            self.AttriInfoDF=args["attrInfo"]
        else:
            self.AttriInfoDF=None

        if args.has_key("dir"):
            if os.path.isdir(args["dir"]):
                self.filePath=LoadFileFromDir(args["dir"])
            if os.path.isfile(args["dir"]):
                self.filePath.append(args["dir"])

    def __LoadFile__(self):
        for file in self.filePath:
            temp=LoadFileFromPath(file,self.AttriInfoDF)
            if self.TraceDataframe is None:
                self.TraceDataframe=temp
            else:
                self.TraceDataframe = self.TraceDataframe.append(temp, ignore_index=True)

# if __name__=="__main__":
#     path=r'E:\data\moto_trackdata_4city_shp\755\000159_20171127_20171203.dbf'
#     c=LoadTraceDataFromShapefileFactory(args=path)
#     c.getTraceData()