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


def weld_sliced(job_offset, feedrate_cmd, vd, measure_distance,pos_vel,jog_vd,height_offset, ONLINE, ARCON, recorded_dir, data_dir):
    ###
    #list of layer heights
    layer_heights = [0]
    convertmm = 1 #constant to convert the output of the weld height to mm

    #####################SENSORS############################################
    if ONLINE:
    # weld state logging
        weld_ser = RRN.SubscribeService('rr+tcp://192.168.55.10:60823?service=welder')
        cam_ser = RRN.ConnectService("rr+tcp://localhost:60827/?service=camera")
        # cam_ser = None
        # mic_ser = RRN.ConnectService('rr+tcp://localhost:60828?service=microphone')
        ## RR sensor objects
        rr_sensors = WeldRRSensor(
            weld_service=weld_ser, cam_service=cam_ser, microphone_service=None
        )

    config_dir = "../../../config/"
    flir_intrinsic = yaml.load(open(config_dir + "FLIR_A320.yaml"), Loader=yaml.FullLoader)

    ################################ Data Directories ###########################
    now = datetime.now()

    
    print_param = {
        'print_speed':vd,
        'job_no':job_offset
    }    
    with open(data_dir + "printed_meta.yml", "w") as file:
        yaml.dump(print_param,file)


    with open(data_dir + "sliced_meta.yml", "r") as file:
        sliced_meta = yaml.safe_load(file)
        

    true_height_offset = height_offset-sliced_meta['z_offset'] ##add this -15 to the yaml file and read it here
    slice_height = sliced_meta['slice_height'] #mm per sliced layer
    num_layers = sliced_meta['layer_num'] #number of layers

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

    for layer in range(0, num_layers):
        
        #adjust layer position
        if layer >0:
            if(ONLINE):
                num_segs = len(glob.glob(f"{recorded_dir}layer_{layer-1}_seg_*/"))
                for seg in range(num_segs):      
                    seg_heights = []
                    start_dir = 0
                    ir_error_flag = False
                    ### Process IR data prev 
                    try:
                        flame_3d_prev, _, job_no_prev = flame_tracking(f"{recorded_dir}layer_{layer-1}_seg_{seg}/", robot, robot2, positioner, flir_intrinsic, height_offset)
                        if flame_3d_prev.shape[0] == 0:
                            raise ValueError("No flame detected")
                    except ValueError as e:
                        print(e)
                        flame_3d_prev = None
                        ir_error_flag = True
                    #else:
                    heights_prev = flame_3d_prev[:,2]
                    seg_heights.append(sum(heights_prev)/len(heights_prev)+true_height_offset)
                average_layer_height = sum(seg_heights)/len(seg_heights)
                layer_heights.append(round(convertmm*average_layer_height/slice_height))
        
        
                print("Layer Position:"+layer_heights[layer])
                overrideLayerHeight = input("If layer is wrong input desired ideal layer position")
                if overrideLayerHeight == "":
                    break
                else:
                    layer_heights[-1] = round(overrideLayerHeight/slice_height)

            else:
                overrideLayerHeight = input("Input build height")
                layer_heights.append(round(overrideLayerHeight/slice_height))

        num_segs = len(glob.glob(f'{data_dir}curve_sliced_relative/slice{layer_heights[layer]}_*.csv'))
        print("Number of Segments: ", num_segs)
        for seg in range(num_segs):
            ### Load Data
            curve_sliced_js = np.loadtxt(
                data_dir + f"curve_sliced_js/MA2010_js{layer_heights[layer]}_{seg}.csv", delimiter=","
            ).reshape((-1, 6))

            positioner_js = np.loadtxt(
                data_dir + f"curve_sliced_js/D500B_js{layer_heights[layer]}_{seg}.csv", delimiter=","
            )
            curve_sliced_relative = np.loadtxt(
                data_dir + f"curve_sliced_relative/slice{layer_heights[layer]}_{seg}.csv", delimiter=","
            )

            
            if layer%2 == 0:
                breakpoints = np.linspace(
                    0, len(curve_sliced_js) - 1, num=len(curve_sliced_js)
                ).astype(int)
            else:
                breakpoints = np.linspace(
                    len(curve_sliced_js) - 1, 0, num=len(curve_sliced_js)
                ).astype(int)


            #### jog to start and position camera
            if seg == 0:
                p_positioner_home = np.mean(
                    [robot.fwd(curve_sliced_js[0]).p, robot.fwd(curve_sliced_js[-1]).p], axis=0
                )
                p_robot2_proj = p_positioner_home + np.array([0, 0, 50])
                p2_in_base_frame = np.dot(H2010_1440[:3, :3], p_robot2_proj) + H2010_1440[:3, 3]
                # pointing toward positioner's X with 15deg tiltd angle looking down
                v_z = H2010_1440[:3, :3] @ np.array([0, -0.96592582628, -0.2588190451])
                # FLIR's Y pointing toward 1440's -X in 1440's base frame,
                # projected on v_z's plane
                v_y = VectorPlaneProjection(np.array([-1, 0, 0]), v_z)
                v_x = np.cross(v_y, v_z)
                # back project measure_distance-mm away from torch
                p2_in_base_frame = p2_in_base_frame - measure_distance * v_z
                R2 = np.vstack((v_x, v_y, v_z)).T
                q2 = robot2.inv(p2_in_base_frame, R2, last_joints=np.zeros(6))[0]
                q_prev = client.getJointAnglesDB(positioner.pulse2deg)
                num2p = np.round((q_prev - positioner_js[0]) / (2 * np.pi))
                positioner_js += num2p * 2 * np.pi
                ws.jog_dual(robot2, positioner, q2, positioner_js[0], v=1)

            print(int(feedrate_cmd / 10) + job_offset)

            
            input("Enter to start welding")
            save_path = recorded_dir + "layer_" + str(layer) +"_seg_"+str(seg)+ "/"
            try:
                os.makedirs(save_path)
            except Exception as e:
                print(e)

            q1_all = [curve_sliced_js[breakpoints[0]]]
            q2_all = [positioner_js[breakpoints[0]]]
            v1_all = [jog_vd]
            v2_all = [pos_vel]
            primitives = ["movej"]
            for j in range(0, len(breakpoints)):
                q1_all.append(curve_sliced_js[breakpoints[j]])
                q2_all.append(positioner_js[breakpoints[j]])
                v1_all.append(max(vd, 0.1))
                v2_all.append(pos_vel)
                primitives.append("movel")
            q_prev = positioner_js[breakpoints[-1]]
            ################ Weld with sensors #############################
            if ONLINE:
                rr_sensors.start_all_sensors()
            global_ts, robot_ts, joint_recording, job_line, _ = ws.weld_segment_dual(
                primitives,
                robot,
                positioner,
                q1_all,
                q2_all,
                v1_all,
                v2_all,
                cond_all=[int(feedrate_cmd / 10) + job_offset],
                # cond_all=[int(feedrate_cmd)],
                arc=ARCON,
                blocking=True,
            )
            if ONLINE:
                rr_sensors.stop_all_sensors()
                global_ts = np.reshape(global_ts, (-1, 1))
                job_line = np.reshape(job_line, (-1, 1))

                # save data
                np.savetxt(
                    save_path + "weld_js_exe.csv",
                    np.hstack((global_ts, job_line, joint_recording)),
                    delimiter=",",
                )
                rr_sensors.save_all_sensors(save_path)

            q_0 = client.getJointAnglesMH(robot.pulse2deg)
            q_0[1] = q_0[1] - np.pi /25
            print(q_0)
            ws.jog_single(robot, q_0, 4)
        print(f"-------Layer {layer} Seg. {seg} Finished-------")
