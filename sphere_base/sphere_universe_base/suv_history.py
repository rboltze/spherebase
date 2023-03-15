# -*- coding: utf-8 -*-

"""
A module containing all code for working with history on a single sphere_base (Undo/Redo)
"""

from sphere_base.sphere_universe_base.suv_utils import dump_exception

DEBUG = False
DEBUG_SELECTION = False


class History:
    """ Class contains all the code for undo/redo operations on a single sphere_base """

    def __init__(self, sphere: 'Sphere'):
        """
        Constructor of the ``History`` class.

        :param sphere: reference to  :class:`~sphere_iot.uv_sphere.Sphere`.
        :type sphere:  :class:`~sphere_iot.uv_sphere.Sphere`

        :Instance Variables:

            - **sphere_base** - :class:`~sphere_iot.uv_sphere.Sphere`.
            - **current_img_id** - id of the current active image.
            - **last_img_id** - id of the last active image.
            - **default_img_id** - id of the default image
            - **selected_img_id** - id of the image when the item is _selected.
            - **hover_img_id** - id of the image when the item is hovered with the mouse pointer.
            - **default_background_color** - ``list``
            - **selected_background_color** - ``list``
            - **hover_background_color** - ``list``
            - **current_background_color** - ``list``

        """

        self.sphere = sphere

        self.clear()

        # history limit pere Sphere
        self.history_limit = 32

        self.undo_selection_has_changed = False

        # listeners
        self._history_modified_listeners = []
        self._history_stored_listeners = []
        self._history_restored_listeners = []

    def clear(self):
        """
        Reset the history stack

        """
        self.history_stack = []
        self.history_current_step = -1

    def store_initial_history_stamp(self):
        """
        Helper function usually used when new or open file requested

        """
        self.store_history("Initial history stamp")

    def add_history_modified_listener(self, callback: 'function'):
        """
        Register callback for 'history modified' event.

        :param callback: callback function

        """
        self._history_modified_listeners.append(callback)

    def add_history_stored_listener(self, callback):
        """
        Register callback for 'history stored' event.

        :param callback: callback function

        """
        self._history_stored_listeners.append(callback)

    def add_history_restored_listener(self, callback: 'function'):
        """
        Register callback for 'history restored' event.

        :param callback: callback function

        """
        self._history_restored_listeners.append(callback)

    def can_undo(self) -> bool:
        """
        True if possible to un-do history.

        :returns: ``bool``

        """
        return self.history_current_step > 0

    def can_redo(self) -> bool:
        """
        True if possible to un-do history.

        :returns: ``bool``

        """
        return self.history_current_step + 1 < len(self.history_stack)

    def undo(self):
        """
        Undo operation

        """
        if DEBUG:
            print("UNDO")

        if self.can_undo():
            self.history_current_step -= 1
            self.restore_history()
            self.sphere.has_been_modified = True

    def redo(self):
        """
        Redo operation

        """
        if DEBUG:
            print("REDO")
        if self.can_redo():
            self.history_current_step += 1
            self.restore_history()
            self.sphere.has_been_modified = True

    def restore_history(self):
        """
        Restore `History Stamp` from `History stack`

        """
        if DEBUG:
            print("Restoring history",
                  ".... current_step: @%d" % self.history_current_step,
                  "(%d)" % len(self.history_stack))

        self.restore_history_stamp(self.history_stack[self.history_current_step])
        for callback in self._history_modified_listeners: callback()
        for callback in self._history_restored_listeners: callback()

    def store_history(self, description: str, set_modified: bool = False):
        """
        Store History Stamp into History Stack. Set modified flag if set_modified is True

        :param description: description
        :type description: ``str``
        :param set_modified: set modified flag
        :type set_modified: ``bool``

        """

        if set_modified:
            self.sphere.has_been_modified = True

        if DEBUG: print("Storing history", '"%s"' % description,
                        ".... current_step: @%d" % self.history_current_step,
                        "(%d)" % len(self.history_stack))

        # if the pointer (history_current_step) is not at the end of history_stack
        if self.history_current_step + 1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_current_step + 1]

        # history is outside of the limits
        if self.history_current_step + 1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        hs = self.create_history_stamp(description)

        self.history_stack.append(hs)
        self.history_current_step += 1
        if DEBUG: print("  -- setting step to:", self.history_current_step)

        # always trigger history modified (for i.e. update_edit_menu)
        for callback in self._history_modified_listeners: callback()
        for callback in self._history_stored_listeners: callback()

    def capture_current_selection(self) -> dict:
        """
        Create dictionary with list of _selected nodes and list of _selected edges

        """

        sel_obj = {
            'nodes': [],
            'edges': [],
        }
        for item in self.sphere.items_selected:
            if item.type == 'node':
                sel_obj['nodes'].append(item.id)
            elif item.type == 'node':
                sel_obj['edges'].append(item.id)
        return sel_obj

    def create_history_stamp(self, description: str) -> dict:
        """
        Create History Stamp. Internally serialize whole scene and current selection.

        """
        history_stamp = {
            'description': description,
            'snapshot': self.sphere.serialize(),
            'selection': self.capture_current_selection(),
        }

        return history_stamp

    def restore_history_stamp(self, history_stamp: dict):
        """
        Restore History Stamp to current `Scene` with selection of items included

        """
        if DEBUG: print("restore_history_stamp: ", history_stamp['description'])

        try:
            self.undo_selection_has_changed = False
            previous_selection = self.capture_current_selection()
            if DEBUG_SELECTION: print("_selected nodes before restore:", previous_selection['nodes'])

            self.sphere.deserialize(history_stamp['snapshot'])

            # restore selection

            # first clear all selection on all items
            for item in self.sphere.items_selected:
                item.on_selected_event(False)

            # now restore _selected edges from history_stamp
            for edge_id in history_stamp['selection']['edges']:
                for item in self.sphere.items:
                    if item.id == edge_id:
                        self.sphere.select_item(item, True)
                        break

            # now restore _selected nodes from history_stamp
            for node_id in history_stamp['selection']['nodes']:
                for item in self.sphere.items:
                    if item.id == node_id:
                        self.sphere.select_item(item, True)
                        break

            current_selection = self.capture_current_selection()
            if DEBUG_SELECTION: print("_selected nodes after restore:", current_selection['nodes'])

            # reset the last_selected_items - since we're comparing change to the last_selected state
            # self.sphere_base._last_selected_items = self.sphere_base.items_selected

            # if the selection of nodes differ before and after restoration, set flag
            if current_selection['nodes'] != previous_selection['nodes'] or current_selection['edges'] != \
                    previous_selection['edges']:
                if DEBUG_SELECTION: print("\nSCENE: Selection has changed")
                self.undo_selection_has_changed = True

        except Exception as e:
            dump_exception(e)
