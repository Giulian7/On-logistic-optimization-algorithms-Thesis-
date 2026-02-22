from decimal import Decimal
from .Decimal import set_to_decimal
from .Item import Item
from .Space import Vector3, Volume
from typing import Sequence, Iterable
from functools import reduce

class BinModel():
    """
    Describes a model of bin
    """
    def __init__(self, name : str, size : Sequence[3], max_weight : Decimal, constraints : Iterable = [], dead_volumes : Iterable[Volume] = []):
        """
        :param name: A descriptive name for the model
        :type name: str
        :param size: 3D vector that defines the sizes of the Bin
        :type size: Vector3
        :param max_weight: Maximum weight allowed to load
        :type max_weight: Decimal
        :param constraints: A list of constraints proper of the model
        :type constraints: list[Constraint]
        """
        self.name = name
        self._size = Vector3(*size)
        self.max_weight = max_weight
        self.set_constraints(constraints)
        self.dead_volumes = list(dead_volumes)

    # Properties to simplify access
    # Note: sizes are only defined on construction
    @property
    def width(self): return self._size.x
    @width.setter
    def width(self,value): self._size.x = value

    @property
    def height(self): return self._size.y
    @height.setter
    def height(self,value): self._size.y = value

    @property
    def depth(self): return self._size.z
    @depth.setter
    def depth(self,value): self._size.z = value

    @property
    def dimensions(self): return self._size

    def volume(self):
        return (self.width * self.height * self.depth) - reduce(lambda x,y: x+y.volume(), self.dead_volumes,0)
    
    def __str__(self):
        return "%s(%sx%sx%s, max_weight:%s) vol(%s)" % (
            self.name, self.width, self.height, self.depth, self.max_weight,
            self.volume()
        )
    
    def set_constraints(self, constraints : list) -> None:
        self.constraints = list(constraints)
        self.constraints.sort()

    def format_numbers(self, number_of_decimals) -> None:
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.max_weight = set_to_decimal(self.max_weight, number_of_decimals)

# BinModel Testing
testmodel1 = BinModel("testmodel",(1,2,3),1,[],[Volume((1,1,1))])
assert str(testmodel1) == "testmodel(1x2x3, max_weight:1) vol(5)", str(testmodel1)
testmodel1.width = Decimal(1.1111)
testmodel1.height = Decimal(2.2222)
testmodel1.depth = Decimal(3.3333)
testmodel1.max_weight = Decimal(1.1111)
testmodel1.format_numbers(2)
assert str(testmodel1) == "testmodel(1.11x2.22x3.33, max_weight:1.11) vol(7.205786)", str(testmodel1)
# set_constraints to test in constraints module

class Bin:
    """
    Describes a loadable bin (i.e. an instance of a bin)
    """
    def __init__(self, id, model : BinModel):
        """
        :param id: identifier (no uniqueness constraint)
        :param model: Reference model
        :type model: BinModel
        """
        self.id = id
        self._model = model
        self.items  = list() # Current loaded items
        self.weight = 0      # Current loaded weight

    # Properties to access model data
    # Note: direct write access is not allowed
    @property
    def width(self):
        return self._model.width
    @property
    def height(self):
        return self._model.height
    @property
    def depth(self):
        return self._model.depth
    @property
    def dimensions(self):
        return self._model.dimensions
    @property
    def max_weight(self):
        return self._model.max_weight
    
    def volume(self):
        return self._model.volume()
    
    def free_volume(self):
        return self.volume() - reduce(lambda x,y: x+y.volume(), self.items, 0)

    def __str__(self):
        return f"Bin {self.id} of model {self._model.name}: loaded items {len(self.items)}"

    def put_item(self, item : Item, additional_constraints : list = list()) -> bool:
        """
        Insert an item in the bin
        
        :param item: Item to insert
        :type item: Item
        :param pivot: Starting position of the item
        :type pivot: Vector3
        :param constraints: List of additional constraints (see .Constraints) to follow
        :type static_constraints: list[Constraint]
        """
        
        if all(map(lambda c: c(self,item), additional_constraints)) and all(map(lambda c: c(self,item),self._model.constraints)):
            self.items.append(item)
            self.weight += item.weight
            return True
        else:
            return False
    
    def remove_item(self, item : Item) -> bool:
        """
        Remove the specified Item from the list, return True if the item was found, False if not
        
        :param item: The item to remove
        :type item: Item
        :return: True if item was present else False
        :rtype: bool
        """
        try:
            self.items.remove(item)
            self.weight -= item.weight
            old_items = self.items
            for item in old_items:
                if not all(map(lambda c: c(self,item),self._model.constraints)):
                    self.items.remove(item)
            return True
        except ValueError:
            return False # the item was not there
        
    def reset(self) -> None:
        """
        Clear the bin from any item
        """
        self.items = list()
        self.weight = 0

    def prune(self,constraint) -> dict[str:list[Item]]:
        """
        Simulate the application of a constraint
        :param constraint: The constraint to apply
        :type constraint: Constraint
        :return: A dictonary which a list of the items that violate the constraint (key notpass) and a list of items that passed the constraint (key pass)
        :rtype: dict[str:list[Item]]
        """
        to_keep = []
        to_remove = []
        for item in self.items:
            if constraint(self,item):
                to_keep.append(item)
            else:
                to_remove.append(item)
        return {"notpass":to_remove,"pass":to_keep}

# Bin testing
testbin1 = Bin(1,testmodel1)
assert str(testbin1) == "Bin 1 of model testmodel: loaded items 0", str(testbin1)
testitem1 = Item("testitem",Volume([2,2,2]),2,0) # no constraints are set so I can put anything
assert testbin1.put_item(testitem1), " ".join(testbin1.items)
testbin1.reset()
assert len(testbin1.items) == 0, len(testbin1.items)
# prune to test in constraints module
