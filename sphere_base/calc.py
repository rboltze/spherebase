# -*- coding: utf-8 -*-

"""
Calculation module. Contains calculations used in several modules.
"""

from pyrr import Vector3, Vector4, vector, matrix44, quaternion
from sphere_base.utils import dump_exception
import math


class Calc:
    """
    contains calculation for putting items on a sphere. These calculations are used
    by nodes, sockets and edges.

    """

    def __init__(self):
        pass

    @staticmethod
    def get_item_direction_pointing_outwards(item: ('Node', 'Edge', 'Socket'), sphere: 'Sphere') -> 'Quaternion':
        """
        Calculates the quaternion pointing outwards from the center of the sphere_base through the center of the item

        :param item: ``Socket``, ``Node``, ``Edge``
        :type item: :class:`~sphere_iot.uv_socket.Socket`, :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`,
         :class:`~sphere_iot.uv_node.Node`
        :param sphere: The target ``sphere_base`` the item is on.
        :type sphere: :class:`~sphere_iot.uv_sphere.Sphere`
        :returns: ``Quaternion``

        """

        up = Vector3([0.0, 1.0, 0.0])
        direction = vector.normalize(Vector3(item.xyz) - Vector3(sphere.xyz))
        right = vector.normalize(Vector3.cross(up, direction))
        up = Vector3.cross(Vector3(direction), Vector3(right))
        m = matrix44.create_look_at(item.xyz, sphere.xyz, up)

        return quaternion.create_from_matrix(m)

    @staticmethod
    def move_to_position(cumulative_orientation: 'Quaternion', sphere: 'Sphere', radius: float) -> 'Vector4':
        """

        :param cumulative_orientation:
        :type cumulative_orientation: ``quaternion``
        :param sphere: The target sphere_base the item is on
        :type sphere: :class:`~sphere_iot.uv_sphere.Sphere`
        :param radius: The radius of the target sphere_base
        :type radius: ´´float´´
        :returns: ``Vector4`` position

        Calculate the xyz position of an item on the surface of a sphere based on the angle with the center of the
        sphere. The cumulative angle takes into account that the sphere_base can rotate and is not in the
        default position.

        The calculation starts with a node vector in the center of the default sphere_base at the [0.0, 0.0, 0.0]
        position, with a length 1.0 on the y axis. This node vector is then rotated so it points at the
        cumulative_orientation. It is then moved over the radius distance to take its place on the surface of the
        default sphere_base. Finally it needs to be translated to the sphere it is actually on.

        """

        # create the rotation matrix
        rm = matrix44.create_from_quaternion(cumulative_orientation)

        # rotating the node vector
        node_origin = Vector4([0.0, radius, 0.0, 1.0])
        xyzw = matrix44.apply_to_vector(rm, node_origin)

        # translation matrix to move the node to world space
        sphere = Vector4([*sphere.xyz, 1])
        tm = matrix44.create_from_translation(sphere)

        # moving the node vector
        xyzw = matrix44.apply_to_vector(tm, xyzw)

        return Vector4(xyzw).xyz

    @staticmethod
    def find_angle_from_world_pos(collision_point, sphere_orientation_offset) -> 'quaternion':
        """
        given the xyz collision point of the mouse_ray with the surface of target sphere,
        calculate the angle from a starting point on the surface of the sphere.

        Find the center and the radius of the sphere. Then the offset of the sphere rotation with the
        zero rotation in angles.

        The calculation starts with a vector of length 1 from the center of the sphere on the y axis.
        This node vector is then rotated so it points at the collision point. We need the angle that the vector rotates
        over the z axis and the angle needed to rotate the vector over the x axis

                # αx =−arctan2(y1, x1).
                # αy = arcsin(x2)−arccos(z1).
                # αx = arctan2(z2, y2).
        """

        if collision_point:
            try:
                p1 = [1, 0, 0]
                p2 = collision_point  # The position of the point in world space

                x1, x2 = p1[0], p2[0]
                y1, y2 = p1[1], p2[1]
                z1, z2 = p1[2], p2[2]

                # The vector [0, 1, 0] is rotated over the z-axis (pitch)
                ay = math.asin(x2) - math.acos(z1)

                # and then over the x axis (yaw)
                ax = math.atan2(z2, y2)

                # Correct the rotation with the default sphere position with the default camera direction
                pitch_rad = -ay + ((math.pi / 180) * 90)
                yaw_rad = ax

                # rotation quaternions
                yaw_q = quaternion.create_from_eulers([yaw_rad, 0.0, 0.0])
                pitch_q = quaternion.create_from_eulers([0.0, pitch_rad, 0.0])

                # first apply the vertical offset to the current sphere orientation, to avoid gimbal lock
                orientation_with_yaw = quaternion.cross(yaw_q, sphere_orientation_offset)

                # then apply the pitch movement over the equator
                pos_orientation_offset = quaternion.cross(orientation_with_yaw, pitch_q)

                return pos_orientation_offset

            except Exception as e:
                dump_exception(e)

    @staticmethod
    def get_distance_on_sphere(point1: Vector3, point2: Vector3, radius: float) -> float:
        """
        Returns the distance between two points on the surface of a sphere_base. Based on ``Great-circle`` distance
        finding the shortest-distance on a sphere_base.

        :param point1: position of point 1
        :param point1: ``Vector3``
        :param point2: position of point 2
        :param point2:  ``Vector3``
        :param radius: radius of the sphere_base
        :param radius:  ``Float``
        :returns: ``Float``

        """

        # two points on the sphere_base
        p1, p2 = Vector3(point1.xyz), Vector3(point2.xyz)

        # finding the direct distance
        d = math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2)

        # compute the angle underlying one half of phi,
        phi = math.asin((d / 2 / radius))

        # return the distance on the great circle
        return 2 * phi * radius
