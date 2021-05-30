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
poly_mode=1

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
    global window_mode, poly_mode, shade_mode, hierarchy_mode, space_key, extra
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
        elif key==glfw.KEY_SPACE:
            space_key *= -1
        elif key==glfw.KEY_E:
            extra *= -1
                
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


#Class Assignment 3
Path = ''

drag_check = 0
space_key = -1

Name_list = []   #save joint name
Stack_list = [] #save {,} for matrix stack
Offset_list = [] #save offsets
Motion_list = []    #save motion info / channel 

k=-1
frame=0
joints_cnt=0
joint=0
pl=1##
get_frame_cnt=0##

extra=-1    #extra credits

def drop_callback(window, paths):
    global Path, BVH_name, Stack_list, Offset_list, Channel_list, drag_check, joints_cnt, Motion_list
    global get_line_motion, get_frame_cnt, space_key##
    Path = ''.join(paths)

    joints_cnt = 0
    st = 0##
    motion = []
    Stack_list = []
    Offset_list = []
    space_key = -1
    
    for F_line in open(Path, 'r'): #read from file

        F_contents = F_line.lstrip().split()
        command = F_contents[0]
        
        if command=="HIERARCHY" or command=="End" or command=="MOTION":
            continue
        
        elif command=="ROOT" or command=="JOINT":
            Name_list.append(F_contents[1]) #name
            joints_cnt += 1

        elif command=="{":
            Stack_list.append("{")

        elif command=="}":
            Stack_list.append("}")

        elif command=="OFFSET":
            Offset_list.append([float(F_contents[1]),float(F_contents[2]),float(F_contents[3])])
            
        elif command=="CHANNELS":

            for i in range(int(F_contents[1])): #channel number
                motion.append([])
                if F_contents[i+2].upper()=="XPOSITION":
                    motion[st].append(1)
                elif F_contents[i+2].upper()=="YPOSITION":
                    motion[st].append(2)
                elif F_contents[i+2].upper()=="ZPOSITION":
                    motion[st].append(3)
                    
                elif F_contents[i+2].upper()=="XROTATION":
                    motion[st].append(4)
                elif F_contents[i+2].upper()=="YROTATION":
                    motion[st].append(5)
                elif F_contents[i+2].upper()=="ZROTATION":
                    motion[st].append(6)
                st+=1
                
        elif command=="Frames:":
            frame_cnt = F_contents[1]

        elif command=="Frame":
            frame_time = F_contents[2]

        else:
            for i in range(st):
                motion[i].append(F_contents[i])  #frame_cnt = Motion_list's element number
            
                    
    drag_check = 1
    get_frame_cnt = str(frame_cnt) ##
    Motion_list = motion

    file_name=Path.split('\\')
    print("File name : " + file_name[len(file_name)-1])
    print("Number of frames : " + str(frame_cnt))
    print("FPS (which is 1/FrameTime) : " + str(1.0/float(frame_time)))
    print("Number of joints : " + str(joints_cnt))
    print("List of all joint names : ",end='')
    for i in range(joints_cnt):
        print(Name_list[i]+", ",end='')
    print(Name_list[i])
        

def drawBVH():
    global BVH_name, Stack_list, Offset_list, Channel_list, Motion_list, k, joints_cnt,joint
    global pl, get_frame_cnt, extra##
    to_ = 0
    k=-1
    num=0
    
    for i in range(len(Stack_list)):
        if Stack_list[i]=="{":
            glPushMatrix()
            
            p1 = np.array(Offset_list[0])
            p2 = p1 + np.array(Offset_list[to_])

            if extra==1:
                if num==0:
                    pass
                else:
                    glColor3ub(0,0,255)
                    varr, iarr, narr = createVertexAndIndexArrayIndexed()
                    v = p1-p2
                    nv = v/np.sqrt(np.dot(v, v))
                    n = np.array([0.,1.,0.])

                    c = np.cross(nv, n)
                    cn = np.sqrt(np.dot(c, c))
                    theta = np.rad2deg(np.arcsin(cn))
                    if np.dot(nv, n) < 0:
                        theta = 180 - theta
                    
                    if cn != 0:
                        c /= cn
                        
                    glPushMatrix()
                    objectColor = (2,2,8.,1.)
                    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
                    glRotatef(-theta, c[0], c[1], c[2])
                    glScalef(.05, np.sqrt(np.dot(v, v)), .03)
                    glEnableClientState(GL_VERTEX_ARRAY)
                    glEnableClientState(GL_NORMAL_ARRAY)
                    glNormalPointer(GL_FLOAT, 3*narr.itemsize, narr)
                    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, varr)
                    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)
                    glPopMatrix()
                    
                    arr = np.array(Offset_list[to_])
                    glTranslatef(arr[0],arr[1],arr[2])
    
            else:
                if num==0:
                    pass
                else:
                    glBegin(GL_LINES)
                    #glColor3ub(0,0,255)
                    glColor3ub(255,255,0)
                    glVertex3fv(p1)
                    glVertex3fv(p2)             
                    glEnd()

                    arr = np.array(Offset_list[to_])
                    glTranslatef(arr[0],arr[1],arr[2])
            
            
            to_+=1

            num+=1

            if Stack_list[i+1]=="}":  #End site
                continue

            
            if space_key==1:      
                if i==0: #root
                    tx=0
                    ty=0
                    tz=0
                    for j in range(3):   #6
                        k+=1
                        k%=len(Motion_list)
                        if Motion_list[k][0]==1:    #X_P
                            tx=float(Motion_list[k][pl])
                        elif Motion_list[k][0]==2:
                            ty=float(Motion_list[k][pl])
                        elif Motion_list[k][0]==3:
                            tz=float(Motion_list[k][pl])
                    glTranslatef(tx,ty,tz)
                    
                    for j in range(3,6):
                        k+=1
                        k%=len(Motion_list)
                        if int(Motion_list[k][0])==4:
                            glRotatef(float(Motion_list[k][pl]), 1,0,0)
                        elif int(Motion_list[k][0])==5:
                            glRotatef(float(Motion_list[k][pl]), 0,1,0)
                        elif int(Motion_list[k][0])==6:
                            glRotatef(float(Motion_list[k][pl]), 0,0,1)
                        
                    

                else: #joints
                                            
                    for j in range(3):   #3
                        k+=1
                        k%=len(Motion_list)
                        if int(Motion_list[k][0])==4:
                            glRotatef(float(Motion_list[k][pl]), 1,0,0)
                        elif int(Motion_list[k][0])==5:
                            glRotatef(float(Motion_list[k][pl]), 0,1,0)
                        elif int(Motion_list[k][0])==6:
                            glRotatef(float(Motion_list[k][pl]), 0,0,1)                      

            else:
                pass
           

        elif Stack_list[i]=="}":
            glPopMatrix()

    

def createVertexAndIndexArrayIndexed():
    varr = np.array([
            np.array([-1,0,1]),
            np.array([-1,0,-1]),
            np.array([1,0,-1]),
            np.array([1,0,1]),
            np.array([-1,-1,1]),
            np.array([-1,-1,-1]),
            np.array([1,-1,-1]),
            np.array([1,-1,1]),
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

    narr = np.array([
            (0,0,1),
            (0,0,-1),
            (0,1,0),
            (0,-1,0),
            (1,0,0),
            (-1,0,0),       
            ], 'float32')
    return varr, iarr, narr

    
def render():
    global Azimuth, Elevation, Distance, At, drag_check, space_key, get_frame_cnt, pl,extra

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if extra == -1:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    elif extra == 1:
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
    #drawFrame()
    drawGrid()

    if extra == 1:
        # light
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
               

        #light 0
        lightPos = (3.,4.,5.,1.)   
        glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
            
        ambientLightColor = (.07, .07,.1,1)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
        
        specularObjectColor = (1.,1.,1.,1.)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
        glMaterialfv(GL_FRONT, GL_SHININESS, 50)
        
        LightColor = (0.7,0.7 ,1.,1.)
        glLightfv(GL_LIGHT0, GL_SPECULAR, LightColor)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, LightColor)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, LightColor)
    
    glPushMatrix()
    if drag_check==1:
        drawBVH()
        if space_key==1:
            pl+=1

            if pl>int(get_frame_cnt):
                pl = 1
        else:
            pl = 1
    glPopMatrix()
       
        
    glDisable(GL_LIGHTING)

def main():
    global PrevCursor, Azimuth, Elevation, click_mode, At

    if not glfw.init():
        return
    window = glfw.create_window(700, 700, "Class Assignment3", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_drop_callback(window, drop_callback)

    glfw.make_context_current(window)
    glfw.swap_interval(1)

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

    
