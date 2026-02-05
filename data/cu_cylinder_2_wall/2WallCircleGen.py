import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import yaml

total_height=150
wall_radius=16
line_resolution=2.5
base_resolution=2.5
stepover_distance=5.5
base_radius=wall_radius+stepover_distance
points_distance=np.pi
y_position = 45
num_layers=int(total_height/line_resolution)
num_base = 2

z_offset = 15+34
x_offset = 90
y_offset = 0
layer_angular_shift = 35*np.pi/180


# generate layers
points_per_layer=int(wall_radius*2)
curve_dense=np.zeros((num_layers*points_per_layer,6))
curve_dense2=np.zeros((num_layers*points_per_layer,6))

#generate list of parameter t value to generate circle
t = np.linspace(0,2*np.pi,points_per_layer)


#generate the inner layer to print first
for layer in range(num_layers):
	curve_dense[layer*points_per_layer:(layer+1)*points_per_layer,0]=(wall_radius-stepover_distance)*np.cos(t+layer_angular_shift*(layer+num_base))+x_offset
	curve_dense[layer*points_per_layer:(layer+1)*points_per_layer,1]=(wall_radius-stepover_distance)*np.sin(t+layer_angular_shift*(layer+num_base))+y_offset
	curve_dense[layer*points_per_layer:(layer+1)*points_per_layer,2]=layer*line_resolution+base_resolution*num_base+z_offset

curve_dense[:,-1]=-np.ones(len(curve_dense))

for layer in range(num_layers):
	np.savetxt('2mm_slice/curve_sliced_relative/slice'+str(layer)+'_0.csv',
            curve_dense[layer*points_per_layer:(layer+1)*points_per_layer],
            delimiter=',')
    
#generate the outer layer to print second
for layer in range(num_layers):
	curve_dense2[layer*points_per_layer:(layer+1)*points_per_layer,0]=wall_radius*np.cos(t+layer_angular_shift*(layer+num_base)+np.pi)+x_offset
	curve_dense2[layer*points_per_layer:(layer+1)*points_per_layer,1]=wall_radius*np.sin(t+layer_angular_shift*(layer+num_base)+np.pi)+y_offset
	curve_dense2[layer*points_per_layer:(layer+1)*points_per_layer,2]=layer*line_resolution+base_resolution*num_base+z_offset

curve_dense2[:,-1]=-np.ones(len(curve_dense))

for layer in range(num_layers):
	np.savetxt('2mm_slice/curve_sliced_relative/slice'+str(layer)+'_1.csv',
            curve_dense2[layer*points_per_layer:(layer+1)*points_per_layer],
            delimiter=',')


vis_step=1
fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
ax.plot3D(curve_dense[::vis_step,0],curve_dense[::vis_step,1],curve_dense[::vis_step,2],'r.-')
ax.plot3D(curve_dense2[::vis_step,0],curve_dense2[::vis_step,1],curve_dense2[::vis_step,2],'r.-')



#generate a solid base of given radius
r = 4

points_per_base=int(base_radius*2)
t = np.linspace(0,2*np.pi,points_per_base)
i=0
while (r<base_radius):
    print(r)
    if(r>base_radius):
        break
    else:
        curve_base=np.zeros((num_base*points_per_base,6))
        
        for layer in range(num_base):
        	curve_base[layer*points_per_base:(layer+1)*points_per_base,0]=r*np.cos(t+layer_angular_shift*(layer)+np.pi*i)+x_offset
        	curve_base[layer*points_per_base:(layer+1)*points_per_base,1]=r*np.sin(t+layer_angular_shift*(layer)+np.pi*i)+y_offset
        	curve_base[layer*points_per_base:(layer+1)*points_per_base,2]=layer*base_resolution+z_offset
        
        curve_base[:,-1]=-np.ones(len(curve_base))
        
        for layer in range(num_base):
        	np.savetxt('2mm_slice/curve_sliced_relative/baselayer'+str(layer)+'_'+str(i)+'.csv',
                    curve_base[layer*points_per_base:(layer+1)*points_per_base],
                    delimiter=',')
        #plot next curve
        ax.plot3D(curve_base[::vis_step,0],curve_base[::vis_step,1],curve_base[::vis_step,2],'b.-')

        
        i+=1
        r = r+stepover_distance
        
        



# ax.quiver(curve_dense[::vis_step,0],curve_dense[::vis_step,1],curve_dense[::vis_step,2],curve_dense[::vis_step,3],curve_dense[::vis_step,4],curve_dense[::vis_step,5],length=1, normalize=True)
plt.show()


with open('2mm_slice/sliced_meta.yml', 'w') as file:
    meta = {
        'baselayer_length': points_per_base,
        'baselayer_num': num_base,
        'baselayer_resolution': base_resolution,
        'layer_length': points_per_layer,
        'layer_num': num_layers,
        'layer_resolution': line_resolution,
        'path_dl': points_distance,
        'smooth_filter' : False,
        'q_positioner_seed':[-0.261799387799149, 1.5708],
		'z_offset' : z_offset
        
    }
    yaml.dump(meta,file)


