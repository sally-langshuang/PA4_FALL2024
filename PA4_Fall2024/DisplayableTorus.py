"""
Define Torus here.
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

##### TODO 6/BONUS 6: Texture Mapping
# Requirements:
#   1. Set up each object's vertex texture coordinates(2D) to the self.vertices 9:11 columns
#   (i.e. the last two columns). Tell OpenGL how to interpret these two columns:
#   you need to set up attribPointer in the Displayable object's initialize method.
#   2. Generate texture coordinates for the torus and sphere. Use “./assets/marble.jpg” for the torus and
#   “./assets/earth.jpg” for the sphere as the texture image.
#   There should be no seams in the resulting texture-mapped model.

class DisplayableTorus(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    nsides = 0
    rings = 0
    innerRadius = 0
    outerRadius = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=ColorType.CYAN):
        super(DisplayableTorus, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(innerRadius, outerRadius, nsides, rings, color)

    def generate(self, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=ColorType.SOFTBLUE):
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.nsides = nsides
        self.rings = rings
        self.color = color

        # we need to pad one more row for both nsides and rings, to assign correct texture coord to them
        self.vertices = np.zeros([(nsides) * (rings), 11])
        self.vertices = self.generate_torus_vertices(outerRadius, innerRadius, rings, nsides, color)

        self.indices = np.zeros(0)
        self.indices = self.generate_torus_indices(rings, nsides)

    import numpy as np

    def generate_torus_vertices(self, outerRadius, innerRadius, rings, nsides, color):
        # 创建顶点数组，假设属性包括：位置(3) + 法向量(3) + 颜色(3) + 纹理坐标(2)
        vertices = np.zeros((rings * nsides, 11))

        # 角度划分
        arr_theta = np.linspace(0, 2 * np.pi, rings, endpoint=False)  # 主圆分段
        arr_phi = np.linspace(0, 2 * np.pi, nsides, endpoint=False)  # 小圆分段

        for i, theta in enumerate(arr_theta):
            for j, phi in enumerate(arr_phi):
                # 计算顶点位置
                x = (outerRadius + innerRadius * np.cos(phi)) * np.cos(theta)
                y = (outerRadius + innerRadius * np.cos(phi)) * np.sin(theta)
                z = innerRadius * np.sin(phi)

                # 计算法向量
                nx = np.cos(phi) * np.cos(theta)
                ny = np.cos(phi) * np.sin(theta)
                nz = np.sin(phi)

                # 纹理坐标 (u, v)
                u = i / (rings - 1)  # 横向纹理坐标
                v = j / (nsides - 1)  # 纵向纹理坐标

                # 填充顶点数据
                k = i * nsides + j  # 当前顶点索引
                vertices[k] = np.array([x, y, z, nx, ny, nz, *color, u, v])

        return vertices

    def generate_torus_indices(self, rings, nsides):
        # 初始化索引列表
        indices = []

        for i in range(rings):
            for j in range(nsides):
                # 当前顶点索引
                current = i * nsides + j
                # 右侧顶点索引（环绕到起点）
                next_side = current + 1 if (j + 1) < nsides else i * nsides
                # 下一个环上的顶点索引（环绕到起点）
                next_ring = current + nsides if (i + 1) < rings else j
                # 对角顶点索引
                diagonal = next_ring + 1 if (j + 1) < nsides else (i + 1) % rings * nsides

                # 两个三角形
                indices.append([current, next_side, next_ring])  # 三角形 1
                indices.append([next_side, diagonal, next_ring])  # 三角形 2

        # 转换为 numpy 数组并返回
        return np.array(indices, dtype=np.uint32)

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

        self.vao.unbind()
