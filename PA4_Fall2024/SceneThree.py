"""
Define a fixed scene with rotating lights
First version in 11/08/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""
import math

import numpy as np

import ColorType
from Animation import Animation
from Component import Component
from Light import Light
from Material import Material
from Point import Point
import GLUtility

from DisplayableCube import DisplayableCube
from DisplayableEllipsoid import DisplayableEllipsoid
from DisplayableTorus import DisplayableTorus
from DisplayableCylinder import DisplayableCylinder

class SceneThree(Component, Animation):
    lights = []
    lightCubes = None
    shaderProg = None
    glutility = None

    lRadius = None
    lAngles = None
    lTransformations = None

    def __init__(self, shaderProg):
        super().__init__(Point((0, 0, 0)))
        self.shaderProg = shaderProg
        self.glutility = GLUtility.GLUtility()

        self.lRadius = 3
        self.lAngles = [0, 0, 0]
        self.cubes = []
        self.cube_radius = 0.8
        cube_num = 8
        ## TODO 6.2
        for i in range(cube_num):
            theta = i * (360 / cube_num)
            x = self.cube_radius * np.cos(theta/360*(2*np.pi))
            z = -self.cube_radius * np.sin(theta/360*(2*np.pi))
            cube = Component(Point((x, 0, z)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1))
            m0 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.7, 0.2, 0.2, 1)),
                          np.array((0.7, 0.4, 0.8, 1.0)), 64)
            cube.rotate(theta, cube.vAxis)
            cube.setMaterial(m0)
            cube.setTexture(shaderProg, "./assets/stoneWall.jpg")
            cube.renderingRouting = "lighttexture"
            self.addChild(cube)
            self.cubes.append(cube)

        torus = Component(Point((0, 0, 0)), DisplayableTorus(shaderProg, 0.05, 1.0, 36, 36))
        m2 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.9, 0.2, 0.2, 1)),
                      np.array((0.8, 0.6, 0.4, 1.0)), 64)
        torus.setMaterial(m2)
        torus.setTexture(shaderProg, "./assets/marble.jpg")
        torus.renderingRouting = "lighttexture"
        torus.rotate(60, torus.uAxis)
        self.torus = torus
        self.addChild(torus)

        torus2 = Component(Point((0, 0, 0)), DisplayableTorus(shaderProg, 0.05, 1.2, 36, 36))
        m2 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.8, 0.2, 0.2, 1)),
                      np.array((0.8, 0.4, 0.4, 1.0)), 64)
        torus2.setMaterial(m2)
        torus2.setTexture(shaderProg, "./assets/marble.jpg")
        torus2.renderingRouting = "lighttexture"
        torus2.rotate(90, torus.uAxis)
        torus2.rotate(30, torus.vAxis)
        self.torus2 = torus2
        self.addChild(torus2)

        sphere = Component(Point((0, 0, 0)), DisplayableEllipsoid(shaderProg, 0.5, 0.5, 0.5, 36, 36))
        m3 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.7, 0.2, 0.5, 1)),
                      np.array((0.6, 0.4, 0.4, 1.0)), 64)
        sphere.setMaterial(m3)
        sphere.setTexture(shaderProg, "./assets/earth.jpg")
        sphere.renderingRouting = "lighttexture"
        self.sphere = sphere
        self.addChild(sphere)

        self.lTransformations = [self.glutility.translate(0, 2, 0, False),
                                 self.glutility.rotate(60, [0, 0, 1], False),
                                 self.glutility.rotate(120, [0, 0, 1], False)]
        l0 = Light(self.lightPos(self.lRadius, self.lAngles[0], self.lTransformations[0]),
                   np.array((*ColorType.SOFTRED, 1.0)), infiniteDirection=self.lightPos(self.lRadius, self.lAngles[0], self.lTransformations[0]))
        lightCube0 = Component(Point((0, 0, 0)), DisplayableEllipsoid(shaderProg, 0.1, 0.1, 0.1, color=ColorType.SOFTRED))
        lightCube0.renderingRouting = "vertex"
        l1 = Light(self.lightPos(self.lRadius, self.lAngles[1], self.lTransformations[1]),
                   np.array((*ColorType.SOFTBLUE, 1.0)))
        lightCube1 = Component(Point((0, 0, 0)), DisplayableEllipsoid(shaderProg, 0.1, 0.1, 0.1, color=ColorType.SOFTBLUE))
        lightCube1.renderingRouting = "vertex"
        l2 = Light(self.lightPos(self.lRadius, self.lAngles[2], self.lTransformations[2]),
                   np.array((*ColorType.SOFTGREEN, 1.0)), spotDirection=np.array([0.0, -1.0, 0.0]), spotRadialFactor=np.array([1.0, 0.1, 0.01]), spotAngleLimit=30)
        lightCube2 = Component(Point((0, 0, 0)), DisplayableEllipsoid(shaderProg, 0.1, 0.1, 0.1, color=ColorType.SOFTGREEN))
        lightCube2.renderingRouting = "vertex"

        self.addChild(lightCube0)
        self.addChild(lightCube1)
        self.addChild(lightCube2)
        self.lights = [l0, l1, l2]
        self.lightCubes = [lightCube0, lightCube1, lightCube2]


    def lightPos(self, radius, thetaAng, transformationMatrix):
        r = np.zeros(4)
        r[0] = radius * math.cos(thetaAng / 180 * math.pi)
        r[2] = radius * math.sin(thetaAng / 180 * math.pi)
        r[3] = 1
        r = transformationMatrix @ r
        return r[0:3]

    def animationUpdate(self):
        self.lAngles[0] = (self.lAngles[0] + 0.5) % 360
        self.lAngles[1] = (self.lAngles[1] + 0.7) % 360
        self.lAngles[2] = (self.lAngles[2] + 1.0) % 360
        for i, v in enumerate(self.lights):
            lPos = self.lightPos(self.lRadius, self.lAngles[i], self.lTransformations[i])
            self.lightCubes[i].setCurrentPosition(Point(lPos))
            self.lights[i].setPosition(lPos)
            if self.lights[i].infiniteOn:
                self.lights[i].setInfiniteDirection(lPos)
            self.shaderProg.setLight(i, v)

        for c in self.children:
            if isinstance(c, Animation):
                c.animationUpdate()


        self.sphere.vAngle =  (self.sphere.vAngle + 1) %360

        rotation_speed = [0.3, 0.4, 0.5]
        comp = self.torus
        comp.uAngle = (comp.uAngle + rotation_speed[0]) % 360
        comp.vAngle = (comp.vAngle + rotation_speed[1]) % 360
        comp.wAngle = (comp.wAngle + rotation_speed[2]) % 360

        rotation_speed = [-0.6, -0.4, 0.2]
        comp = self.torus2
        comp.uAngle = (comp.uAngle + rotation_speed[0]) % 360
        comp.vAngle = (comp.vAngle + rotation_speed[1]) % 360
        comp.wAngle = (comp.wAngle + rotation_speed[2]) % 360

        for cube in self.cubes:
            rotation_speed = [0, 0.4, 0]
            theta = (cube.vAngle + rotation_speed[1]) % 360
            x = self.cube_radius * np.cos(theta /360 * (2 * np.pi))
            z = -self.cube_radius * np.sin(theta /360 * (2 * np.pi))
            cube.setCurrentPosition(Point((x, 0, z)))
            cube.vAngle = theta


    def initialize(self):
        self.shaderProg.clearAllLights()
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)
        super().initialize()
