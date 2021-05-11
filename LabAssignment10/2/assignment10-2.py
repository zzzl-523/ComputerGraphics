import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo

gCamAng = 0.
gCamHeight = 1.
frameNum = 0

def l2norm(v):
    return np.sqrt(np.dot(v, v))
def normalized(v):
    l = l2norm(v)
    return 1/l * np.array(v)

def lerp(v1, v2, t):
    return (1-t)*v1 + t*v2

def exp(rv):
    th = l2norm(rv)
    rv = normalized(rv)
    exp_matrix = np.array([[np.cos(th)+rv[0]*rv[0]*(1-np.cos(th)), rv[0]*rv[1]*(1-np.cos(th))-rv[2]*np.sin(th), rv[0]*rv[2]*(1-np.cos(th))+rv[1]*np.sin(th),0],
                            [rv[1]*rv[0]*(1-np.cos(th))+rv[2]*np.sin(th), np.cos(th)+rv[1]*rv[1]*(1-np.cos(th)), rv[1]*rv[2]*(1-np.cos(th))-rv[0]*np.sin(th),0],
                           [rv[2]*rv[0]*(1-np.cos(th))-rv[1]*np.sin(th), rv[2]*rv[1]*(1-np.cos(th))+rv[0]*np.sin(th), np.cos(th)+rv[2]*rv[2]*(1-np.cos(th)),0],
                          [0,0,0,1]])
    return exp_matrix
    
def log(R):
    th = np.arccos((R[0][0]+R[1][1]+R[2][2]-1)/2)
    v1 = (R[2][1]-R[1][2])/(2*np.sin(th))
    v2 = (R[0][2]-R[2][0])/(2*np.sin(th))
    v3 = (R[1][0]-R[0][1])/(2*np.sin(th))
    rv = np.array([v1,v2,v3])
    rv = normalized(rv)
     
    return th * rv

def slerp(R1, R2, t):
    R = R1@(exp(t*log(R1.T@R2)))
    return R

def XYZEulerToRotMat(euler):
    zang, yang, xang = euler
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    R = np.identity(4)
    R[:3,:3]= Rx @ Ry @ Rz
    return R


def createVertexAndIndexArrayIndexed():
    varr = np.array([
            ( -0.5773502691896258 , 0.5773502691896258 ,  0.5773502691896258 ),
            ( -1 ,  1 ,  1 ), # v0
            ( 0.8164965809277261 , 0.4082482904638631 ,  0.4082482904638631 ),
            (  1 ,  1 ,  1 ), # v1
            ( 0.4082482904638631 , -0.4082482904638631 ,  0.8164965809277261 ),
            (  1 , -1 ,  1 ), # v2
            ( -0.4082482904638631 , -0.8164965809277261 ,  0.4082482904638631 ),
            ( -1 , -1 ,  1 ), # v3
            ( -0.4082482904638631 , 0.4082482904638631 , -0.8164965809277261 ),
            ( -1 ,  1 , -1 ), # v4
            ( 0.4082482904638631 , 0.8164965809277261 , -0.4082482904638631 ),
            (  1 ,  1 , -1 ), # v5
            ( 0.5773502691896258 , -0.5773502691896258 , -0.5773502691896258 ),
            (  1 , -1 , -1 ), # v6
            ( -0.8164965809277261 , -0.4082482904638631 , -0.4082482904638631 ),
            ( -1 , -1 , -1 ), # v7
            ], 'float32')
    iarr = np.array([
            (0,2,1),
            (0,3,2),
            (4,5,6),
            (4,6,7),
            (0,1,5),
            (0,5,4),
            (3,6,2),
            (3,7,6),
            (1,2,6),
            (1,6,5),
            (0,7,3),
            (0,4,7),
            ])
    return varr, iarr

def drawCube_glDrawElements():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([3.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,3.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,3.]))
    glEnd()

def draw(ex, ey, ez, ex2, ey2, ez2):
    T1 = np.identity(4) 
    T1[0][3] = 1. 
    R1 = np.identity(4) 
    
    R1 = XYZEulerToRotMat(np.array([ex, ey, ez])) 
    J1 = R1
    
    glPushMatrix() 
    glMultMatrixf(J1.T) 
    glPushMatrix() 
    glTranslatef(0.5, 0, 0) 
    glScalef(0.5, 0.05, 0.05) 
    drawCube_glDrawElements()
    glPopMatrix() 
    glPopMatrix() 
        
    R2 = np.identity(4) 
    
    R2 = XYZEulerToRotMat(np.array([ex2, ey2, ez2])) 
    J2 = R1 @ T1 @ R2 
        
    glPushMatrix() 
    glMultMatrixf(J2.T) 
    glPushMatrix() 
    glTranslatef(0.5, 0, 0) 
    glScalef(0.5, 0.05, 0.05) 
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
        
def render(t):
    global gCamAng, gCamHeight, frameNum
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1,10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng),gCamHeight,5*np.cos(gCamAng), 0,0,0, 0,1,0)

    # draw global frame
    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_RESCALE_NORMAL)

    lightPos = (3.,4.,5.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

    lightColor = (1.,1.,1.,1.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    
    
    R1_e = [[0]]*20*8
    
    R1_e[0] = ([np.radians(20), np.radians(30), np.radians(30)])
    R1_e[1] = ([np.radians(45), np.radians(60), np.radians(40)])
    R1_e[2] = ([np.radians(60), np.radians(70), np.radians(50)])
    R1_e[3] = ([np.radians(80), np.radians(85), np.radians(70)])
    Color = np.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]])
    Color[0] = np.array([1,0,0,1])
    Color[1] = np.array([1,1,0,1])
    Color[2] = np.array([0,1,0,1])
    Color[3] = np.array([0,0,1,1])

    R2_e = [[0]]*20*8
    R2_e[0] = ([np.radians(15),np.radians(30),np.radians(25)])
    R2_e[1] = ([np.radians(25),np.radians(40),np.radians(40)])
    R2_e[2] = ([np.radians(40),np.radians(60),np.radians(50)])
    R2_e[3] = ([np.radians(55),np.radians(80),np.radians(65)])

    
    i = 0
    for i in range(4):
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, Color[i])
        glMaterialfv(GL_FRONT, GL_SHININESS, 10)
        glMaterialfv(GL_FRONT, GL_SPECULAR, Color[i]*0.1)
        draw(R1_e[i][0],R1_e[i][1],R1_e[i][2], R2_e[i][0],R2_e[i][1],R2_e[i][2])


    objectColor = (1.,1.,1.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    i = 0
    if(frameNum>=0 and frameNum < 20):
        i = 0
    elif frameNum >= 20 and frameNum < 40:
        i = 1
    elif frameNum >= 40 and frameNum < 60:
        i = 2
    

    
    R1_m = XYZEulerToRotMat(R1_e[i])
    R1_m2 = XYZEulerToRotMat(R1_e[i+1])
    R2_m = XYZEulerToRotMat(R2_e[i])
    R2_m2 = XYZEulerToRotMat(R2_e[i+1])
    
    R1 = slerp(R1_m, R1_m2, (frameNum-20*i)/20)
    R2 = slerp(R2_m, R2_m2, (frameNum-20*i)/20)

    frameNum = (frameNum + 1) % 61


    J1 = R1    
    glPushMatrix()
    glMultMatrixf(J1.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    
    
    T1 = np.identity(4)
    T1[0][3] = 1.

    J2 = R1 @ T1 @ R2

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    

    glDisable(GL_LIGHTING)


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    # rotate the camera when 1 or 3 key is pressed or repeated
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key==glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key==glfw.KEY_2:
            gCamHeight += .1
        elif key==glfw.KEY_W:
            gCamHeight += -.1

gVertexArrayIndexed = None
gIndexArray = None

def main():
    global gVertexArrayIndexed, gIndexArray
    if not glfw.init():
        return
    window = glfw.create_window(640,640,'2019060164', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        t = glfw.get_time()
        render(t)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

