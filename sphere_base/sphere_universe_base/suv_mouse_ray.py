# -*- coding: utf-8 -*-

"""
This is the ``MouseRay`` module. This module is used for determining which object is on_current_row_changed
by the mouse pointer.
It uses the ``PyBullet`` library to shoot a ray into the ``PyBullet`` physics simulation
which is a copy of the :class:`~sphere_iot.uv_universe.Universe` with all its ``Model`` objects.
It returns the collision object the mouse ray hits.

This module also creates all collision objects in the ``PyBullet`` simulation world for all the models used in the
:class:`~sphere_iot.uv_universe.Universe` implementation.

"""

import pybullet as p
from pyrr import Vector3, Vector4, vector, matrix44
from sphere_base.constants import *
from sphere_base.utils import dump_exception
from pybullet_utils import bullet_client as bc

DEBUG = False
DEBUG_SHOW_GUI = False
DEBUG_MOUSE_RAY = False

COLLISION_SHAPES = {
    "sphere_base": {"type": p.GEOM_SPHERE, "radius": SPHERE_RADIUS, "height": 0, "base_mass": 0,
                    "baseVisualShapeIndex": -1},
    "node": {"type": p.GEOM_SPHERE, "radius": NODE_DISC_RADIUS, "height": 0, "base_mass": 0,
             "baseVisualShapeIndex": -1},
    "socket": {"type": p.GEOM_CYLINDER, "radius": SOCKET_RADIUS, "height": 0, "base_mass": 0,
               "baseVisualShapeIndex": -1},
    "edge": {"type": p.GEOM_MESH, "height": .025, "base_mass": 0, "baseVisualShapeIndex": -1},
    "sphere_small": {"type": p.GEOM_CYLINDER, "radius": SPHERE_SMALL_RADIUS, "height": .026, "base_mass": 0,
                     "baseVisualShapeIndex": -1},
          }


class MouseRay:
    """
    This class maintains a parallel PyBullet physics reality of the :class:`~sphere_iot.uv_universe.Universe`.
    For this it creates, places and maintains collision object shapes for all models which can be hit
    by a ray emitted from the mouse pointer.

    """

    def __init__(self, universe: 'Universe', pybullet_key=None):

        """
        Constructor of the ``MouseRay`` class.

        :param universe: The 'PyBullet' physics simulation is a copy of the :class:`~sphere_iot.uv_universe.Universe`
        :type universe:  :class:`~sphere_iot.uv_universe.Universe`

        :Instance Attributes:

            - **camera** - Instance of :class:`~sphere_iot.uv_cam.camera`
            - **uv** - Instance of :class:`~sphere_iot.uv_universe.Universe`

        """

        self.uv = universe
        self.cam = universe.cam

        self.client_id = 0
        self.pybullet_key = pybullet_key
        self.abs_pos = [0.0, 0.0, 0.0]  # position of mouse ray collision point in world space

        self._collision_objects = {}
        self._collision_shapes = {}

        self._open_bullet_client(self.pybullet_key)
        self._create_collision_shapes()

    def _open_bullet_client(self, pybullet_key):
        if DEBUG_SHOW_GUI:
            p.connect(p.GUI)
        elif pybullet_key:
            try:

                self.bullet = bc.BulletClient(connection_mode=p.DIRECT)
                self.client_id = self.bullet._client

            except Exception as e:
                dump_exception(e)

        else:
            p.connect(p.DIRECT)

    def _create_collision_shapes(self):
        """
        Creates a dictionary with collision shapes used for all models used in the implementation.

        """

        self._collision_shapes = {
            'sphere_small': self.bullet.createCollisionShape(p.GEOM_SPHERE, radius=SPHERE_SMALL_RADIUS, height=0),
            'sphere_base': self.bullet.createCollisionShape(p.GEOM_SPHERE, radius=SPHERE_RADIUS, height=0),
            'node': self.bullet.createCollisionShape(p.GEOM_CYLINDER, radius=NODE_DISC_RADIUS, height=0.025),
            'socket': self.bullet.createCollisionShape(p.GEOM_CYLINDER, radius=SOCKET_RADIUS, height=0.026),

        }

    def create_collision_object(self, obj: ('Sphere', 'Node', 'Socket', 'Edge'), vertices: list = None):
        """
        Allocates the correct collision object.

        :param obj: Each item has a type.
        :param obj: Can be: :class:`~sphere_iot.uv_sphere.Sphere`, :class:`~sphere_iot.uv_node.Node`,
        :class:`~sphere_iot.uv_socket.Socket`, :class:`~sphere_iot.uv_edge.SphereSurfaceEdge``
        :param vertices: when lines are drawn, the vertices determine the collision shape
        :param vertices: ``list``
        """
        cs = COLLISION_SHAPES

        for key in cs.keys():
            if key == obj.type:

                if key == "edge":
                    pass
                    collision_shape = self.bullet.createCollisionShape(p.GEOM_MESH, vertices=vertices)
                    object_id = self.bullet.createMultiBody(baseMass=cs[key]["base_mass"],
                                                            baseCollisionShapeIndex=collision_shape,
                                                            baseVisualShapeIndex=cs[key]["baseVisualShapeIndex"],
                                                            physicsClientId=self.client_id)
                else:

                    object_id = self.bullet.createMultiBody(baseMass=cs[key]["base_mass"],
                                                            baseCollisionShapeIndex=self._collision_shapes[key],
                                                            baseVisualShapeIndex=cs[key]["baseVisualShapeIndex"],
                                                            basePosition=[obj.xyz[0], obj.xyz[1], obj.xyz[2]],
                                                            baseOrientation=obj.orientation,
                                                            physicsClientId=self.client_id)

                self._collision_objects[object_id] = obj.id
                return object_id

    def delete_collision_object(self, item: ('Sphere', 'Node', 'Socket', 'Edge')):
        """
        Delete the collision object of the item

        :param item: The model the collision object belongs to.
        :param item: :class:`~sphere_iot.uv_sphere.Sphere`, :class:`~sphere_iot.uv_node.Node`,
        :class:`~sphere_iot.uv_socket.Socket`, :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
        """
        self.bullet.removeBody(item.collision_object_id, physicsClientId=self.client_id)

    def reset_position_collision_object(self, item: ('Sphere', 'Node', 'Socket', 'Edge')):
        """
        Reset the collision object of the item

        :param item: The model the collision object belongs to.
        :param item: :class:`~sphere_iot.uv_sphere.Sphere`, :class:`~sphere_iot.uv_node.Node`,
        :class:`~sphere_iot.uv_socket.Socket`, :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`

        .. warning::

            The build in 'reset method' of PyBullet does not not give the desired result. It did not work for me.
            The work around is to delete the current collision object and create a new one. This is likely
            more expensive.

            It is also executed quite often and more than is strictly needed. When the position
            of the model changes the position of the collision object is updated too. This might be changed in
            an update that only takes place when dragging stops or when a button is released.

        """
        # TODO: resetting does not work correctly and we are using a work round of destroying
        #  the current collision object and re-creating it
        #
        # This does not work correctly:
        # self.bullet.resetBasePositionAndOrientation(bodyUniqueId=item.collision_object_id,
        #                                   posObj=[item.xyz[0], item.xyz[1], item.xyz[2]],
        #                                   ornObj=item.orientation)

        # the below works for now.... But it seems to have too much overhead. Instead of moving an
        # object we are destroying and then recreating it.

        self.bullet.removeBody(item.collision_object_id, physicsClientId=self.client_id)
        self.create_collision_object(item)

        if DEBUG and item.collision_object_id == 1:
            self.debug_collision_object(item.collision_object_id, item)

        return item.id, item.xyz

    def check_mouse_ray(self, mouse_x: float, mouse_y: float) -> (int, list):
        """
        returns name and position of the collision object the the mouse ray collides with.

        :param mouse_x: mouse x position
        :type mouse_x: ``float``
        :param mouse_y: mouse y position
        :type mouse_y: ``float``
        :returns: id of the collision object id and its position
        """
        ray_world = self.get_mouse_point(mouse_x, mouse_y)

        intersection = self.bullet.rayTest(self.cam.xyz, self.cam.xyz + (ray_world * 100),
                                           physicsClientId=self.client_id)
        object_id = intersection[0][0]

        try:
            if object_id >= 0:
                if DEBUG_MOUSE_RAY:
                    self.debug_mouse_ray(intersection)
                self.abs_pos = intersection[0][3]
                return self._collision_objects[object_id], self.abs_pos
            else:
                return None, None
        except Exception as e:
            print(mouse_x, mouse_y, intersection)
            dump_exception(e)
            return None, None

    def check_mouse_ray_batch(self, sphere: 'Sphere', ray_array_start: 'Vector3', ray_array_end: 'Vector3') -> list:
        """
        Returns a ``list`` of object id`s of the collision objects in the path of the mouse ray.

        :param sphere:
        :type sphere: :class:`~sphere_iot.uv_sphere.Sphere`
        :param ray_array_start: The mouse ray starting point
        :type ray_array_start: ``Vector3``
        :param ray_array_end: The mouse ray ending point
        :type ray_array_end: ``Vector3``
        :return: list of collision object ids
        """

        # used by rubber band box
        result_array = []
        point_at = self.bullet.rayTestBatch(ray_array_start, ray_array_end, physicsClientId=self.client_id)

        for result in point_at:
            if result[0] > -1 and self._collision_objects[result[0]] != sphere.id:
                if self._collision_objects[result[0]] not in result_array:
                    result_array.append(self._collision_objects[result[0]])

        return result_array

    def get_ray_clip(self, mouse_x: float, mouse_y: float, mouse_z: float = -1.0) -> 'Vector4':
        """
        Mouse position in opengl clip space
        showing mouse position as fraction of the screen. The center of the screen is the 0.0 position.

        :param mouse_x: x position of the mouse.
        :param mouse_x: ``float``
        :param mouse_y: y position of the mouse.
        :param mouse_y: ``float``
        :param mouse_z: fixed z plane position of the plane the mouse moves over.
        :param mouse_z: ``float``
        :return: ``Vector4`` mouse position as a fraction of the screen

        """
        x = (2.0 * mouse_x) / self.uv.view.view_width - 1.0
        y = 1.0 - (2.0 * mouse_y) / self.uv.view.view_height
        z = mouse_z
        return Vector4([x, y, z, 1.0])

    def get_mouse_point(self, mouse_x: float, mouse_y: float) -> 'Vector3':
        """
        Get the position of the mouse pointer in world view

        :param mouse_x: x position of the mouse.
        :param mouse_x: ``float``
        :param mouse_y: y position of the mouse.
        :param mouse_y: ``float``
        :return: ``Vector3`` position of mouse pointer in world view
        """

        # ray origin is the camera position and goes through the mouse
        ray_clip = self.get_ray_clip(mouse_x, mouse_y, mouse_z=-1.0)

        # projection_matrix: camera parameters (ratio, field of view, near and far planes)
        projection_matrix = self.uv.shader.projection_matrix
        inverse_projection_matrix = matrix44.inverse(projection_matrix)

        ray_eye = Vector4(matrix44.multiply(inverse_projection_matrix, ray_clip))
        ray_eye = Vector4([ray_eye.x, ray_eye.y, -1.0, 0.0])

        view_matrix = self.cam.get_view_matrix()

        ray_world = Vector4(matrix44.multiply(view_matrix, ray_eye)).xyz
        ray_world = Vector3(ray_world)
        ray_world = vector.normalize(ray_world)

        return ray_world

    def reset(self):
        """
        Resetting the physics simulation and recreating all collision shapes

        """
        self.bullet.resetSimulation(physicsClientId=self.client_id)
        self._create_collision_shapes()

    def debug_collision_object(self, collision_object_id: int, item: ('Sphere', 'Node', 'Socket', 'Edge')):
        """
        Method used for debugging.

        :param collision_object_id: ìd of the collision object
        :param collision_object_id: ``int``
        :type item: :class:`~sphere_iot.uv_sphere.Sphere`, :class:`~sphere_iot.uv_node.Node`,
        :class:`~sphere_iot.uv_socket.Socket, :class:`~sphere_iot.uv_edge.SphereSurfaceEdge``

        :return:
        """
        print("\n---------------------------")
        print("Node id and collision object id  :             ", item.id, collision_object_id)
        print("Node id and position and rotation :            ", item.xyz, item.orientation)
        print("Collision object id, position and rotation :   ",
              self.bullet.getBasePositionAndOrientation(collision_object_id, physicsClientId=self.client_id))
        print("Collision shape data :                          ",
              self.bullet.getCollisionShapeData(collision_object_id, -1, physicsClientId=self.client_id))

    def debug_mouse_ray(self, intersection):
        print("objectUniqueId:", intersection[0][0])
        print("global collision object id:", self._collision_objects[intersection[0][0]])
        print("linkIndex:", intersection[0][1])
        print("hit fraction:", intersection[0][2])
        print("hit position:", intersection[0][3])
        print("hit normal:", intersection[0][4])
