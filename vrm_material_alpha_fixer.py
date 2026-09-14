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
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "VRM Material & Alpha Fixer",
    "author": "lordblcksyde",
    "version": (1, 2, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > VRM Fix",
    "description": "Fixes VRM MToon shaders, texture Alpha links, customizable Emission mapping, and Roughness",
    "category": "Material",
    "doc_url": "https://github.com/lordblcksyde/VRM-BLENDER-MATERIAL-FIX",
    "tracker_url": "https://github.com/lordblcksyde/VRM-BLENDER-MATERIAL-FIX/issues",
}

import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import BoolProperty, FloatProperty, PointerProperty


class VRM_MaterialFixer_Settings(PropertyGroup):
    emission_strength: FloatProperty(
        name="Emission Strength",
        description="Emission strength value to assign to materials",
        default=0.5,
        min=0.0,
        soft_max=10.0,
        step=10,
        precision=2,
    )
    roughness_val: FloatProperty(
        name="Roughness Value",
        description="Roughness value to assign to materials",
        default=1.0,
        min=0.0,
        max=1.0,
        step=10,
        precision=2,
    )


def get_target_materials(context, only_selected):
    if only_selected and context and context.selected_objects:
        materials = set()
        for obj in context.selected_objects:
            if hasattr(obj, "material_slots"):
                for slot in obj.material_slots:
                    if slot.material:
                        materials.add(slot.material)
        return materials
    return set(bpy.data.materials)


def fix_alpha_and_mtoon(
    context=None,
    disable_mtoon=True,
    fix_alpha=True,
    set_surface_method=True,
    surface_method='DITHERED',
    only_selected=False,
):
    materials = get_target_materials(context, only_selected)
    mt_count = 0
    alpha_count = 0

    for m in materials:
        if disable_mtoon:
            try:
                if hasattr(m, "vrm_addon_extension") and hasattr(m.vrm_addon_extension, "mtoon1"):
                    m.vrm_addon_extension.mtoon1.enabled = False
                    mt_count += 1
            except Exception:
                pass

        if fix_alpha:
            if not m.node_tree:
                continue

            bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if not bsdf:
                continue

            base = bsdf.inputs.get('Base Color')
            ain = bsdf.inputs.get('Alpha')
            if not base or not ain or not base.is_linked:
                continue

            src = base.links[0].from_node
            if src and src.type == 'TEX_IMAGE' and 'Alpha' in src.outputs:
                for link in list(ain.links):
                    m.node_tree.links.remove(link)
                m.node_tree.links.new(src.outputs['Alpha'], ain)

                if set_surface_method:
                    try:
                        if hasattr(m, 'surface_render_method'):
                            m.surface_render_method = surface_method
                    except Exception:
                        pass
                    try:
                        if hasattr(m, 'blend_method') and m.blend_method == 'OPAQUE':
                            m.blend_method = 'CLIP' if surface_method == 'DITHERED' else 'BLEND'
                    except Exception:
                        pass

                alpha_count += 1

    return mt_count, alpha_count


def fix_emission_and_roughness(
    context=None,
    emission_strength=0.5,
    roughness_val=1.0,
    only_selected=False,
):
    materials = get_target_materials(context, only_selected)
    em_count = 0
    rough_count = 0

    for m in materials:
        if not m.node_tree:
            continue

        bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not bsdf:
            continue

        base = bsdf.inputs.get('Base Color')
        emission_socket = bsdf.inputs.get('Emission Color') or bsdf.inputs.get('Emission')
        strength = bsdf.inputs.get('Emission Strength')
        roughness = bsdf.inputs.get('Roughness')

        if base and base.is_linked and emission_socket:
            src = base.links[0].from_node
            if src and src.type == 'TEX_IMAGE' and 'Color' in src.outputs:
                for link in list(emission_socket.links):
                    m.node_tree.links.remove(link)
                m.node_tree.links.new(src.outputs['Color'], emission_socket)
                if strength:
                    strength.default_value = emission_strength
                em_count += 1

        if roughness:
            for link in list(roughness.links):
                m.node_tree.links.remove(link)
            roughness.default_value = roughness_val
            rough_count += 1

    return em_count, rough_count


class MATERIAL_OT_fix_vrm_alpha(Operator):
    """Disable VRM MToon1 shader and connect texture Alpha to Principled BSDF Alpha"""
    bl_idname = "material.fix_vrm_alpha_mtoon"
    bl_label = "Fix VRM Alpha & MToon"
    bl_options = {'REGISTER', 'UNDO'}

    disable_mtoon: BoolProperty(
        name="Disable MToon",
        default=True,
    )
    fix_alpha: BoolProperty(
        name="Connect Texture Alpha",
        default=True,
    )
    set_surface_method: BoolProperty(
        name="Set Surface Method to Dithered",
        default=True,
    )
    only_selected: BoolProperty(
        name="Only Selected Objects",
        default=False,
    )

    def execute(self, context):
        mt, alpha = fix_alpha_and_mtoon(
            context=context,
            disable_mtoon=self.disable_mtoon,
            fix_alpha=self.fix_alpha,
            set_surface_method=self.set_surface_method,
            surface_method='DITHERED',
            only_selected=self.only_selected,
        )
        msg = f"Done: disabled MToon on {mt} materials, fixed alpha on {alpha} materials."
        self.report({'INFO'}, msg)
        print(msg)
        return {'FINISHED'}


class MATERIAL_OT_fix_vrm_emission_roughness(Operator):
    """Connect Base Color Texture to Emission and set Roughness to 1.0"""
    bl_idname = "material.fix_vrm_emission_roughness"
    bl_label = "Fix Emission & Roughness"
    bl_options = {'REGISTER', 'UNDO'}

    emission_strength: FloatProperty(
        name="Emission Strength",
        description="Emission strength value",
        default=0.5,
        min=0.0,
        soft_max=10.0,
    )
    roughness_val: FloatProperty(
        name="Roughness Value",
        description="Roughness value (unlinks existing connections)",
        default=1.0,
        min=0.0,
        max=1.0,
    )
    only_selected: BoolProperty(
        name="Only Selected Objects",
        default=False,
    )

    def invoke(self, context, event):
        if hasattr(context.scene, "vrm_fixer_settings"):
            self.emission_strength = context.scene.vrm_fixer_settings.emission_strength
            self.roughness_val = context.scene.vrm_fixer_settings.roughness_val
        return self.execute(context)

    def execute(self, context):
        em, rough = fix_emission_and_roughness(
            context=context,
            emission_strength=self.emission_strength,
            roughness_val=self.roughness_val,
            only_selected=self.only_selected,
        )
        msg = f"Done: Emission set to {self.emission_strength:.2f} on {em} materials, Roughness set to {self.roughness_val:.2f} on {rough} materials."
        self.report({'INFO'}, msg)
        print(msg)
        return {'FINISHED'}


class MATERIAL_OT_fix_vrm_full(Operator):
    """Run both Alpha/MToon fix and Emission/Roughness fix on materials"""
    bl_idname = "material.fix_vrm_full"
    bl_label = "Run Full Fix (All Steps)"
    bl_options = {'REGISTER', 'UNDO'}

    emission_strength: FloatProperty(
        name="Emission Strength",
        default=0.5,
        min=0.0,
        soft_max=10.0,
    )
    roughness_val: FloatProperty(
        name="Roughness Value",
        default=1.0,
        min=0.0,
        max=1.0,
    )
    only_selected: BoolProperty(
        name="Only Selected Objects",
        default=False,
    )

    def invoke(self, context, event):
        if hasattr(context.scene, "vrm_fixer_settings"):
            self.emission_strength = context.scene.vrm_fixer_settings.emission_strength
            self.roughness_val = context.scene.vrm_fixer_settings.roughness_val
        return self.execute(context)

    def execute(self, context):
        mt, alpha = fix_alpha_and_mtoon(context=context, only_selected=self.only_selected)
        em, rough = fix_emission_and_roughness(
            context=context,
            emission_strength=self.emission_strength,
            roughness_val=self.roughness_val,
            only_selected=self.only_selected,
        )
        msg = f"Full Fix: MToon off: {mt}, Alpha linked: {alpha}, Emission ({self.emission_strength:.2f}) linked: {em}, Roughness: {rough}"
        self.report({'INFO'}, msg)
        print(msg)
        return {'FINISHED'}


class VIEW3D_PT_vrm_material_fixer(Panel):
    """Panel in the 3D Viewport N Sidebar"""
    bl_label = "VRM Material Fixer"
    bl_idname = "VIEW3D_PT_vrm_material_fixer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "VRM Fix"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.vrm_fixer_settings

        # Section 1: Alpha & MToon
        box1 = layout.box()
        box1.label(text="1. Alpha & MToon Fix", icon='NODE_MATERIAL')
        row1 = box1.row(align=True)
        row1.scale_y = 1.2
        op1_all = row1.operator(MATERIAL_OT_fix_vrm_alpha.bl_idname, text="Fix Alpha (All)", icon='MATERIAL')
        op1_all.only_selected = False
        op1_sel = row1.operator(MATERIAL_OT_fix_vrm_alpha.bl_idname, text="Selected", icon='RESTRICT_SELECT_OFF')
        op1_sel.only_selected = True

        # Section 2: Emission & Roughness
        box2 = layout.box()
        box2.label(text="2. Emission & Roughness", icon='LIGHT_SUN')
        
        # Adjustable input controls
        col_props = box2.column(align=True)
        col_props.prop(settings, "emission_strength", text="Emission Strength", slider=True)
        col_props.prop(settings, "roughness_val", text="Roughness", slider=True)

        row2 = box2.row(align=True)
        row2.scale_y = 1.2
        op2_all = row2.operator(MATERIAL_OT_fix_vrm_emission_roughness.bl_idname, text="Fix Emission (All)", icon='SHADING_RENDERED')
        op2_all.only_selected = False
        op2_all.emission_strength = settings.emission_strength
        op2_all.roughness_val = settings.roughness_val

        op2_sel = row2.operator(MATERIAL_OT_fix_vrm_emission_roughness.bl_idname, text="Selected", icon='RESTRICT_SELECT_OFF')
        op2_sel.only_selected = True
        op2_sel.emission_strength = settings.emission_strength
        op2_sel.roughness_val = settings.roughness_val

        # Section 3: Full Setup
        layout.separator()
        col = layout.column(align=True)
        col.scale_y = 1.3
        op_full = col.operator(MATERIAL_OT_fix_vrm_full.bl_idname, text="Run Full Fix (All Steps)", icon='CHECKMARK')
        op_full.only_selected = False
        op_full.emission_strength = settings.emission_strength
        op_full.roughness_val = settings.roughness_val


classes = (
    VRM_MaterialFixer_Settings,
    MATERIAL_OT_fix_vrm_alpha,
    MATERIAL_OT_fix_vrm_emission_roughness,
    MATERIAL_OT_fix_vrm_full,
    VIEW3D_PT_vrm_material_fixer,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vrm_fixer_settings = PointerProperty(type=VRM_MaterialFixer_Settings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, "vrm_fixer_settings"):
        del bpy.types.Scene.vrm_fixer_settings


if __name__ == "__main__":
    register()
