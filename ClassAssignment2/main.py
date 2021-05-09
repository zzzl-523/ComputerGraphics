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
    global window_mode, poly_mode, shade_mode, hierarchy_mode
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_V:
            if(window_mode==0):
                window_mode = 1
            elif(window_mode==1):
                window_mode = 0
                
        elif key==glfw.KEY_Z:   #wireframe/solid mode
            poly_mode *= -1
        elif key==glfw.KEY_S:   #shading using normal data in obj file / forced smooth shading
            shade_mode *= -1
        elif key==glfw.KEY_H:
            hierarchy_mode *= -1
                
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

    glColor3ub(175,175,175)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 3*varr1.itemsize, varr1)
    glDrawArrays(GL_LINES,0,int(varr2.size/3))
    glVertexPointer(3, GL_FLOAT, 3*varr1.itemsize, varr2)
    glDrawArrays(GL_LINES,0,int(varr2.size/3))


#Class Assignment 2
Path = ''
varr = None
iarr = None
narr = None
narr_s = None

drag_check = 0
shade_mode = 1 #1:normal data in obj / -1:forced smooth
poly_mode = 1  #1:wireframe / -1:solid
hierarchy_mode = -1 #1: hierarchy / -1:ordinary

drag_check2 = 0
cart_varr = None
cart_iarr = None
cart_narr = None
cart_narr_s = None

bear_varr = None
bear_iarr = None
bear_narr = None
bear_narr_s = None

ball_varr = None
ball_iarr = None
ball_narr = None
ball_narr_s = None

count = [0,0,0]

def drop_callback(window, paths):
    global Path, Face, iarr, varr, narr, narr_s, drag_check, drag_check2
    Path = ''.join(paths)

    v_xyz = []
    vn_xyz = []

    v_index = []
    n_index = []

    Face = [0, 0, 0]
    
    for F_line in open(Path, 'r'): #read from file

        #print(F_line.strip()+"\n")
        if F_line=='\n':
            continue
        
        F_line_content = F_line.split()
        
        command = F_line_content[0]
        value = F_line_content[1:]

                 
        if command == 'v':
            v_xyz.append([float(value[0]), float(value[1]), float(value[2])])                     
        elif command == 'vn':
            vn_xyz.append([float(value[0]), float(value[1]), float(value[2])])                   
        elif command == 'f':
            if len(value) == 3:
                Face[0]+=1
            elif len(value) == 4:
                Face[1]+=1
            else:
                Face[2]+=1
                
                
            for i in range(0, len(value)-2):
                f_v = []
                f_n = []

                #more than 3 -> triangle
                for j in range(i, i+2):      
                    f_value = value[j].split('/')
                    f_v.append(int(f_value[0])-1)
                    f_n.append(int(f_value[2])-1)                   
                f_value = value[len(value)-1].split('/')
                f_v.append(int(f_value[0])-1)
                f_n.append(int(f_value[2])-1)
               
                v_index.append(f_v)
                n_index.append(f_n)

        else:
            continue
         

    narr = [[0]]*len(v_xyz)
    narr_s = [[0]]*len(v_xyz) 

    for i in range(len(v_index)):   #narr
        #normal from obj file
        narr[v_index[i][0]] = vn_xyz[n_index[i][0]]
        narr[v_index[i][1]] = vn_xyz[n_index[i][1]]
        narr[v_index[i][2]] = vn_xyz[n_index[i][2]]
            
    for i in range(len(v_index)):   #narr_s (smooth)
        #normal vector (triangle face)
        vec1 = np.subtract(v_xyz[v_index[i][1]], v_xyz[v_index[i][0]])
        vec2 = np.subtract(v_xyz[v_index[i][2]], v_xyz[v_index[i][0]])      
        normal_vec = np.cross(vec1, vec2)
        normal_vec /= np.linalg.norm(normal_vec)
        
        narr_s[v_index[i][0]] += normal_vec
        narr_s[v_index[i][1]] += normal_vec
        narr_s[v_index[i][2]] += normal_vec

    for i in range(len(v_xyz)): #narr_s 
        narr_s[i] /= np.linalg.norm(narr_s[i])
    
    varr = np.array(v_xyz, 'float32')
    iarr = np.array(v_index)
    narr = np.array(narr)
    narr_s = np.array(narr_s)

    if hierarchy_mode == -1:
        drag_check = 1
    elif hierarchy_mode == 1:
        drag_check2 += 1

    print("File name : " + Path)
    print("Total number of faces : " + str(Face[0] + Face[1] + Face[2]))
    print("Number of faces with 3 vertices : " + str(Face[0]))
    print("Number of faces with 4 vertices : " + str(Face[1]))
    print("Number of faces with more than 4 vertices : " + str(Face[2]))
   

    

def drawObject_glDrawElements():
    global varr, iarr, narr, narr_s, shade_mode

    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)
    
    if shade_mode == 1: 
        glNormalPointer(GL_FLOAT, 3*varr.itemsize, narr)
    elif shade_mode == -1: # smooth shading
        glNormalPointer(GL_FLOAT, 3*varr.itemsize, narr_s)

    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, varr)
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)

def drawCart():
    global varr, iarr, narr, narr_s, shade_mode, count
    global cart_varr, cart_iarr, cart_narr, cart_narr_s

    if count[0] == 0:
        cart_varr = varr
        cart_iarr = iarr
        cart_narr = narr
        cart_narr_s = narr_s
        
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)
    
    if shade_mode == 1: 
        glNormalPointer(GL_FLOAT, 3*cart_varr.itemsize, cart_narr)
    elif shade_mode == -1: # smooth shading
        glNormalPointer(GL_FLOAT, 3*cart_varr.itemsize, cart_narr_s)

    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, cart_varr)
    glDrawElements(GL_TRIANGLES, cart_iarr.size, GL_UNSIGNED_INT, cart_iarr)

    count[0] = 1

def drawBear():
    global varr, iarr, narr, narr_s, shade_mode, count
    global bear_varr, bear_iarr, bear_narr, bear_narr_s

    if count[1] == 0:
        bear_varr = varr
        bear_iarr = iarr
        bear_narr = narr
        bear_narr_s = narr_s
        
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)
    
    if shade_mode == 1: 
        glNormalPointer(GL_FLOAT, 3*bear_varr.itemsize, bear_narr)
    elif shade_mode == -1: # smooth shading
        glNormalPointer(GL_FLOAT, 3*bear_varr.itemsize, bear_narr_s)

    glVertexPointer(3, GL_FLOAT, 3*bear_varr.itemsize, bear_varr)
    glDrawElements(GL_TRIANGLES, bear_iarr.size, GL_UNSIGNED_INT, bear_iarr)

    count[1] = 1
    
def drawBalloons():
    global varr, iarr, narr, narr_s, shade_mode
    global ball_varr, ball_iarr, ball_narr, ball_narr_s

    if count[2] == 0:
        ball_varr = varr
        ball_iarr = iarr
        ball_narr = narr
        ball_narr_s = narr_s
        
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)
    
    if shade_mode == 1: 
        glNormalPointer(GL_FLOAT, 3*ball_varr.itemsize, ball_narr)
    elif shade_mode == -1: # smooth shading
        glNormalPointer(GL_FLOAT, 3*ball_varr.itemsize, ball_narr_s)

    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, varr)
    glDrawElements(GL_TRIANGLES, ball_iarr.size, GL_UNSIGNED_INT, ball_iarr)
    
    count[2] = 1

#frame & draw
def Cart():
    glPushMatrix()
    objectColor = (1.,0.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    
    glScalef(.05,.05,.05)
    glRotatef(-90,1,0,0)
    drawCart()
    glPopMatrix()
def Bear():
    glPushMatrix()
    objectColor = (3,2,.12,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    
    glRotatef(-90,1,0,0)
    glTranslate(0,0,1.5)
    drawBear()
    glPopMatrix()
def Balloons():
    glPushMatrix()
    objectColor = (6,2,4.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    
    glScalef(.2,.2,.2)
    glRotatef(-90,1,0,0)
    glTranslate(10,0,23)
    glColor3ub(255,0,0)
    drawBalloons()
    glPopMatrix()
    
def render():
    global Azimuth, Elevation, Distance, At, poly_mode

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if poly_mode == 1:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    elif poly_mode == -1:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if window_mode==0:
        gluPerspective(45, 1, .001, 900)
    elif window_mode==1:
        glOrtho(-5,5, -5,5, -10,900)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    eyePoint = (Distance*np.sin(Azimuth)*np.cos(Elevation),Distance*np.sin(Elevation),Distance*np.cos(Azimuth)*np.cos(Elevation)) + At
    gluLookAt(*eyePoint, *At, 0,1,0)
    drawFrame()
    drawGrid()

    time = glfw.get_time()
    # light
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
        

    # light 0
    glPushMatrix()
    lightPos = (3.,4.,5.,1.)   
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    glPopMatrix()
    # light 1
    glPushMatrix()
    glRotatef(120,0,1,0)
    lightPos = (-3.,-4.,5.,1.)   
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos)
    glPopMatrix()
    # light 2
    glPushMatrix()
    glRotatef(240,0,1,0)
    lightPos = (3.,-4.,-5.,1.)   
    glLightfv(GL_LIGHT2, GL_POSITION, lightPos)
    glPopMatrix()
  
    
    ambientLightColor = (.1, .0,.0,1)
    LightColor = (1,0. ,0.,1.)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, LightColor)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, LightColor)

    ambientLightColor = (0.0,0.0,.1,1.)
    LightColor = (0.,.0,1,1.)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor)
    glLightfv(GL_LIGHT1, GL_SPECULAR, LightColor)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, LightColor)
     
    ambientLightColor = (0.0,.1,0.0,1.)
    LightColor = (.0,1,.0,1.)
    glLightfv(GL_LIGHT2, GL_AMBIENT, ambientLightColor)
    glLightfv(GL_LIGHT2, GL_SPECULAR, LightColor)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, LightColor)

       
    specularObjectColor = (1.,1.,1.,1.) 
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    

    if hierarchy_mode == -1:
        glPushMatrix()
        if drag_check==1:
            #glColor3ub(175,175,175)
            drawObject_glDrawElements()
        glPopMatrix()

    elif hierarchy_mode == 1:
        
              
        if drag_check2==1:          
            Cart()       
        elif drag_check2==2:
            Cart()
            Bear()
        elif drag_check2==3:
            
            
            glPushMatrix()
            t = glfw.get_time()
            glTranslatef(np.sin(t)*4, 0, 0)
            Cart()

            glPushMatrix()
            #glTranslatef(np.sin(t*1.3)*0.5, 0, 0)
            glRotatef(t*(180/np.pi), 0, 1, 0)
            Bear()

            glPushMatrix()
            glTranslatef(0, np.sin(t*1.3)*.5, 0)
            Balloons()

            glPopMatrix()
            glPopMatrix()
            glPopMatrix()
        
        
    glDisable(GL_LIGHTING)

def main():
    global PrevCursor, Azimuth, Elevation, click_mode, At

    if not glfw.init():
        return
    window = glfw.create_window(700, 700, "Class Assignment2", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_drop_callback(window, drop_callback)

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
            u = np.cross((0,1,0), w)
            u = u / np.sqrt(u @ u)
            v = np.cross(w, u)
            
            num = Distance*.0012
            At += num *(PrevCursor[0]-CurrCursor[0])*u + num*(CurrCursor[1]-PrevCursor[1])*v
            
        PrevCursor = CurrCursor
            
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

    
