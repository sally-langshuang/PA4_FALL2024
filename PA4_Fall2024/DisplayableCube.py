"""
Define displayable cube here. Current version only use VBO
First version in 10/20/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
import numpy as np
import ColorType

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


class DisplayableCube(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    vertices = None  # array to store vertices information
    indices = None  # stores triangle indices to vertices

    # stores current cube's information, read-only
    length = None
    width = None
    height = None
    color = None

    def __init__(self, shaderProg, length=1, width=1, height=1, color=ColorType.BLUE, render=False):
        super(DisplayableCube, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(length, width, height, color, render)

    def generate(self, length=1, width=1, height=1, color=None, render=False):
        self.length = length
        self.width = width
        self.height = height
        self.color = color

        self.vertices = np.zeros([36, 11])
        # TODO 1.1 rewrite vertices and self.indices

        vl = np.array([
            # back face
            -length / 2, -width / 2, -height / 2, 0, 0, -1, *color, 0, 0,
            -length / 2, width / 2, -height / 2, 0, 0, -1, *color, 0, 1,
            length / 2, -width / 2, -height / 2, 0, 0, -1, *color, 1, 0,

            -length / 2, width / 2, -height / 2, 0, 0, -1, *color, 0, 1,
            length / 2, -width / 2, -height / 2, 0, 0, -1, *color, 1, 0,
            length / 2, width / 2, -height / 2, 0, 0, -1, *color, 1, 1,

            # front face
            -length / 2, -width / 2, height / 2, 0, 0, 1, *color, 0, 0,
            length / 2, -width / 2, height / 2, 0, 0, 1, *color, 1, 0,
            length / 2, width / 2, height / 2, 0, 0, 1, *color, 1, 1,
            -length / 2, -width / 2, height / 2, 0, 0, 1, *color, 0, 0,
            length / 2, width / 2, height / 2, 0, 0, 1, *color, 1, 1,
            -length / 2, width / 2, height / 2, 0, 0, 1, *color, 0, 1,

            # left face
            -length / 2, -width / 2, -height / 2, -1, 0, 0, *color, 0, 0,
            -length / 2, -width / 2, height / 2, -1, 0, 0, *color, 0, 1,
            -length / 2, width / 2, height / 2, -1, 0, 0, *color, 1, 1,
            -length / 2, -width / 2, -height / 2, -1, 0, 0, *color, 0, 0,
            -length / 2, width / 2, height / 2, -1, 0, 0, *color, 1, 1,
            -length / 2, width / 2, -height / 2, -1, 0, 0, *color, 1, 0,
            # right face
            length / 2, -width / 2, height / 2, 1, 0, 0, *color, 0, 1,
            length / 2, -width / 2, -height / 2, 1, 0, 0, *color, 0, 0,
            length / 2, width / 2, -height / 2, 1, 0, 0, *color, 1, 0,
            length / 2, -width / 2, height / 2, 1, 0, 0, *color, 0, 1,
            length / 2, width / 2, -height / 2, 1, 0, 0, *color, 1, 0,
            length / 2, width / 2, height / 2, 1, 0, 0, *color, 1, 1,
            # top face
            -length / 2, width / 2, height / 2, 0, 1, 0, *color, 0, 1,
            length / 2, width / 2, height / 2, 0, 1, 0, *color, 1, 1,
            length / 2, width / 2, -height / 2, 0, 1, 0, *color, 1, 0,
            -length / 2, width / 2, height / 2, 0, 1, 0, *color, 0, 1,
            length / 2, width / 2, -height / 2, 0, 1, 0, *color, 1, 0,
            -length / 2, width / 2, -height / 2, 0, 1, 0, *color, 0, 0,
            # bot face
            -length / 2, -width / 2, -height / 2, 0, -1, 0, *color, 0, 0,
            length / 2, -width / 2, -height / 2, 0, -1, 0, *color, 1, 0,
            length / 2, -width / 2, height / 2, 0, -1, 0, *color, 1, 1,
            -length / 2, -width / 2, -height / 2, 0, -1, 0, *color, 0, 0,
            length / 2, -width / 2, height / 2, 0, -1, 0, *color, 1, 0,
            -length / 2, -width / 2,height / 2, 0, -1, 0, *color, 0, 0,
        ]).reshape((36, 11))

        self.vertices[0:36, 0:11] = vl
        if render:
            for vertice in self.vertices:
                x, y, z, nx, ny, nz, r, g, b, u, v = vertice
                r, g, b = (nx + 1) / 2 , (ny + 1) / 2 , (nz + 1) / 2
                vertice[6:9] = [r, g, b]

        self.indices = np.array([x for x in range(36)])
        # self.vertices = np.zeros([8, 11])
        # vl = np.array([
        #     # back face
        #     -length / 2, -width / 2, -height / 2, 0, 0, -1, *color,
        #     -length / 2, width / 2, -height / 2, 0, 0, -1, *color,
        #     length / 2, width / 2, -height / 2, 0, 0, -1, *color,
        #     length / 2, -width / 2, -height / 2, 0, 0, -1, *color,
        #     # front face
        #     -length / 2, -width / 2, height / 2, 0, 0, 1, *color,
        #     length / 2, -width / 2, height / 2, 0, 0, 1, *color,
        #     length / 2, width / 2, height / 2, 0, 0, 1, *color,
        #     -length / 2, width / 2, height / 2, 0, 0, 1, *color,
        # ]).reshape((8, 9))
        # self.vertices[0:8, 0:9] = vl
        #
        # self.indices = np.array([
        #     # back face
        #     0, 1, 2,  # 第一个三角形
        #     0, 2, 3,  # 第二个三角形
        #
        #     # front face
        #     4, 5, 6,  # 第一个三角形
        #     4, 7, 6,  # 第二个三角形
        #
        #     # left face
        #     0, 1, 7,  # 第一个三角形
        #     0, 7, 4,  # 第二个三角形
        #
        #     # right face
        #     2, 5, 6,  # 第一个三角形
        #     2, 5, 3,  # 第二个三角形
        #
        #     # top face
        #     1, 6, 2,  # 第一个三角形
        #     1, 6, 7,  # 第二个三角形
        #
        #     # bottom face
        #     0, 5, 4,  # 第一个三角形
        #     0, 5, 3,  # 第二个三角形
        # ], dtype=np.int32)

    def draw(self):
        self.vao.bind()
        # TODO 1.1 is at here, switch from vbo to ebo
        # self.vbo.draw()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems that don't enable a default VAO after GLProgram compilation
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
        # TODO/BONUS 6.1 is at here, you need to set attribPointer for texture coordinates
        # you should check the corresponding variable name in GLProgram and set the pointer
        self.vao.unbind()
