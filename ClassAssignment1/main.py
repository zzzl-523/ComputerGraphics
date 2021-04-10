import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

Azimuth = np.radians(45)
Elevation = np.radians(45)
Distance = 5.

PrevCursor = None
At = np.array([0.,0.,0.])

click_mode = 'N' # N : initial, L : Left click, R : Right click
window_mode = 0 # 0 : perspective, 1 : ortho
zoom = 0
scroll_buffer = 0

def mouse_button_callback(window, button, action, mods):
    global Azimuth, Elevation, click_mode, PrevCursor
    if action==glfw.PRESS:
        if button==glfw.MOUSE_BUTTON_LEFT:
            click_mode = 'L'
            PrevCursor = glfw.get_cursor_pos(window)
        elif button==glfw.MOUSE_BUTTON_RIGHT:
            click_mode = 'R'
            PrevCursor = glfw.get_cursor_pos(window)

    else:
        click_mode = 'N'
            
            
    
def scroll_callback(window, xoffset, yoffset):
    global Distance, zoom, scroll_buffer
    if yoffset<0:
        zoom=-10
    elif yoffset>0:
        zoom=+10
  
    scroll_buffer+=zoom
    Distance *= 0.99**int(scroll_buffer)
    scroll_buffer-=int(scroll_buffer)
    
    
def key_callback(window, key, scancode, action, mods):
    global window_mode
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_V:
            if(window_mode==0):
                window_mode = 1
            elif(window_mode==1):
                window_mode = 0
                
def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([-100.,0.,0.]))
    glVertex3fv(np.array([100.,0.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,-100]))
    glVertex3fv(np.array([0.,0.,100.]))
    glEnd()

def drawGrid():
    varr1 = np.array(list(((-100,0,x), (100,0,x)) for x in range(-100,100)),'float32')
    varr2 = np.array(list(((x,0,-100),(x,0,100)) for x in range(-100,100)),'float32')

    glColor3ub(255,255,255)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 3*varr1.itemsize, varr1)
    glDrawArrays(GL_LINES,0,int(varr2.size/3))
    glVertexPointer(3, GL_FLOAT, 3*varr1.itemsize, varr2)
    glDrawArrays(GL_LINES,0,int(varr2.size/3))

def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f( 0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f( 0.5, 0.5, 0.5) 
                             
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f( 0.5,-0.5,-0.5) 
                             
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
                             
    glVertex3f( 0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5,-0.5)
 
    glVertex3f(-0.5, 0.5, 0.5) 
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5) 
    glVertex3f(-0.5,-0.5, 0.5) 
                             
    glVertex3f( 0.5, 0.5,-0.5) 
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5,-0.5)
    glEnd()
   
def render():
    global Azimuth, Elevation, Distance, At

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glLoadIdentity()

    if(window_mode==0):
        gluPerspective(45, 1, .001, 900)
    elif(window_mode==1):
        glOrtho(-5,5, -5,5, .001,900)

    eyePoint = (Distance*np.sin(Azimuth)*np.cos(Elevation),Distance*np.sin(Elevation),Distance*np.cos(Azimuth)*np.cos(Elevation)) + At
    gluLookAt(*eyePoint, *At, 0,1,0)
    drawFrame()
    drawGrid()

    glColor3ub(150,150,150)
    drawUnitCube()



def main():
    global PrevCursor, Azimuth, Elevation, click_mode, At

    if not glfw.init():
        return
    window = glfw.create_window(700, 700, "Class Assignment1", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()

        CurrCursor = glfw.get_cursor_pos(window)
        if click_mode=='L':
            Azimuth += (PrevCursor[0]-CurrCursor[0])*.01
            Elevation += (CurrCursor[1]-PrevCursor[1])*.01
            

        elif click_mode=='R':
            w = np.array([np.sin(Azimuth)*np.cos(Elevation),np.sin(Elevation),np.cos(Azimuth)*np.cos(Elevation)])
            w = w / np.sqrt(w @ w)
            u = np.cross((0,np.cos(Elevation),0), w)
            u = u / np.sqrt(u @ u)
            v = np.cross(w, u)
            
            num = Distance*.0012
            At += num *(PrevCursor[0]-CurrCursor[0])*u + num*(CurrCursor[1]-PrevCursor[1])*v
            
        PrevCursor = CurrCursor
            
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

    
