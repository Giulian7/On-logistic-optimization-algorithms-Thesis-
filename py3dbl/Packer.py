from .Item import Item
from .Bin import Bin, BinModel
from .Constraints import constraints, Constraint
from .Algorithms import PackingAlgorithm, algorithms

class Packer():
    """
    Store configurations and execute 3D bin packing algorithm(s)
    """
    def __init__(self, algorithm : PackingAlgorithm = algorithms['base_packer'], default_bin : None|BinModel = None, fleet : list[Bin] = [], items : list[Item] = [], current_configuration : list[Bin] = []):
        """
        :param default_bin: A bin model that describes the preferred bin to pack in case the fleet is insufficent
        :type default_bin: None | BinModel
        :param bins: List of bin models that describes the fleet to pack
        :type bins: list[BinModel]
        :param items: List of items to fit in the fleet
        :type items: list[Item]
        :param current_configuration: A configuration to start on
        :type current_configuration: None | list[Bin]
        """
        self.bins   =  list(fleet)
        self.items  =  list(items)
        self.default_bin           = default_bin
        self.current_configuration = list(current_configuration)
        self.algorithm = algorithm
    
    def set_default_bin(self, bin : BinModel):
        """
        Set the default bin, if packing is executed with no fleet or the fleet is not sufficient, new bins with the default model will be added
        
        :param bin: A model of bin to set as default
        :type bin: BinModel
        """
        self.default_bin = bin

    def set_algorithm(self, algorithm : PackingAlgorithm):
        """
        Set the algorithm to use for packing
        
        :param algorithm: The packing algorithm to use
        :type algorithm: PackingAlgorithm
        """
        self.algorithm, algorithm = algorithm, self.algorithm
        return algorithm
    
    def add_bin(self, bin : Bin):
        """
        Add a bin to the current fleet
        """
        self.bins.append(bin)

    def add_fleet(self, fleet : list[Bin]):
        """
        Add another fleet to the current fleet
        
        :param fleet: A fleet (list of bins) to add
        :type fleet: list[Bin]
        """
        self.bins.extend(fleet)

    def add_batch(self, batch : list[Item]):
        """
        Add a batch of items to the current items list
        
        :param batch: A batch (list of items) to add
        :type batch: list[Item]
        """
        self.items.extend(batch)

    def reset_fleet(self):
        """
        Clear the fleet
        """
        self.bins = list()

    def reset_items(self):
        """
        Clear the items list
        """
        self.items = list()

    def reset_current_configuration(self):
        """
        Clear the current configuration
        """
        self.current_configuration = list()

    def pack_test_on_models(self, models : list[BinModel], algorithm : None|PackingAlgorithm = None, constraints : list[Constraint] = []):
        """
        Execute the packing algorithm on each of the models passed
        
        :param models: List of models to test
        :type models: list[BinModel]
        :param algorithm: A packing algorithm to use
        :type algorithm: PackingAlgorithm
        :param constraints: A list of constraints to use, models still follow the constraints in their constraints list
        :type constraints: list[Constraint]
        """
        bins = []
        for model in models:
            bins.append(Bin(model.name,model))
        if algorithm == None:
            algorithm = self.algorithm
        return algorithm(bins,self.items,constraints)
    
    
    def pack(self, algorithm : PackingAlgorithm = None, constraints : list[Constraint] = []):
        """
        Execute the 3D bin packing on the given batch and fleet
        
        :param bigger_first: Description
        :param number_of_decimals: Description
        """
        if algorithm == None:
            algorithm = self.algorithm

        algorithm.set_parameter("default_bin",self.default_bin)
        self.current_configuration = algorithm(self.bins,self.items,constraints)

    def calculate_statistics(self) -> dict[str:any]:
        statistics = {
            "bins_used": len(self.current_configuration),
            "items_loaded": 0,
            "loaded_volume": 0,
            "loaded_weight": 0,
        }
        configuration_volume = 0
        for bin in self.current_configuration:
            for item in bin.items:
                statistics["loaded_volume"] += item.volume()
            statistics["loaded_weight"] += bin.weight
            statistics['items_loaded'] += len(bin.items)
            configuration_volume += bin.volume()
        statistics["average_volume"] = statistics["loaded_volume"]/configuration_volume
        return statistics
    
# Packer testing

