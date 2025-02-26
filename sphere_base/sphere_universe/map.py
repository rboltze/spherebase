# -*- coding: utf-8 -*-

"""
Module map. The map contains all the spheres.

"""

from collections import OrderedDict
from sphere_base.utils.serializable import Serializable
from sphere_base.sphere.sphere import Sphere
from sphere_base.model.models import Models
from sphere_base.sphere_universe.mouse_ray import MouseRay
from sphere_base.sphere_universe.camera import Camera
from sphere_base.sphere_universe.skybox import Skybox
from sphere_base.sphere_universe.rubber_band_box import RubberBand
from sphere_base.clipboard import Clipboard
from sphere_base.config import UvConfig
from sphere_base.shader.default_shader import DefaultShader
from sphere_base.utils.utils import dump_exception
import os.path

TEST_SPHERE_NUMBER = 1


class Map(Serializable):
    # This class represents the map or map. It contains all the objects in the space

    Camera_class = Camera
    Models_class = Models
    Sphere_class = Sphere
    Shader_class = DefaultShader
    Ray_class = MouseRay
    Skybox_class = Skybox
    RubberBand_class = RubberBand
    Clipboard_class = Clipboard
    Config_class = UvConfig

    def __init__(self, parent, skybox_img_dir=None, sphere_texture_dir=None, sphere_icon_dir=None,
                 pybullet_key=None):

        super().__init__("map")

        self.map_widget = parent

        self._spheres = []
        self._edges = []
        self._lens_index = 1  # variable to decide how to texture a sphere_base

        self.mouse_last_x, self.mouse_last_y = self.map_widget.view_width / 2, self.map_widget.view_height / 2
        self.mouse_x, self.mouse_y = self.mouse_last_x, self.mouse_last_y
        self.mouse_offset = 0
        self.target_sphere = None
        self._has_been_modified = False

        self._init_listeners()

        self.config = self.__class__.Config_class(self, skybox_img_dir=skybox_img_dir,
                                                  sphere_texture_dir=sphere_texture_dir,
                                                  sphere_icon_dir=sphere_icon_dir)
        self.shader = self.__class__.Shader_class(self)
        self.cam = self.__class__.Camera_class(self)
        self.models = self.__class__.Models_class(self)
        self.Sphere = self.__class__.Sphere_class  # not instantiated here!

        self.mouse_ray = self.__class__.Ray_class(self, 1)
        self.skybox = self.__class__.Skybox_class(self)
        self.rubber_band_box = self.__class__.RubberBand_class(self)
        self.clipboard = self.__class__.Clipboard_class(self)

        if not os.path.exists("default.json"):
            self.create_test_spheres(TEST_SPHERE_NUMBER)

    def _init_listeners(self):
        # initialize all listeners
        self._has_been_modified_listeners = []
        self._selection_changed_listeners = []
        self._items_deselected_listeners = []

    @property
    def lens_index(self):
        return self._lens_index

    @lens_index.setter
    def lens_index(self, value):
        pass
        # self._lens_index = value

        # Change the relevance colors of all spheres
        # for sphere in self._spheres:
        #     pass
        # sphere.on_lens_index_changed()

    def clear(self):
        # Removes all spheres. This will then cascade down first removing all sphere_base items on each sphere_base.
        # These items include nodes, sockets and edges.

        for sphere in self._spheres:
            sphere.remove()
        self._spheres = []

        for edge in self._edges:
            edge.remove()
        self._edges = []

    def uv_new(self):
        """
        Re-create the sphere_iot map
        :return:
        """

        self.clear()
        self.create_test_spheres(TEST_SPHERE_NUMBER)
        self.cam.reset_to_default_view(self.target_sphere)
        self.on_selection_changed(None, None)

    def create_test_spheres(self, number: int = 0):
        """
        Create spheres for testing purposes

        :param number: number of spheres to create.
        :type number: ``int``

        """
        if number == 0:
            return

        self.target_sphere = self.Sphere(self, position=[0.0, 0.0, 0.0], texture_id=0)

        for i in range(number - 1):
            sphere = self.Sphere(self)
            sphere.index = i

    def add_sphere(self, sphere):
        """
        Add a new sphere_base to the internal list. Adds listeners.

        :param sphere: The ``sphere_base`` that will be added to the ``Map``
        :type sphere: :class:`~sphere_iot.uv_sphere.Sphere`

        """

        self._spheres.append(sphere)
        sphere.add_selection_changed_listener(self.on_selection_changed)
        sphere.add_has_been_modified_listener(self.on_modified)

    def remove_sphere(self, sphere):
        """
        Removing a sphere_base from the internal list.

        :param sphere: The ``sphere_base`` that will be removed from the internal list``
        :type sphere: :class:`~sphere_iot.uv_sphere.Sphere`

        """

        if sphere in self._spheres:
            self._spheres.remove(sphere)

    def add_edge(self, edge):
        """
        Add a new edge to the internal list.

        :param edge: The ``edge`` that will be added to the ``Map``
        :type edge: :class:`~sphere_iot.uv_sphere_edge.SphereEdge`

        """

        self._edges.append(edge)

    def remove_edge(self, edge):
        """
        Removing a sphere_base from the internal list.

        :param edge: The ``edge`` that will be removed from the internal list``
        :type edge: :class:`~sphere_iot.uv_sphere_edge.SphereEdge`

        """

        if edge in self._edges:
            self._edges.remove(edge)

    def add_selection_changed_listener(self, callback):
        """
        Register callback for 'selection changed' event.

        :param callback: callback function

        """
        self._selection_changed_listeners.append(callback)

    def add_modified_listener(self, callback):
        """
        Register callback for 'modified' event.

        :param callback: callback function

        """
        self._has_been_modified_listeners.append(callback)

    def on_selection_changed(self, sphere, sphere_items: [list, None] = None):
        """
        Handles 'selection changed' and triggers event 'selection changed'.

        :param sphere: The target sphere_base that is _selected
        :type sphere: :class:`~sphere_iot.uv_sphere.Sphere`
        :param sphere_items: ``list`` of items on the sphere_base
        :type sphere_items: list with items of type :class:`~sphere_iot.uv_node.Node` or
        :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`

        """
        for callback in self._selection_changed_listeners:
            callback(sphere, sphere_items)

    def on_modified(self):
        """
        Handles 'modified' event and executes the callback functions

        """
        self._has_been_modified = True
        for callback in self._has_been_modified_listeners:
            callback()

    def is_modified(self) -> bool:
        """
        Returns the status of the modified flag
        :return: ``bool``

        """
        return self._has_been_modified

    def reset_has_been_modified(self):
        """
        Resets the 'has been modified' flag. After saving or loading this flag needs to be set to false.

        """

        for sphere in self._spheres:
            sphere.has_been_modified = False
        self._has_been_modified = False

    def on_sphere_has_been_modified(self):
        """
        Handles 'sphere_base has been modified', calls registered listeners.

        """

        # call all registered listeners
        for callback in self._has_been_modified_listeners:
            callback()

        self._has_been_modified = True

    def set_target_sphere(self, selected_sphere_id) -> bool:
        """
        From the internal list of spheres find the _selected sphere_base by its id.
        Returns ``true`` when a target sphere_base is found.

        :param selected_sphere_id: _selected sphere_base id
        :type selected_sphere_id: ``int``
        :return:

        """
        is_sphere = False
        for sphere in self._spheres:
            if selected_sphere_id == sphere.id:
                self.target_sphere.selected = False
                sphere.selected = True
                self.target_sphere = sphere
                self.cam.move_to_new_target_sphere(sphere)
                is_sphere = True
                self.on_selection_changed(self.target_sphere, None)
        return is_sphere

    def rotate_target_sphere_with_mouse(self, offset: float = 0, collision_point=None):
        """
        Rotating the target sphere_base with the mouse y-axis.
        Set the mouse offset here which will be picked up and used from the main loop and will be translated to rotation

        :param offset: mouse current x-position offset and last stored position.
        :param collision_point: mouse ray collision point with sphere.
        :type offset: ``float``

        .. note::

            This method only sets the mouse offset value which is then picked up from the main loop

        """
        # set the mouse offset here which will be picked up and used from the main loop

        offset *= .05   # * self.cam.distance_to_target
        self.mouse_offset += offset

    def rotate_target_sphere(self):
        """
        Rotating the target sphere_base with the left and right arrows or dragging with the mouse.
        This method is called from the main loop

        """
        offset = 0

        # rotating the target sphere with the left and right arrows
        if self.map_widget.arrow_right:
            offset = 1.0  # degree
        if self.map_widget.arrow_left:
            offset = -1.0  # degree
        if self.mouse_offset != 0:
            offset = self.mouse_offset
            self.mouse_offset = 0

        # only continue if and when there are changes
        if offset != 0:
            self.target_sphere.rotate_sphere(offset)

    def do_camera_movement(self):
        """
        Moving the camera. Setting up the movement values.

        """
        # do the movement, call this function from the main loop
        rotation, angle_up, radius = None, None, None

        if self.map_widget.left:
            rotation = -.5
        if self.map_widget.right:
            rotation = .5
        if self.map_widget.forward:
            radius = -.05
        if self.map_widget.back:
            radius = .05
        if self.map_widget.up:
            angle_up = .5
        if self.map_widget.down:
            angle_up = -.5

        # only process if there is movement
        if rotation or angle_up or radius:
            self.cam.process_movement(self.target_sphere, rotation, angle_up, radius=radius)

    def get_mouse_pos(self):
        # helper function to get the mouse variables
        print("here")
        return self.view.get_mouse_pos()

    def draw(self):
        for sphere in self._spheres:
            sphere.draw()
        for edge in self._edges:
            edge.draw()

    def serialize(self):
        spheres = []
        for sphere in self._spheres:
            spheres.append(sphere.serialize())

        try:
            return OrderedDict([
                ('id', self.id),
                ('type', self.type),
                ('view_width', self.view.view_width),
                ('view_height', self.view.view_height),
                ('skybox_id', self.skybox.skybox_id),
                ('camera', [self.cam.serialize()]),
                ('spheres', spheres),
                ('target_sphere_id', self.target_sphere.id)
            ])
        except Exception as e:
            dump_exception(e)

    def deserialize(self, data: dict, hashmap: dict = None, restore_id: bool = True) -> bool:
        if not data:
            self.target_sphere = self.Sphere(self, [0.0, 0.0, 0.0], 0)
            self.target_sphere.history.store_initial_history_stamp()
            return False

        self.clear()
        hashmap = hashmap if hashmap else {}
        self.id = data['id']
        self.mouse_ray.reset()
        if 'skybox_id' in data:
            if self.skybox.skybox_id != data['skybox_id']:
                self.skybox.skybox_id = data['skybox_id']
                self.skybox.create_skybox_faces()

        # deserialize spheres
        for sphere_data in data['spheres']:
            self.Sphere(self, [0.0, 0.0, 0.0], 0).deserialize(sphere_data, hashmap)

        for sphere in self._spheres:
            if data['target_sphere_id'] == sphere.id:
                self.target_sphere = sphere
                self.target_sphere.history.store_initial_history_stamp()

        # deserialize camera
        for camera in data['camera']:
            self.cam.deserialize(camera, hashmap)

        return True
