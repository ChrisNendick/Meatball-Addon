import bpy
import random
import mathutils

# Basic information about the add-on
bl_info = {
    'name': 'Meatball Generator',
    'category': 'Side Menu',
    'version': (1, 0, 0),
    'blender': (4, 0, 0),
    'location': "Side Menu; Shortcut: N",
    'author': 'Chris Nendick',
    'description': "Generates random Meatball meshes",
}

#keeps track of existing meatballs
existing_meatballs = []

def generate_meatball_mesh(size, offset, distortion_factor=0.1, subdivisions=32):
    #Create a sphere for the meatball
    bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=offset, segments=subdivisions, ring_count=subdivisions)
    sphere_obj = bpy.context.active_object  # Get the newly created object

    #Apply random displacement to each vertex to create a distorted effect
    for vert in sphere_obj.data.vertices:
        displacement = mathutils.Vector((random.uniform(-distortion_factor, distortion_factor),
                                         random.uniform(-distortion_factor, distortion_factor),
                                         random.uniform(-distortion_factor, distortion_factor)))
        vert.co += displacement  #Update vertex position with displacement

    #Add a Subdivision Surface modifier to smooth the mesh
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = 2  
    bpy.ops.object.modifier_apply(modifier="Subdivision")  

    return sphere_obj.data  

def generate_custom_mesh(mesh):
    #Create a new object with the generated mesh and link it to the current collection
    custom_obj = bpy.data.objects.new("CustomMeatBall", mesh)
    bpy.context.collection.objects.link(custom_obj)

class OBJECT_OT_GenerateRandomMeatBall(bpy.types.Operator):
    bl_idname = "mesh.generate_random_meatball"
    bl_label = "Generate MeatBall"

    def execute(self, context):
        global existing_meatballs

        #Remove existing meatballs from the scene
        for meatball in existing_meatballs:
            bpy.data.objects.remove(meatball, do_unlink=True)
        existing_meatballs.clear()  

        #Generate a random size and a valid offset for the new meatball
        size = random.uniform(1.0, 3.0)  # Random size between 1 and 3
        offset = self.get_valid_offset()  # Get a non-colliding position
        meatball_mesh = generate_meatball_mesh(size, offset, distortion_factor=0.1)  # Generate the meatball mesh
        generate_custom_mesh(meatball_mesh) 
        
        return {'FINISHED'}

    def get_valid_offset(self):
        #Generate a random position within specified limits
        offset = (random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0))
        
        #Collision Control
        while self.check_collision(offset):
            offset = (random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0))
        return offset 

    def check_collision(self, offset):
        #Checks Collisions
        for meatball in existing_meatballs:
            #Calculate distance to existing meatballs
            distance = (meatball.location - mathutils.Vector(offset)).length  
            #Check if distance is less than the sum of scales (adjustable)
            if distance < (meatball.scale.x + 3.0):  
                return True  # Collision detected
        return False 

class OBJECT_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Custom Panel"  
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = 'VIEW_3D'  
    bl_region_type = 'UI'  
    bl_category = "MeatBall Tool :)"  
    bl_context = "objectmode"  

    def draw(self, context):
        layout = self.layout 

        # Create a button to generate a meatball
        row = layout.row()
        row.operator("mesh.generate_random_meatball", text="Generate MeatBall!")

def register():
    # Register the custom panel and operator
    bpy.utils.register_class(OBJECT_PT_CustomPanel)
    bpy.utils.register_class(OBJECT_OT_GenerateRandomMeatBall)

def unregister():
    # Unregister the custom panel and operator
    bpy.utils.unregister_class(OBJECT_PT_CustomPanel)
    bpy.utils.unregister_class(OBJECT_OT_GenerateRandomMeatBall)

if __name__ == "__main__":
    register()  
