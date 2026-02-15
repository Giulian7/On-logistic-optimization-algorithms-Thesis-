from .Item import Item
from .Bin import Bin, BinModel
from .Decimal import decimals
from .Constraints import constraints, Constraint
from .Algorithms import PackingAlgorithm

class Packer():
    """
    Store configurations and execute 3D bin packing algorithm(s)
    """
    def __init__(self, default_bin : None|BinModel = None, fleet : list[Bin] = [], items : list[Item] = [], current_configuration : list[Bin] = []):
        """
        :param default_bin: a bin model that describes the preferred bin to pack in case the fleet is insufficent
        :type default_bin: None | BinModel
        :param bins: list of bin models that describes the fleet to pack
        :type bins: list[BinModel]
        :param items: list of items to fit in the fleet
        :type items: list[Item]
        :param current_configuration: a configuration to start on
        :type current_configuration: None | list[Bin]
        """
        self.bins   =  list(fleet)
        self.items  =  list(items)
        self.default_bin           = default_bin
        self.current_configuration = list(current_configuration)
        self.algorithm = None
    
    def set_default_bin(self, bin : BinModel):
        self.default_bin = bin

    def set_algorithm(self, algorithm : PackingAlgorithm):
        self.algorithm, algorithm = algorithm, self.algorithm
        return algorithm
    
    def add_bin(self, bin : Bin):
        self.bins.append(bin)

    def add_fleet(self, fleet : list[Bin]):
        self.bins.extend(fleet)

    def add_batch(self, batch : list[Item]):
        self.items.extend(batch)

    def clear_current_configuration(self):
        self.current_configuration = []

    def pack_test_on_models(self, models : list[BinModel], algorithm : PackingAlgorithm, constraints : list[Constraint] = []):
        bins = []
        for model in models:
            bins.append(Bin(model.name,model))
        return algorithm(bins,self.items,constraints)
    
    
    def pack(self, algorithm : PackingAlgorithm = None, constraints : list[Constraint] = [], bigger_first=True, follow_priority=True, number_of_decimals=decimals):
        """
        Execute the 3D bin packing on the given batch and fleet
        
        :param self: Current Packer object
        :param bigger_first: Description
        :param number_of_decimals: Description
        """
        if algorithm == None:
            if self.algorithm == None:
                raise ValueError()
            else:
                algorithm = self.algorithm
        algorithm.set_parameter("default_bin",self.default_bin)
        self.current_configuration = algorithm(self.bins,self.items,constraints)

    def calculate_statistics(self):
        statistics = {
            "loaded_volume": 0,
            "loaded_weight": 0,
        }
        configuration_volume = 0
        for bin in self.current_configuration:
            for item in bin.items:
                statistics["loaded_volume"] += item.volume()
            statistics["loaded_weight"] += bin.weight
            configuration_volume += bin.volume()
        statistics["average_volume"] = statistics["loaded_volume"]/configuration_volume
        return statistics