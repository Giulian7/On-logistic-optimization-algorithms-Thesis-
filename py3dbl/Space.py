from decimal import Decimal
import functools as tools

class Vector3:
    """
    A point in a 3D space

    Note: keep an eye on object assignment (which is by reference) and argument packing/unpacking in constructors
    """
    AXIS = { "x": 0, "y": 1, "z": 2}

    def __init__(self, x : Decimal = 0, y : Decimal = 0, z : Decimal = 0):
        self.vect = [Decimal(x),Decimal(y),Decimal(z)]

    @property
    def x(self):
        return self.vect[self.AXIS["x"]]
    @property
    def y(self):
        return self.vect[self.AXIS["y"]]
    @property
    def z(self):
        return self.vect[self.AXIS["z"]]
    @x.setter
    def x(self,value):
        self.vect[self.AXIS["x"]] = value
    @y.setter
    def y(self,value):
        self.vect[self.AXIS["y"]] = value
    @z.setter
    def z(self,value):
        self.vect[self.AXIS["z"]] = value

    def __len__(self):
        return 3
    
    def __getitem__(self,idx : int):
        return self.vect[idx]
    
    def __setitem__(self,idx : int, value : Decimal):
        self.vect[idx] = value
    
    def __str__(self):
        return f"x:{self.x},y:{self.y},z:{self.z}"
    
    def __add__(self,target):
        y = Vector3(*target)
        y.x += self.x
        y.y += self.y
        y.z += self.z
        return y

    def rotate90(self, orizontal : bool = False, vertical : bool = False):
        """
        Rotate of 90 degrees in orizontal or vertical
        
        :param self: Current Vector3 object
        :param orizontal: True to make a orizontal rotation (i.e. width-depth)
        :type orizontal: bool
        :param vertical: True to make a vertical rotation (i.e. height-depth)
        :type vertical: bool
        """
        if orizontal:
            self.vect[0], self.vect[2] = self.vect[2], self.vect[0]
        if vertical:
            self.vect[1], self.vect[2] = self.vect[2], self.vect[1]

# Vector3 Testing

v3test1 = Vector3(2,1)
assert str(v3test1) == "x:2,y:1,z:0", str(v3test1)
assert str(v3test1+[1,1,1]) == "x:3,y:2,z:1", str(v3test1+[1,1,1])
v3test2 = Vector3(*v3test1)
assert str(v3test2) == str(v3test1)
v3test2.rotate90(orizontal=True)
assert v3test2.x == v3test1.z and v3test2.z == v3test1.x, (v3test2,v3test1)
v3test2.rotate90(orizontal=True)
assert str(v3test2) == str(v3test1), (v3test2, v3test1)
v3test2.rotate90(vertical=True)
assert v3test2.y == v3test1.z and v3test2.z == v3test1.y

class Volume:
    """
    Models an occupied space
    """

    def __init__(self, size : Vector3, position : Vector3 = Vector3()):
        """
        Constructor for Volume object
        
        :param self: Current Volume object
        :param size: 3D Vector that describes the size of the occupied space
        :type size: Vector3
        :param position: 3D Vector that describes the central point 
        :type position: Vector3
        """
        self.position = Vector3(*position)
        self.size = Vector3(*size)

    @property
    def width(self):
        return self.size.x
    @property
    def height(self):
        return self.size.y
    @property
    def depth(self):
        return self.size.z

    def volume(self):
        """
        Volumetric occupation
        """
        return tools.reduce(lambda x,y: x*y, self.size.vect, 1)

    def rotate90(self, orizontal : bool = False, vertical : bool = False):
        """
        Rotate of 90 degrees in orizontal or vertical
        
        :param orizontal: True to make a orizontal rotation (i.e. width-depth)
        :type orizontal: bool
        :param vertical: True to make a vertical rotation (i.e. height-depth)
        :type vertical: bool
        """
        self.size.rotate90(orizontal,vertical)

    def _find_surface(self, type : bool) -> tuple[int,int]:
        """
        Common routine for shortest_surface and widest_surface
        
        :param type: True for shortest_s, False for widest_s 
        :type type: bool
        :return: A tuple containing the two axis that generates the required surface
        :rtype: tuple[int, int]
        """
        operator = (lambda x,y: x < y) if type else (lambda x,y: x > y)
        ax1 = 0
        ax2 = ax1+1
        v1 = self.size[ax1]
        v2 = self.size[ax2]
        for idx in range(1,3):
            dim = self.size[idx]
            if operator(dim,v1):
                ax2, ax1 = ax1, idx
                v2, v1 = v1, dim
            elif operator(dim,v2):
                ax2 = idx
                v2 = dim
        return (ax1,ax2)

    def shortest_surface(self):
        """
        Find the shortest surface (in terms of generating axis)
        
        :return: A tuple containing the two axis that generates the shortest surface
        """
        return self._find_surface(True)

    def widest_surface(self):
        """
        Find the widest surface (in terms of generating axis)
        
        :return: A tuple containing the two axis that generates the widest surface
        """
        return self._find_surface(False)

    def set_bottom_surface(self,axes : tuple[int,int]) -> None:
        """
        Rotate the object to have the surface generated by axes on the bottom
        
        :param axes: The couple of axes that generates the surface (i.e. (0,1) back-front, (0,2) bottom-top, (1,2) left-right)
        :type axes: tuple[int, int]
        """
        rot = sum(axes)
        if rot == 1:
            self.rotate90(vertical=True)
        elif rot == 3:
            self.rotate90(orizontal=True,vertical=True)

def rect_intersect(item1 : Volume, item2 : Volume, x : int, y : int, as_surface : bool = True) -> Decimal|tuple[Decimal,Decimal]:
    """
    Check for 2D intersection on the plane formed by the given axis (x,y)
    
    :param item1: First 3D object (intersected)
    :type item1: Volume
    :param item2: Second 3D object (intersector)
    :type item2: Volume
    :param x: First axis
    :type x: int
    :param y: Second axis
    :type y: int
    :param as_surface: if True the intersection is returned as the area of overlap, if False as a couple (x_overlap,y_overlap)
    :return: The intersection area value (if as_surface is True) or projection tuple on the two axes (is as_surface is False)
    :rtype: tuple[Decimal,Decimal]
    """
    d1 = item1.size # sizes of 1
    d2 = item2.size # sizes of 2

    cx1 = item1.position[x] + d1[x]/2 # center of 1 on axis x
    cy1 = item1.position[y] + d1[y]/2 # center of 1 on axis y
    cx2 = item2.position[x] + d2[x]/2 # center of 2 on axis x
    cy2 = item2.position[y] + d2[y]/2 # center of 2 on axis y

    # distance between the centers
    ix = abs(cx2 - cx1)
    iy = abs(cy2 - cy1)

    overlap_x = max(0,(d1[x]+d2[x])/2 - ix)
    overlap_y = max(0,(d1[y]+d2[y])/2 - iy)

    return overlap_x*overlap_y if as_surface else (overlap_x,overlap_y)


def intersect(item1 : Volume, item2 : Volume) -> bool:
    """
    Simple 3D intersection utility
    
    :param item1: First 3D object (intersected)
    :type item1: Volume
    :param item2: Second 3D object (intersector)
    :type item2: Volume
    :return: True if there's volumetric intersection else False
    :rtype: bool
    """
    return (
        rect_intersect(item1, item2, Vector3.AXIS["x"], Vector3.AXIS["y"])!=0 and
        rect_intersect(item1, item2, Vector3.AXIS["y"], Vector3.AXIS["z"])!=0 and
        rect_intersect(item1, item2, Vector3.AXIS["x"], Vector3.AXIS["z"])!=0
    )

# Volume Testing

v3size = Vector3(3,2,1)
voltest1 = Volume(v3size)
assert str(v3size) == str(voltest1.size) and str(Vector3()) == str(voltest1.position), ",".join(str(voltest1.size),str(voltest1.position))
assert voltest1.volume() == 6, voltest1.volume()
voltest2 = Volume(v3size)
assert rect_intersect(voltest1,voltest2,0,1) == 6, rect_intersect(voltest1,voltest2,0,1)
assert rect_intersect(voltest1,voltest2,0,2) == 3, rect_intersect(voltest1,voltest2,0,2)
assert rect_intersect(voltest1,voltest2,1,2) == 2, rect_intersect(voltest1,voltest2,1,2)
voltest2.position = Vector3(3,2,1)
assert rect_intersect(voltest1,voltest2,0,1) == 0, rect_intersect(voltest1,voltest2,0,1)
assert rect_intersect(voltest1,voltest2,0,2) == 0, rect_intersect(voltest1,voltest2,0,2)
assert rect_intersect(voltest1,voltest2,1,2) == 0, rect_intersect(voltest1,voltest2,1,2)
assert voltest1.widest_surface() == (0,1) or voltest1.widest_surface() == (1,0) , str(voltest1.widest_surface())
assert voltest1.widest_surface() == voltest2.widest_surface(), str(voltest1.widest_surface())
assert voltest1.shortest_surface() == (2,1) or voltest1.shortest_surface() == (1,2)
assert voltest1.shortest_surface() == voltest2.shortest_surface()
surface_axes = voltest1.widest_surface()
surface_area = voltest1.size[surface_axes[0]]*voltest1.size[surface_axes[1]]
voltest1.set_bottom_surface(surface_axes)
assert voltest1.width*voltest1.depth == surface_area
surface_axes = voltest1.shortest_surface()
surface_area = voltest1.size[surface_axes[0]]*voltest1.size[surface_axes[1]]
voltest1.set_bottom_surface(surface_axes)
assert voltest1.width*voltest1.depth == surface_area