import py3dbl
import time
import platform
from datetime import datetime

START = 100
STEP = 100
ITER = 3

BIN_PARAMS = {
    "width":2,
    "depth":2,
    "height":2,
    "max_weight":100
}

ITEM_PARAMS = {
    "width":(.1,1),
    "depth":(.1,1),
    "height":(.1,1),
    "weight":(.1,1)
}

def packing_benchmarker(algorithms : list[str], constraints : list[py3dbl.Constraints.Constraint], end : int, start : int = START, step : int = 100, bin_params : dict = BIN_PARAMS, item_params : dict = ITEM_PARAMS, iterations : int = ITER, output_file : str = "benchmarking_result.txt"):
    """
    Put the listed algorithms in the same conditions (constraints set, item batch, model, ecc.) and test it for the number of times set by iterations
    
    :param algorithms: List names of algorithms to use, the name should be a registred in py3dbl.algorithms or py3dbp
    """
    
    model = py3dbl.BinModel(None,[bin_params['width'],bin_params['height'],bin_params['depth']],bin_params['max_weight'],constraints)
    def packer_from_algorithm(algorithm : str):
        if algorithm == 'py3dbp':
            # in case of py3dbp I need to adjust the packer interface
            import py3dbp
            def _add_batch(packer,batch):
                for i in batch:
                    packer.items.append(py3dbp.Item(None,i.width,i.height,i.depth,i.weight))
                    packer.bins.append(py3dbp.Bin(None,bin_params['width'],bin_params['height'],bin_params['depth'],bin_params['max_weight']))
            def _reset_items(self):
                self.items = list()
                self.bins = list()
            packer = py3dbp.Packer()
            packer.reset_items = (lambda :_reset_items(packer))
            packer.add_batch = (lambda batch: _add_batch(packer, batch))
            packer.pack = (lambda : py3dbp.Packer.pack(packer,distribute_items=True))
            def _count_bin(packer):
                idx = 0
                for bin in packer.bins:
                    if len(bin.items) == 0:
                        break
                    idx += 1
                return idx
            packer.used_bins = (lambda : _count_bin(packer))
        else:
            packer = py3dbl.Packer(algorithm=py3dbl.algorithms[algorithm],default_bin=model)
            packer.used_bins = (lambda : len(packer.current_configuration))
        packer.name = algorithm
        return packer
    
    packers = [packer_from_algorithm(algorithm) for algorithm in algorithms]

    results = dict()
    with open(output_file,mode="a",newline='') as file:
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
        file.write("Banchmarking Parameters:\n")
        file.writelines([
            " items dimensions:\n",
            *["  "+str(param)+": "+str(value)+"\n" for param,value in item_params.items()],
            " bin parameters:\n",
            *["  "+str(param)+": "+str(value)+"\n" for param,value in bin_params.items()],
            " constraints:\n",
            *["  "+str(constraint)+"\n" for constraint in constraints]
        ])
        for size in range(start,end+1,step):
            results[size] = dict()
            for algorithm in algorithms:
                results[size][algorithm] = {"time":0,"bins":0}
            for _ in range(iterations):
                items = py3dbl.item_generator(
                    width=item_params['width'],
                    height=item_params['height'],
                    depth=item_params['depth'],
                    weight=item_params['weight'],
                    batch_size=size,
                    use_gaussian_distrib=False
                )
                for packer in packers:
                    packer.reset_items()
                    packer.add_batch(items)
                    start = time.time()
                    packer.pack()
                    end = time.time()
                    results[size][packer.name]["time"] += end-start
                    results[size][packer.name]["bins"] += packer.used_bins()
                    

            file.write(str(size)+" items:\n")
            for algorithm,result in results[size].items():
                result["time"] /= iterations
                result["bins"] /= iterations
                file.write(" " + algorithm + ":\n")
                file.write("  time: " + str(round(result["time"],2)) + ", bins: " + str(round(result["bins"],2)) + "\n")

        return results