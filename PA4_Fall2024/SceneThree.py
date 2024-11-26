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

        self.lTransformations = [self.glutility.translate(0, 2, 0, False),
                                 self.glutility.rotate(60, [0, 0, 1], False),
                                 self.glutility.rotate(120, [0, 0, 1], False)]
        self.lRadius = 3
        self.lAngles = [0, 0, 0]
        cube = Component(Point((-1, -1, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1))
        m0 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.6, 0.4, 0.8, 1.0)), 64)
        cube.setMaterial(m0)
        cube.setTexture(shaderProg, "./assets/stoneWall.jpg")
        cube.renderingRouting = "texture"
        self.addChild(cube)

        torus = Component(Point((0, 0, 0)), DisplayableTorus(shaderProg, 0.1, 1.0, 36, 36))
        m2 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.8, 0.6, 0.4, 1.0)), 64)
        torus.setMaterial(m2)
        torus.setTexture(shaderProg, "./assets/marble.jpg")
        torus.renderingRouting = "texture"
        torus.rotate(60, torus.uAxis)
        self.torus = torus
        self.addChild(torus)

        torus2 = Component(Point((0, 0, 0)), DisplayableTorus(shaderProg, 0.1, 1.4, 36, 36))
        m2 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.8, 0.6, 0.4, 1.0)), 64)
        torus2.setMaterial(m2)
        torus2.setTexture(shaderProg, "./assets/marble.jpg")
        torus2.renderingRouting = "texture"
        torus2.rotate(90, torus.uAxis)
        torus2.rotate(30, torus.vAxis)
        self.torus2 = torus2
        self.addChild(torus2)

        sphere = Component(Point((0, 0, 0)), DisplayableEllipsoid(shaderProg, 0.5, 0.5, 0.5, 36, 36))
        m3 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.6, 0.4, 0.8, 1.0)), 64)
        sphere.setMaterial(m3)
        sphere.setTexture(shaderProg, "./assets/earth.jpg")
        sphere.renderingRouting = "texture"
        self.sphere = sphere
        self.addChild(sphere)



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


        self.sphere.vAngle =  (self.sphere.vAngle + 1) %360
        rotation_speed = [0.3, 0.4, 0.5]
        comp = self.torus
        comp.uAngle = (comp.uAngle + rotation_speed[0]) % 360
        comp.vAngle = (comp.vAngle + rotation_speed[1]) % 360
        comp.wAngle = (comp.wAngle + rotation_speed[2]) % 360
        rotation_speed = [-0.3, -0.4, 0.2]
        comp = self.torus2
        comp.uAngle = (comp.uAngle + rotation_speed[0]) % 360
        comp.vAngle = (comp.vAngle + rotation_speed[1]) % 360
        comp.wAngle = (comp.wAngle + rotation_speed[2]) % 360

    def initialize(self):
        self.shaderProg.clearAllLights()
        # for i, v in enumerate(self.lights):
        #     self.shaderProg.setLight(i, v)
        super().initialize()
