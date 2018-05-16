import unittest
from LoadData import LoadTraceDataFromMysqlDBFactory

class TestLoadTraceDataFromMysqlDBFactory(unittest.TestCase):
    def test_init(self):
        loader = LoadTraceDataFromMysqlDBFactory(dbname='mydatabase',tblname="trajectory")
        self.assertEqual(loader.database.name,"mydatabase")
        self.assertTrue(isinstance(loader,LoadTraceDataFromMysqlDBFactory))

    def test_getTraceData(self):
        loader=LoadTraceDataFromMysqlDBFactory(dbname='mydatabase',tblname="trajectory",whereClause="order by un,tm")
        loader.getTraceData()
        self.assertEqual(len(loader.TraceDataframe),40152)

if __name__ == '__main__':
    unittest.main()