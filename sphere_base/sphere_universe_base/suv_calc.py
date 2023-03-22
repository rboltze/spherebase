# -*- coding: utf-8 -*-

"""
Calculation module. Contains calculations used in several modules.
"""

from pyrr import Vector3, Vector4, vector, matrix44, quaternion
import math



class UvCalc:
    """
    contains calculation for putting items on a sphere_base. These calculations are used
    by nodes, sockets and edges.

    """

    def __init__(self):
        pass

    def get_item_direction_pointing_outwards(self, item: ('Node', 'Edge', 'Socket'), sphere: 'Sphere') -> 'Quaternion':
        """
        Calculates the quaternion pointing outwards from the center of the sphere_base through the center of the item

        :param item: ``Socket``, ``Node``, ``Edge``
        :type item: :class:`~sphere_iot.uv_socket.Socket`, :class:`~sphere_iot.uv_edge.SphereSurfaceEdge` :class:`~sphere_iot.uv_node.SphereNode`
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

    def move_to_position(self, cumulative_orientation: 'Quaternion', sphere: 'Sphere', radius: float) -> 'Vector4':
        """

        :param cumulative_orientation:
        :type cumulative_orientation: ``quaternion``
        :param sphere: The target sphere_base the item is on
        :type sphere: :class:`~sphere_iot.uv_sphere.Sphere`
        :param radius: The radius of the target sphere_base
        :type radius: ´´float´´
        :returns: ``Vector4`` position

        Calculate the xyz position of the item based on the angle with the center of the sphere_base it is on.
        The cumulative angle takes into account that the sphere_base can rotate and is not in the default position.

        The calculation starts with a node vector in the center of the default sphere_base at the [0.0, 0.0, 0.0] position,
        with a length 1.0 on the y axis. This node vector is then rotated so it points at the cumulative_orientation.

        It is then moved over the radius distance to take its place on the surface of the default sphere_base.

        Finally it needs to be translated to the sphere_base it is actually on.

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

    def get_pos_orientation_offset(self, pitch_degrees: float, yaw_degrees: float, orientation_offset: 'Quaternion') -> 'Quaternion':
        """
        :param pitch_degrees: Horizontal movement
        :type pitch_degrees: ``float``
        :param yaw_degrees: Vertical movement
        :type yaw_degrees: ``float``
        :param orientation_offset:
        :type orientation_offset: ``Quaternion``
        :returns: ``Quaternion``

        function to get new position orientation offset. It returns the new angle based on the
        old angle adjusted by euler angles.

        .. Warning::

            unfortunately I got quite confused with pitch, roll and yaw and how to apply this to a virtual universe
            where up, down, rotation, x, y, and z are interchangeable and prone to conventions and not absolutes.
            The function works as designed but the naming of the variable may be incorrect.

            This is an area that needs to be looked into, in a later iteration.

        """
        # pitch and yaw in radians
        pitch_rad = (math.pi / 180 * -pitch_degrees)
        yaw_rad = (math.pi / 180 * -yaw_degrees)

        # rotation quaternions
        yaw_q = quaternion.create_from_eulers([yaw_rad, 0.0, 0.0])
        pitch_q = quaternion.create_from_eulers([0.0, pitch_rad, 0.0])

        # first apply the vertical offset to the orientation, to avoid gimbal lock
        orientation_with_yaw = quaternion.cross(yaw_q, orientation_offset)

        # then the pitch movement over the equator
        pos_orientation_offset = quaternion.cross(orientation_with_yaw, pitch_q)

        return pos_orientation_offset

    def get_distance_on_sphere(self, point1: Vector3, point2: Vector3, radius: float) -> float:
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

    @staticmethod
    def get_position_modifier(ratio: float, mod_x=True) -> int:
        """

        This is a modifier based on the distance between the mouse pointer and the center of the screen.
        ratio is between 0 and 1. There are some differences between horizontal, vertical, positive and negative.

        :param ratio: ratio modifier between -1.0 and 1.0
        :type ratio: ``float``
        :param mod_x: ``True`` if the modifier is meant for the x-axis
        :type mod_x: ``bool``
        :return: position modifier ``int``
        """
        position_modifier_x = {0: 9, 1: 8, 2: 7, 3: 7, 4: 7, 5: 7, 6: 7, 7: 7, 8: 7, 9: 7,
                               -1: 7, -2: 6, -3: 6, -4: 6, -5: 6, -6: 6, -7: 6, -8: 6, -9: 7}
        position_modifier_y = {0: 9, 1: 8, 2: 7, 3: 7, 4: 8, 5: 8, 6: 8, 7: 9, 8: 9, 9: 9,
                               -1: 7, -2: 6, -3: 7, -4: 8, -5: 8, -6: 8, -7: 9, -8: 9, -9: 9}

        position_modifier = position_modifier_x if mod_x else position_modifier_y

        d = int(ratio * 10)
        if d in position_modifier:
            return position_modifier[d]
        elif d > 10:
            return position_modifier[10]
        else:
            return 9

    @staticmethod
    def get_distance_modifier(distance: float) -> int:
        """

        This function returns a modifier based on the distance between the camera and the target sphere_base center.
        It is used while dragging object and creating new objects. The modifier is larger when the distance is larger.

        :param distance: Distance between camera position and the center of the target sphere_base
        :type distance: ``float``
        :return: distance modifier ``int``

        .. note::

           All spheres in the basic implementation use a radius of 1. The minimum workable distance after extensive
           testing is 1.5. Getting closer to the sphere_base causes sometimes the camera to jump inside the sphere_base.
           When keeping a minimum distance of 2 this does not happen.

        """

        distance_modifier = {2: 3, 3: 6, 4: 9, 5: 12, 6: 15, 7: 18, 8: 21, 9: 24, 10: 27}
        d = int(distance)
        if d in distance_modifier:
            return distance_modifier[int(distance)]
        elif d > 10:
            return distance_modifier[10]
        else:
            return pow(distance, 2)

