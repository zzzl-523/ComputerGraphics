import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

k_in = '1'

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # draw cooridnates
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    
    glColor3ub(255, 255, 255)
    
    #k_in.reverse()
    for i in range(len(k_in)-1,0,-1):
        if k_in[i] == 'Q':
            glTranslatef(-.1,0,0)
        elif k_in[i] == 'E':
            glTranslatef(.1,0,0)
        elif k_in[i] == 'A':
            glRotate(10, 0, 0,1)
        elif k_in[i] == 'D':
            glRotate(-10, 0, 0,1)
        elif k_in[i] == '1':
            glLoadIdentity()
            break

    drawTriangle()
                          

def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0.,.5]))
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([.5,0.]))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global k_in
    
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_Q:
            k_in += 'Q'    
            
        elif key==glfw.KEY_E:
            k_in += 'E'

        elif key==glfw.KEY_A:
            k_in += 'A'
            
        elif key==glfw.KEY_D:
            k_in += 'D'
            
        elif key==glfw.KEY_1:
            k_in += '1'
            

            

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, "2019060164", None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        ##
        render()
        
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
    
    
