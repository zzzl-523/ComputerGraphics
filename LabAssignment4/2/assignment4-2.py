import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def render(th):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
 # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()

    glColor3ub(255, 255, 255)
    
    # calculate matrix M1, M2 using th
    R = np.identity(3)
    R[:2,:2] = [[np.cos(th),-np.sin(th)],
                [np.sin(th), np.cos(th)]]
    
    T = np.identity(3)
    T[:2,2] = [.5,0]
    T2 = np.identity(3)
    T2[:2,2] = [0,.5]

    M1 = R @ T
    M2 = R @ T2
   
    
    # draw point p
    glBegin(GL_POINTS)
    glVertex2fv((M1 @ np.array([.5,0.,1]))[:-1]) #p1
    glVertex2fv((M2 @ np.array([0,.5,1]))[:-1])  #p2
    glEnd()
    
    # draw vector v
    glBegin(GL_LINES)
    glVertex2fv((np.array([0.,0.,0]))[:-1])
    glVertex2fv((M1 @ np.array([.5,0.,0]))[:-1]) #v1
    
    glVertex2fv((np.array([0.,0.,0]))[:-1])
    glVertex2fv((M2 @ np.array([0,.5,0]))[:-1])  #v2
    glEnd()


def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, "2019060164", None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        t = glfw.get_time()
        th = -t
        render(th)
        
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
