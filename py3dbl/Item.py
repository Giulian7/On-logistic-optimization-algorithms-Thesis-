from decimal import Decimal
from .Space import Vector3, Volume
from .Decimal import set_to_decimal

class Item(Volume):
    def __init__(self, name, volume : Volume, weight : Decimal, priority : int):
        """
        :param name: A name associated to the item
        :param volume: The space occupied by the item
        :type volume: Volume
        :param weight: Weight of the Item
        :param priority: Priority given to the Item
        """
        super().__init__(size=volume.size,position=volume.position)
        self.name   = name
        self.weight = weight
        self.priority = priority

    @property
    def dimensions(self):
        return self.size

    def __str__(self):
        return f"{self.name}({self.width}x{self.height}x{self.depth}, weight:{self.weight}) pos({self.position}) vol({self.volume()})"
    
    def format_numbers(self, number_of_decimals):
        self.size.x = set_to_decimal(self.width, number_of_decimals)
        self.size.y = set_to_decimal(self.height, number_of_decimals)
        self.size.z = set_to_decimal(self.depth, number_of_decimals)
        self.weight = set_to_decimal(self.weight, number_of_decimals)

# Item testing
testitem1 = Item("testitem",Volume((1,2,3)),1,0)
assert str(testitem1) == "testitem(1x2x3, weight:1) pos(x:0,y:0,z:0) vol(6)", str(testitem1)
testitem2 = Item("testitem",Volume((1.1111,2.2222,3.3333)),1.1111,0)
testitem2.format_numbers(2)
assert str(testitem2) == "testitem(1.11x2.22x3.33, weight:1.11) pos(x:0,y:0,z:0) vol(8.205786)", str(testitem2)