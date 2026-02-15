from .Bin import Bin,BinModel
from .Item import Item
from .Space import Volume,Vector3, intersect, rect_intersect

class Constraint:
    """
    A Constraint to apply to a bin packing problem
    """
    def __init__(self,func ,weight : int = 0):
        """
        :param func: Function that evaluates the constraint
        :param weight: Weight used for evaluation order (generally more expensive constraint should have higher weight)
        :type weight: int
        :param type: A Type used to distinguish between constraints: STATIC a constraint that depends on statical properties of the bin and the item, SPACE_DEPENDENT a constraint that depends on the position of the item
        :type type: ConstraintType
        """
        self.func = func
        self.weight = weight
        self.kwargs = dict()
    
    def set_parameter(self,name : str, value) -> None:
        """
        Set parameters different from the bin and the item
        
        :param name: Name of the parameter
        :type name: str
        :param value: Value to set
        """
        self.kwargs[name] = value

    def __lt__(self,cmp): # used for ordering
        return self.weight < cmp.weight
    def __call__(self, bin : Bin, item : Item) -> bool:
        return self.func(bin,item,**self.kwargs)
    def __str__(self):
        return f"Constraint {self.func.__name__} weight({self.weight})"

# dictionary of currently available constraints
constraints = dict()

def constraint(weight : int):
    """
    Decorator for simple Constraint generation
    
    :param weight: Weight of the constraint (used for execution ordering - lighter before heavy)
    :type weight: int
    """
    def wrapper(func):
        constraints[func.__name__] = Constraint(func,weight)
        return func
    return wrapper

# Ready-Made Constraint

@constraint(weight=5)
def weight_within_limit(bin : Bin, item : Item) -> bool:
    """
    Check if the weight is under the limit if item would be added
    
    :param bin: Target bin
    :type bin: Bin
    :param item: Target item
    :type item: Item
    """
    return bin.weight+item.weight <= bin.max_weight

@constraint(weight=10)
def fits_inside_bin(bin : Bin, item : Item) -> bool:
    """
    Check if the item with its current position can fit inside the bin
    
    :param bin: Target bin
    :type bin: Bin
    :param item: Target item
    :type item: Item
    """
    return all(map(lambda axis: 0 <= item.position[axis] <= bin.dimensions[axis] - item.dimensions[axis],range(3)))
    
@constraint(weight=15)
def no_overlap(bin : Bin, item : Item) -> bool:
    """
    Check if the item with its current position overlap with other items inside the bin
    
    :param bin: Target bin
    :type bin: Bin
    :param item: Target item
    :type item: Item
    """
    return all(map(lambda vol: not intersect(vol,item),bin._model.dead_volumes)) and all(map(lambda vol: not intersect(vol,item), bin.items))

@constraint(weight=20)
def is_supported(bin: Bin, item : Item, allow_item_fall : bool = False, minimum_support : float = 0.5) -> bool:
    """
    Check if the item with its current position has something beneath to support it
    
    :param bin: Target bin
    :type bin: Bin
    :param item: Target item
    :type item: Item
    :param allow_item_fall: if True the item will be autorepositioned to the lowest height possible
    :type allow_item_fall: bool
    :param minimum_support: Minimum support surface in therms of total item surface
    :type minimum_support: float
    """
    complete_volumes_list = list(bin._model.dead_volumes)
    complete_volumes_list.extend(bin.items)
    current_support = 1.0
    lowest_available_y = 0
    item_surface = item.width*item.depth
    # only volumes that are positioned lower can support my item
    for vol in filter(lambda vol: vol.position.y < item.position.y, complete_volumes_list):
        # check for base intersection (plane x-z)
        support = rect_intersect(vol,item,Vector3.AXIS['x'],Vector3.AXIS['z'])/item_surface
        if support > 0:
            height = vol.position.y+vol.height
            if lowest_available_y < height:
                lowest_available_y = height
                current_support = support
            # in case two objects makes a same height plane both the areas cooperate in the support surface
            elif lowest_available_y == height:
                current_support += support

    if lowest_available_y == item.position.y:
        return current_support > minimum_support
    elif not allow_item_fall:
        return False
    elif current_support > minimum_support:
        item.position.y = lowest_available_y
        return True
    else:
        return False
        
# Constraint Testing
assert len(constraints) == 4, len(constraints)
assert constraints['weight_within_limit'] < constraints['fits_inside_bin'], constraints['weight_within_limit'].weight
testmodel1 = BinModel(None,[1,1.5,1],1,[constraints['weight_within_limit']],[Volume((1,.5,1),(0,1,0))])
testbin1 = Bin(None,testmodel1)
testitem1 = Item(None,Volume([1,.5,1]),.5,0)
testitem2 = Item(None,Volume([1,.5,1]),.5,0)
assert testbin1.put_item(testitem1), constraints['weight_within_limit'](testbin1,testitem1)
assert testbin1.items[0] == testitem1, testbin1.items
assert testbin1.put_item(testitem2,[constraints['fits_inside_bin']])
assert testbin1.items[1] == testitem2
prune_return = testbin1.prune(constraint=constraints['no_overlap'])
assert prune_return['notpass'] == [testitem1,testitem2] and prune_return['pass'] == [], (prune_return['notpass'],prune_return['pass'])
assert testbin1.remove_item(testitem2) and len(testbin1.items) == 1, testbin1.items
testmodel1.set_constraints([constraints['weight_within_limit'],constraints['fits_inside_bin'],constraints['no_overlap'],constraints['is_supported']])
assert not testbin1.put_item(testitem2) and len(testbin1.items) == 1
testitem2.position = Vector3(0,.5,0)
assert testbin1.put_item(testitem2), [c(testbin1,testitem2) for c in testbin1._model.constraints]
testitem3 = Item(None,Volume([.5,.5,.5]),0,0)
assert [c(testbin1,testitem3) for c in constraints.values()] == [ True, True, False, True], [c(testbin1,testitem3) for c in constraints.values()]
testitem3.position = Vector3(1,1.5,1)
testmodel1._size.y = 2 # bin 1x2x1
testitem3.weight = .001
assert [c(testbin1,testitem3) for c in constraints.values()] == [ False, False, True, False], [c(testbin1,testitem3) for c in constraints.values()]