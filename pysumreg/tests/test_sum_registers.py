from ..sum_registers import SummationRegisters
import pytest

# fmt: off
# ophyd.sim: noisy_det v motor
TEST_DATA_WEAK_PEAK = {
    'x': ['-7.822', '-7.322', '-6.822', '-6.322', '-5.822', '-5.322',
        '-4.822', '-4.322', '-3.822', '-3.322', '-2.822', '-2.322',
        '-1.822', '-1.322', '-0.822', '-0.322', '0.178', '0.678'],
    'y': ['-0.070', '-0.001', '0.081', '-0.041', '0.058', '-0.044', '-0.025',
        '0.077', '0.023', '0.054', '0.098', '0.018', '0.098', '0.420',
        '0.721', '0.930', '1.079', '0.764']
}
# USAXS: I0_USAXS v. m_stage_r, uid=8a0c1b76-1e2a-4455-b5d7-596fa4783f66
TEST_DATA_STRONG_PEAK = {
    "x": [6.61855017, 6.61874433, 6.61892933, 6.61910517, 6.61930183,
       6.619486  , 6.61967933, 6.6198535 , 6.6200435 , 6.62022767,
       6.6204185 , 6.62060183, 6.62079183, 6.62096683, 6.6211635 ,
       6.62133933, 6.621531  , 6.62172183, 6.621911  , 6.622091  ,
       6.62229017, 6.622466  , 6.62266267, 6.62285017, 6.62302683,
       6.6232085 , 6.62339683, 6.623591  , 6.62377433, 6.623966  ,
       6.624146  ],
    "y": [  392.,   393.,   395.,   399.,   405.,   420.,   478.,   818.,
        1987.,  4170.,  7426., 11318., 15220., 18448., 20585., 21263.,
       20030., 17632., 14223., 10267.,  6882.,  4339.,  2509.,  1454.,
         842.,   580.,   481.,   444.,   426.,   415.,   409.]
}
# fmt: on


def test_create():
    reg = SummationRegisters()

    for k in reg._registers:
        assert hasattr(reg, k)
        assert getattr(reg, k) == 0, k

    for k in reg._property_methods:
        assert k in dir(reg), k  # avoids implicit evaluation during getattr()

    expected = {k: 0 for k in reg._registers}
    expected.update({k: None for k in reg._property_methods})
    expected.update({k: None for k in reg._extrema_names})
    actual = reg.to_dict(use_registers=True)
    assert actual == expected


def test_sample1():
    # example from https://goodcalculators.com/linear-regression-calculator/
    y_arr = [4.182, 3.887, 2.283, 7.327, 8.411, 7.808, 8.422, 6.330, 10.138, 5.871]
    x_arr = list(range(1, 1 + len(y_arr)))
    assert len(x_arr) == 10

    reg = SummationRegisters()
    for x, y in zip(x_arr, y_arr):
        reg.add(x, y)
    assert reg.min_x == min(x_arr)
    assert reg.max_x == max(x_arr)
    assert reg.min_y == min(y_arr)
    assert reg.max_y == max(y_arr)
    assert reg.x_at_max_y == x_arr[y_arr.index(reg.max_y)]
    assert reg.x_at_min_y == x_arr[y_arr.index(reg.min_y)]

    assert reg.n == 10
    assert round(reg.X, 3) == 55
    assert round(reg.Y, 3) == 64.659
    assert round(reg.XX, 3) == 385.000
    assert round(reg.XY, 3) == 396.562
    assert round(reg.YY, 3) == 471.451

    assert round(reg.mean_x, 3) == 5.5
    assert round(reg.mean_y, 3) == 6.466
    assert round(reg.stddev_x, 3) == 3.028
    assert round(reg.stddev_y, 3) == 2.435

    assert round(reg.slope, 3) == 0.496
    assert round(reg.intercept, 3) == 3.737
    assert round(reg.correlation, 3) == 0.617


@pytest.mark.parametrize(
    "data, expected, ndigits",
    [
        # fmt: off
        [  # sample 1 - a noisy line with positive slope
            # data from https://www.statssolver.com/simple-regression.html
            dict(x=[2, 4, 6, 8, 10], y=[9, 14, 7, 18, 27]),
            dict(
                slope=2,
                intercept=3,
                correlation=0.79,
                centroid=7.07,
                sigma=2.87,
            ),
            2,
        ],
        [  # sample 2 - a noisy line with negative slope
            # data from https://www.statssolver.com/simple-regression.html
            dict(x=[4, 12, 8, 16, 10], y=[45, 35, 45, 15, 25]),
            dict(
                slope=-2.5,
                intercept=58,
                correlation=-0.86,
                min_x=4,
                max_x=16,
                min_y=15,
                max_y=45,
                centroid=8.79,
                sigma=3.68,
            ),
            2,
        ],
        [  # sample 3 - a triangle centered at zero (in x)
            dict(x=[-1, -0.5, 0, 0.5, 1], y=[0, 0.5, 1, 0.5, 0]),
            dict(
                slope=0,
                intercept=0.4,
                correlation=0,
                centroid=0,
                sigma=0.35,
            ),
            2,
        ],
        [  # sample 4 - some non-zero y values
            dict(x=[0, 5, 10, 20, 21, 22, 51, 105], y=[0, 0, 0, 0.1, 1, 0, 0, 0]),
            dict(
                x_at_max_y=21,
                centroid=20.91,
                sigma=0.29,
            ),
            2,
        ],
        [  # sample 5 - NeXus simple example
            dict(  # https://manual.nexusformat.org/examples/python/index.html
                x=[  # mr
                    17.92608,
                    17.92591,
                    17.92575,
                    17.92558,
                    17.92541,
                    17.92525,
                    17.92508,
                    17.92491,
                    17.92475,
                    17.92458,
                    17.92441,
                    17.92425,
                    17.92408,
                    17.92391,
                    17.92375,
                    17.92358,
                    17.92341,
                    17.92325,
                    17.92308,
                    17.92291,
                    17.92275,
                    17.92258,
                    17.92241,
                    17.92225,
                    17.92208,
                    17.92191,
                    17.92175,
                    17.92158,
                    17.92141,
                    17.92125,
                    17.92108,
                ],
                y=[  # I00
                    1037,
                    1318,
                    1704,
                    2857,
                    4516,
                    9998,
                    23819,
                    31662,
                    40458,
                    49087,
                    56514,
                    63499,
                    66802,
                    66863,
                    66599,
                    66206,
                    65747,
                    65250,
                    64129,
                    63044,
                    60796,
                    56795,
                    51550,
                    43710,
                    29315,
                    19782,
                    12992,
                    6622,
                    4198,
                    2248,
                    1321,
                ],
            ),
            dict(
                x_at_max_y=17.9239,
                max_y=66863,
                centroid=17.9235,
                sigma=0.0009,
            ),
            4,
        ],
        [  # sample 6 - a square wave
            dict(x=[-2, -1, 0, 1, 2, 3, 4, 5, 6], y=[0, 0, 0, 1, 1, 1, 0, 0, 0]),
            dict(
                slope=0,
                intercept=0.333,
                correlation=0,
                centroid=2,
                sigma=0.816,
            ),
            3,
        ],
        [  # sample 7 - ophyd.sim: noisy_det v motor
            {
                "x": [-7.822, -7.322, -6.822, -6.322, -5.822, -5.322,
                    -4.822, -4.322, -3.822, -3.322, -2.822, -2.322,
                    -1.822, -1.322, -0.822, -0.322, 0.178, 0.678],
                "y": [-0.070, -0.001, 0.081, -0.041, 0.058, -0.044, -0.025,
                    0.077, 0.023, 0.054, 0.098, 0.018, 0.098, 0.420,
                    0.721, 0.930, 1.079, 0.764]
            },
            dict(
                correlation=0.804,
                centroid=-0.367,
                sigma=0.789,
            ),
            3,
        ],
        [  # sample 8 - USAXS: I0_USAXS v. m_stage_r
            # uid=8a0c1b76-1e2a-4455-b5d7-596fa4783f66
            # Multiplied X data by 10 to get more sig figs on sigma
            {
                "x": [
                    66.1855017, 66.1874433, 66.1892933, 66.1910517, 66.1930183,
                    66.19486  , 66.1967933, 66.198535 , 66.200435 , 66.2022767,
                    66.204185 , 66.2060183, 66.2079183, 66.2096683, 66.211635 ,
                    66.2133933, 66.21531  , 66.2172183, 66.21911  , 66.22091  ,
                    66.2229017, 66.22466  , 66.2266267, 66.2285017, 66.2302683,
                    66.232085 , 66.2339683, 66.23591  , 66.2377433, 66.23966  ,
                    66.24146
                ],
                "y": [
                    392.,   393.,   395.,   399.,   405.,   420.,   478.,   818.,
                    1987.,  4170.,  7426., 11318., 15220., 18448., 20585., 21263.,
                    20030., 17632., 14223., 10267.,  6882.,  4339.,  2509.,  1454.,
                    842.,   580.,   481.,   444.,   426.,   415.,   409.
                ]
            },
            dict(
                correlation=0.001,
                centroid=66.214,
                sigma=0.007,
            ),
            3,
        ],
        # fmt: on
    ],
)
def test_samples(data, expected, ndigits):
    assert len(data["x"]) == len(data["y"])

    reg = SummationRegisters()
    for x, y in zip(data["x"], data["y"]):
        reg.add(x, y)
    for k, v in expected.items():
        assert round(getattr(reg, k), ndigits) == v, str(k)

    # are these values within expectations?
    assert reg.min_x <= reg.centroid <= reg.max_x
    assert (reg.max_x - reg.min_x) >= reg.sigma

    assert reg.linear_y(0) == reg.intercept  # OK to evaluate with full precision
    assert round(reg.linear_y(1) - reg.intercept, 2) == round(reg.slope, 2)


@pytest.mark.parametrize(
    "data, exception",
    [
        # fmt: off
        [  # array length of 0
            dict(x=[], y=[]),
            ZeroDivisionError,
        ],
        [  # array length of 1
            dict(x=[1], y=[0]),
            ZeroDivisionError,
        ],
        [  # array length of 2
            dict(x=[1, 2], y=[0, None]),
            TypeError,
        ],
        # fmt: on
    ],
)
def test_exceptions(data, exception):
    """Test with "bad" data that raises exceptions."""
    reg = SummationRegisters()
    with pytest.raises(exception):
        for x, y in zip(data["x"], data["y"]):
            reg.add(x, y)
        assert reg.sigma is not None


@pytest.mark.parametrize(
    "data, expected",
    [
        # fmt: off
        [
            dict(x=[2, 1, 3], y=[5, 1, 2]),
            dict(
                mean_x=2,
                mean_y=2.67,
                stddev_x=1,
                stddev_y=2.08,
                slope=0.5,
                intercept=1.67,
                correlation=0.24,
                centroid=2.12,
                sigma=0.6,
                min_x=1,
                max_x=3,
                min_y=1,
                max_y=5,
                x_at_max_y=2,
                x_at_min_y=1,
                n=3,
                X=6,
                Y=8,
                XX=14,
                XY=17,
                XXY=39,
                YY=30,
            ),
        ],
        # fmt: on
    ],
)
def test_to_dict(data, expected):
    reg = SummationRegisters()
    for x, y in zip(data["x"], data["y"]):
        reg.add(x, y)
    actual = reg.to_dict(use_registers=True)
    for k in actual.keys():
        assert k in expected, k
    for k, e in sorted(expected.items()):
        assert k in actual, k
        assert round(actual[k], 2) == e, k


def test_subtract():
    reg = SummationRegisters()
    assert reg.n == 0
    assert reg.X == 0
    assert reg.XX == 0
    assert reg.min_x is None
    assert reg.max_x is None
    assert reg.x_at_max_y is None

    reg.add(1, 1)
    assert reg.n == 1
    assert reg.X != 0
    assert reg.XX != 0
    assert reg.min_x is not None
    assert reg.max_x is not None
    assert reg.x_at_max_y is not None
    assert reg.min_x == 1
    assert reg.max_x == 1
    assert reg.x_at_max_y == 1

    reg.subtract(1, 1)
    assert reg.n == 0
    assert reg.X == 0
    assert reg.XX == 0
    assert reg.min_x is not None
    assert reg.max_x is not None
    assert reg.x_at_max_y is not None
    assert reg.min_x == 1
    assert reg.max_x == 1
    assert reg.x_at_max_y == 1
