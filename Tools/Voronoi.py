# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 12:37:14 2020

@author: David
"""


from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
#import numpy as np
#import csv
import pickle

## Calculate Voronoi Polygons 
#square = [(0, 0), (0, 1.6), (1.4, 1), (1, 0.8), (0.5,0.5)]
#vor = Voronoi(square)
#print(vor)

def simple_voronoi(vor, saveas=None, lim=None):
    # Make Voronoi Diagram 
    fig = voronoi_plot_2d(vor, show_points=True, show_vertices=True, s=2)

    # Configure figure 
    fig.set_size_inches(5,5)
    plt.axis("equal")

    if lim:
        plt.xlim(*lim)
        plt.ylim(*lim)
        

    if not saveas is None:
        plt.savefig("../pics/%s.png"%saveas)

    plt.show()

#simple_voronoi(vor)
#vor.regions #it shows the index of the vertices used to form the region
with open('/home/david.perez/Desktop/dic-crystal-111-checked.pickle', 'rb') as handle:
    dic_crystal = pickle.load(handle)

Peaks=[]
for i in dic_crystal.keys():
    if dic_crystal[i]["center"]:
        for peak in dic_crystal[i]["center"].keys():
            Peaks.append(dic_crystal[i]["center"][peak][0]) #what to do with double labels? they should have the same region

vor = Voronoi(Peaks)
simple_voronoi(vor)
    
"""
points: ndarray of double, shape (npoints, ndim)

    Coordinates of input points.
    
vertices: ndarray of double, shape (nvertices, ndim)

    Coordinates of the Voronoi vertices.
    
ridge_points: ndarray of ints, shape (nridges, 2)

    Indices of the points between which each Voronoi ridge lies.
    
ridge_vertices: list of list of ints, shape (nridges, *)

    Indices of the Voronoi vertices forming each Voronoi ridge.
    
regions: list of list of ints, shape (nregions, *)

    Indices of the Voronoi vertices forming each Voronoi region. -1 indicates vertex outside the Voronoi diagram.
    
point_region: list of ints, shape (npoints)

    Index of the Voronoi region for each input point. If qhull option “Qc” was not specified, the list will contain -1 for points that are not associated with a Voronoi region.
"""

#import random
#from PIL import Image 
#from scipy import spatial
#import numpy as np
#
## define the size of the x and y bounds
#screen_width = 500
#screen_height = 500
#
## define the number of points that should be used
#number_of_points = 500
#
## randomly generate a list of n points within the given x and y bounds
#point_x_coordinates = random.sample(range(0, screen_width), number_of_points)
#point_y_coordinates = random.sample(range(0, screen_height), number_of_points)
#points = list(zip(point_x_coordinates, point_y_coordinates))
#
## each point needs to have a corresponding list of pixels
#point_pixels = []
#for i in range(len(points)):
#    point_pixels.append([]) 
#
## build a search tree
#tree = spatial.KDTree(points)
#
## build a list of pixed coordinates to query
#pixel_coordinates = np.zeros((screen_height*screen_width, 2));
#i = 0
#for pixel_y_coordinate in range(screen_height):
#    for pixel_x_coordinate in  range(screen_width):
#        pixel_coordinates[i] = np.array([pixel_x_coordinate, pixel_y_coordinate])
#        i = i+1
#        
## for each pixel within bounds, determine which point it is closest to and add it to the corresponding list in point_pixels
#[distances, indices] = tree.query(pixel_coordinates)
#
#i = 0
#for pixel_y_coordinate in range(screen_height):
#    for pixel_x_coordinate in  range(screen_width):
#        point_pixels[indices[i]].append((pixel_x_coordinate, pixel_y_coordinate))
#        i = i+1
#
## each point needs to have a corresponding centroid
#point_pixels_centroid = []
#
#for pixel_group in point_pixels:
#    x_sum = 0
#    y_sum = 0
#    for pixel in pixel_group:
#        x_sum += pixel[0]
#        y_sum += pixel[1]
#
#    x_average = x_sum / max(len(pixel_group),1)
#    y_average = y_sum / max(len(pixel_group),1)
#
#    point_pixels_centroid.append((round(x_average), round(y_average)))
#
#
## display the resulting voronoi diagram
#display_voronoi = Image.new("RGB", (screen_width, screen_height), "white")
#
#for pixel_group in point_pixels:
#    rgb = random.sample(range(0, 255), 3)
#    for pixel in pixel_group:
#        display_voronoi.putpixel( pixel, (rgb[0], rgb[1], rgb[2], 255) )
#
#for centroid in point_pixels_centroid:
#    #print(centroid)
#    display_voronoi.putpixel( centroid, (1, 1, 1, 255) )
#
#display_voronoi.show()
##display_voronoi.save("test.png")