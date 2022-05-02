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

import os
import bpy
import typing


if "polib" not in locals():
    import polib
else:
    import importlib
    polib = importlib.reload(polib)


telemetry = polib.get_telemetry("quest_system")


MODULE_CLASSES: typing.List[typing.Type] = []


class StepProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        default=""
    )
    description: bpy.props.StringProperty(
        name="Description",
        default=""
    )


MODULE_CLASSES.append(StepProperties)


class TaskProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        default=""
    )
    description: bpy.props.StringProperty(
        name="Description",
        default=""
    )
    steps: bpy.props.CollectionProperty(
        type=StepProperties
    )
    current_step: bpy.props.IntProperty(
        name="Current Step",
        min=0,
        default=0
    )

    def is_finished(self) -> bool:
        return self.current_step >= len(self.steps)

    def get_current_step(self) -> typing.Optional[StepProperties]:
        if self.current_step < 0 or self.current_step >= len(self.steps):
            return None
        return self.steps[self.current_step]


MODULE_CLASSES.append(TaskProperties)


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    task: bpy.props.PointerProperty(
        type=TaskProperties
    )

    difficulty: bpy.props.EnumProperty(
        name="difficulty",
        default='BEGINNER',
        items=(
            ('BEGINNER', "Beginner", "Easy journey"),
            ('MEDIUM', "Medium", "You may sweat a little"),
            ('GURU', "Guru", "All hope abandon you who enter here")
        )
    )

    def draw(self, context):
        row = self.layout.row()
        row.operator(CopyTelemetry.bl_idname, icon='EXPERIMENTAL')

        polib.ui.draw_settings_footer(self.layout)


MODULE_CLASSES.append(Preferences)


def get_preferences(context: bpy.types.Context) -> Preferences:
    return context.preferences.addons[__package__].preferences


class CopyTelemetry(bpy.types.Operator):
    bl_idname = "quest_system.copy_telemetry"
    bl_label = "Copy Telemetry (Debug Information)"
    bl_description = (
        "Copies debugging information about usage of polygoniq products to clipboard. "
        "This is useful when requesting support or reporting bugs."
    )
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.window_manager.clipboard = telemetry.dump()

        return {'FINISHED'}


MODULE_CLASSES.append(CopyTelemetry)


def register():
    for cls in MODULE_CLASSES:
        telemetry.wrap_blender_class(cls)
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(MODULE_CLASSES):
        bpy.utils.unregister_class(cls)
