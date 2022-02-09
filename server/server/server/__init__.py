from django import test
import time


@classmethod
def setUpClass(cls):
    cls.startTime = time.time()


@classmethod
def tearDownClass(cls):
    print("\n%s.%s: %.3f" % (cls.__module__, cls.__name__, time.time() - cls.startTime))
    time_count = time.time() - cls.startTime
    hours = int(time_count // 3600)
    time_count = time_count % 3600
    minutes = int(time_count // 60)
    time_count = time_count % 60
    decimals = 10000
    seconds = float(float(int(time_count * decimals)) / decimals)


test.TestCase.setUpClass = setUpClass
test.TestCase.tearDownClass = tearDownClass
