# -*- coding: utf-8 -*-

"""
camera movement module. Contains the camera movement class. It has the calculations needed to move the camera.

"""

from math import sin, cos, radians
from pyrr import Vector3, Vector4, matrix44
from sphere_base.constants import *


class CameraMovement:
    def __init__(self, camera: 'Camera'):
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
        self._init_variables()

    def _init_variables(self):
        self.yaw = 0
        self.rotation = ROTATION
        self.radius = self.cam.get_distance_to_target()

    def set_minimum_values(self, min_radius=MIN_RADIUS, cam_movement_steps=CAM_MOVEMENT_STEPS):
        # The camera should not get closer to the sphere_base
        self.min_radius = min_radius
        self.cam_movement_steps = cam_movement_steps

    def reset(self):
        """
        Reset to the initial values.

        """
        self._init_variables()

    def orbit_around_target(self, target: 'Sphere', rotation: int = 0, yaw: int = 0, offset: float = 0):
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

        new_xyzw = None
        if self.radius < self.min_radius:
            if offset and offset > 0:
                self.radius += offset
        elif offset:
            self.radius += offset

        if self.radius < target.radius:
            # print("camera is inside sphere_base at: " + str(self.cam.target) + " and is pushed back")
            self.radius = self.min_radius

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

        # get current position
        if not self.cam.movement_stack:
            current_pos = Vector3(self.cam.xyz)
            current_target = self.cam.target
            relative_position = self.cam.xyz - current_target
        else:
            current_pos = Vector3(self.cam.movement_stack[len(self.cam.movement_stack) - 1])
            current_target = self.cam.target
            relative_position = self.cam.xyz - current_target

        # new position
        new_target = Vector3(target_sphere.xyz)
        new_pos = new_target + relative_position

        # divide the "position" length in intermediate positions and store in list
        diff = Vector3(new_pos - current_pos)
        step = Vector3(diff / self.cam_movement_steps)

        pos = current_pos
        for x in range(self.cam_movement_steps):
            pos = Vector3(pos + step)
            self.cam.movement_stack.append(pos)

        # the same for the target
        diff = Vector3(new_target - current_target)
        step = Vector3(diff / self.cam_movement_steps)

        pos = self.cam.target
        for x in range(self.cam_movement_steps):
            pos = Vector3(pos + step)
            self.cam.target_stack.append(pos)
