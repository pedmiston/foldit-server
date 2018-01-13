from folditdb.irdata import IRData

def test_cache_all_properties():
    irdata = IRData.from_file('tests/test_data/top_solution.json')
    assert len(irdata._cache) == 0
    assert len(dir(irdata)) > 0
    irdata.cache_all_properties()
    print(sorted(irdata._cache.keys()))
    print(sorted(dir(irdata)))
    print(set(irdata._cache.keys()) - set(dir(irdata)))
    assert len(irdata._cache) == len(dir(irdata))
