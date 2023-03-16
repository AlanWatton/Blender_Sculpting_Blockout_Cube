bl_info = {
    "name": "SculptingBlockoutCube",
    "author": "Alan Watton",
    "version": (1, 0),
    "blender": (3 , 4, 0),
    "location": "View3D > Add & View3D > Context",
    "description": "Adds Blockout Cube to Context Menu",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Operator, AddonPreferences
from bpy.props import (
    FloatProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatVectorProperty
)
import random

### Preferences ###
class BlockoutCubeAddonPreferences(AddonPreferences):    
    bl_idname = __name__
    
    default_blockout_cube_size: FloatProperty(
        name="Default Size (Meters)",
        min=0.001, max=100.0,
        default=0.3
    )
    
    adjust_size_for_subdivided_mesh: BoolProperty(
        name="Adjust Size for Subdivisions",
        default=True
    )
    
    default_blockout_cube_subdivisions: IntProperty(
        name="Default Subdivisions",
        min=1, max=10,
        default=3
    )
    
    auto_disable_optimal_display: BoolProperty(
        name="Disable Optimal Display On Subdivision Modifier",
        default=True
    )
    

    def draw(self, context):
        
        layout = self.layout
        layout.use_property_split = True
        
        layout.label(text="Blockout Cube Options")
        layout.prop(self, "default_blockout_cube_size")
        layout.prop(self, "adjust_size_for_subdivided_mesh")
        
        layout.row()
        layout.row()
        
        layout.prop(self, "default_blockout_cube_subdivisions")
        layout.prop(self, "auto_disable_optimal_display")
        
        layout.row()
        layout.row()
        
        layout.label(text="*Changes Require Restart")
        
      

# Register the Preferences now so they can be referenced in the Operator
register_class(BlockoutCubeAddonPreferences)

### Blockout Cube Operator ###
class BlockoutCubeOperator(Operator):
    """Construct a blockout cube mesh"""
    bl_idname = "blockoutcube.1"
    bl_label = "Blockout Cube"
    bl_options = {'REGISTER', 'UNDO'}

    size: FloatProperty(
        name="Size",
        description="Default(2.0) Range(0.01-100.0)",
        min=0.01, max=100.0,
        default=bpy.context.preferences.addons[__name__].preferences.default_blockout_cube_size
    )
    
    adjust_size: BoolProperty(
        name="Subdivided Mesh Size",
        default=bpy.context.preferences.addons[__name__].preferences.adjust_size_for_subdivided_mesh
    ) 
    
    subdivisions: IntProperty(
        name="Subdivisions",
        description="Default(3) Range[1-10]",
        min=1, max=10,
        default=bpy.context.preferences.addons[__name__].preferences.default_blockout_cube_subdivisions
    ) 
    
    optimal_display: BoolProperty(
        name="Optimal Display",
        default= not bpy.context.preferences.addons[__name__].preferences.auto_disable_optimal_display
    ) 
        
    generate_uvs: BoolProperty(
        name="Generate UVs",
        description="Generate default UV map",
        default=True,
    )
    
    location: FloatVectorProperty(
        name="Location",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0),
        size=3,
        options={'SKIP_SAVE'}
    )
    
    rotation: FloatVectorProperty(
        name="Rotation",
        subtype="EULER",
        default=(0.0, 0.0, 0.0),
        size=3,
        options={'SKIP_SAVE'}
    )
    
    color_set = False
    color = (0,0,0)
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        layout.prop(self, "size", text="Size")
        layout.prop(self, "adjust_size", text="Subdivided Mesh Size")
        
        layout.separator()
        layout.separator()
        
        layout.prop(self, "subdivisions", text="Subdivisions")
        layout.prop(self, "optimal_display", text="Optimal Display")
        
        layout.separator()
        layout.separator()
        
        layout.prop(self, "generate_uvs", text="Generate UVs")
        layout.prop(self, "location", text="Location")
        layout.prop(self, "rotation", text="Rotation")
        
    
    def execute(self, context):
        # Update Size
        size = self.size
        
        if self.adjust_size:
            size += (self.size * 0.157079632679) # Correct size with pi/2 for every unit of size
        
        # Spawn Object
        bpy.ops.mesh.primitive_cube_add(calc_uvs=self.generate_uvs, size=size, enter_editmode=False, rotation=self.rotation, location=self.location)
        bpy.ops.object.subdivision_set(level=self.subdivisions, relative=False)
        bpy.context.object.modifiers["Subdivision"].show_only_control_edges = self.optimal_display
        
        # Set a Unique Name so it is assigned a unique color for the Random mode in Viewport Shading 
        blockout_cubes_count = len(set(o.data.name for o in context.scene.objects if o.type == 'MESH' and "Blockout Cube" in o.name))
        blockout_cube_number = "{:0>3}".format(blockout_cubes_count) if blockout_cubes_count > 0 else ""
        bpy.context.object.name = "Blockout Cube." + blockout_cube_number

        self.report({'OPERATOR'}, "Added " + bpy.context.object.name)
        
        return {'FINISHED'}
    
  

### Menu Creation Funcs ###
def add_menu_func(self, context):
    self.layout.operator(BlockoutCubeOperator.bl_idname, text="Blockout Cube Mesh", icon='OUTLINER_OB_MESH')
       
       
def register():
    # Register Operator
    register_class(BlockoutCubeOperator)
    
    # Add Menu Entries
    bpy.types.VIEW3D_MT_mesh_add.append(add_menu_func)
    
    
def unregister():
    # Unregister both Preferences and Operator
    unregister_class(BlockoutCubeAddonPreferences)
    unregister_class(BlockoutCubeOperator)
        
    # Remove Menu Entries
    bpy.types.VIEW3D_MT_mesh_add.remove(add_menu_func)


if __name__ == "__main__":
    register()

