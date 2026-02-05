
from decimal import Decimal
from .Decimal import set_to_decimal
from .Item import Item
from .Space import Vector3, Volume, intersect, rect_intersect

MINIMUM_SUPPORT_SURFACE = .5

class BinModel:
    """
    Describes a model of bin
    """
    def __init__(self, name : str, size : Vector3, max_weight : Decimal):
        """
        BinModel constructor
        
        :param self: Current BinModel object
        :param name: A descriptive name for the model
        :type name: str
        :param size: 3D vector that defines the sizes of the Bin
        :type size: Vector3
        :param max_weight: Maximum weight allowed to load
        :type max_weight: Decimal
        """
        self.name = name
        self._size = Vector3(*size)
        self.max_weight = max_weight

    # Properties to simplify access
    # Note: sizes are only defined on construction
    @property
    def width(self):  return self._size.x
    @width.setter
    def width(self,value):  self._size.x = value

    @property
    def height(self): return self._size.y
    @height.setter
    def height(self,value): self._size.y = value

    @property
    def depth(self):  return self._size.z
    @depth.setter
    def depth(self,value):  self._size.z = value

    @property
    def dimension(self): return self._size

    @property
    def volume(self):    return self.width * self.height * self.depth
    
    def __str__(self):
        return "%s(%sx%sx%s, max_weight:%s) vol(%s)" % (
            self.name, self.width, self.height, self.depth, self.max_weight,
            self.volume
        )
    
    def format_numbers(self, number_of_decimals):
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.max_weight = set_to_decimal(self.max_weight, number_of_decimals)


class Bin:
    """
    Describes a loadable bin (i.e. an instance of a bin)
    """
    def __init__(self, id, model : BinModel):
        """
        Bin constructor
        
        :param self: Current Bin object
        :param id: identifier (no uniqueness constraint)
        :param model: Reference model
        :type model: BinModel
        """
        self.id = id
        self._model : BinModel   = model
        self.weight : Decimal    = 0   # Current loaded weight
        self.items  : list[Item] = []  # Current loaded items

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
    def dimension(self):
        return self._model.dimension
    @property
    def max_weight(self):
        return self._model.max_weight

    def __str__(self):
        return f"Bin {self.id} of model {self._model.name}: loaded items {len(self.items)}"

    def put_item(self, item : Item, pivot : Vector3 = Vector3(), static_constraints = [], space_constraints = []):
        """
        Insert an item in the bin
        
        :param item: Item to insert
        :type item: Item
        :param pivot: Starting position of the item
        :type pivot: Vector3
        :param static_constraints: List of static constraints (see .Constraints) to follow
        :param space_constraints: List of space constraints (see .Constraints) to follow
        """
        valid_item_position = item.position
        item.position = Vector3(*pivot)

        # Static constraints depends only on the static properties of the bin and the item
        # we can evaluate them for first
        if not all([c(self,item) for c in static_constraints]):
            return False

        for oriz_deg_free in range(2):
            for vert_deg_free in range(2):
                # Space constraints must be evaluated for every spatial configuration
                if all([c(self,item) for c in space_constraints]):
                    self.items.append(item)
                    self.weight += item.weight
                    return True
                else:
                    item.rotate90(vertical=True)
            
            item.rotate90(orizontal=True)

        item.position = valid_item_position
        return False
    
    def remove_item(self, item : Item):
        try:
            self.items.remove(item)
            self.weight -= item.weight
            return True
        except ValueError:
            return False # the item was not there