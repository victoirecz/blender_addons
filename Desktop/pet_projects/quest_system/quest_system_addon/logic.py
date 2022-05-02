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
    from . import preferences
    from . import loader
else:
    import importlib
    polib = importlib.reload(polib)
    preferences = importlib.reload(preferences)
    loader = importlib.reload(loader)


telemetry = polib.get_telemetry("quest_system")


MODULE_CLASSES: typing.List[typing.Type] = []


# TODO: Add periodical checking of current step

class StartTask(bpy.types.Operator):
    bl_idname = "quest_system.start_task"
    bl_label = "Start Task"
    bl_description = "Starts task with the given name, can be also used to restart task"

    bl_options = {'REGISTER', 'UNDO'}

    task_name: bpy.props.StringProperty(
        default=""
    )

    def execute(self, context):
        loaded_successfully = loader.load_task(self.task_name, preferences.get_preferences(context))
        if not loaded_successfully:
            self.report(
                {'ERROR'}, f"Task '{self.task_name}' was not loaded successfully, does it exist?")
            return {'CANCELLED'}

        return {'FINISHED'}


MODULE_CLASSES.append(StartTask)


class CheckCurrentStep(bpy.types.Operator):
    bl_idname = "quest_system.check_current_step"
    bl_label = "Not yet! Try one more time!"
    bl_description = "Checks if current step was satisfied"

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = preferences.get_preferences(context)
        if prefs.task.is_finished():
            return {'FINISHED'}

        current_step = prefs.task.get_current_step()
        if current_step is None:
            self.report({'ERROR'}, f"Couldn't retrieve current step!")
            return {'CANCELLED'}

        for step_data in loader.current_task.steps:
            if step_data.name == current_step.name:
                if all(test() for test in step_data.tests):
                    prefs.task.current_step += 1
                    return {'FINISHED'}
                else:
                    polib.ui.show_message_box(
                        "Try one more time!", "Not yet!", 'ERROR')
                    return {'FINISHED'}

        self.report({'ERROR'}, f"Not found step with name '{self.step.name}' in the current task!")
        return {'CANCELLED'}


MODULE_CLASSES.append(CheckCurrentStep)


def register():
    for cls in MODULE_CLASSES:
        telemetry.wrap_blender_class(cls)
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(MODULE_CLASSES):
        bpy.utils.unregister_class(cls)
