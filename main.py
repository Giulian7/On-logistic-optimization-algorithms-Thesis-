import py3dbp as BP
import py3dbl as AP

import random
def run():
    AP.MyBin()
    packer = BP.Packer()
    # F.Ducato
    dim = {"W": 1.87, "D":6.00, "H":2.52, "L":3000}

    Ducato = BP.Bin("Ducato",width=dim["W"],height=dim["H"],depth=dim["D"],max_weight=dim["L"])

    items = []
    for i in range(100):
        x = BP.Item(f"Item_{i}",random.random()*2.0,random.random()*2.0,random.random()*2.0,random.randint(1,200))
        items.append(x)
        packer.add_item(x)
        packer.add_bin(BP.Bin(f"Bin_{i}",width=dim["W"],height=dim["H"],depth=dim["D"],max_weight=dim["L"]))

    packer.pack(bigger_first=True,distribute_items=True)

    #print(packer.exec_time)

    for b in packer.bins:
        average_occupation = []
        average_occupation.append(0)
        average_occupation.append(0)
        if b.items:
            print(f"Bin: {b.string()}")
            occupied_volume = 0
            for i in b.items:
                print(i.string())
                occupied_volume += i.get_volume()
            percentage_occupation = occupied_volume/b.get_volume()*100
            average_occupation[0] += percentage_occupation
            average_occupation[1] += 1
            print(f"Volume Occupation: {occupied_volume} ({percentage_occupation}%)")
    return packer
    #print(f"Execution time: {end-start}(s)")
    #print(average_occupation)
    #print(f"Average Occupation: {average_occupation[0]/average_occupation[1]}")
        
