bl_info = {
    "name": "Z Shading Pie Menu",
    "author": "Garzon",
    "version": (1, 2, 1),
    "blender": (3, 6, 0),
    "category": "3D View",
}

import bpy


class SetShadingAndEngineOperator(bpy.types.Operator):
    bl_idname = "view3d.set_shading_and_engine"
    bl_label = "Set Shading and Engine"

    shading_type: bpy.props.EnumProperty(
        items=[
            ('WIREFRAME', "Wireframe", ""),
            ('SOLID', "Solid", ""),
            ('MATERIAL', "Material Preview", ""),
            ('RENDERED', "Rendered", ""),
        ]
    )

    render_engine: bpy.props.EnumProperty(
        items=[
            ('NONE', "None", ""),
            ('CYCLES', "Cycles", ""),
            ('BLENDER_EEVEE', "Eevee", ""),
            ('BLENDER_WORKBENCH', "Workbench", ""),
        ],
        default='NONE'
    )

    eevee_ray_tracing: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        scene = context.scene
        view_space = context.area.spaces.active

        current_shading_type = view_space.shading.type
        current_render_engine = scene.render.engine
        current_eevee_ray_tracing = scene.eevee.use_raytracing

        # Early exit if nothing would change
        if self.shading_type != 'RENDERED':
            if current_shading_type == self.shading_type:
                return {'CANCELLED'}
        else:
            if (
                current_shading_type == 'RENDERED'
                and current_render_engine == self.render_engine
                and (
                    self.render_engine != 'BLENDER_EEVEE'
                    or current_eevee_ray_tracing == self.eevee_ray_tracing
                )
            ):
                return {'CANCELLED'}

        # Apply changes
        view_space.shading.type = self.shading_type

        if self.shading_type == 'RENDERED' and self.render_engine != 'NONE':
            scene.render.engine = self.render_engine

            if self.render_engine == 'BLENDER_EEVEE':
                scene.eevee.use_raytracing = self.eevee_ray_tracing

        return {'FINISHED'}


class VIEW3D_MT_z_shading_engine_pie(bpy.types.Menu):
    bl_label = "Z Shading Pie"
    bl_idname = "VIEW3D_MT_z_shading_engine_pie"

    def draw(self, context):
        pie = self.layout.menu_pie()
        rendered_icon = 'SHADING_RENDERED'

        # 1 — LEFT (4)
        operator_instance = pie.operator(
            "view3d.set_shading_and_engine",
            text="Wireframe",
            icon='SHADING_WIRE'
        )
        operator_instance.shading_type = 'WIREFRAME'

        # 2 — RIGHT (6)
        operator_instance = pie.operator(
            "view3d.set_shading_and_engine",
            text="Solid",
            icon='SHADING_SOLID'
        )
        operator_instance.shading_type = 'SOLID'

        # 3 — BOTTOM (2)
        operator_instance = pie.operator(
            "view3d.set_shading_and_engine",
            text="Material Preview",
            icon='SHADING_TEXTURE'
        )
        operator_instance.shading_type = 'MATERIAL'

        # 4 — TOP (8)
        operator_instance = pie.operator(
            "view3d.set_shading_and_engine",
            text="Cycles",
            icon=rendered_icon
        )
        operator_instance.shading_type = 'RENDERED'
        operator_instance.render_engine = 'CYCLES'

        # 5 — BOTTOM-LEFT (1)
        operator_instance = pie.operator(
            "view3d.set_shading_and_engine",
            text="Workbench",
            icon=rendered_icon
        )
        operator_instance.shading_type = 'RENDERED'
        operator_instance.render_engine = 'BLENDER_WORKBENCH'

        # 6 — BOTTOM-RIGHT (3)
        operator_instance = pie.operator(
            "view3d.set_shading_and_engine",
            text="Eevee (Ray Tracing)",
            icon=rendered_icon
        )
        operator_instance.shading_type = 'RENDERED'
        operator_instance.render_engine = 'BLENDER_EEVEE'
        operator_instance.eevee_ray_tracing = True

        # 7 — TOP-LEFT (7)
        pie.separator()

        # 8 — TOP-RIGHT (9)
        operator_instance = pie.operator(
            "view3d.set_shading_and_engine",
            text="Eevee",
            icon=rendered_icon
        )
        operator_instance.shading_type = 'RENDERED'
        operator_instance.render_engine = 'BLENDER_EEVEE'
        operator_instance.eevee_ray_tracing = False


class ZShadingPieAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    shortcut_key: bpy.props.EnumProperty(
        name="Shortcut Key",
        items=[
            ('Z', 'Z', ''),
            ('Q', 'Q', ''),
            ('W', 'W', ''),
            ('E', 'E', ''),
            ('R', 'R', ''),
        ],
        default='Z'
    )

    def draw(self, context):
        self.layout.prop(self, "shortcut_key")


addon_keymaps = []


def register_keymap():
    window_manager = bpy.context.window_manager
    keyconfig = window_manager.keyconfigs.addon

    if not keyconfig:
        return

    preferences = bpy.context.preferences.addons[__name__].preferences

    keymap = keyconfig.keymaps.new(
        name="3D View",
        space_type="VIEW_3D"
    )

    keymap_item = keymap.keymap_items.new(
        "wm.call_menu_pie",
        type=preferences.shortcut_key,
        value='PRESS'
    )
    keymap_item.properties.name = "VIEW3D_MT_z_shading_engine_pie"

    addon_keymaps.append((keymap, keymap_item))


def unregister_keymap():
    for keymap, keymap_item in addon_keymaps:
        keymap.keymap_items.remove(keymap_item)
    addon_keymaps.clear()


def register():
    bpy.utils.register_class(SetShadingAndEngineOperator)
    bpy.utils.register_class(VIEW3D_MT_z_shading_engine_pie)
    bpy.utils.register_class(ZShadingPieAddonPreferences)
    register_keymap()


def unregister():
    unregister_keymap()
    bpy.utils.unregister_class(ZShadingPieAddonPreferences)
    bpy.utils.unregister_class(VIEW3D_MT_z_shading_engine_pie)
    bpy.utils.unregister_class(SetShadingAndEngineOperator)


if __name__ == "__main__":
    register()