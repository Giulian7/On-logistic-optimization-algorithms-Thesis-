import benchmarking as b
from py3dbl.Constraints import constraints

b.packing_benchmarker(["py3dbp","base_packer"],[constraints['weight_within_limit'],constraints['fits_inside_bin'],constraints['no_overlap']],end=300,start=100)