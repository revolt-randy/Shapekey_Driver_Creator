# ##### BEGIN GPL LICENSE BLOCK #####

#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Shapekey Driver Creator",
    "author": "Andreas Esau, revolt_randy",
    "version": (1, 2),
    "blender": (3, 6, 5),
    "location": "View3D - Pose mode > Pose Menu",
    "description": "This Operator creates a shape key driver for a bone with one single dialog operator. Quick and easy.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"}

import bpy
from math import radians,degrees
from mathutils import Vector,Quaternion,Euler


class ShapekeyDriverCreator(bpy.types.Operator):
    #"""This Operator creates a driver for a shape and connects it to a posebone transformation"""
    bl_idname = "object.shapekey_driver_creator"
    bl_label = "Shapekey Driver Creator"
    bl_description = "This Operator creates a driver for a shape and connects it to a posebone transformation"
    
    def shapes(self,context):
        shapes = []
        i=0
        
        object = bpy.context.selected_objects[0]
        shape_keys = None
        if object.data.shape_keys != None:
            shape_keys = object.data.shape_keys.key_blocks
              
        if shape_keys != None:
            for shape in shape_keys:
                if shape.relative_key != shape:
                    shapes.append((shape.name,shape.name,shape.name,'SHAPEKEY_DATA',i)) 
                    i+=1
        shapes.append(("CREATE_NEW_SHAPE","create new shape","create new shape",'NEW',i)) 
        
            
        return shapes
        
    get_limits_auto : bpy.props.BoolProperty(name = "Get Limits",default=True,description="This will set the limits based on the bone location/rotation/scale automatically.")
    shape_name : bpy.props.EnumProperty(items = shapes, name = "Shape", description="Select the shape you want to add a driver to.")
    
    type_values = []
    type_values.append(("LOC_X","X Location","X Location","None",0))
    type_values.append(("LOC_Y","Y Location","Y Location","None",1))
    type_values.append(("LOC_Z","Z Location","Z Location","None",2))
    type_values.append(("ROT_X","X Rotation","X Rotation","None",3))
    type_values.append(("ROT_Y","Y Rotation","Y Rotation","None",4))
    type_values.append(("ROT_Z","Z Rotation","Z Rotation","None",5))
    type_values.append(("SCALE_X","X Scale","X Scale","None",6))
    type_values.append(("SCALE_Y","Y Scale","Y Scale","None",7))
    type_values.append(("SCALE_Z","Z Scale","Z Scale","None",8))
    
    type : bpy.props.EnumProperty(name = "Type",items=type_values, description="Set the type you want to be used as input to drive the shapekey.")
        
    space_values = []
    space_values.append(("LOCAL_SPACE","Local Space","Local Space","None",0))
    space_values.append(("TRANSFORM_SPACE","Transform Space","Transform Space","None",1))
    space_values.append(("WORLD_SPACE","World Space","World Space","None",2))
    space : bpy.props.EnumProperty(name = "Space",items=space_values, description="Set the space the bone is transformed in. Local Space recommended.")
            
    min_value : bpy.props.FloatProperty(name = "Min Value",default=0.0, description="That value is used as 0.0 value for the shapekey.")
    max_value : bpy.props.FloatProperty(name = "Max Value",default=1.0, description="That value is used as 1.0 value for the shapekey.")
        
    add_constraint : bpy.props.BoolProperty(name = "Add Limit Constraint", default=False, description="This will add Limit Loc/Rot/Scale constraint on the bone automatically.")

    constraint_space_values = []
    constraint_space_values.append(("WORLD", "World Space", "World Space", "None", 0))
    constraint_space_values.append(("CUSTOM", "Custom Space", "Custom Space", "None", 1))
    constraint_space_values.append(("POSE", "Pose Space", "Pose Space", "None", 2))  
    constraint_space_values.append(("LOCAL_WITH_PARENT", "Local With Parent Space", "Local With Parent Space", "None", 3))
    constraint_space_values.append(("LOCAL", "Local Space", "Local Space", "None", 4))
    
    constraint_space : bpy.props.EnumProperty(name = "Constraint_Space", items=constraint_space_values, description="description text goes here" ) 

    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def set_defaults(self,context):
        bone = context.active_pose_bone
        ### set location
        if bone.location != Vector((0,0,0)):
            l = [abs(bone.location.x),abs(bone.location.y),abs(bone.location.z)]
            m = max(l)
            type = ["LOC_X","LOC_Y","LOC_Z"]
            
            for i,value in enumerate(l):
                if l[i] == m:
                    self.min_value = 0.0
                    self.max_value = bone.location[i]
                    self.type = type[i]        
            return
        
        ### set rotation
        bone_rotation = Euler()
        if bone.rotation_mode == "QUATERNION":
            bone_rotation = bone.rotation_quaternion.to_euler("XYZ")
        else:
            bone_rotation = bone.rotation_euler
        
        if Vector((bone_rotation.x,bone_rotation.y,bone_rotation.z)) != Vector((0,0,0)):
            l = [abs(bone_rotation.x),abs(bone_rotation.y),abs(bone_rotation.z)]
            m = max(l)
            type = ["ROT_X","ROT_Y","ROT_Z"]
            
            for i,value in enumerate(l):
                if l[i] == m:
                    self.min_value = 0.0
                    self.max_value = degrees(bone_rotation[i])
                    self.type = type[i]
            return
        
        ### set scale
        if bone.scale != Vector((1,1,1)):
            l = [abs(bone.location.x),abs(bone.location.y),abs(bone.location.z)]
            m = max(l)
            type = ["SCALE_X","SCALE_Y","SCALE_Z"]
            
            for i,value in enumerate(l):
                if l[i] == m:
                    self.min_value = 1.0
                    self.max_value = bone.scale[i]
                    self.type = type[i]
            return

    
    def create_new_shape(self,context,object):
        new_shape = object.shape_key_add(name=context.active_pose_bone.name,from_mix=False)
        return new_shape.name
    
    
    def adjust_limit_constraint(self, context, constraint):
        print("\n  adjuse_limit_constraint() - Started.")
        print("constraint type = ", constraint.type)
        
        print("self.type = ", self.type)
        
        if self.type == 'LOC_X':
            if constraint.use_min_x == False:
                constraint.min_x = self.min_value
                constraint.use_min_x = True
            else:
                if self.min_value < constraint.min_x:
                    constraint.min_x = self.min_value
            
            if constraint.use_max_x == False:
                constraint.max_x = self.max_value
                constraint.use_max_x = True
            else:
                if self.max_value > constraint.max_x:
                    constraint.max_x = self.max_value
                elif self.max_value < constraint.min_x:
                    constraint.min_x = self.max_value
                            
        elif self.type == 'LOC_Y':
            if constraint.use_min_y == False:
                constraint.min_y = self.min_value
                constraint.use_min_y = True
            else:
                if self.min_value < constraint.min_y:
                    constraint.min_y = self.min_value
            
            if constraint.use_max_y == False:
                constraint.max_y = self.max_value
                constraint.use_max_y = True
            else:
                if self.max_value > constraint.max_y:
                    constraint.max_y = self.max_value
                elif self.max_value < constraint.min_y:
                    constraint.min_y = self.max_value
                    
        elif self.type == 'LOC_Z':
            if constraint.use_min_z == False:
                constraint.min_z = self.min_value
                constraint.use_min_z = True
            else:
                if self.min_value < constraint.min_z:
                    constraint.min_z = self.min_value
            
            if constraint.use_max_z == False:
                constraint.max_z = self.max_value
                constraint.use_max_z = True
            else:
                if self.max_value > constraint.max_z:
                    constraint.max_z = self.max_value
                elif self.max_value < constraint.min_z:
                    constraint.min_z = self.max_value
                    
        elif self.type == "ROT_X":
            if constraint.use_limit_x == False:
                constraint.use_limit_x = True
                
            if radians(self.min_value) < constraint.min_x:
                constraint.min_x = radians(self.min_value)
            if radians(self.max_value) > constraint.max_x:
                constraint.max_x = radians(self.max_value) 
            elif radians(self.max_value) < constraint.min_x:
                constraint.min_x = radians(self.max_value)
                
            
        elif self.type == "ROT_Y":
            if constraint.use_limit_y == False:
                constraint.use_limit_y = True
                
            if radians(self.min_value) < constraint.min_y:
                constraint.min_y = radians(self.min_value)
            if radians(self.max_value) > constraint.max_y:
                constraint.max_y = radians(self.max_value)
            elif radians(self.max_value) < constraint.min_y:
                constraint.min_y = radians(self.max_value)
        
        elif self.type == "ROT_Z":
            if constraint.use_limit_z == False:
                constraint.use_limit_z = True
                
            if radians(self.min_value) < constraint.min_z:
                constraint.min_z = radians(self.min_value)
            if radians(self.max_value) > constraint.max_z:
                constraint.max_z = radians(self.max_value)
            elif radians(self.max_value) < constraint.min_z:
                constraint.min_z = radians(self.max_value)
        
        elif self.type == "SCALE_X":
            if constraint.use_min_x == False:
                constraint.min_x = self.min_value
                constraint.use_min_x = True
            else:
                if self.min_value < constraint.min_x:
                    constraint.min_x = self.min_value
            
            if constraint.use_max_x == False:
                constraint.max_x = self.max_value
                constraint.use_max_x = True
            else:
                if self.max_value > constraint.max_x:
                    constraint.max_x = self.max_value
        
        elif self.type == 'SCALE_Y':         
            if constraint.use_min_y == False:
                constraint.min_y = self.min_value
                constraint.use_min_y = True
            else:
                if self.min_value < constraint.min_y:
                    constraint.min_y = self.min_value
            
            if constraint.use_max_y == False:
                constraint.max_y = self.max_value
                constraint.use_max_y = True
            else:
                if self.max_value > constraint.max_y:
                    constraint.max_y = self.max_value
            
        
        elif self.type == 'SCALE_Z':
            if constraint.use_min_z == False:
                constraint.min_z = self.min_value
                constraint.use_min_z = True
            else:
                if self.min_value < constraint.min_z:
                    constraint.min_z = self.min_value
            
            if constraint.use_max_z == False:
                constraint.max_z = self.max_value
                constraint.use_max_z = True
            else:
                if self.max_value > constraint.max_z:
                    constraint.max_z = self.max_value  
            
        constraint.owner_space = self.constraint_space
        
        return
    

    def add_bone_limit_constraint(self, context, type):
        bone = context.active_pose_bone
        
        if "LOC" in self.type:
            constraint = bone.constraints.new("LIMIT_LOCATION")
        elif "ROT" in self.type:
            constraint = bone.constraints.new("LIMIT_ROTATION")            
        else:
            constraint = bone.constraints.new("LIMIT_SCALE")
            
        self.adjust_limit_constraint(context, constraint)
        
        return


    def add_limit_constraint(self, context):
        bone = context.active_pose_bone
        
        if len(bone.constraints) == 0:
            self.add_bone_limit_constraint(context, type)
        else:
            for constraint in bone.constraints:
                                
                if "LIMIT_LOCATION" in constraint.type :
                    if "LOC" in self.type:
                        self.adjust_limit_constraint(context, constraint)
                        return
                elif "LIMIT_ROTATION" in constraint.type:
                    if "ROT" in self.type:
                        self.adjust_limit_constraint(context, constraint)
                        return
                elif "LIMIT_SCALE" in constraint.type:
                    if "SCALE" in self.type:
                        self.adjust_limit_constraint(context, constraint)
                        return

            self.add_bone_limit_constraint(context, type)
        
        return    
    
    
    def execute(self, context):
        wm = context.window_manager
        object = bpy.context.selected_objects[0]
        shape = None
        if self.shape_name != "CREATE_NEW_SHAPE":
            shape = object.data.shape_keys.key_blocks[self.shape_name]
        else:
            if object.data.shape_keys == None:
                object.shape_key_add(name="Basis",from_mix=False)
            shape = object.data.shape_keys.key_blocks[self.create_new_shape(context,object)]
        
        curve = shape.driver_add("value")
        
        if len(curve.driver.variables) < 1:
            curve_var = curve.driver.variables.new()
        else:
            curve_var = curve.driver.variables[0]
        
        if len(curve.modifiers) > 0:
            curve.modifiers.remove(curve.modifiers[0])
            
        curve.driver.type = "SUM"
        curve_var.type = "TRANSFORMS"
        curve_var.targets[0].id = bpy.context.active_object
        curve_var.targets[0].bone_target = bpy.context.active_pose_bone.name
        curve_var.targets[0].transform_space = self.space
        curve_var.targets[0].transform_type = self.type
        
        if self.type in ["ROT_X","ROT_Y","ROT_Z"]:
            min_value = radians(self.min_value)
            max_value = radians(self.max_value)
        else:
            min_value = self.min_value
            max_value = self.max_value
        
        delete_len = 0
        for point in curve.keyframe_points:
            delete_len += 1
        for i in range(delete_len):    
            curve.keyframe_points.remove(curve.keyframe_points[0])
        
        point_a = curve.keyframe_points.insert(min_value,0)
        point_a.interpolation = "LINEAR"
        
        point_b = curve.keyframe_points.insert(max_value,1.0)
        point_b.interpolation = "LINEAR"
        
        if self.add_constraint:
            self.add_limit_constraint(context)
            
        
        msg = "Shape Key: "+ self.shape_name +" driver to Bone: " + context.active_pose_bone.name
        self.report({'INFO'},msg)
        return {'FINISHED'}
    
            
    def invoke(self, context, event):
        wm = context.window_manager 
                
        if len(context.selected_objects) != 2:
            self.report({'WARNING'},'Select a Mesh Object and then a Pose Bone')
            return{'FINISHED'}
        
        if context.selected_objects[1].type != "ARMATURE":
            self.report({'WARNING'},'Select a Mesh Object and then a Pose Bone')
            return{'FINISHED'}
        
        if context.selected_objects[0].type != "MESH":
            self.report({'WARNING'},'Select a Mesh Object and then a Pose Bone')
            return{'FINISHED'}
        
        if context.active_pose_bone == None:
            self.report({'WARNING'},'Select a Mesh Object and then a Pose Bone')
            return{'FINISHED'}
        
        if self.get_limits_auto:
            self.set_defaults(context)

        return wm.invoke_props_dialog(self)


def add_to_specials(self,context):
    if len(bpy.context.selected_objects) > 1:
        if bpy.context.selected_objects[0].type == "MESH":
            self.layout.operator_context = "INVOKE_DEFAULT"
            self.layout.separator()
            op = self.layout.operator("object.shapekey_driver_creator",text="Shapekey Driver Creator",icon="DRIVER")


def add_pose_menu(self,context):
    if len(bpy.context.selected_objects) > 1:
        if bpy.context.selected_objects[0].type == "MESH":
            self.layout.operator_context = "INVOKE_DEFAULT"
            self.layout.separator()
            op = self.layout.operator("object.shapekey_driver_creator",text="Shapekey Driver Creator",icon="DRIVER")
    
    
def register():
    bpy.types.VIEW3D_MT_pose_context_menu.append(add_to_specials)
    bpy.types.VIEW3D_MT_pose.append(add_pose_menu)  
    bpy.utils.register_class(ShapekeyDriverCreator)


def unregister():
    bpy.types.VIEW3D_MT_pose_context_menu.remove(add_to_specials)
    bpy.types.VIEW3D_MT_pose.remove(add_pose_menu)            
    bpy.utils.unregister_class(ShapekeyDriverCreator)


if __name__ == "__main__":
    register()


# change log - 9/1/24 -
# - got initial functionality working...
#   - changed property assignments to use ':' instead of '='
#   - fixed 'pose context menu'
#   - need to fix VIEW3D_PT_tools_posemode menu - see note above - fixed 9/3/24
#   - fixed order of context.selected_objects - think it previously was ordered by the order of 
#       selecting the objects. Now it appears to be ordered such as mesh objects is first. Double
#       check this and test code in def invoke(self, context, event) function.
#   - minor testing of functionality
#
# - 9/3/24 -
#   - removed all wording releated to 'constraint' - to avoid confusion with blender constraints
#   - renamed add on to 'Shapekey Driver Creator' 
#
# - 9/9/24 -
#   - worked on 'Add Limit Constraint' feature -
#       this feature will add a limit loc/rot/scale constraint to the bone, limiting transforms
#       of the bone to the settings used to drive the shapekey
#
# - 9/30/24 -
#   - tidy up the code and changed version to 1.2
#


