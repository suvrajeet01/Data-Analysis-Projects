import multiprocessing
import time
import test
if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=6)
    result = []
    for i in [0,600,1200,1800,2400,3000]:
        result.append(pool.apply_async(test.run_task, (i,str(i) )))
    pool.close()
    pool.join()
    print ("Sub-process(es) done.")