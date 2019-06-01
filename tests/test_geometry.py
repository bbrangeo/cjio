"""Geometry methods and functions

"""
import pytest

from cjio import models


@pytest.fixture(scope='module')
def data_geometry():
    vertices = [
        (0.0,1.0,0.0),
        (1.0,1.0,0.0),
        (2.0,1.0,0.0),
        (3.0,1.0,0.0),
        (4.0,1.0,0.0),
        (5.0,1.0,0.0)
    ]
    
    geometry = [{
        'type': 'CompositeSolid',
        'lod': 2,
        'boundaries': [
            [
                [
                    [[0, 0, 0, 0, 0]], [[1, 1, 1, 1]], [[2, 2, 2, 2]], [[3, 3, 3, 3]]
                ],
                [
                    [[2, 2, 2, 2]], [[3, 3, 3, 3]], [[4, 4, 4, 4]], [[5, 5, 5, 5]]
                ]
            ],
            [
                [[[0, 0, 0, 0, 0]], [[1, 1, 1, 1]], [[2, 2, 2, 2]], [[3, 3, 3, 3]]]
            ]
        ],
        'semantics': {
            'surfaces': [
                {
                    'type': 'WallSurface',
                    'slope': 33.4,
                    'children': [2],
                    'parent': 1
                },
                {
                    'type': 'RoofSurface',
                    'slope': 66.6,
                    'children': [0]
                },
                {
                    'type': 'Door',
                    'parent': 0,
                    'colour': 'blue'
                },
                {
                    'type': 'Door',
                    'parent': 0,
                    'colour': 'blue'
                }
            ],
            'values': [
                [[2, 1, 0, 3], [2, 1, 0, 3]],
                [None]
            ]
        }
    }]

    yield (geometry, vertices)


class TestGeometry:
    @pytest.mark.parametrize('type, boundary, result', [
        ('multipoint', [], []),
        ('multipoint',
         [2,4,5],
         [(2.0,1.0,0.0),(4.0,1.0,0.0),(5.0,1.0,0.0)]),
        ('multisurface',
         [[[2,4,5]]],
         [[[(2.0,1.0,0.0),(4.0,1.0,0.0),(5.0,1.0,0.0)]]]),
        ('multisurface',
         [[[2,4,5],[2,4,5]]],
         [[[(2.0,1.0,0.0),(4.0,1.0,0.0),(5.0,1.0,0.0)],[(2.0,1.0,0.0),(4.0,1.0,0.0),(5.0,1.0,0.0)]]]),
        ('solid',
         [
             [ [[0, 3, 2]], [[4, 5, 1]], [[0, 1, 5]] ],
             [ [[0, 3, 2]], [[4, 5, 1]], [[0, 1, 5]] ]
         ],
         [
             [ [[(0.0, 1.0, 0.0), (3.0, 1.0, 0.0), (2.0, 1.0, 0.0)]], [[(4.0, 1.0, 0.0), (5.0, 1.0, 0.0), (1.0, 1.0, 0.0)]],
               [[(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (5.0, 1.0, 0.0)]]],
             [ [[(0.0, 1.0, 0.0), (3.0, 1.0, 0.0), (2.0, 1.0, 0.0)]], [[(4.0, 1.0, 0.0), (5.0, 1.0, 0.0), (1.0, 1.0, 0.0)]],
               [[(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (5.0, 1.0, 0.0)]]]
         ]
         ),
        ('compositesolid',
         [
            [ [ [[0, 3, 2]], [[4, 5, 1]], [[0, 1, 5]] ] ],
            [ [ [[0, 3, 2]], [[4, 5, 1]], [[0, 1, 5]] ] ]
        ],
         [
             [[[[(0.0, 1.0, 0.0), (3.0, 1.0, 0.0), (2.0, 1.0, 0.0)]], [[(4.0, 1.0, 0.0), (5.0, 1.0, 0.0), (1.0, 1.0, 0.0)]],
               [[(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (5.0, 1.0, 0.0)]]]],
             [[[[(0.0, 1.0, 0.0), (3.0, 1.0, 0.0), (2.0, 1.0, 0.0)]], [[(4.0, 1.0, 0.0), (5.0, 1.0, 0.0), (1.0, 1.0, 0.0)]],
               [[(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (5.0, 1.0, 0.0)]]]]
         ]
         )
    ])
    def test_dereference_boundaries(self, data_geometry, type, boundary, result):
        vertices = data_geometry[1]
        geom = models.Geometry(type=type, boundaries=boundary, vertices=vertices)
        assert geom.boundaries == result


    def test_dereference_boundaries_wrong_type(self, data_geometry):
        geometry, vertices = data_geometry
        geometry[0]['type'] = 'CompositeSurface'
        with pytest.raises(TypeError) as e:
            models.Geometry(type=geometry[0]['type'],
                            boundaries=geometry[0]['boundaries'],
                            vertices=vertices)
            assert e == "Boundary definition does not correspond to MultiSurface or CompositeSurface"


    @pytest.mark.parametrize('values, surface_idx', [
        (
            None,
            dict()
        ),
        (
            [None],
            dict()
        ),
        (
            [[[0, 1, 2, None], [0, 1, 2, None]], [None]],
            {0: [[0, 0, 0],[0, 1, 0]],
             1: [[0, 0, 1],[0, 1, 1]],
             2: [[0, 0, 2],[0, 1, 2]]}
        )
    ])
    def test_index_surface_boundaries(self, values, surface_idx):
        res = models.Geometry._index_surface_boundaries(values)
        assert res == surface_idx


    @pytest.mark.parametrize('surface_idx, boundaries, surfaces', [
        (
                [],
                [],
                []
        ),
        (
                None,
                [],
                []
        ),
        (
                [[0]],  # 1. surface in a MultiSurface
                [[[0]], [[1]]],
                [[[0]]]
        ),
        (
                [[0], [1]],  # 1.,2. surface in a MultiSurface
                [[[0], [1]], [[2]]],
                [[[0], [1]], [[2]]]
        ),
        (
                [[0, 1], [0, 2], [1, 0]],
                # 2.,3. surface in exterior shell of Solid, 1. surface in interior shell of Solid
                [[[[0, 0]], [[0, 1]], [[0, 2]]], [[[1, 0]], [[1, 1]], [[1, 2]]]],
                [[[0, 1]], [[0, 2]], [[1, 0]]]
        ),
        (
                [[0, 0, 0], [0, 0, 2], [1, 0, 0]],
                # 1.,3. surf. of exterior of 1. Solid, 1. surface of exterior of 2. Solid
                [[[[[0, 0, 0]], [[0, 0, 1]], [[0, 0, 2]]]], [[[[1, 0, 0]], [[1, 0, 1]], [[1, 0, 2]]]]],
                [[[0, 0, 0]], [[0, 0, 2]], [[1, 0, 0]]]
        )
    ])
    def test_get_surface_boundaries(self, boundaries, surface_idx, surfaces):
        geom = models.Geometry()
        geom.boundaries = boundaries
        res = geom.get_surface_boundaries(surface_idx)
        assert res == surfaces

    def test_dereference_surfaces(self, data_geometry):
        geometry, vertices = data_geometry
        geom = models.Geometry(type='CompositeSurface')
        geom.boundaries = geometry[0]['boundaries']
        geom.semantics = geom._dereference_surfaces(geometry[0]['semantics'])
        result = {
            0: {
                'type': 'WallSurface',
                'attributes': {
                    'slope': 33.4,
                },
                'children': [2],
                'parent': 1,
                'surface_idx': [[0, 0, 2],[0, 1, 2]]
            },
            1: {
                'type': 'RoofSurface',
                'attributes': {
                    'slope': 66.6,
                },
                'children': [0],
                'surface_idx': [[0, 0, 1],[0, 1, 1]]
            },
            2: {
                'type': 'Door',
                'attributes': {
                    'colour': 'blue'
                },
                'parent': 0,
                'surface_idx': [[0, 0, 0],[0, 1, 0]]
            }
        }
        assert geom.semantics == result


    def test_get_surfaces(self, data_geometry):
        geometry, vertices = data_geometry
        geom = models.Geometry(type='CompositeSurface')
        geom.boundaries = geometry[0]['boundaries']
        geom.surfaces = {
            0: {
                'type': 'WallSurface',
                'attributes': {
                    'slope': 33.4,
                },
                'children': [2],
                'parent': 1,
                'surface_idx': [[0, 0, 2],[0, 1, 2]]
            },
            1: {
                'type': 'RoofSurface',
                'attributes': {
                    'slope': 66.6,
                },
                'children': [0],
                'surface_idx': [[0, 0, 1],[0, 1, 1]]
            },
            2: {
                'type': 'Door',
                'attributes': {
                    'colour': 'blue'
                },
                'parent': 0,
                'surface_idx': [[0, 0, 0],[0, 1, 0]]
            },
            3: {
                'type': 'Door',
                'attributes': {
                    'colour': 'red'
                },
                'parent': 0,
                'surface_idx': [[0, 0, 3], [0, 1, 3]]
            }
        }
        roof = list(geom.get_surfaces('roofsurface'))
        wall = list(geom.get_surfaces('wallsurface'))
        door = list(geom.get_surfaces('door'))
        assert roof == [{
            'type': 'RoofSurface',
            'attributes': {
                'slope': 66.6,
            },
            'children': [0],
            'surface_idx': [[0, 0, 1], [0, 1, 1]]
        }]
        assert wall == [{
            'type': 'WallSurface',
            'attributes': {
                'slope': 33.4,
            },
            'children': [2],
            'parent': 1,
            'surface_idx': [[0, 0, 2], [0, 1, 2]]
        }]
        assert door == [
            {
                'type': 'Door',
                'attributes': {
                    'colour': 'blue'
                },
                'parent': 0,
                'surface_idx': [[0, 0, 0], [0, 1, 0]]
            },
            {
                'type': 'Door',
                'attributes': {
                    'colour': 'red'
                },
                'parent': 0,
                'surface_idx': [[0, 0, 3], [0, 1, 3]]
            }
        ]


class TestGeometryIntegration:
    """Integration tests for operations on Geometry objects

    These tests mainly meant to mimic user workflow and test concepts
    """
    def test_get_surface_boundaries(self, data_geometry):
        """Test how to get the boundaries (geometry) of semantic surfaces"""
        geometry, vertices = data_geometry
        geom = models.Geometry(type=geometry[0]['type'],
                               lod=geometry[0]['lod'],
                               boundaries=geometry[0]['boundaries'],
                               semantics_obj=geometry[0]['semantics'],
                               vertices=vertices)
        roofsurfaces = geom.get_surfaces('roofsurface')
        rsrf_bndry = [geom.get_surface_boundaries(rsrf['surface_idx'])
                      for rsrf in roofsurfaces]
        roof_geom = [
            [
                [[(1.0, 1.0, 0.0), (1.0, 1.0, 0.0), (1.0, 1.0, 0.0), (1.0, 1.0, 0.0)]],
                [[(3.0, 1.0, 0.0), (3.0, 1.0, 0.0), (3.0, 1.0, 0.0), (3.0, 1.0, 0.0)]]
            ]
        ]
        assert rsrf_bndry == roof_geom

        doorsurfaces = geom.get_surfaces('door')
        dsrf_bndry = [geom.get_surface_boundaries(dsrf['surface_idx'])
                      for dsrf in doorsurfaces]
        door_geom = [
            [
                [[(0.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 0.0)]],
                [[(2.0, 1.0, 0.0), (2.0, 1.0, 0.0), (2.0, 1.0, 0.0), (2.0, 1.0, 0.0)]]
            ],
            [
                [[(3.0, 1.0, 0.0), (3.0, 1.0, 0.0), (3.0, 1.0, 0.0), (3.0, 1.0, 0.0)]],
                [[(5.0, 1.0, 0.0), (5.0, 1.0, 0.0), (5.0, 1.0, 0.0), (5.0, 1.0, 0.0)]]
            ]
        ]
        assert dsrf_bndry == door_geom

    def test_set_surface_attributes(self, data_geometry):
        """Test how to set attributes on semantic surfaces"""
        geometry, vertices = data_geometry
        geom = models.Geometry(type=geometry[0]['type'],
                               lod=geometry[0]['lod'],
                               boundaries=geometry[0]['boundaries'],
                               semantics_obj=geometry[0]['semantics'],
                               vertices=vertices)
        roofsurfaces = list(geom.get_surfaces('roofsurface'))
        rsrf_bndry = [geom.get_surface_boundaries(rsrf['surface_idx'])
                      for rsrf in roofsurfaces]
