import py3dbl
import py3dbp
import time
import platform
from datetime import datetime

START = 100
END = 800
STEP = 100

lpacker = py3dbl.Packer()
ppacker = py3dbp.Packer()

model = py3dbl.BinModel("",[2,2,2],100,[
    py3dbl.constraints['weight_within_limit'],
    py3dbl.constraints['fits_inside_bin'],
    py3dbl.constraints['no_overlap']
])

lpacker.set_default_bin(model)

results = dict()
with open('benchmarking_result.txt',mode="a",newline='') as file:
    file.write(("="*10)+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+("="*10)+"\n")
    file.write("System Information:\n")
    uname = platform.uname()
    file.writelines([
        f" System: {uname.system}\n",
        f" Node Name: {uname.node}\n",
        f" Release: {uname.release}\n",
        f" Version: {uname.version}\n",
        f" Machine: {uname.machine}\n",
        f" Processor: {uname.processor}\n"
    ])
    for size in range(START,END+1,STEP):
        timed_counter = [0,0]
        bin_counter = [0,0]
        for _ in range(3):
            lpacker.reset_items()
            ppacker.items = list()
            ppacker.bins = list()
            items = py3dbl.item_generator(
                width=(.1,1),
                height=(.1,1),
                depth=(.1,1),
                weight=(.1,1),
                batch_size=size
            )
            lpacker.add_batch(items)
            for item in items:
                ppacker.add_item(py3dbp.Item(None,width=item.width,height=item.height,depth=item.depth,weight=item.weight))
                ppacker.add_bin(py3dbp.Bin(None,width=model.width,height=model.height,depth=model.depth,max_weight=model.max_weight))
            timed_execution = [0,0]
            bin_count = [0,0]
            for _ in range(2):
                start = time.time()
                lpacker.pack()
                end = time.time()
                timed_execution[0] += end - start
                bin_count[0] += len(lpacker.current_configuration)
                start = time.time()
                ppacker.pack(distribute_items=True)
                end = time.time()
                timed_execution[1] += end - start
                i = 0
                for b in ppacker.bins:
                    if len(b.items) == 0:
                        break
                    i+=1
                bin_count[1] += i
            timed_execution[0] /= 2
            timed_execution[1] /= 2
            bin_count[0] /= 2
            bin_count[1] /= 2

            timed_counter[0] += timed_execution[0]
            bin_counter[0] += bin_count[0]
            timed_counter[1] += timed_execution[1]
            bin_counter[1] += bin_count[1]
        results[size]["py3dbl"] = {"time": round(timed_counter[0]/5,2), "bins": round(bin_counter[0]/5,2)}
        results[size]["py3dbp"] = {"time": round(timed_counter[1]/5,2), "bins": round(bin_counter[1]/5,2)}
        file.write(str(size)+" items:\n")
        for test in results[size].keys():
            file.write(" " + str(test) + ":\n")
            file.write("  time: " + str(results[size][test]["time"]) + ", bins: " + str(results[size][test]["bins"]) + "\n")

        
    #writer = csv.DictWriter(file,fieldnames=["py3dbl","py3dbp"])
    #writer.writeheader()
    #writer.writerows(results)
    #writer.writerow(results['py3dbp'])