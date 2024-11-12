# Open-source bio-image analysis using surface meshes (I2K-2024, Milano)

![event cover](https://events.humantechnopole.it/event/1/logo-3075248334.png)

This repository contains three exercises used during the workshop about using meshes instead of voxels held at Milano in October 2024 for I2K.
The slides used during the workshop are also available in the release's assets.

## The workshop's description

> In some cases, meshes have advantages over using voxels for image analysis (lightweight representation, surface features, ...)
> In this workshop, participants will learn:
> - How do we pass from a voxel representation to a mesh and vice versa?
> - How do you use Blender and Napari and some dedicated Python modules to filter, process, or extract measures from meshes?

**Duration:** 1h30

**Keywords:** `mesh`, `3D`, `surface`, `measure`, `blender`, `napari`, `python`, `open3d`

## The exercises

There are three of them, and they are becoming increasingly complicated.
The PDFs explaining what you have to do and the resources (images) are in this repo's release assets.

- **Ex 1:** Transform masks or labeled maps into meshes from Fiji and visualize them on Blender. This allows you to see images that wouldn't fit your RAM otherwise, explore occluded areas, and better understand objects by going through multiple z-planes.
- **Ex 2:** Segment nuclei and spots from images that don't fit your RAM using LabKit, turn them into meshes, post-process your segmentation in Blender, and do some measures (distance repartition between each spot and the closest nuclear membrane, count the number of spots inside and outside nuclei, ...). This project was inspired by an actual project we submitted at our facility. It consisted of counting the number of extra-cellular vesicles absorbed and analyzing their distance repartition over time.
- **Ex 3:** Use Napari and Open3D (exercise in Python, no GUI) to create a 2.5D mesh representing a contact surface between an astrocyte and a blood vessel. The goal is to analyze such a structure's topology (curvature, number of holes, area, perimeter, etc.). The final step was to represent our metrics as textures over our meshes.

## Note

The second exercise is a valid Blender addon that you can reuse out-of-the-box in an actual project.
