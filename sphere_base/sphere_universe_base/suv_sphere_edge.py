# -*- coding: utf-8 -*-

"""
Sphere Edge module. Contains the SphereEdge class. Edges are drawn between spheres.

"""

from pyrr import quaternion, Vector3
# from sphere_iot.uv_socket import *
from sphere_base.sphere_universe_base.suv_graphic_edge import GraphicEdge
from sphere_base.serializable import Serializable
from collections import OrderedDict


DEBUG = False

class SphereEdge(Serializable):
    """
    Class representing an ``Edge`` between two ``Spheres``.

    """
    GraphicsEdge_class = GraphicEdge

    def __init__(self, universe, start_sphere, end_sphere):

        super().__init__("edge")
        self.uv = universe
        self._start_sphere_xyz = start_sphere
        self._end_sphere_xyz = end_sphere

        self.edge_model = self.uv.models.get_model('edge')
        self._init_variables()

        self.scale = Vector3(end_sphere) - Vector3(start_sphere)
        self.xyz = start_sphere
        self.orientation = [0.0, 0.0, 0.0, 1.0]

        # register the edge to the universe for rendering
        self.uv.add_edge(self)

    def _init_variables(self):
        self._edge_type = 0

    def update_position(self):
        pass

    def draw(self):
        self.edge_model.draw(self)

    def remove(self):
        """
         Remove this edge and the associated collision object
        """

        # self.uv.mouse_ray.delete_collision_object(self)
        self.uv.remove_edge(self)

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('type', self.type),
            ('edge_type', self._edge_type)
        ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        if restore_id: self.id = data['id']
        self.edge_type = data['edge_type']
        self.update_position()
        return True


