from decimal import Decimal
from .Bin import Bin, BinModel
from .Item import Item
from .Space import Vector3
from .Constraints import Constraint

class PackingAlgorithm:
    def __init__(self,func):
        self.func = func
        self.kwargs = dict()

    def set_parameter(self, name : str, value):
        """
        Set the parameter with the given name to the given value
        
        :param name: Target parameter name 
        :type name: str
        :param value: Target paramenter value
        """
        self.kwargs[name] = value

    def __call__(self, bins : list[Bin], items : list[Item], constraints : list[Constraint]):
        """
        Algorithm Execution
        
        :param bins: Fleet to run the algorithm on
        :type bins: list[Bin]
        :param items: Items to pack
        :type items: list[Item]
        :param constraints: Constraints to follow during the packing
        :type constraints: list[Constraint]
        """
        return self.func(bins,items,constraints,**self.kwargs)

algorithms : dict[str:PackingAlgorithm] = dict()

def algorithm(algorithm_function):
    """
    Decorator for simple PackingAlgorithm generation
    """
    algorithms[algorithm_function.__name__] = PackingAlgorithm(algorithm_function)
    return algorithm_function

@algorithm
def base_packer(available_bins : list[Bin], items_to_pack : list[Item], constraints : list[Constraint], default_bin : None|BinModel = None):
    """
    The algorithm used by the original py3dbp Packer.pack()
    
    :param available_bins: A fleet of bins to use
    :type available_bins: list[Bin]
    :param items_to_pack: The list of items to pack
    :type items_to_pack: list[Item]
    :param constraints: Constraints to follow (additional to the constraints of the model)
    :type constraints: list[Constraint]
    :param default_bin: A default bin to use if there are no more available bins
    :type default_bin: None | BinModel
    """
    def try_fit(bin : Bin, item : Item):
        old_pos = item.position
        for ib in bin.items:
            pivot = Vector3(*ib.position)
            for axis in range(3):
                item.position = pivot + map(lambda x: ib.dimensions[x] if x == axis else 0, range(3))
                for oriz_deg_free in range(2):
                    for vert_deg_free in range(2):
                        if bin.put_item(item,constraints):
                            return True
                        else:
                            item.rotate90(vertical=True)
                    item.rotate90(orizontal=True)
        item.position = old_pos
        return False

    current_configuration = []
    unfitted_items = []
    constraints.sort()
    items_to_pack.sort(key=lambda item: item.volume())
    available_bins.sort(key=lambda bin: bin.volume())

    while len(items_to_pack) != 0:
        if available_bins != None and len(available_bins) != 0:
            bin = Bin(len(current_configuration),available_bins.pop(0))
        elif default_bin != None:
            bin = Bin(len(current_configuration),default_bin)
        else:
            break

        for item in items_to_pack:
            if not bin.items:
                item.position = Vector3()
                if not bin.put_item(item,constraints):
                    unfitted_items.append(item)
            else:
                if not try_fit(bin,item):
                    unfitted_items.append(item)

        # if no item has been packed probably there's no solution
        if len(bin.items) == 0:
            break

        items_to_pack = unfitted_items
        unfitted_items = []
        current_configuration.append(bin)
    
    return current_configuration

## Here I left some very simple algorithms

def _try_fit(bin : Bin, item : Item, constraints : list[Constraint], allow_full_rotation = False):
    old_pos = item.position
    initial_state = item.stand
    for ib in bin.items:
        pivot = Vector3(*ib.position)
        for axis in [0,2,1]:
            for versor in [1,-1]:
                item.position = pivot + map(lambda x: ib.dimensions[x]*versor if x == axis else 0, range(3))
                for orizontal_deg_free in range(2):
                    for vertical_deg_free in range(2):
                        if bin.put_item(item,constraints):
                            return True
                        item.rotate90(orizontal=not initial_state,vertical=initial_state)
                    if allow_full_rotation: item.rotate90(vertical=not initial_state, orizontal=initial_state)
                    else: break
    item.position = old_pos
    return False

@algorithm
def all_stand(available_bins : list[Bin], items_to_pack : list[Item], constraints : list[Constraint], default_bin : None|BinModel = None, allow_full_rotation : bool = False):
    """
    An algorithm that before the insertion makes all the item stand on the smallest side
    
    :param available_bins: A fleet of bins to use
    :type available_bins: list[Bin]
    :param items_to_pack: The list of items to pack
    :type items_to_pack: list[Item]
    :param constraints: Constraints to follow (additional to the constraints of the model)
    :type constraints: list[Constraint]
    :param default_bin: A default bin to use if there are no more available bins
    :type default_bin: None | BinModel
    :param allow_full_rotation: True allow items to rotate on the axis "other" axis
    :type allow_full_rotation: bool
    """
    current_configuration = []
    unfitted_items = []
    constraints.sort()
    available_bins.sort(key=lambda bin: bin.volume())

    for item in items_to_pack:
        surface_idx = item.shortest_surface()
        item.stand = True
        item.min_surface = item.dimensions[surface_idx[0]] * item.dimensions[surface_idx[1]]
        item.set_bottom_surface(surface_idx)
        

    items_to_pack.sort(key=lambda item: item.volume(),reverse=True)
    items_to_pack.sort(key=(lambda item: item.min_surface),reverse=True)
    for idx, item in enumerate(items_to_pack):
        item.name = idx  

    while len(items_to_pack) != 0:
        if available_bins != None and len(available_bins) != 0:
            bin = Bin(len(current_configuration),available_bins.pop(0))
        elif default_bin != None:
            bin = Bin(len(current_configuration),default_bin)
        else:
            break

        for item in items_to_pack:
            
            if not bin.items:
                item.position = Vector3()
                if not bin.put_item(item,constraints):
                    unfitted_items.append(item)
            else:
                if not _try_fit(bin,item,constraints,allow_full_rotation=allow_full_rotation):
                    unfitted_items.append(item)

        # if no item has been packed probably there's no solution
        if len(bin.items) == 0 and (available_bins == None or len(available_bins)==0):
            break

        items_to_pack = unfitted_items
        unfitted_items = []
        current_configuration.append(bin)
    
    return current_configuration

@algorithm
def all_lay(available_bins : list[Bin], items_to_pack : list[Item], constraints : list[Constraint], default_bin : None|BinModel = None, allow_full_rotation = False):
    """
    An algorithm that before the insertion makes all the item lay on the widest side
    
    :param available_bins: A fleet of bins to use
    :type available_bins: list[Bin]
    :param items_to_pack: The list of items to pack
    :type items_to_pack: list[Item]
    :param constraints: Constraints to follow (additional to the constraints of the model)
    :type constraints: list[Constraint]
    :param default_bin: A default bin to use if there are no more available bins
    :type default_bin: None | BinModel
    :param allow_full_rotation: True allow items to rotate on the axis "other" axis
    :type allow_full_rotation: bool
    """
    current_configuration = []
    unfitted_items = []
    constraints.sort()
    available_bins.sort(key=lambda bin: bin.volume())

    for item in items_to_pack:
        surface_idx = item.widest_surface()
        item.stand = False
        item.max_surface = item.dimensions[surface_idx[0]] * item.dimensions[surface_idx[1]]
        item.set_bottom_surface(surface_idx)

    items_to_pack.sort(key=lambda item: item.volume())
    items_to_pack.sort(key=(lambda item: item.max_surface),reverse=True)
    for idx, item in enumerate(items_to_pack):
        item.name = idx  

    while len(items_to_pack) != 0:
        if available_bins != None and len(available_bins) != 0:
            bin = Bin(len(current_configuration),available_bins.pop(0))
        elif default_bin != None:
            bin = Bin(len(current_configuration),default_bin)
        else:
            break

        for item in items_to_pack:
            
            if not bin.items:
                item.position = Vector3()
                if not bin.put_item(item,constraints):
                    unfitted_items.append(item)
            else:
                if not _try_fit(bin,item,constraints,allow_full_rotation=allow_full_rotation):
                    unfitted_items.append(item)

        # if no item has been packed probably there's no solution
        if len(bin.items) == 0:
            break

        items_to_pack = unfitted_items
        unfitted_items = []
        current_configuration.append(bin)
    
    return current_configuration

@algorithm
def big_lay_small_stand(available_bins : list[Bin], items_to_pack : list[Item], constraints : list[Constraint], default_bin : None|BinModel = None, volume_threashold = Decimal(.5), allow_full_rotation = False):
    """
    An algorithm that before the insertion makes the items that have less volume than threshold stand on the smallest side and the items that have more volume than threshold lay on the widest side
    
    :param available_bins: A fleet of bins to use
    :type available_bins: list[Bin]
    :param items_to_pack: The list of items to pack
    :type items_to_pack: list[Item]
    :param constraints: Constraints to follow (additional to the constraints of the model)
    :type constraints: list[Constraint]
    :param default_bin: A default bin to use if there are no more available bins
    :type default_bin: None | BinModel
    :param volume_threshold: Absolute volume units threshold for decide if an item is small or big
    :type volume_threshold: Decimal
    :param allow_full_rotation: True allow items to rotate on the axis "other" axis
    :type allow_full_rotation: bool
    """

    current_configuration = []
    unfitted_items = []
    constraints.sort()
    available_bins.sort(key=lambda bin: bin.volume())

    for item in items_to_pack:
        item.stand = item.volume() < volume_threashold
        item.set_bottom_surface(
            item.shortest_surface() if item.volume() < volume_threashold else
            item.widest_surface()
        )     

    items_to_pack.sort(key=lambda item: item.volume(), reverse=True)
    for idx, item in enumerate(items_to_pack):
        item.name = idx  

    while len(items_to_pack) != 0:
        if available_bins != None and len(available_bins) != 0:
            bin = Bin(len(current_configuration),available_bins.pop(0))
        elif default_bin != None:
            bin = Bin(len(current_configuration),default_bin)
        else:
            break

        for item in items_to_pack:
            
            if not bin.items:
                item.position = Vector3()
                if not bin.put_item(item,constraints):
                    unfitted_items.append(item)
            else:
                if not _try_fit(bin,item,constraints, allow_full_rotation=allow_full_rotation):
                    unfitted_items.append(item)

        # if no item has been packed probably there's no solution
        if len(bin.items) == 0:
            break

        items_to_pack = unfitted_items
        unfitted_items = []
        current_configuration.append(bin)
    
    return current_configuration