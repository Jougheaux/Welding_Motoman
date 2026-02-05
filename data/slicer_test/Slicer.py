import os
import numpy as np
import matplotlib.pyplot as plt
import yaml

#import pygcode
#from pygcode import Machine, Line

# constants
PART = 'GcodeSamples/'
GCODE = 'SolidFuzzy'
# PART = 'radial_seg_thin'
# GCODE = 'radial_slice_new_origin_thin'
# PART = 'casing_scaled'
# GCODE = 'engine_casing_1'

def main():
    gcode_path = f'{PART}/{GCODE}.gcode'

    #### offsets ####
    X_SET = 0
    Y_SET = 0
    Z_SET = 13
    
    layer_height = .1
    

    # trailing decimals do not parse.
    # fix_trailing_decimals(gcode_path, clean_gcode)

    curr_x = 0.0
    curr_y = 0.0
    curr_z = layer_height



    # log position values
    x = []
    y = []
    z = []
    
    A = []
    B = []
    C = []

    # track layer and segment number
    layer = -2
    segment = 0
    num_layers = 0

    # flags for when the layer is changing
    seg_flag = False
    layer_flag = False
    
    #flag for when to record data
    movement_flag = False
    
    vis_step=1
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    

    # load gcode
    with open(gcode_path, 'r') as f:
        for line in f:
            if (
                line.startswith('G1') or
                #line.startswith('M') or
                line.startswith(';LAYER_CHANGE') or
                line.startswith('PRINT_END') or 
                line.startswith(';Z:')
            ):
                for cmd_str in line.split():
                    # parse comments
                    if cmd_str.startswith('//'): 
                        break
                    
                        
                    if(cmd_str[0:4] == 'G1 Z'):
                        curr_z = float(cmd_str[3:])
                        break
                        
                    cmd_letter = cmd_str[0]
                    # print(cmd_letter)
                    cmd_val = cmd_str[1:]
                    # print(cmd_val)
                    # check valid commands
                    if cmd_letter == 'X':
                        curr_x = float(cmd_val)
                        movement_flag = True
                        
                    if cmd_letter == 'Y':
                        curr_y = float(cmd_val)
                        movement_flag = True
                        
                    if cmd_letter == 'Z':
                        curr_z = float(cmd_val)
                        layer_flag = True
                        print("layer change"+str(curr_z)+','+str(segment))
                        
                    if cmd_letter == 'E':
                        if(float(cmd_val) <= 0):
                            if len(x) >0:
                                seg_flag = True
                            break
                    
                        
                   
                        
    # TODO: need to make sure M commands are detected properly 
              #      elif cmd_letter == 'M':

                # update the positions once gcode is processed
                if(movement_flag):
                    x.append(curr_x + X_SET)
                    y.append(curr_y + Y_SET)
                    z.append(curr_z + Z_SET)
                    
                    A.append(0)
                    B.append(0)
                    C.append(-1)
                    
            
                movement_flag = False

                # handle segment end or layer changes
                if (seg_flag):
                    data = convert_lists(x,y,z, A, B, C)
                    #print(data)
                    np.savetxt(
                        '.1mm_slice/curve_sliced_relative/slice'+str(layer)+'_'+str(segment)+'.csv',
                        data,
                        delimiter=','
                    )
                    #plot
                    ax.plot3D(x,y,z,'r.-')
                    #print(x)
                    
                    # reset to recieve next segment
                    if(layer>=0):
                        print("reset")
                        x = []
                        y = []
                        z = []
                        
                        A = []
                        B = []
                        C = []
                    segment += 1
                    seg_flag = False
                    
                if layer_flag:
                    #data = convert_lists(x,y,z)
                    # reset to recieve next segment
                    segment = 0
                    layer += 1
                    layer_flag = False
                    seg_flag = False
                    num_layers = layer


        #data = convert_lists(x,y,z)
        #os.makedirs(f"{PART}/curve_sliced/", exist_ok=True)
        #np.savetxt(f"{PART}/curve_sliced/raw.csv",data, delimiter=',')

        with open('.1mm_slice/sliced_meta.yml', 'w') as file:
            meta = {
                'baselayer_length': 0,
                'baselayer_num': 0,
                'baselayer_resolution': layer_height,
                'layer_length': 0,
                'layer_num': num_layers,
                'smooth_filter' : False,
                'q_positioner_seed':[-0.261799387799149, 1.5708],
                'z_offset':Z_SET,
                'slice_height':layer_height
            }
            yaml.dump(meta,file)
 
plt.show()

def convert_lists(x,y,z, A, B, C):

    # convert to one big numpy array and save
    data = np.zeros((len(x),6))
    data[:,0] = x
    data[:,1] = y
    data[:,2] = z
    data[:,3] = A
    data[:,4] = B
    data[:,5] = C

    return data


if __name__=='__main__':
    main()




