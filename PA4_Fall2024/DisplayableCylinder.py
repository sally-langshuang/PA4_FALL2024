"""
Define Cylinder here.
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""
from inspect import stack

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
from Point import Point
import numpy as np
import ColorType
import math
try:
    import OpenGL

    try:
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
    except ImportError:
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res:
                return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
except ImportError:
    raise ImportError("Required dependency PyOpenGL not present")


class DisplayableCylinder(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    stacks = 0
    slices = 0
    radiusX = 0
    radiusY = 0
    radiusZ = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, radiusX=0.5, radiusY = 0.5, Z=0.5, stacks=18, slices=36, color=ColorType.PINK):
        super(DisplayableCylinder, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(radiusX, radiusY, Z, stacks, slices, color)

    def generate(self, radiusX=0.5, radiusY=0.5, radiusZ=0.5, stacks=18, slices=36, color=ColorType.SOFTBLUE):
        self.radiusX = radiusX
        self.radiusY = radiusY
        self.radiusZ = radiusZ
        self.stacks = stacks
        self.slices = slices
        self.color = color

        # we need to pad two more rows for poles and one more column for slice seam, to assign correct texture coord
        # self.vertices = np.zeros([(stacks) * (slices), 11])
        self.vertices = self.generate_cylinder_vertices(radiusX, radiusY, radiusZ, stacks, slices, color)
        self.indices = self.generate_cylinder_indices(stacks, slices)

    def generate_cylinder_vertices(self, radiusX, radiusY, radiusZ, stacks, slices, color):
        vertices = np.zeros((stacks * slices, 11))
        arr_stack = np.linspace(radiusZ, -radiusZ, stacks)
        arr_slice = np.linspace(0, 2 * np.pi, slices, endpoint=False)

        top_center = np.array([[0, 0, radiusZ, 0, 0, 1, *color, 0, 0]])
        bottom_center = np.array([[0, 0, -radiusZ, 0, 0, -1,*color, 0, 0]])

        index_func = lambda i, j: i * slices + j

        for i, z in enumerate(arr_stack):
            for j, theta in enumerate(arr_slice):
                # vertice position
                x = radiusX * np.cos(theta)
                y = radiusY * np.sin(theta)

                # norm（针对侧面）
                nx = np.cos(theta)
                ny = np.sin(theta)
                nz = 0

                # texture pos (u, v)
                u = j / slices
                v = i / stacks

                # idx
                k = index_func(i, j)
                vertices[k] = np.array([x, y, z, nx, ny, nz, *color, u, v])
        # top circle vertices
        top_vertices =  np.zeros((slices, 11))
        for j, theta in enumerate(arr_slice):
            x = radiusX * np.cos(theta)
            y = radiusY * np.sin(theta)
            z = radiusZ
            nx, ny, nz = 0, 0, 1
            top_vertices[j] = np.array([x, y, z, nx, ny, nz, *color, u, v])
        # bottom circle vertices
        bottom_vertices = np.zeros((slices, 11))
        for j, theta in enumerate(arr_slice):
            x = radiusX * np.cos(theta)
            y = radiusY * np.sin(theta)
            z = -radiusZ
            nx, ny, nz = 0, 0, -1
            bottom_vertices[j] = np.array([x, y, z, nx, ny, nz, *color, u, v])

        all_vertices = np.concatenate([top_center, top_vertices,  vertices, bottom_vertices,  bottom_center ], axis=0)
        return all_vertices

    def generate_cylinder_indices(self, stacks, slices):
        indices = []

        # middle index
        for i in range(stacks-1):
            for j in range(slices):
                offset = 1 + slices
                current = i * slices + j + offset
                next_stack = (i + 1) * slices + j + offset
                next_slice = i * slices + (j + 1) % slices + offset  # net slice
                next_next_stack = (i + 1) * slices + (j + 1) % slices + offset  # next stack

                # two triangles
                indices.append([current, next_stack, next_slice])  # first triangle
                indices.append([next_stack, next_next_stack, next_slice])  # second triangle


        top_center = 0
        bottom_center = (stacks + 2) * slices + 2 - 1

        for j in range(slices):
            current = j
            next = (j + 1) % slices
            offset_top = 1
            indices.append([top_center , current + offset_top, next + offset_top])

        for j in range(slices):
            current = j
            next = (j + 1) % slices
            offset_bottom = 1 + slices * (stacks + 1)
            indices.append([bottom_center, current + offset_bottom, next + offset_bottom])

        return np.array(indices)

    def draw(self):
        self.vao.bind()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems which don't enable a default VAO after GLProgram compilation
        """
        self.vao.bind()
        self.vbo.setBuffer(self.vertices, 11)
        self.ebo.setBuffer(self.indices)

        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=11, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=11, offset=3, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=11, offset=6, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexTexture"),
                                  stride=11, offset=9, attribSize=2)
        self.vao.unbind()
