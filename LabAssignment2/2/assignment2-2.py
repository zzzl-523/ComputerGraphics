import numpy as np
import glfw
from OpenGL.GL import *

hand_angle = 0
hand_num = 0
graphic_num = 0
lin = np.linspace(30,360,12)
    
def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    glBegin(GL_LINE_LOOP)
    for i in range(0,12):
        angle = (lin[i]-30)*np.pi/180
        glVertex2f(1.0*(np.cos(angle)), 1.0*(np.sin(angle)))
    glEnd()

    glBegin(GL_LINES)
    hand_angle = (lin[graphic_num]+60)*np.pi/180
    glVertex2f(0.0,0.0)
    glVertex2f(1.0*(np.cos(hand_angle)), 1.0*(np.sin(hand_angle)))
    
    glEnd()

    
def key_callback(window, key, scancode, action, mods):
    global hand_num, graphic_num
    
    if key==glfw.KEY_1:
        if action==glfw.PRESS:
            hand_num = 1
            graphic_num = 11
    elif key==glfw.KEY_2:
        if action==glfw.PRESS:
            hand_num = 2
            graphic_num = 10
    elif key==glfw.KEY_3:
        if action==glfw.PRESS:
            hand_num = 3
            graphic_num = 9
    elif key==glfw.KEY_4:
        if action==glfw.PRESS:
            hand_num = 4
            graphic_num = 8
    elif key==glfw.KEY_5:
        if action==glfw.PRESS:
            hand_num = 5
            graphic_num = 7
    elif key==glfw.KEY_6:
        if action==glfw.PRESS:
            hand_num = 6
            graphic_num = 6
    elif key==glfw.KEY_7:
        if action==glfw.PRESS:
            hand_num = 7
            graphic_num = 5
    elif key==glfw.KEY_8:
        if action==glfw.PRESS:
            hand_num = 8
            graphic_num = 4
    elif key==glfw.KEY_9:
        if action==glfw.PRESS:
            hand_num = 9
            graphic_num = 3
    elif key==glfw.KEY_0:
        if action==glfw.PRESS:
            hand_num = 10
            graphic_num = 2
    elif key==glfw.KEY_Q:
        if action==glfw.PRESS:
            hand_num = 11
            graphic_num = 1
    elif key==glfw.KEY_W:
        if action==glfw.PRESS:
            hand_num = 0
            graphic_num = 0      

        
def main():
    if not glfw.init():
        return
    window = glfw.create_window(480,480,"2019060164",None, None)   #create window
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback) #key event

    glfw.make_context_current(window) #context current

    while not glfw.window_should_close(window): #until window closed
        glfw.poll_events() #button
        render()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
        
