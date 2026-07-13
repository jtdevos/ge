from ge.data import GameData, I_MEN


def test_ship_classes_load():
    d = GameData()
    assert len(d.classes) == 34
    interceptor = d.classes[1]
    assert interceptor.name == "Interceptor"
    assert interceptor.acceleration == 5000
    assert interceptor.max_warp == 10
    assert interceptor.price == 65000
    assert len(d.user_classes()) == 10  # classes 1-9 plus 41


def test_constants_and_config():
    d = GameData()
    assert d.const.ENGYMAX == 65000
    assert d.const.TICKTIME == 6
    assert d.cfg.UNIVMAX == 300
    assert d.cfg.UNIVWRAP is False
    assert len(d.shield_prices) == 19
    assert d.shield_prices[0] == 5000
    assert d.baseprice[I_MEN] == 2


def test_neutral_sector_table():
    d = GameData()
    assert len(d.neutral_planets) == 6
    zygor = d.neutral_planets[0]
    assert zygor.name == "Zygor"
    assert zygor.type == 1
    assert (zygor.x, zygor.y) == (5000, 5000)
    portals = [p for p in d.neutral_planets if p.type == 3]
    assert {p.name for p in portals} == {
        "Kayriez Portal", "Lydorian Portal", "Tryklon Portal"}
