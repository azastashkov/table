"""Build the oak table in Blender from the sketch (1.jpg) and photos (2-6.jpg).

Run:  blender --background --python build_table.py
Output: table.blend (textures packed) in this directory.

Dimensions (cm) from the sketch: top length 180, leg frames inset 21 from each
end, leg members 9 wide, 120 clear between the frames. Overall 180 x 90 x 79;
all frame members and slats are 90x45 stock, the top is 45 thick.
"""
import os
import bpy
import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(HERE, "textures")

# --- dimensions (metres) ---------------------------------------------------
TOP_L, TOP_W, TOP_T = 1.80, 0.90, 0.045
HEIGHT = 0.79                       # floor to top surface
END_INSET = 0.21                    # sketch: 21
MEMBER = 0.09                       # sketch: 9 (frame thickness along length)
FRAME_SIDE_INSET = 0.06             # frame inset from the long edges
FRAME_FACE = 0.045                  # in-plane width of posts / rails (90x45 stock)
STRETCHER_W, STRETCHER_H = 0.09, 0.045   # 90x45 laid flat on the floor
APRON_W, APRON_H = 0.09, 0.045      # 4.jpg: two 90x45 slats laid flat under the top
APRON_Y = 0.20                      # slat centre distance from the long axis
BEVEL = 0.003

FRAME_H = HEIGHT - TOP_T
FRAME_X = TOP_L / 2 - END_INSET - MEMBER / 2   # frame centre along X
FRAME_Y = TOP_W / 2 - FRAME_SIDE_INSET          # half outer span along Y


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"


def make_material(name, image_path, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Coat Weight"].default_value = 0.25   # oiled / lacquered finish
    bsdf.inputs["Coat Roughness"].default_value = 0.15

    img = bpy.data.images.load(image_path)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "REPEAT"
    tex.location = (-600, 200)
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

    # Grain bump from the texture's luminance.
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.15
    bump.inputs["Distance"].default_value = 0.0005
    bump.location = (-250, -200)
    links.new(tex.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def add_box(name, size, location, material, uv_fn):
    """Axis-aligned box; uv_fn(world_co, face_normal) -> (u, v)."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    uv = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        for loop in face.loops:
            co = loop.vert.co + obj.location
            loop[uv].uv = uv_fn(co, face.normal)
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(material)
    for p in mesh.polygons:
        p.use_smooth = False
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = BEVEL
    mod.segments = 2
    mod.limit_method = "ANGLE"
    return obj


def top_uv(co, n):
    # Whole tabletop image spans the top surface; edges reuse the nearby strip.
    u = (co.x + TOP_L / 2) / TOP_L
    v = (co.y + TOP_W / 2) / TOP_W
    if abs(n.x) > 0.5:      # end grain faces: map Y across, Z along a thin strip
        u = (co.z - HEIGHT) / TOP_L + (0.0 if n.x < 0 else 1.0)
    elif abs(n.y) > 0.5:    # long edges
        v = (co.z - HEIGHT) / TOP_W + (0.0 if n.y < 0 else 1.0)
    return (u, v)


def grain_uv(axis, tile_w=0.15, tile_l=0.75, offset=(0.0, 0.0)):
    """Leg texture with the grain (image V) running along `axis`."""
    others = [a for a in "xyz" if a != axis]

    def fn(co, n):
        along = getattr(co, axis)
        # pick the cross axis that lies in this face
        normal_axis = "xyz"[max(range(3), key=lambda i: abs(n[i]))]
        cross = others[0] if others[0] != normal_axis else others[1]
        if normal_axis == axis:      # end grain: just use the two others
            along = getattr(co, others[1])
            cross = others[0]
        return (getattr(co, cross) / tile_w + offset[0],
                along / tile_l + offset[1])
    return fn


def build():
    reset_scene()
    top_mat = make_material("Oak_Top", os.path.join(TEX_DIR, "tabletop_oak.png"), 0.35)
    leg_mat = make_material("Oak_Legs", os.path.join(TEX_DIR, "leg_oak.png"), 0.4)

    parts = [add_box("Tabletop", (TOP_L, TOP_W, TOP_T),
                     (0, 0, HEIGHT - TOP_T / 2), top_mat, top_uv)]

    for i, sx in enumerate((-1, 1)):
        x = sx * FRAME_X
        side = "L" if sx < 0 else "R"
        # Both posts run from the floor to the tabletop; the top and bottom
        # rails sit between them.
        for j, sy in enumerate((-1, 1)):
            y = sy * (FRAME_Y - FRAME_FACE / 2)
            parts.append(add_box(f"Post_{side}{j}", (MEMBER, FRAME_FACE, FRAME_H),
                                 (x, y, FRAME_H / 2), leg_mat,
                                 grain_uv("z", offset=(0.3 * i + 0.5 * j, 0.17 * j))))
        for k, z in enumerate((FRAME_H - FRAME_FACE / 2, FRAME_FACE / 2)):
            parts.append(add_box(f"Rail_{side}{'TB'[k]}", (MEMBER, 2 * (FRAME_Y - FRAME_FACE), FRAME_FACE),
                                 (x, 0, z), leg_mat,
                                 grain_uv("y", offset=(0.4 * k + 0.2 * i, 0.3 * k))))

    inner = FRAME_X - MEMBER / 2
    # Reinforcing slats laid flat against the underside of the top, between the
    # frames' top rails, set in towards the centre of the table.
    for j, sy in enumerate((-1, 1)):
        parts.append(add_box(f"Apron_{j}", (2 * inner, APRON_W, APRON_H),
                             (0, sy * APRON_Y, FRAME_H - APRON_H / 2),
                             leg_mat, grain_uv("x", offset=(0.25 + 0.4 * j, 0.5))))
    parts.append(add_box("Floor_Stretcher", (2 * inner, STRETCHER_W, STRETCHER_H),
                         (0, 0, STRETCHER_H / 2), leg_mat, grain_uv("x", offset=(0.6, 0.0))))

    # Parent everything to an empty so the table moves as one piece.
    root = bpy.data.objects.new("Table", None)
    bpy.context.collection.objects.link(root)
    for p in parts:
        p.parent = root
    return root


def add_presentation():
    scene = bpy.context.scene
    floor_mesh = bpy.data.meshes.new("Floor")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3.0)
    bm.to_mesh(floor_mesh)
    bm.free()
    floor = bpy.data.objects.new("Floor", floor_mesh)
    scene.collection.objects.link(floor)
    fm = bpy.data.materials.new("Floor")
    fm.use_nodes = True
    fm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.45, 0.43, 0.40, 1)
    fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    floor_mesh.materials.append(fm)

    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 35
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (-2.3, -2.1, 1.75)
    track = cam.constraints.new("TRACK_TO")
    aim = bpy.data.objects.new("CameraTarget", None)
    scene.collection.objects.link(aim)
    aim.location = (0, 0, 0.45)
    track.target = aim
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    scene.camera = cam

    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 2.0
    sun.rotation_euler = (0.8, 0.2, 0.9)
    scene.collection.objects.link(sun)
    area = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", "AREA"))
    area.data.energy = 300
    area.data.size = 2.0
    area.location = (1.5, -2.0, 2.5)
    area.rotation_euler = (0.7, 0, 0.6)
    scene.collection.objects.link(area)

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.82, 0.85, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    scene.world = world

    scene.view_settings.view_transform = "Standard"
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.render.resolution_x, scene.render.resolution_y = 1280, 960


if __name__ == "__main__":
    build()
    bpy.data.objects["Table"].location.z = 0.0
    add_presentation()
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "table.blend"))
    print("Saved", os.path.join(HERE, "table.blend"))
