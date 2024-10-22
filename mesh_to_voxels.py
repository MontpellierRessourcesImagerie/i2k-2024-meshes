import trimesh
import numpy as np
import os
import tifffile

def mesh_to_voxels(mesh, voxel_size=0.136):
    bounds = mesh.bounds
    grid_shape = ((bounds[1] - bounds[0]) / voxel_size).astype(int) + 1
    print("Grid shape: ", grid_shape)
    voxel_grid = mesh.voxelized(pitch=voxel_size)
    voxels = voxel_grid.matrix
    return voxels

if __name__ == "__main__":
    folder = "/home/benedetti/Downloads/wrl-v2/output"
    file = "1-centered-MM_01_601_WGA 647_uplay ctx d_x25 zstack-02_processed_3D_V1_astro2contact-0001.obj"
    full_path = os.path.join(folder, file)

    mesh = trimesh.load(full_path)
    voxel_grid = mesh_to_voxels(mesh)

    print(voxel_grid.shape)
    tifffile.imwrite("/home/benedetti/Downloads/wrl-v2/tests/voxel_grid.tif", voxel_grid.astype(np.uint8)*255)

