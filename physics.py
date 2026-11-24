import bpy

TEMP = "SDG_Physics"
WALL = 0.2

BOX_FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def make_box(name, size, center, collection):
    """Build a box mesh from scratch, with no operators and no selection."""
    sx, sy, sz = size
    corners = [(x * sx / 2, y * sy / 2, z * sz / 2)
               for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(corners, [], BOX_FACES)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    collection.objects.link(obj)
    return obj


def make_container(temp, settings, top):
    """The invisible ground, and the four walls if they are switched on.
    'top' is the highest z the objects start at, so the walls can be tall enough."""
    length, width = settings.area_length, settings.area_width
    ground = settings.ground_height

    helpers = [make_box("SDG_ground", (length + 0.5, width + 0.5, WALL),
                (0, 0, ground - WALL / 2), temp)]

    if settings.use_walls:
        height = top - ground + 1.0
        z = ground + height / 2
        hl, hw = length / 2, width / 2
        helpers += [
            make_box("SDG_wall_px", (WALL, width + 2 * WALL, height), (hl + WALL / 2, 0, z), temp),
            make_box("SDG_wall_nx", (WALL, width + 2 * WALL, height), (-hl - WALL / 2, 0, z), temp),
            make_box("SDG_wall_py", (length + 2 * WALL, WALL, height), (0, hw + WALL / 2, z), temp),
            make_box("SDG_wall_ny", (length + 2 * WALL, WALL, height), (0, -hw - WALL / 2, z), temp),
        ]
    return helpers


def add_rigid_bodies(context, objects, body_type, shape, settings):
    """Turn these objects into rigid bodies, one at a time."""
    view_layer = context.view_layer
    for obj in objects:
        # object_add (singular) works on the ACTIVE object, like in the test script.
        view_layer.objects.active = obj
        bpy.ops.rigidbody.object_add(type=body_type)    # 'ACTIVE' falls, 'PASSIVE' stays put

        rb = obj.rigid_body
        if rb is None:                                  # a clear message instead of a vague crash
            raise RuntimeError(f"Could not make '{obj.name}' a rigid body")

        rb.collision_shape = shape
        rb.friction = settings.friction
        rb.restitution = settings.bounciness            # Blender calls "bounce" restitution
        rb.use_margin = True
        rb.collision_margin = 0.001                     # tiny, so small objects don't float


def settle(context, settings, objects):
    """Drop the objects and let them come to rest."""
    if not objects:
        return

    scene = context.scene
    view_layer = context.view_layer

    saved_frame = scene.frame_current
    saved_selection = list(context.selected_objects)
    saved_active = view_layer.objects.active
    created_world = scene.rigidbody_world is None

    proxies = []
    helpers = []
    world = None
    temp = bpy.data.collections.new(TEMP)
    scene.collection.children.link(temp)

    try:
        if created_world:
            bpy.ops.rigidbody.world_add()
        world = scene.rigidbody_world
        saved_cache = (world.point_cache.frame_start, world.point_cache.frame_end)
        saved_enabled = world.enabled
        world.enabled = True
        world.point_cache.frame_start = 1
        world.point_cache.frame_end = settings.sim_frames + 1

        for obj in objects:
            proxy = obj.copy()
            temp.objects.link(proxy)
            proxies.append(proxy)

        top = max(obj.location.z for obj in objects)
        helpers = make_container(temp, settings, top)
        view_layer.update()

        add_rigid_bodies(context, helpers, 'PASSIVE', 'BOX', settings)
        add_rigid_bodies(context, proxies, 'ACTIVE', 'CONVEX_HULL', settings)

        scene.frame_set(1)
        for frame in range(2, settings.sim_frames + 2):
            scene.frame_set(frame)

        for real, proxy in zip(objects, proxies):
            real.matrix_world = proxy.matrix_world.copy()
        view_layer.update()

    finally:
        for obj in proxies:
            bpy.data.objects.remove(obj, do_unlink=True)
        for obj in helpers:
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(mesh)
        bpy.data.collections.remove(temp)

        if world is not None:
            if created_world:
                rb_collection = world.collection
                bpy.ops.rigidbody.world_remove()
                if rb_collection is not None and rb_collection.users == 0:
                    bpy.data.collectiuons.remove(rb_collection)
            else:
                world.point_cache.frame_start, world.point_cache.frame_end = saved_cache
                world.enabled = saved_enabled

        scene.frame_set(saved_frame)

        bpy.ops.object.select_all(action='DESELECT')
        for obj in saved_selection:
            try:
                obj.select_set(True)
            except ReferenceError:
                pass
        view_layer.objects.active = saved_active
