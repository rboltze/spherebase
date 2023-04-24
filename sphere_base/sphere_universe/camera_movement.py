# -*- coding: utf-8 -*-

"""
camera movement module. Contains the camera movement class. It has the calculations needed to move the camera.

"""

from math import sin, cos, radians
from pyrr import Vector3, Vector4, matrix44
from sphere_base.constants import *
DEFAULT_TARGET = Vector3([0.0, 0.0, 0.0])


class CameraMovement:
    def __init__(self, camera):
        """
        Constructor of the camera movement class. This class is instantiated from within the 'Camera class'.
        It contains the calculations for orbiting the camera around the current target Sphere and also the calculations
        for moving the camera to another target Sphere.

        :param camera:  :class:`~sphere_iot.uv_cam.Camera`
        :type camera: :class:`~sphere_iot.uv_cam.Camera`

        :Instance Variables:

        - **yaw** - Euler angle in degrees
        - **rotation** - Euler angle in degrees
        - **radius** - Distance from the camera to the center of the target sphere_base.

        """
        self.cam = camera
        self.yaw = 0
        self.rotation = ROTATION
        self.radius = self.cam.get_distance_to_target()
        self.min_radius = 0
        self.cam_movement_steps = CAM_MOVEMENT_STEPS

    def reset(self):
        """
        Reset to the initial values.

        """
        self.yaw = 0
        self.rotation = ROTATION
        self.radius = self.cam.get_distance_to_target()

    def orbit_around_target(self, target, rotation: float = 0, yaw: float = 0, offset: float = 0):
        """
        Camera orbits around a ``Target Sphere``

        :param target: reference to :class:`~sphere_iot.uv_sphere.Sphere`
        :type target: :class:`~sphere_iot.uv_sphere.Sphere`
        :param rotation: rotation angle
        :type rotation: ``int``
        :param yaw: yaw angle
        :type yaw: ``int``
        :param offset: distance from center of ``Target Sphere``
        :type offset: ``float``

        """
        if self.cam.uv.target_sphere:
            self.min_radius = self.cam.uv.target_sphere.radius + 0.1

        new_xyzw = None
        if self.radius < self.min_radius:
            if offset and offset > 0:
                self.radius += offset
        elif offset:
            self.radius += offset

        if self.radius < self.min_radius:
            self.radius = self.min_radius

        if rotation:
            self.rotation += rotation

        if yaw and yaw > 0:
            if self.yaw < MAX_YAW_UP:
                self.yaw += yaw
        elif yaw and yaw < 0:
            if MIN_YAW_DOWN < self.yaw:
                self.yaw += yaw

        # update the camera position
        x = cos(radians(self.rotation)) * cos(radians(self.yaw)) * self.radius
        y = sin(radians(self.yaw)) * self.radius
        z = sin(radians(self.rotation)) * cos(radians(self.yaw)) * self.radius

        if target:
            m = matrix44.create_from_translation(target.xyz)

            pos = Vector4([x, y, z, 1])
            new_xyzw = matrix44.apply_to_vector(m, pos)

        return new_xyzw

    def move_to_new_target(self, target_sphere):
        """
        Moves the camera to a new ``Target Sphere``

        :param target_sphere: The current ``Target Sphere``
        :type target_sphere: :class:`~sphere_iot.uv_sphere.Sphere`

        """
        return NotImplemented
