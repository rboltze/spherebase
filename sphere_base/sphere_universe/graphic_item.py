# -*- coding: utf-8 -*-

class GraphicItem:
    def __init__(self, parent, item_type):
        """
        Default constructor automatically creates common data to any Graphical item.
        In our case we create ``self.id`` and ``self.type`` which we use in every graphic object.

        """

        self.id = id(self)
        self.type = item_type
