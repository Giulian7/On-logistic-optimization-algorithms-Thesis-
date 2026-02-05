
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
    
    # Constraint Checks

    def _weight_whitin_limit(self, item : Item):
        return self.weight+item.weight <= self.max_weight
    
    def _fits_inside_bin(self, item : Item):
        dimension = item.dimensions
        return (self.width > item.position.x + dimension.x and
            self.height > item.position.y + dimension.y and
            self.depth > item.position.z + dimension.z
        )
    
    def _no_overlap(self, item : Item):
        return len(self.items) == 0 or not any([intersect(ib.volume,item.volume) for ib in self.items])

    def _is_supported(self, item : Item, allow_item_fall : bool = True, minimum_support = MINIMUM_SUPPORT_SURFACE):
        if item.position.y == 0:
            return True
        else:
            highest_y = 0
            target_items = []
            for ib in self.items:
                # check for 
                if rect_intersect(ib.volume,item.volume,Vector3.AXIS['x'],Vector3.AXIS['z']) > minimum_support:
                    target_items.append(ib)
                    highest_y = max(highest_y,ib.position.y+ib.height)

            if len(target_items)==0 or (not allow_item_fall and highest_y!=item.position.y):
                return False
            else:
                item.position.y = highest_y
                return True

    def put_item(self, item : Item, pivot : Vector3 = Vector3(), minimum_support=MINIMUM_SUPPORT_SURFACE):

        valid_item_position = item.position
        item.position = Vector3(*pivot)

        # first check on weight constraint (simplest check)
        if not self._weight_whitin_limit(item):
            return False

        for oriz_deg_free in range(2):
            for vert_deg_free in range(2):

                if self._fits_inside_bin(item) and \
                   self._no_overlap(item) and \
                   self._is_supported(item=item, allow_item_fall=True, minimum_support=minimum_support):                    
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
            return False