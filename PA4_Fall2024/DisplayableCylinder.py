"""
Define Cylinder here.
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

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
        vertices = np.zeros((stacks * slices + 2, 11))
        arr_stack = np.linspace(radiusZ, -radiusZ, stacks)  # 高度分层
        arr_slice = np.linspace(0, 2 * np.pi, slices, endpoint=False)  # 圆周分片

        # 添加顶部和底部中心点的顶点
        top_center = stacks * slices  # 顶部中心点索引
        bottom_center = stacks * slices + 1  # 底部中心点索引
        nx, ny, nz = 0, 0, 1
        r, g, b = nx/2+0.5, ny/2+0.5, nz/2+0.5
        vertices[top_center] = np.array([0, 0, radiusZ, 0, 0, 1, r, g, b, 0, 0])  # 顶部中心点
        nx, ny, nz = 0, 0, -1
        r, g, b = nx / 2 + 0.5, ny / 2 + 0.5, nz / 2 + 0.5
        vertices[bottom_center] = np.array([0, 0, -radiusZ, 0, 0, -1, r, g, b, 0, 0])  # 底部中心点

        index_func = lambda i, j: i * slices + j  # 顶点索引

        for i, z in enumerate(arr_stack):  # 沿着高度方向
            for j, theta in enumerate(arr_slice):  # 沿着圆周方向
                # 计算顶点位置
                x = radiusX * np.cos(theta)
                y = radiusY * np.sin(theta)

                # 计算法向量（针对侧面）
                nx = np.cos(theta)
                ny = np.sin(theta)
                nz = 0

                # 纹理坐标 (u, v)
                u = j / slices
                v = i / stacks

                # 填充顶点
                k = index_func(i, j)
                r, g, b = nx / 2 + 0.5, ny / 2 + 0.5, nz / 2 + 0.5
                vertices[k] = np.array([x, y, z, nx, ny, nz, r, g, b, u, v])

        return vertices

    def generate_cylinder_indices(self, stacks, slices):
        indices = []

        # 生成侧面的索引
        for i in range(stacks - 1):  # 每一层
            for j in range(slices):  # 每个分片
                current = i * slices + j
                next_stack = (i + 1) * slices + j
                next_slice = i * slices + (j + 1) % slices  # 下一个slice，循环回到0
                next_next_stack = (i + 1) * slices + (j + 1) % slices  # 下一个分片

                # 侧面，两个三角形
                indices.append([current, next_stack, next_slice])  # 第一个三角形
                indices.append([next_stack, next_next_stack, next_slice])  # 第二个三角形

        # 生成顶部和底部的索引
        # 顶部，中心顶点是第0层，每个顶点都与中心顶点组成三角形
        top_center = stacks * slices  # 顶部中心点的索引
        bottom_center = stacks * slices + 1  # 底部中心点的索引

        for j in range(slices):
            current = j
            next = (j + 1) % slices
            # 顶部索引
            indices.append([top_center, current, next])
            # 底部索引
            indices.append([bottom_center, current + (stacks - 1) * slices, next + (stacks - 1) * slices])

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
