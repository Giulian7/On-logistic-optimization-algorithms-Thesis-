import py3dbl

packer = py3dbl.Packer(algorithm=py3dbl.algorithms['base_packer'])
packer.set_default_bin(py3dbl.BinModel(
    name="Container",
    size=[2,2,4],
    max_weight=3000,
    constraints=[
        py3dbl.constraints['weight_within_limit'],
        py3dbl.constraints['fits_inside_bin'],
        py3dbl.constraints['no_overlap']
        ],
    ))
packer.add_batch(py3dbl.item_generator(
    width=(.1,1),
    height=(.1,1),
    depth=(.1,1),
    weight=(.1,1),
    batch_size=100
))
packer.pack()
