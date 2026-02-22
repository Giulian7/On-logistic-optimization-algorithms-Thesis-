import plotly.graph_objects as go
from .Bin import Bin
from .Item import Item
from .Space import Volume

COLORS = ["cyan","red","yellow","blue","green","brown","magenta"]
BORDER_WIDTH = 1
BORDER_COLOR = "black"
TRANSPARENCY = .5

def render_volume_interactive(volume : Volume, fig : go.Figure, color : str, name : str = "", show_border : bool = True, border_width : float = BORDER_WIDTH, border_color : str = BORDER_COLOR, transparency : float = TRANSPARENCY):   
    """
    An interactive 3D rendering of a volume object
    
    :param volume: Target volume
    :type volume: Volume
    :param fig: A go figure as rendering target
    :type fig: go.Figure
    :param color: Color of the rendered volume
    :type color: str
    :param name: A name to associate to the volume
    :type name: str
    :param border_width: Size of the volume's border
    :type border_width: float
    :param border_color: Color of the volume's border
    :type border_color: str
    :param transparency: Transparency of the object
    :type transparency: float
    """
    x, y, z = [float(value) for value in volume.position]   # position from bottom-back-left corner
    w, h, d = [float(value) for value in volume.size] # actual dimensions of the item (considered rotation)
    fig.add_trace(go.Mesh3d(
            x=[x, x+w, x+w, x, x, x+w, x+w, x],
            z=[y, y, y+h, y+h, y, y, y+h, y+h],
            y=[z, z, z, z, z+d, z+d, z+d, z+d],
            contour_show = show_border,
            contour_width= border_width,
            contour_color= border_color,
            color=color,
            opacity= (1.0 - transparency),
            name=name,
            alphahull=0,
            showscale=False
        ))
    
def render_item_interactive(item : Item, fig : go.Figure, color : str, show_border : bool = True, border_width : float = BORDER_WIDTH, border_color : str = BORDER_COLOR, transparency : float = TRANSPARENCY):
    render_volume_interactive(item,fig,color,item.name,show_border,border_width,border_color,transparency)

def render_bin_interactive(bin : Bin, colors : list[str] = COLORS, render_bin : bool = True, border_width : float = BORDER_WIDTH, border_color : str = BORDER_COLOR, transparency : float = TRANSPARENCY):

    fig = go.Figure()

    bin_render_params = {
        "color": "lightgrey",
        "name": "Bin",
        "show_border": False
    }

    for dead_volume in bin._model.dead_volumes:
         render_volume_interactive(volume=dead_volume,fig=fig,transparency=.1,**bin_render_params)

    for idx,item in enumerate(bin.items):
        render_item_interactive(item=item,fig=fig,color=colors[idx%len(colors)],border_width=border_width,border_color=border_color,transparency=transparency)

    if render_bin:
        render_volume_interactive(Volume(bin.dimensions),fig=fig,transparency=.9,**bin_render_params)

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Width'),
            zaxis=dict(title='Height'),
            yaxis=dict(title='Depth'),
            aspectmode='data'
        ),
        title=f"3D Packing Visualization - {bin}"
    )

    fig.show()