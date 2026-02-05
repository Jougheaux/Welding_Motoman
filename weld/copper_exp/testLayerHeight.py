# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 10:32:01 2025

@author: jbrew
"""

import sys
import glob
import yaml
import numpy as np

from lambda_calc import *
from dual_robot import *
from dx200_motion_program_exec_client import *
from WeldSend import *
from RobotRaconteur.Client import *
from weldRRSensor import *
from motoman_def import *
from flir_toolbox import *
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.optimize import minimize, Bounds
from numpy.linalg import norm
from matplotlib import pyplot as plt

from angled_layers import *

###set up control parameters
job_offset = 140
feedrate_cmd = 0
base_feedrate_cmd = 0
base_vd = 6.0
vd = 10
measure_distance = 500
pos_vel = 1.0
jog_vd = 1.0
job_no_offset = 3
num_layers = 24
num_baselayers = 0
height_offset = -7.9287 #mm this accounts for where the camera thinks the bead is
layer_height = 3 # mm
bead_width = 5.5 # mm
ONLINE = False
ARCON = True

###
#list of layer heights
layer_heights = []
layer_height_abs = [0]
layer_height_inc=[]
convertmm = 1 #constant to convert the output of the weld height to mm
slice_height = 0.1 #mm per sliced layer

true_height_offset = height_offset-15

#####################SENSORS############################################
config_dir = "../../config/"
flir_intrinsic = yaml.load(open(config_dir + "FLIR_A320.yaml"), Loader=yaml.FullLoader)
################################ Data Directories ###########################
now = datetime.now()

dataset = "al_slicer_test/2mm_slice/"
data_dir = "../../data/" + dataset 
rec_folder = ""
if rec_folder == "":
    recorded_dir = now.strftime(
        "../../../recorded_data/LeakTest1FirstHalf/"
    )
    os.makedirs(recorded_dir, exist_ok=True)
else:
    recorded_dir = "../../recorded_data/" + rec_folder + "/"
    

robot = robot_obj(
    "MA2010_A0",
    def_path=f"{config_dir}/MA2010_A0_robot_default_config.yml",
    tool_file_path=f"{config_dir}/torch_robot.csv",
    pulse2deg_file_path=f"{config_dir}/MA2010_A0_pulse2deg_real.csv",
    d=15,
)
robot2 = robot_obj(
    "MA1440_A0",
    def_path=f"{config_dir}/MA1440_A0_robot_default_config.yml",
    tool_file_path=f"{config_dir}/flir.csv",
    pulse2deg_file_path=f"{config_dir}/MA1440_A0_pulse2deg_real.csv",
    base_transformation_file=f"{config_dir}/MA1440_pose.csv",
)
positioner = positioner_obj(
    "D500B",
    def_path=f"{config_dir}/D500B_robot_default_config.yml",
    tool_file_path=f"{config_dir}/positioner_tcp.csv",
    pulse2deg_file_path=f"{config_dir}/D500B_pulse2deg_real.csv",
    base_transformation_file=f"{config_dir}/D500B_pose.csv",
)

H2010_1440 = H_inv(robot2.base_H)
client = MotionProgramExecClient()
ws = WeldSend(client)


###########################################layer welding############################################
print("----------Normal Layers-----------")
if ONLINE:
    q_prev = client.getJointAnglesDB(positioner.pulse2deg)
    # q_prev = np.array([9.53e-02, -2.71e00])  ###for motosim tests only

for layer in range(1, num_layers):
        

    start_dir = 0
    ir_error_flag = False
    ### Process IR data prev 
    try:
        flame_3d_prev, _, job_no_prev = flame_tracking(f"{recorded_dir}layer_{layer-1}_seg_0/", robot, robot2, positioner, flir_intrinsic, height_offset)
        if flame_3d_prev.shape[0] == 0:
            raise ValueError("No flame detected")
    except ValueError as e:
        print(e)
        flame_3d_prev = None
        ir_error_flag = True
    #else:
    heights_prev = flame_3d_prev[:,2]
    average_layer_height = sum(heights_prev)/len(heights_prev)+true_height_offset
    layer_heights.append(round(convertmm*average_layer_height/slice_height))
    layer_height_abs.append(average_layer_height)
    layer_height_inc.append(layer_height_abs[layer]-layer_height_abs[layer-1])

    
    #print(f"-------Layer {layer} Seg. {seg} Finished-------")
print(layer_height_inc)
print(sum(layer_height_inc)/len(layer_height_inc))