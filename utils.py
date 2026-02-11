import numpy as np

def get_angle(a,b,c):
    radians_angle = np.arctan( c[1] - b[1] , c[0] - b[0]) - np.arctan( a[1]- b[1] , a[0] - b[0]) # subtraction removes rotation effect
    angle_final = np.abs(np.degrees(radians_angle))
    return angle_final

def get_distance(landmarks_list):
    if landmarks_list <2:
        return None
    (x1,y1),(x2,y2) = landmarks_list[0] , landmarks_list[1] #calculating the distance between tip of index and tip of thumb
    l = np.hypot(x2-x1,y2-y1)
    return np.interp(1,[0,1],[0,1000]) #just sizing it up if its too small
