from .Item import Item
from .Bin import Bin, BinModel
from .Space import Vector3, Volume
from .Decimal import decimals

class Packer():
    """
    Store configurations and execute 3D bin packing algorithm(s)
    """
    def __init__(self, default_bin : None|BinModel = None, fleet : list[BinModel] = [], items : list[Item] = [], current_configuration : None|list[Bin] = None):
        """
        Docstring for __init__
        
        :param self: Current Packer object
        :param default_bin: a bin model that describes the preferred bin to pack in case the fleet is insufficent
        :type default_bin: None | BinModel
        :param bins: list of bin models that describes the fleet to pack
        :type bins: list[BinModel]
        :param items: list of items to fit in the fleet
        :type items: list[Item]
        :param current_configuration: a configuration to start on
        :type current_configuration: None | list[Bin]
        """
        self.bins   =  fleet
        self.items  =  items
        self.default_bin           = default_bin
        self.current_configuration = current_configuration
    
    def set_default_bin(self, bin : BinModel):
        self.default_bin = bin
    
    def add_bin(self, bin : Bin):
        self.bins.append(bin)

    def add_fleet(self, fleet : list[BinModel]):
        self.bins.extend(fleet)

    def add_batch(self, batch : list[Item]):
        self.items.extend(batch)

    def clear_current_configuration(self):
        self.current_configuration.clear()

    def pack_to_bin(self, bin : Bin, item : Item):
        if not bin.items:
            return bin.put_item(item)
        else:
            for axis in range(0, 3):
                for ib in bin.items:
                    pivot = Vector3(*ib.position)
                    pivot[axis] += ib.dimensions[axis]
                    if bin.put_item(item, pivot):
                        return True
            return False

    def pack_test_on_models(self, models : list[BinModel]):
        configuration = []
        for model in models:
            bin = Bin(0,model)
            for item in self.items:
                self.pack_to_bin(bin,item)
            configuration.append(bin)
        return configuration
    
    def pack(self, bigger_first=True, follow_priority=True, number_of_decimals=decimals):
        """
        Execute the 3D bin packing on the given batch and fleet
        
        :param self: Current Packer object
        :param bigger_first: Description
        :param number_of_decimals: Description
        """
        available_bins = self.bins
        items_to_pack = self.items

        for bin in available_bins:
            bin.format_numbers(number_of_decimals)

        for item in items_to_pack:
            item.format_numbers(number_of_decimals)

        self.default_bin.format_numbers(number_of_decimals)
        
        available_bins.sort(
            key=lambda bin: bin.volume, reverse=bigger_first
        )
        items_to_pack.sort(
            key=lambda item: item.volume.volume(), reverse=bigger_first
        )
        
        self.current_configuration = []
        unfitted_items = []

        while len(items_to_pack) != 0:
            if available_bins != None and len(available_bins) != 0:
                bin = available_bins.pop(0)
            elif self.default_bin != None:
                bin = Bin(len(self.current_configuration),self.default_bin)
            else:
                return

            for item in items_to_pack:
               if not self.pack_to_bin(bin,item):
                   unfitted_items.append(item)

            if len(bin.items) == 0:
                return

            items_to_pack = unfitted_items
            unfitted_items = []
            self.current_configuration.append(bin)

    def calculate_statistics(self):
        statistics = {
            "loaded_volume": 0,
            "loaded_weight": 0,
        }
        configuration_volume = 0
        for bin in self.current_configuration:
            for item in bin.items:
                statistics["loaded_volume"] += item.volume.volume()
                statistics["loaded_weight"] += item.weight
            configuration_volume += bin._model.volume
        statistics["average_volume"] = statistics["loaded_volume"]/configuration_volume
        return statistics