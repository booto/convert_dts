from cffi import FFI

ffi = FFI()

ffi.set_source("_lib3ds",
  """
  #include <lib3ds/atmosphere.h>
  #include <lib3ds/background.h>
  #include <lib3ds/camera.h>
  #include <lib3ds/chunk.h>
  #include <lib3ds/ease.h>
  #include <lib3ds/file.h>
  #include <lib3ds/io.h>
  #include <lib3ds/light.h>
  #include <lib3ds/material.h>
  #include <lib3ds/matrix.h>
  #include <lib3ds/mesh.h>
  #include <lib3ds/node.h>
  #include <lib3ds/quat.h>
  #include <lib3ds/shadow.h>
  #include <lib3ds/tcb.h>
  #include <lib3ds/tracks.h>
  #include <lib3ds/types.h>
  #include <lib3ds/vector.h>
  #include <lib3ds/viewport.h>
  """,
  libraries=['3ds'])


ffi.cdef("""
typedef int32_t Lib3dsBool;
typedef uint8_t Lib3dsByte;
typedef uint16_t Lib3dsWord;
typedef uint32_t Lib3dsDword;
typedef int8_t Lib3dsIntb;
typedef int16_t Lib3dsIntw;
typedef int32_t Lib3dsIntd;

typedef float Lib3dsFloat;
typedef double Lib3dsDouble;

typedef float Lib3dsVector[3];
typedef float Lib3dsTexel[2];
typedef float Lib3dsQuat[4];
typedef float Lib3dsMatrix[4][4];
typedef float Lib3dsRgb[3];
typedef float Lib3dsRgba[4];

typedef struct Lib3dsIo Lib3dsIo;
typedef struct Lib3dsFile Lib3dsFile;
typedef struct Lib3dsBackground Lib3dsBackground;
typedef struct Lib3dsAtmosphere Lib3dsAtmosphere;
typedef struct Lib3dsShadow Lib3dsShadow;
typedef struct Lib3dsViewport Lib3dsViewport;
typedef struct Lib3dsMaterial Lib3dsMaterial;
typedef struct Lib3dsFace Lib3dsFace; 
typedef struct Lib3dsBoxMap Lib3dsBoxMap; 
typedef struct Lib3dsMapData Lib3dsMapData; 
typedef struct Lib3dsMesh Lib3dsMesh;
typedef struct Lib3dsCamera Lib3dsCamera;
typedef struct Lib3dsLight Lib3dsLight;
typedef struct Lib3dsBoolKey Lib3dsBoolKey;
typedef struct Lib3dsBoolTrack Lib3dsBoolTrack;
typedef struct Lib3dsLin1Key Lib3dsLin1Key;
typedef struct Lib3dsLin1Track Lib3dsLin1Track;
typedef struct Lib3dsLin3Key Lib3dsLin3Key;
typedef struct Lib3dsLin3Track Lib3dsLin3Track;
typedef struct Lib3dsQuatKey Lib3dsQuatKey;
typedef struct Lib3dsQuatTrack Lib3dsQuatTrack;
typedef struct Lib3dsMorphKey Lib3dsMorphKey;
typedef struct Lib3dsMorphTrack Lib3dsMorphTrack;
typedef struct Lib3dsNode Lib3dsNode;

typedef struct Lib3dsPoint {
    Lib3dsVector pos;
} Lib3dsPoint;

typedef union Lib3dsUserData {
    void *p;
    Lib3dsIntd i;
    Lib3dsDword d;
    Lib3dsFloat f;
    Lib3dsMaterial *material;
    Lib3dsMesh *mesh;
    Lib3dsCamera *camera;
    Lib3dsLight *light;
    Lib3dsNode *node;
} Lib3dsUserData;

struct Lib3dsFace {
    Lib3dsUserData user;	/*! Arbitrary user data */
    char material[64];		/*! Material name */
    Lib3dsWord points[3];	/*! Indices into mesh points list */
    Lib3dsWord flags;		/*! See Lib3dsFaceFlag, below */
    Lib3dsDword smoothing;	/*! Bitmask; each bit identifies a group */
    Lib3dsVector normal;
};

struct Lib3dsBoxMap {
    char front[64];
    char back[64];
    char left[64];
    char right[64];
    char top[64];
    char bottom[64];
};

struct Lib3dsMapData {
    Lib3dsWord maptype;
    Lib3dsVector pos;
    Lib3dsMatrix matrix;
    Lib3dsFloat scale;
    Lib3dsFloat tile[2];
    Lib3dsFloat planar_size[2];
    Lib3dsFloat cylinder_height;
};


struct Lib3dsMesh {
    Lib3dsUserData user;    	/*< Arbitrary user data */
    Lib3dsMesh *next;
    char name[64];		        /*< Mesh name. Don't use more than 8 characters  */
    Lib3dsDword object_flags; /*< @see Lib3dsObjectFlags */ 
    Lib3dsByte color;
    Lib3dsMatrix matrix;    	/*< Transformation matrix for mesh data */
    Lib3dsDword points;		    /*< Number of points in point list */
    Lib3dsPoint *pointL;	    /*< Point list */
    Lib3dsDword flags;		    /*< Number of flags in per-point flags list */
    Lib3dsWord *flagL;		    /*< Per-point flags list */
    Lib3dsDword texels;		    /*< Number of U-V texture coordinates */
    Lib3dsTexel *texelL;	    /*< U-V texture coordinates */
    Lib3dsDword faces;	    	/*< Number of faces in face list */
    Lib3dsFace *faceL;		    /*< Face list */
    Lib3dsBoxMap box_map;
    Lib3dsMapData map_data;
}; 

extern Lib3dsMesh* lib3ds_mesh_new(const char *name);
extern void lib3ds_mesh_free(Lib3dsMesh *mesh);
extern Lib3dsBool lib3ds_mesh_new_point_list(Lib3dsMesh *mesh, Lib3dsDword points);
extern void lib3ds_mesh_free_point_list(Lib3dsMesh *mesh);
extern Lib3dsBool lib3ds_mesh_new_face_list(Lib3dsMesh *mesh, Lib3dsDword flags);
extern void lib3ds_mesh_free_face_list(Lib3dsMesh *mesh);

struct Lib3dsFile {
    Lib3dsDword mesh_version;
    Lib3dsWord keyf_revision;
    char name[13];
    Lib3dsFloat master_scale;
    Lib3dsVector construction_plane;
    Lib3dsRgb ambient;
    Lib3dsShadow shadow;
    Lib3dsBackground background;
    Lib3dsAtmosphere atmosphere;
    Lib3dsViewport viewport;
    Lib3dsViewport viewport_keyf;
    Lib3dsIntd frames;
    Lib3dsIntd segment_from;
    Lib3dsIntd segment_to;
    Lib3dsIntd current_frame;
    Lib3dsMaterial *materials;
    Lib3dsMesh *meshes;
    Lib3dsCamera *cameras;
    Lib3dsLight *lights;
    Lib3dsNode *nodes;
}; 

extern Lib3dsFile* lib3ds_file_load(const char *filename);
extern Lib3dsBool lib3ds_file_save(Lib3dsFile *file, const char *filename);
extern Lib3dsFile* lib3ds_file_new();
extern void lib3ds_file_free(Lib3dsFile *file);
extern void lib3ds_file_insert_mesh(Lib3dsFile *file, Lib3dsMesh *mesh);
extern void lib3ds_file_remove_mesh(Lib3dsFile *file, Lib3dsMesh *mesh);

extern void lib3ds_matrix_zero(Lib3dsMatrix m);
extern void lib3ds_matrix_identity(Lib3dsMatrix m);
extern void lib3ds_matrix_copy(Lib3dsMatrix dest, Lib3dsMatrix src);
extern void lib3ds_matrix_neg(Lib3dsMatrix m);
extern void lib3ds_matrix_abs(Lib3dsMatrix m);
extern void lib3ds_matrix_transpose(Lib3dsMatrix m);
extern void _lib3ds_matrix_add(Lib3dsMatrix m, Lib3dsMatrix a, Lib3dsMatrix b);
extern void _lib3ds_matrix_sub(Lib3dsMatrix m, Lib3dsMatrix a, Lib3dsMatrix b);
extern void lib3ds_matrix_mult(Lib3dsMatrix m, Lib3dsMatrix n);
extern void lib3ds_matrix_scalar(Lib3dsMatrix m, Lib3dsFloat k);
extern Lib3dsFloat lib3ds_matrix_det(Lib3dsMatrix m);
extern void lib3ds_matrix_adjoint(Lib3dsMatrix m);
extern Lib3dsBool lib3ds_matrix_inv(Lib3dsMatrix m);
extern void lib3ds_matrix_translate_xyz(Lib3dsMatrix m, Lib3dsFloat x, Lib3dsFloat y, Lib3dsFloat z);
extern void lib3ds_matrix_translate(Lib3dsMatrix m, Lib3dsVector t);
extern void lib3ds_matrix_scale_xyz(Lib3dsMatrix m, Lib3dsFloat x, Lib3dsFloat y, Lib3dsFloat z);
extern void lib3ds_matrix_scale(Lib3dsMatrix m, Lib3dsVector s);
extern void lib3ds_matrix_rotate_x(Lib3dsMatrix m, Lib3dsFloat phi);
extern void lib3ds_matrix_rotate_y(Lib3dsMatrix m, Lib3dsFloat phi);
extern void lib3ds_matrix_rotate_z(Lib3dsMatrix m, Lib3dsFloat phi);
extern void lib3ds_matrix_rotate(Lib3dsMatrix m, Lib3dsQuat q);
extern void lib3ds_matrix_rotate_axis(Lib3dsMatrix m, Lib3dsVector axis, Lib3dsFloat angle);
extern void lib3ds_matrix_camera(Lib3dsMatrix matrix, Lib3dsVector pos, Lib3dsVector tgt, Lib3dsFloat roll);
extern void lib3ds_matrix_dump(Lib3dsMatrix matrix);

extern void lib3ds_vector_zero(Lib3dsVector c);
extern void lib3ds_vector_copy(Lib3dsVector dest, Lib3dsVector src);
extern void lib3ds_vector_neg(Lib3dsVector c);
extern void lib3ds_vector_add(Lib3dsVector c, Lib3dsVector a, Lib3dsVector b);
extern void lib3ds_vector_sub(Lib3dsVector c, Lib3dsVector a, Lib3dsVector b);
extern void lib3ds_vector_scalar(Lib3dsVector c, Lib3dsFloat k);
extern void lib3ds_vector_cross(Lib3dsVector c, Lib3dsVector a, Lib3dsVector b);
extern Lib3dsFloat lib3ds_vector_dot(Lib3dsVector a, Lib3dsVector b);
extern Lib3dsFloat lib3ds_vector_squared(Lib3dsVector c);
extern Lib3dsFloat lib3ds_vector_length(Lib3dsVector c);
extern void lib3ds_vector_normalize(Lib3dsVector c);
extern void lib3ds_vector_normal(Lib3dsVector n, Lib3dsVector a,
  Lib3dsVector b, Lib3dsVector c);
extern void lib3ds_vector_transform(Lib3dsVector c, Lib3dsMatrix m, Lib3dsVector a);
extern void lib3ds_vector_cubic(Lib3dsVector c, Lib3dsVector a, Lib3dsVector p,
  Lib3dsVector q, Lib3dsVector b, Lib3dsFloat t);
extern void lib3ds_vector_min(Lib3dsVector c, Lib3dsVector a);
extern void lib3ds_vector_max(Lib3dsVector c, Lib3dsVector a);
extern void lib3ds_vector_dump(Lib3dsVector c);



""")

if __name__ == "__main__":
    ffi.compile()
