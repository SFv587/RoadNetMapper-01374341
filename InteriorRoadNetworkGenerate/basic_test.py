import unittest
from basic import ProjectTrans

class Testbasic(unittest.TestCase):
    def test_WGS84ToXian80(self):
        x,y=ProjectTrans.WGS84ToXian80(114,22)
        x,y=ProjectTrans.Xian80ToWGS84(x,y)
        self.assertAlmostEqual(x,114)
        self.assertAlmostEqual(y,30)


if __name__=="__main__":
    unittest.main()