import napari
import open3d as o3d
from scipy.spatial import KDTree, Delaunay
import csv
from multiprocessing import Pool
from functools import partial
import numpy as np
import os
import math


def isSmall(e):
    """Determines if a value can be considered as neglectable (whether it's positive or negative)."""
    return abs(e) < 0.0001


def normalize(v):
    """Turns the vector passed as argument into a unit vector."""
    return v / np.linalg.norm(v)


def makeSourceName(name):
    return os.path.basename(name).split('.')[0]


class AstrocytesContactState(object):
    
    def __init__(self):
        self.meshes = None
        self.transforms = None
        self.measures = None
        self.vertices_colors = None

    def open_mesh(self, path, scale=1.0):
        """
        Opens a mesh file and stores it in the 'meshes' attribute.
        Refreshes the normals of the mesh in case they are not present.
        """
        self.meshes = [o3d.io.read_triangle_mesh(path)]
        for m in self.meshes:
            vertices = np.asarray(m.vertices)
            m.vertices = o3d.utility.Vector3dVector(vertices * scale)
            m.compute_vertex_normals()
            m.compute_triangle_normals()

    def _mesh_to_origin(self, mesh):
        """
        Centers the meshes around their centroid.
        Returns the list of the centers of the meshes before they were centered.
        """
        center = mesh.get_center()
        mesh.translate(-center)
        return center
    
    def mesh_to_origin(self, mesh, factor=0.2):
        """
        Centers the meshes around their centroid.
        Returns the list of the centers of the meshes before they were centered.
        """
        center = mesh.get_center()
        mesh.translate(-center)
        good_vertices = self.normals_pointing_to_origin(mesh)
        vertices_idx = np.where(good_vertices)[0]
        if len(vertices_idx) > 0:
            return center
        n_normals = np.asarray(mesh.vertex_normals) / np.linalg.norm(np.asarray(mesh.vertex_normals), axis=1)[:, np.newaxis]
        avg_normal = np.mean(n_normals, axis=0)
        avg_normal /= np.linalg.norm(avg_normal)
        mesh.translate(avg_normal * factor)
        return center + avg_normal * factor

    def split_connected_components(self):
        """
        Connected components labeling.
        """
        meshes = []
        for mesh in self.meshes:
            # List of the same size as 'triangles', containing the index of the cluster for each triangle.
            triangle_clusters, _, _ = mesh.cluster_connected_triangles()
            # Open3D objects are std::vector-like, so we need to convert them to numpy arrays.
            triangle_clusters = np.asarray(triangle_clusters)
            unique_clusters = np.unique(triangle_clusters) # list of unique cluster IDs
            for cluster_id in unique_clusters:
                indices_f = np.where(triangle_clusters == cluster_id)[0] # list of indices of faces where the face belongs to the cluster
                faces = np.asarray(mesh.triangles)
                indices_v = np.unique(faces[indices_f].flatten()) # list of indices of the vertices in the cluster
                component_mesh = mesh.select_by_index(indices_v) # Selecting desired vertices
                meshes.append(component_mesh)
        self.meshes = meshes
    
    def merge_close_vertices(self, threshold):
        """
        Merges vertices that are closer than the threshold.
        """
        for mesh in self.meshes:
            mesh.merge_close_vertices(threshold)
    
    def _smooth_mesh(self, mesh, iterations):
        return mesh.filter_smooth_simple(number_of_iterations=iterations)
    
    def smooth_meshes(self, iterations):
        """
        Smooths all the meshes in the list.
        """
        for i in range(len(self.meshes)):
            self.meshes[i] = self._smooth_mesh(self.meshes[i], iterations)

    def normals_pointing_to_origin(self, mesh, threshold=1e-6):
        """
        In this function, we want to identify the vertices whose normals are pointing towards the origin.
        With them, we can identify the inner part of the mesh from the outer part.
        The dot product between the normal and the vector towards the origin is computed for each vertex.
        Given the rule: dot(a, b) > 0 if the angle between a and b is less than 90 degrees, we can identify those vertices.

        Returns:
            - (np.array): A boolean array of the same size as the number of vertices in the mesh.
                          It contains True for the vertices whose normals are pointing towards the origin.
        """
        mesh.compute_vertex_normals()
        mesh.compute_triangle_normals()
        
        vertices = np.asarray(mesh.vertices)
        normals  = np.asarray(mesh.vertex_normals)
        
        vertex_directions = -vertices  # Vectors towards the origin.
        vertex_directions /= np.linalg.norm(vertex_directions, axis=1)[:, np.newaxis]

        dot_products = np.einsum('ij,ij->i', normals, vertex_directions) # dot_product(normals, vertex_directions)
        is_pointing_to_origin = dot_products > threshold
        
        return is_pointing_to_origin
    
    def flatten(self):
        """
        Takes a volume mesh and transforms it into a surface mesh.
        The produced object is a 2D plane deformed in a way that it takes a 3D space to represent it.
        This surface has no thickness as it is a 2D object.
        Depending on the threshold used for `normals_pointing_to_origin`, there can be a small part of transitive area left over.
        """
        new_meshes = []
        for mesh in self.meshes:
            center = self.mesh_to_origin(mesh)
            good_vertices = self.normals_pointing_to_origin(mesh)
            vertices_idx = np.where(good_vertices)[0]
            if len(vertices_idx) == 0:
                continue
            component_mesh = mesh.select_by_index(vertices_idx)
            component_mesh.translate(center)
            new_meshes.append(component_mesh)
        self.meshes = new_meshes

    def fill_holes(self, size=0.02):
        """
        Fills the holes in the mesh, if the hole is smaller than the size specified.
        """
        for i, mesh in enumerate(self.meshes):
            t_mesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
            t_mesh_filled = t_mesh.fill_holes(size)
            mesh_filled = t_mesh_filled.to_legacy()
            mesh_filled.orient_triangles()
            mesh_filled.compute_vertex_normals()
            mesh_filled.compute_triangle_normals()
            self.meshes[i] = mesh_filled

    def decimate(self, factor):
        """
        Factor is a float between 0 and 1.
        It represents the percentage of faces to keep.
        """
        for i, mesh in enumerate(self.meshes):
            decimated = mesh.simplify_quadric_decimation(int(len(mesh.triangles) * factor))
            self.meshes[i] = decimated
    
    def _get_all_edges(self, mesh):
        """
        If i goes to j, then j goes to i.
        So we don't need to duplicate the information.
        """
        faces = np.asarray(mesh.triangles)
        edges = set()
        pairs = [(0, 1), (0, 2), (1, 2)]
        for face in faces:
            for i, j in pairs:
                p1, p2 = face[i], face[j]
                if p1 > p2:
                    p1, p2 = p2, p1
                edges.add((p1, p2))
        return np.array(list(edges))
    
    def _get_faces_count(self, mesh):
        """
        Processes the number of faces in which a given vertex is involved.
        Returns a 1D array with the number of faces for each vertex.
        Indices are the vertex indices.
        """
        faces = np.asarray(mesh.triangles).flatten()
        faces_count = np.bincount(faces, minlength=len(mesh.vertices))
        return faces_count
    
    def n_incident_edges(self, v_index, all_edges):
        """
        Returns the number of edges incident to a given vertex.
        """
        return len(np.where((all_edges[:, 0] == v_index) | (all_edges[:, 1] == v_index))[0])

    def _get_exterior_vertices(self, mesh):
        faces_count = self._get_faces_count(mesh)
        all_edges = self._get_all_edges(mesh)
        exterior_vertices = np.zeros(len(mesh.vertices), dtype=bool)
        
        for v_idx, n_faces in enumerate(faces_count):
            n_edges = self.n_incident_edges(v_idx, all_edges)
            
            if n_faces != n_edges:
                exterior_vertices[v_idx] = True
                
        return exterior_vertices

    def get_exterior_vertices(self):
        """
        Returns the list of exterior vertices for each mesh.
        """
        return [self._get_exterior_vertices(m) for m in self.meshes]
    
    @staticmethod
    def build_neighborhood_graph(faces):
        graph = {}
        for face in faces:
            for i in range(3):
                v1 = face[i]
                v2 = face[(i + 1) % 3]
                
                if v1 not in graph:
                    graph[v1] = set()
                graph[v1].add(v2)
                
                if v2 not in graph:
                    graph[v2] = set()
                graph[v2].add(v1)

        for key in graph:
            graph[key] = list(graph[key])
        
        return graph
    
    @staticmethod
    def build_participation_graph(faces):
        """
        keys: vertex indices
        values: list of face indices in which the vertex is involved.
        """
        vertex_face_dict = {}
        for f_idx, face in enumerate(faces):
            for vertex in face:
                vertex_face_dict.setdefault(vertex, set()).add(f_idx)
        return vertex_face_dict

    def most_isolated(self, v_indices, neighbors):
        connections = sorted([(len(neighbors[v]), v) for v in v_indices])
        return connections[0][1]

    def browse_hole(self, neighbors, ext_indices, hole):
        current = hole[0]
        while True:
            vns = neighbors[current]
            vns = [v for v in vns if (v in ext_indices) and (v not in hole)]
            if len(vns) == 0:
                break
            hole.append(self.most_isolated(vns, neighbors))
            current = hole[-1]
            if current == hole[0]:
                break

    def _process_n_holes(self, mesh, exterior_vertices):
        """
        Given the list of exterior vertices, this function computes the number of holes in the mesh.
        It consists in counting the number of connected vertices in the exterior vertices.
        We use the list of edges to find the connected components.
        The largest connected component is considered the perimeter of the mesh.

        Args:
            - mesh (open3d.geometry.TriangleMesh): The mesh to process.
            - exterior_vertices (np.array): A boolean array of the same size as the number of vertices in the mesh.
                                            It contains True for the vertices that are considered exterior.
        """
        print("Start")
        neighbors = self.build_neighborhood_graph(np.asarray(mesh.triangles))
        # List of vertices indices that are considered exterior.
        ext_indices = np.where(exterior_vertices)[0]
        holes = []
        used  = set()
        idx = 0
        hole = []
        while idx < len(ext_indices):
            current = ext_indices[idx]
            if current in used:
                idx += 1
                continue
            hole.append(current)
            self.browse_hole(neighbors, ext_indices, hole)
            holes.append(hole)
            used = used.union(set(hole))
            hole = []
            idx += 1
        return holes
    
    def process_n_holes(self):
        """
        Computes the number of holes in each mesh.
        """
        return [self._process_n_holes(m, e) for m, e in zip(self.meshes, self.get_exterior_vertices())]
    
    def _edge_loop_to_colors(self, mesh, holes):
        v_colors = np.zeros((len(mesh.vertices), 3), dtype=np.float32)
        v_colors += 0.75
        for i, hole in enumerate(holes):
            rdm_color = np.random.rand(3)
            for v_index in hole:
                v_colors[v_index] = rdm_color
        return v_colors

    def edge_loop_to_colors(self):
        """
        Returns the list of exterior vertices for each mesh.
        """
        self.vertices_colors = []
        all_holes = self.process_n_holes()
        for mesh, holes in zip(self.meshes, all_holes):
            v_colors = self._edge_loop_to_colors(mesh, holes)
            self.vertices_colors.append(v_colors)

    def exterior_vertices_to_colors(self):
        """
        Returns the list of exterior vertices for each mesh.
        """
        self.vertices_colors = []
        for mesh in self.meshes:
            vtcs = np.where(self._get_exterior_vertices(mesh))[0]
            colors = np.zeros((len(mesh.vertices), 3), dtype=np.float32)
            colors += 0.75
            colors[vtcs] = [1.0, 0.0, 0.0]
            self.vertices_colors.append(colors)
    
    def _discrete_angular_curvature(self, mesh):
        curvature = np.zeros(len(mesh.vertices))
        mesh.compute_vertex_normals()
        mesh.compute_triangle_normals()
        normals = np.asarray(mesh.triangle_normals)
        faces = np.asarray(mesh.triangles)
        normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)
        neighbors_dict = self.build_participation_graph(faces)
        v_normals = np.asarray(mesh.vertex_normals)
        v_normals = v_normals / np.linalg.norm(v_normals, axis=1, keepdims=True)
        for i, neighbors in neighbors_dict.items():
            if len(neighbors) < 2:
                continue
            # print(normals)
            normal_diffs = normals[list(neighbors)] - v_normals[i]
            norm_diffs = np.linalg.norm(normal_diffs, axis=1)
            curvature[i] = np.mean(norm_diffs) / math.sqrt(2)
        return curvature
    
    def discrete_angular_curvature(self):
        """
        Computes the discrete angular curvature for each mesh.
        """
        return [self._discrete_angular_curvature(m) for m in self.meshes]
    
    def angular_curvature_to_color(self):
        """
        Computes the angular curvature for each mesh and assigns a color to each vertex.
        """
        self.vertices_colors = []
        curvatures = self.discrete_angular_curvature()
        for mesh, curvature in zip(self.meshes, curvatures):
            colors = np.zeros((len(mesh.vertices), 3), dtype=np.float32)
            colors[:, 0] = curvature
            self.vertices_colors.append(colors / np.max(colors))

    def coordinates_to_color(self):
        """
        Assigns a color to each vertex based on its coordinates.
        """
        self.vertices_colors = []
        for mesh in self.meshes:
            colors = np.asarray(mesh.vertices)
            colors = colors - np.min(colors, axis=0)
            colors = colors / np.max(colors, axis=0)
            self.vertices_colors.append(colors)
                
    

###########################################################

def show_in_napari(acs):
    viewer = napari.Viewer()
    # Choosing coloration:
    # acs.exterior_vertices_to_colors()
    # acs.edge_loop_to_colors()
    # acs.angular_curvature_to_color()
    acs.coordinates_to_color()
    # -----------
    for i in range(len(acs.meshes)):
        mesh = acs.meshes[i]
        print(f"--- Adding mesh {i} ---")
        surface = viewer.add_surface(
            (np.asarray(mesh.vertices), np.asarray(mesh.triangles)),
            name="Astrocytes-" + str(i),
            shading='smooth'
        )
        surface.wireframe.visible = True
        colors = acs.vertices_colors[i]
        surface.vertex_colors = colors
        print("--")
    napari.run()


def run_workflow():
    acs = AstrocytesContactState()
    target_folder = "/home/benedetti/Downloads/I2K/data/astrocytes"
    target_path = os.path.join(target_folder, "contact-surface.ply")
    acs.open_mesh(target_path)
    acs.split_connected_components()
    acs.merge_close_vertices(0.1)
    acs.smooth_meshes(5)
    acs.flatten()
    acs.fill_holes()
    acs.smooth_meshes(5)
    acs.decimate(0.8)

    # Exporting mesh as PLY
    for i, m in enumerate(acs.meshes):
        o3d.io.write_triangle_mesh(f"/home/benedetti/Downloads/I2K/data/astrocytes/astrocytes-{i}.ply", m)

    # Counting holes
    # all_holes = acs.process_n_holes()
    # for holes in all_holes:
    #     print("Number of holes: ", len(holes))
    #     print(np.unique([len(hole) for hole in holes]))
    show_in_napari(acs)


def dump():
    acs = AstrocytesContactState()
    target_folder = "/home/benedetti/Downloads/I2K/data/"
    target_path = os.path.join(target_folder, "test-holes.ply")
    acs.open_mesh(target_path)
    
    all_holes = acs.process_n_holes()
    for holes in all_holes:
        print("Number of holes: ", len(holes))
        print(np.unique([len(hole) for hole in holes]))
        # for hole in holes:
        #     print("Hole size: ", len(hole))

if __name__ == "__main__":
    run_workflow()
    # show_in_napari(acs)