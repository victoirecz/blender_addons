#!/usr/bin/python3
# copyright (c) 2018- polygoniq xyz s.r.o.

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


import bpy
import typing

if "polib" not in locals():
    import polib
    from . import preferences
    from . import logic
    from . import loader
else:
    import importlib
    polib = importlib.reload(polib)
    preferences = importlib.reload(preferences)
    logic = importlib.reload(logic)
    loader = importlib.reload(loader)


telemetry = polib.get_telemetry("quest_system")


MODULE_CLASSES: typing.List[typing.Type] = []


class ShowHint(bpy.types.Operator):
    bl_idname = "quest.show_hint"
    bl_label = "Show Hint"
    bl_description = "Shows further instructions"
    bl_options = {'REGISTER'}

    message: bpy.props.StringProperty(
        default="No instructions",
        options={'HIDDEN'}
    )

    title: bpy.props.StringProperty(
        default="Hint!",
        options={'HIDDEN'}
    )

    def execute(self, context):
        polib.ui.show_message_box(self.message, self.title)
        return {'FINISHED'}


MODULE_CLASSES.append(ShowHint)


class QuestSystemPanelInfoMixin:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "polygoniq"


class QuestSystemPanel(QuestSystemPanelInfoMixin, bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_quest_system"
    bl_label = "quest"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "polygoniq"
    bl_order = 100 + 5

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(text="", icon='ANIM')

    def draw(self, context: bpy.types.Context):
        # I moved this UI from preferences to here. It was the easiest way how not to get circular
        # dependencies, hope it's not problem as we discussed people don't look in preferences.
        prefs = preferences.get_preferences(context)
        task_names = loader.get_available_tasks(prefs.difficulty)
        row = self.layout.row()
        row.prop(prefs, "difficulty")
        box = self.layout.box()
        for task_name in task_names:
            row = box.row()
            row.label(text=task_name)
            row.operator(logic.StartTask.bl_idname, text="", icon='PLAY').task_name = task_name

        box = self.layout.box()
        row = box.row()
        row.label(text=f"Your Task: {prefs.task.name}")
        row = box.row()
        row.label(text=prefs.task.description)

        self.layout.separator()
        row = self.layout.row()
        row.alert = True
        row.operator(logic.StartTask.bl_idname, text="Restart Task").task_name = prefs.task.name


MODULE_CLASSES.append(QuestSystemPanel)


class QuestStepsPanel(QuestSystemPanelInfoMixin, bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_grumpy_cat_tools"
    bl_parent_id = QuestSystemPanel.bl_idname
    bl_label = "Steps"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(text="", icon='WORDWRAP_OFF')

    def draw(self, context: bpy.types.Context):
        prefs = preferences.get_preferences(context)
        for i, step in enumerate(prefs.task.steps):
            row = self.layout.row()
            step_icon = 'CHECKBOX_HLT' if i < prefs.task.current_step else 'CHECKBOX_DEHLT'
            row.label(text=step.name, icon=step_icon)
            col = row.column()
            prop = col.operator(ShowHint.bl_idname, text="", icon='QUESTION')
            prop.message = step.description
            if i == prefs.task.current_step:
                row = self.layout.row()
                row.operator(logic.CheckCurrentStep.bl_idname, text="Submit Current Step")


MODULE_CLASSES.append(QuestStepsPanel)


def register(panel_name: str = "Quests"):
    QuestSystemPanel.bl_label = panel_name
    for cls in MODULE_CLASSES:
        telemetry.wrap_blender_class(cls)
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(MODULE_CLASSES):
        bpy.utils.unregister_class(cls)
