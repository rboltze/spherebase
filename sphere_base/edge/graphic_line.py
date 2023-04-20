# -*- coding: utf-8 -*-

"""

This class takes a sequence of points forming a line and turns them into a pipe.
    - Each vertex in the line is expanded into a circle around the vertex
    - The former point with the next point indicates the normal for the circle.
    - the plain is perpendicular to the normal
    - The circle consists of a number of points on the plain with the same radius
    - for each point we need to find the corresponding points on its circle



"""
class GraphicLine:

    def __init__(self, parent, line_points):

        self.parent = parent
        self.line_ponts = line_points  # a list with vector3 vertices
        
        self.vertices = []
        self.indices = []
        self.plane_normal = None
        self.circle_radius = 0.1







