import py3dbp
from random import random

packer = py3dbp.Packer()
for idx in range(100):
    packer.add_item(py3dbp.Item(
        name=idx,
        width=.1+random()*.9,
        height=.1+random()*.9,
        depth=.1+random()*.9,
        weight=.1+random()*.9,
    ))
    packer.add_bin(py3dbp.Bin(
        name="Container",
        width=2,
        height=2,
        depth=4,
        max_weight=3000
    ))
packer.pack(distribute_items=True)
