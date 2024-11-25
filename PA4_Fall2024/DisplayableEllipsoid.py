"""
Define ellipsoid here.
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""
from unicodedata import normalize

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


class DisplayableEllipsoid(Displayable):
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

    def __init__(self, shaderProg, radiusX=0.6, radiusY=0.3, radiusZ=0.9, stacks=18, slices=36, color=ColorType.YELLOW):
        super(DisplayableEllipsoid, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(radiusX, radiusY, radiusZ, stacks, slices, color)

    def generate(self, radiusX=0.6, radiusY=0.3, radiusZ=0.9, stacks=18, slices=36, color=ColorType.SOFTBLUE):
        self.radiusX = radiusX
        self.radiusY = radiusY
        self.radiusZ = radiusZ
        self.stacks = stacks
        self.slices = slices
        self.color = color

        # we need to pad two more rows for poles and one more column for slice seam, to assign correct texture coord
        # self.vertices = np.zeros([(stacks) * (slices), 11])
        self.vertices = self.generate_ellipsoid_vertices(radiusX, radiusY, radiusZ, stacks, slices, color)
        self.indices = self.generate_ellipsoid_indices(stacks, slices)


    def generate_ellipsoid_vertices(self, a, b, c, stacks, slices,  color):
        vertices = np.zeros([stacks * slices, 11])
        arr_stack = np.linspace(0, 2 * np.pi, stacks)
        arr_slice = np.linspace(0, 2 * np.pi, slices)
        north = np.array([0, b, 0, 0, 0, 0, *color, 0, 0])
        south = np.array([0, -b, 0, 0, 0, 0, *color, 0, 0])
        index_func = lambda i, j: i * slices + j
        for i in range(stacks):
            phi = arr_stack[i]  # φ方向分层
            for j in range(slices):
                theta = arr_slice[j]  # θ方向分片
                x = a * np.cos(theta) * np.sin(phi)
                y = b * np.cos(phi)
                z = c * np.sin(theta) * np.sin(phi)
                k = index_func(i, j)

                # norm
                nx, ny, nz = 2*x/(a**2), 2*y/(b**2), 2*z/(c**2)
                l = np.linalg.norm(np.array([nx, ny, nz]))
                nx, ny, nz = nx / l, ny / l, nz / l
                # texture (u, v)
                u = theta / (2 * np.pi)  # u ∈ [0, 1]
                v = phi / np.pi  # v ∈ [0, 1]
                vertices[k] = np.array([x, y, z, nx, ny, nz, *color, u, v])
        return vertices

    def generate_ellipsoid_indices(self, stacks, slices):
        indices = np.array([])
        index_func = lambda i, j: i * (slices) + j
        same_pos = lambda a, b: a[0] == b[0] and a[1] == b[1] and a[2] == b[2]
        for i in range(1, stacks):
            for j in range(slices):
                current_index = index_func(i, j)
                current_vertice = self.vertices[current_index]
                up_index = index_func(i - 1, j)
                up_vertice = self.vertices[up_index]
                if j > 0:
                    up_left_index, = index_func(i - 1, j - 1),
                    up_left_vertice = self.vertices[up_left_index]
                    if not same_pos(up_left_vertice, up_vertice):
                        indices = np.append(indices, [up_left_index, up_index, current_index])
                if j < slices - 1:
                    right_index = index_func(i, j + 1)
                    right_vertice = self.vertices[right_index]
                    if not same_pos(right_vertice, current_vertice):
                        indices = np.append(indices, [current_index, right_index, up_index])
        return indices



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
