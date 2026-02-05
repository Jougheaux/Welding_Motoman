import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import yaml

total_height=50
wall_diameter=50
base_diameter=wall_diameter
line_resolution=2
base_resolution=2
stepover_distance=4
points_distance=np.pi
y_position = 45
num_layers=int(total_height/line_resolution)
num_base = 2


# generate layers
points_per_layer=int(wall_diameter)
curve_dense=np.zeros((num_layers*points_per_layer,6))

#generate list of parameter t value to generate circle
t = np.linspace(0,2*np.pi,points_per_layer)


#generate the inner layer to print first
for layer in range(num_layers):
	curve_dense[layer*points_per_layer:(layer+1)*points_per_layer,0]=(wall_diameter-2*stepover_distance)*np.cos(t)
	curve_dense[layer*points_per_layer:(layer+1)*points_per_layer,1]=(wall_diameter-2*stepover_distance)*np.sin(t)
	curve_dense[layer*points_per_layer:(layer+1)*points_per_layer,2]=layer*line_resolution+base_resolution*num_base

curve_dense[:,-1]=-np.ones(len(curve_dense))

for layer in range(num_layers):
	np.savetxt('2mm_slice/layers/slice'+str(layer)+'_0.csv',
            curve_dense[layer*points_per_layer:(layer+1)*points_per_layer],
            delimiter=',')
    
#generate the outer layer to print second
for layer in range(num_layers):
	curve_dense[layer*points_per_layer:(layer+1)*points_per_layer,0]=wall_diameter*np.cos(t)
	curve_dense[layer*points_per_layer:(layer+1)*points_per_layer,1]=wall_diameter*np.sin(t)
	curve_dense[layer*points_per_layer:(layer+1)*points_per_layer,2]=layer*line_resolution+base_resolution*num_base

curve_dense[:,-1]=-np.ones(len(curve_dense))

for layer in range(num_layers):
	np.savetxt('2mm_slice/layers/slice'+str(layer)+'_1.csv',
            curve_dense[layer*points_per_layer:(layer+1)*points_per_layer],
            delimiter=',')

# generate inner base to print first
points_per_base=int(base_diameter)
curve_base=np.zeros((num_base*points_per_base,6))

for layer in range(num_base):
	curve_base[layer*points_per_base:(layer+1)*points_per_base,0]=(wall_diameter-2*stepover_distance)*np.cos(t)
	curve_base[layer*points_per_base:(layer+1)*points_per_base,1]=(wall_diameter-2*stepover_distance)*np.sin(t)
	curve_base[layer*points_per_base:(layer+1)*points_per_base,2]=layer*base_resolution

curve_base[:,-1]=-np.ones(len(curve_base))

for layer in range(num_base):
	np.savetxt('2mm_slice/layers/baselayer'+str(layer)+'_0.csv',
            curve_base[layer*points_per_base:(layer+1)*points_per_base],
            delimiter=',')
    
# generate inner base to print first
points_per_base=int(base_diameter)
curve_base=np.zeros((num_base*points_per_base,6))

for layer in range(num_base):
	curve_base[layer*points_per_base:(layer+1)*points_per_base,0]=base_diameter*np.cos(t)
	curve_base[layer*points_per_base:(layer+1)*points_per_base,1]=base_diameter*np.sin(t)
	curve_base[layer*points_per_base:(layer+1)*points_per_base,2]=layer*base_resolution

curve_base[:,-1]=-np.ones(len(curve_base))

for layer in range(num_base):
	np.savetxt('2mm_slice/layers/baselayer'+str(layer)+'_1.csv',
            curve_base[layer*points_per_base:(layer+1)*points_per_base],
            delimiter=',')

vis_step=1
fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
ax.plot3D(curve_dense[::vis_step,0],curve_dense[::vis_step,1],curve_dense[::vis_step,2],'r.-')
ax.plot3D(curve_base[::vis_step,0],curve_base[::vis_step,1],curve_base[::vis_step,2],'b.-')
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
        'path_dl': points_distance
    }
    yaml.dump(meta,file)


