# -*- coding: utf-8 -*-
"""
Created on Thu May 21 12:12:58 2020

@author: David
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as pch

from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)

def layer(x_ini,x_fin,y_ini,y_fin):
    xiter = np.arange(x_ini,x_fin,1.34) #1.34 is the theoretical one, but adaptative to electronics
    yiter = np.arange(y_ini,y_fin,1.34)
    print(len(xiter)*len(yiter))
    print(len(xiter))
    print(len(yiter))
    xx=np.fromiter(xiter,dtype=np.float)
    yy=np.fromiter(yiter,dtype=np.float)
    xo, yo = np.meshgrid(xx,yy,indexing='xy')
    return xo,yo

def axis_f(MLx, MLy,AMLx, AMLy,xl,yl,ax):
    ax.set_xlim(xl)
    ax.set_ylim(yl)
    
    # Change major ticks to show every 20.
    ax.xaxis.set_major_locator(MultipleLocator(MLx))
    ax.yaxis.set_major_locator(MultipleLocator(MLy))
    
    # Change minor ticks to show every 5. (20/4 = 5)
    ax.xaxis.set_minor_locator(AutoMinorLocator(AMLx))
    ax.yaxis.set_minor_locator(AutoMinorLocator(AMLy))
    
    # Turn grid on for both major and minor ticks and style minor slightly
    # differently.
    ax.grid(which='major', color='#CCCCCC', linestyle='--')
    ax.grid(which='minor', color='#CCCCCC', linestyle=':')
            
    ax.set_axisbelow(True)
    #
    ax.set_aspect(1.0) #keep aspects 1:1 between axis
    return ax

# make grid First Layer
xo, yo = layer(-22.11,22.78,-23.45,24.12) #0.67 -21.95982 x, 21.6704 y
#xo, yo = layer(-21.95982, 21.6704,-23.33,24.0)
#print(xo)
#print(yo)
# make grid Second Layer
xo2, yo2 = layer(-20.1,20.77,-23.45,24.12)

# make grid Third Layer
xo3, yo3 = layer(-20.1,20.77,-22.78,23.45)

x_size = 3.8016
y_size = 3.2
pix_x = [-21.95982,-18.04018,-13.95982,-10.04018,-5.95982, -2.04018, 2.04018,5.98982,10.04018,13.95982,18.04018,21.95982]
pix_y = [21.6704,18.3296,13.6704,10.3296,5.6704,2.3296,-2.3296,-5.6704,-10.3296,-13.6704,-18.3296,-21.6704]

fig1, ax1 = plt.subplots(figsize=(10, 10))
# Set axis ranges; by default this will put major ticks every 25.
ax1 = axis_f(22.78, 24.12, 17,18,(-22.78, 22.78),(-24.12, 24.12),ax1) #14.925373134328357

#for i in np.arange(-23, 23,3.8):
#    plt.axvline(x=i, ymin=0, ymax=49.3333333, linewidth=1.2, color='dimgray')
#    
#for i in np.arange(-24, 24,4.025):
#    plt.axhline(y=i, xmin=0, xmax=46.6666666, linewidth=1.2, color='dimgray')
#
#for i in np.arange(-23, 23,7.6):
#    plt.axvline(x=i, ymin=0, ymax=49.3333333, linewidth=1.4, color='k')
#    
#for i in np.arange(-24, 24,8.05):
#    plt.axhline(y=i, xmin=0, xmax=46.6666666, linewidth=1.4, color='k')
    

plt.scatter(xo, yo, s=20, marker='2', c="green", label="1st Layer") #first layer
ax1 = plt.gca()
cs1 = ax1.collections[0]
cs1.set_offset_position("data")
coord_1 = cs1.get_offsets()
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

        
#plt.show()

fig2, ax2 = plt.subplots(figsize=(10, 10))
# Set axis ranges; by default this will put major ticks every 25.
ax2 = axis_f(22.78, 24.12, 17,18,(-22.78, 22.78),(-24.12, 24.12),ax2) #14.925373134328357


plt.scatter(xo2, yo2, s=20, marker='x', c="red", label="2nd Layer") # second layer
ax2 = plt.gca()
cs2 = ax2.collections[0]
cs2.set_offset_position("data")
coord_2 = cs2.get_offsets()
print(len(coord_2))
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)



        
#plt.show()

fig3, ax3 = plt.subplots(figsize=(10, 10))
# Set axis ranges; by default this will put major ticks every 25.
ax3 = axis_f(22.78, 24.12, 17,18,(-22.78, 22.78),(-24.12, 24.12),ax3) #14.925373134328357


plt.scatter(xo3, yo3, s=20, marker='+', c="blue", label="3rd Layer") # third layer
ax3 = plt.gca()
cs3 = ax3.collections[0]
cs3.set_offset_position("data")
coord_3 = cs3.get_offsets()
print(len(coord_3))
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)



        
#plt.show()

fig, ax = plt.subplots(figsize=(10, 10))


# Set axis ranges; by default this will put major ticks every 25.
ax = axis_f(22.78, 24.12, 17,18,(-22.78, 22.78),(-24.12, 24.12),ax) #14.925373134328357

for pix_x_i in pix_x:
    for pix_y_i in pix_y:
        rect = pch.Rectangle((pix_x_i-x_size/2,pix_y_i-y_size/2),x_size,y_size, linewidth=0.5, edgecolor="dimgray",facecolor="none")
        ax.add_patch(rect)

plt.scatter(xo, yo, s=20, marker='2', c="green", label="1st Layer") #first layer
plt.scatter(xo2, yo2, s=20, marker='x', c="red", label="2nd Layer") # second layer
plt.scatter(xo3, yo3, s=20, marker='+', c="blue", label="3rd Layer") # third layer

plt.legend(bbox_to_anchor=(-0.03, 0.75), loc='lower right', borderaxespad=0.) #bbox_to_anchor=(1.05, 1),

plt.xlabel("x [mm]")
plt.ylabel("y [mm]")


        
plt.show()

def CrystalDict(self):
    """
    Define Crystal identification dictionary
     
    @return: None
    @rtype:
    """
    
    layer_1 = 1224
    layer_2 = 1116
    layer_3 = 1085
    n_crystal = layer_1+layer_2+layer_3
    self.dic_crystal = {}
    for i in np.arange(layer_1):
        peakii={
        'id'         : i,
        'layer'      : 1,
        'center'     : {},
        'theo_center': {coord_1[i]}
        }
        self.dic_crystal[i] = peakii
    for j in np.arange(layer_1, layer_1+layer_2):
        peakjj={
        'id'         : j,
        'layer'      : 2,
        'center'     : {},
        'theo_center': {coord_2[i]}
        }
        self.dic_crystal[j] = peakjj
    for k in np.arange(layer_1+layer_2, n_crystal):
        peakkk={
        'id'         : k,
        'layer'      : 3,
        'center'     : {},
        'theo_center': {coord_3[i]}
        }
        self.dic_crystal[k] = peakkk
m=1
row=[]
j=0
p=0
rows=[]
for i in range(3426):
    if i >= (65*m + 31*p) and j%2 == 0:
        rows.append(row)
        row = []
        j += 1
        p += 1
    elif i >= (65*m+ 31*p) and j%2 != 0:
        rows.append(row)
        row = []
        j += 1
        m += 1
    else:
        pass
    row.append(i)
    

        

#fig2, ax2 = plt.subplots(figsize=(100, 100))
#
#xo, yo = layer(0.666666666,15.0,0.666666666,18.0)
##print(xo)
##print(yo)
## make grid Second Layer
#xo2, yo2 = layer(2.666666666,13.0,0.666666666,18.0)
#
## make grid Third Layer
#xo3, yo3 = layer(2.666666666,13.0,1.333333333,17.0)
#
#ax2 = axis_f(20,15,(0, 15.6666666),(0, 18.3333333),ax2)
#
#plt.scatter(xo, yo, s=50, marker='2', c="green", label="1st Layer") #first layer
#
#plt.scatter(xo2, yo2, s=40, marker='x', c="red", label="2nd Layer") # second layer
#
#plt.scatter(xo3, yo3, s=50, marker='+', c="blue", label="3rd Layer") # third layer
#
#plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
#     
#plt.show()