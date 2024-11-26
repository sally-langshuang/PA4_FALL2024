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

class SceneTwo(Component, Animation):
    lights = None
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

        self.lTransformations = [self.glutility.translate(0, 2, 0, False),
                                 self.glutility.rotate(60, [0, 0, 1], False),
                                 self.glutility.rotate(120, [0, 0, 1], False)]
        self.lRadius = 3
        self.lAngles = [0, 0, 0]
        cube = Component(Point((-1, 1, 0)), DisplayableCube(shaderProg, 1.0))
        m1 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.4, 0.8, 0.6, 0.1)), 64)
        cube.setMaterial(m1)
        cube.renderingRouting = "normal"
        self.addChild(cube)

        torus = Component(Point((1, 1, 0)), DisplayableTorus(shaderProg, 0.15, 0.3, 36, 36))
        m2 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.8, 0.6, 0.4, 1.0)), 64)
        torus.setMaterial(m2)
        torus.renderingRouting = "normal"
        torus.rotate(90, torus.uAxis)
        self.addChild(torus)

        sphere = Component(Point((0, 0, 0)), DisplayableEllipsoid(shaderProg, 0.4, 0.4, 0.4, 36, 36))
        m3 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.6, 0.4, 0.8, 1.0)), 64)
        sphere.setMaterial(m3)
        sphere.renderingRouting = "normal"
        self.addChild(sphere)


        cylinder = Component(Point((-1, -1, 0)), DisplayableCylinder(shaderProg, 0.3, 0.3, 0.4, 36, 36))
        m3 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.6, 0.4, 0.8, 1.0)), 64)
        cylinder.setMaterial(m3)
        cylinder.renderingRouting = "normal"
        self.addChild(cylinder)

        ellipsoid = Component(Point((1, -1, 0)), DisplayableEllipsoid(shaderProg, 0.4, 0.4, 0.6, 36, 36))
        m3 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.8, 0.4, 0.8, 1.0)), 64)
        ellipsoid.setMaterial(m3)
        ellipsoid.renderingRouting = "normal"
        self.addChild(ellipsoid)

        self.lights = []
        self.lightCubes = []

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
            self.shaderProg.setLight(i, v)

        for c in self.children:
            if isinstance(c, Animation):
                c.animationUpdate()

    def initialize(self):
        self.shaderProg.clearAllLights()
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)
        super().initialize()
