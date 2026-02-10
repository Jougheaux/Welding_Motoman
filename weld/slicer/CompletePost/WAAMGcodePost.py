# -*- coding: utf-8 -*-
"""
@author: jbrew
brewsj@rpi.edu

This is the complete post, import gcode and it will run the waam cell

If you're using this after Spring 2026, send me any cool pictures of parts at jbrewster9894@gmail.com
"""

import subprocess
from subprocess import Popen, CREATE_NEW_CONSOLE #needed for running bat files
import os #this is used for file management

import numpy as np
import matplotlib.pyplot as plt

from redundancy_resolution import *

from parse_gcode import parse_gcode
from baseline_joint_func import run_baseline_joint

from weld_sliced_func import weld_sliced

from angled_layers import *



#Flags
slice_flag = False
js_flag = slice_flag
print_flag = True

file_number_index = 0 #use to set the file extension number if just welding and not slicing

#SLICING PARAMETERS
#all in mm needs to have nice input box in slicer ui eventually
X_SET = 0
Y_SET = 0
Z_SET = 26 #build plate thickness


#WELDING PARAMETERS

ARCON = True
flir_on = True
job_offset = 94
feedrate_cmd = 0
vd = 15
measure_distance = 500
pos_vel = 1.0
jog_vd = 5.0
height_offset = -7.9287 #mm this accounts for where the camera thinks the bead is, DO NOT USE TO CHANGE LAYER POSITION

make_new_slice_dir = True



current_dir = os.getcwd()

    #GcodeFileName
gcode_dir = current_dir+'/input/'
part_name = (os.listdir(gcode_dir)[-1]).split('.')[0]
if(not(slice_flag)):
    if(file_number_index ==0):
        data_dir = current_dir+'/parts/'+part_name+'/sliced_output/'
    else:
        data_dir = current_dir+'/parts/'+part_name+'/sliced_output'+' (' + str(file_number_index) + ')'+'/'


#Creates the paths to put the output CSV files
def make_unique_path(path):
    filename, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = filename + ' (' + str(counter) + ')' + extension
        counter += 1
    return path


#step 1: import and parse gcode
#save it in a folder in the directory of the post
#slicer func inouts are x y z offaets and lywr height

def slice_part(part_name): 
    
    if(not(make_new_slice_dir)):
        if(file_number_index ==0):
            data_dir = current_dir+'/parts/'+part_name+'/sliced_output/'
        else:
            data_dir = current_dir+'/parts/'+part_name+'/sliced_output'+' (' + str(file_number_index) + ')'+'/'
    else:
        data_dir = make_unique_path(current_dir+'/parts/'+part_name+'/sliced_output')+'/'
    os.makedirs(data_dir)
    os.makedirs(data_dir+'curve_sliced_relative')
    os.makedirs(data_dir+'curve_sliced_js')
    
    parse_gcode(gcode_dir, part_name, X_SET, Y_SET, Z_SET, data_dir)
    
    return data_dir

if(slice_flag):
    data_dir = slice_part(part_name)



#step 2: redundacy resolution

if(js_flag):
    run_baseline_joint(data_dir)

#step 3: run drivers
def run_drivers():
    driver_dir = current_dir+'/../../../run_driver_cmd/'

    subprocess.Popen(['cmd.exe', '/k', 'run_flir.bat'], cwd=driver_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
    subprocess.Popen(['cmd.exe', '/k', 'run_fronius_monitor.bat'], cwd=driver_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
    return

recorded_dir = make_unique_path(data_dir+'/data/')

#step 4: run welder 
if(print_flag):
    run_drivers():
    input("Enter to start welding process")
    weld_sliced(job_offset, feedrate_cmd, vd, measure_distance,pos_vel,jog_vd,height_offset, (ARCON and flir_on), ARCON, recorded_dir, data_dir)

#4.1 is motion test 4.2 is run part
#create a folder in the same folder with the same name as the gcode to hold flir data


