from ge.geometry import Coord, cbearing, cdistance, coord1, coord2, normal, smallest, vector


def test_normal_wraps():
    assert normal(370) == 10
    assert normal(-10) == 350
    assert normal(0) == 0
    assert normal(720.5) == 0.5


def test_smallest_angle():
    assert smallest(350, 10) == 20
    assert smallest(10, 350) == 20
    assert smallest(0, 180) == 180
    assert smallest(90, 90) == 0


def test_vector_cardinals():
    o = Coord(0.0, 0.0)
    assert vector(o, Coord(0.0, -1.0)) == 0      # north
    assert vector(o, Coord(1.0, 0.0)) == 90      # east
    assert vector(o, Coord(0.0, 1.0)) == 180     # south
    assert vector(o, Coord(-1.0, 0.0)) == 270    # west


def test_cbearing_relative():
    o = Coord(0.0, 0.0)
    east = Coord(1.0, 0.0)
    # facing north, target east -> starboard 90
    assert cbearing(o, east, heading=0.0) == 90
    # facing south, target east -> port 90
    assert cbearing(o, east, heading=180.0) == -90
    # facing east, target east -> dead ahead
    assert cbearing(o, east, heading=90.0) == 0


def test_coord_split():
    assert coord1(5.25) == 5
    assert coord1(-5.25) == -6
    assert coord2(5.25) == 2500
    assert cdistance(Coord(0, 0), Coord(3, 4)) == 5
