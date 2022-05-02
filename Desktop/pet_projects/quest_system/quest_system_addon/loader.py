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
import itertools


if "polib" not in locals():
    import polib
    from . import preferences
else:
    import importlib
    polib = importlib.reload(polib)
    preferences = importlib.reload(preferences)


STARTUP_FILES_PATH = "../startup_files/"


telemetry = polib.get_telemetry("quest_system")


MODULE_CLASSES: typing.List[typing.Type] = []


def clear_blend() -> None:
    bpy.data.batch_remove(ids=itertools.chain(
        bpy.data.objects,
        bpy.data.collections,
        bpy.data.materials,
        bpy.data.meshes,
        bpy.data.images,
        bpy.data.particles)
    )


def mock_startup_blend() -> None:
    clear_blend()
    collection = bpy.data.collections.new("Collection")
    bpy.context.scene.collection.children.link(collection)
    layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    bpy.context.view_layer.active_layer_collection = layer_collection

    bpy.ops.object.camera_add(location=(7.359, -6.927, 4.958), rotation=(1.109, 0.0, 0.815))
    bpy.ops.object.light_add(type='POINT', location=(4.076, 1.005, 5.904))
    bpy.ops.mesh.primitive_cube_add()


PrepareBlendLambda = typing.Callable[[], None]
TestLambda = typing.Callable[[], bool]


class Step:
    def __init__(self, name: str, description: str, tests: typing.List[TestLambda]) -> None:
        self.name = name
        self.description = description
        self.tests = tests


class Task:
    def __init__(self, name: str, description: str, difficulty: str, steps: typing.List[Step], prepare_blend: PrepareBlendLambda = mock_startup_blend) -> None:
        self.name = name
        self.description = description
        # TODO: Make this enum not string
        self.difficulty = difficulty
        self.steps = steps
        self.prepare_blend = prepare_blend


current_task: typing.Optional[Task] = None


# Test functions
def test_monkey_has_material() -> bool:
    if "Suzanne" not in bpy.data.objects:
        return False
    monkey = bpy.data.objects["Suzanne"]
    return "MonkeyMaterial" in monkey.data.materials


def monkey_has_red_material() -> bool:
    if not test_monkey_has_material():
        return False
    monkey_material = bpy.data.objects["Suzanne"].data.materials["MonkeyMaterial"]
    base_color = monkey_material.node_tree.nodes["Principled BSDF"].inputs[0].default_value
    # Red-ish color has R channel bigger than B and G channels
    return base_color[0] > base_color[1] and base_color[0] > base_color[2]


def is_material_or_render_shading_enabled() -> bool:
    for area in bpy.context.screen.areas:
        if area.type != 'VIEW_3D':
            continue
        for space in area.spaces:
            if space.type != 'VIEW_3D':
                continue
            if space.shading.type == 'MATERIAL' or space.shading.type == 'RENDERED':
                return True
    return False


# TODO: Load these from files?
TASKS = [
    Task(
        "Red Monkey",
        "Teaches basics of Blender.",
        "BEGINNER",
        [
            Step(
                "Remove Default Cube",
                "Select default cube and press Delete.",
                [lambda: "Cube" not in bpy.data.objects]
            ),
            Step(
                "Spawn Monkey",
                "Click Add -> Mesh -> Monkey.",
                [lambda: "Suzanne" in bpy.data.objects]
            ),
            Step(
                "Add material MonkeyMaterial",
                "In Properties Window select Material Properties tab, click New to add new "
                "material and rename it to 'MonkeyMaterial'.",
                [test_monkey_has_material]
            ),
            Step(
                "Change material color to red",
                "In Material Properties tab open Surface panel and change Base Color to red.",
                [monkey_has_red_material]
            ),
            Step(
                "View result",
                "You noticed that color of the monkey object didn't change. It's because we are in "
                "Solid view mode. Change Viewport shading to Material Preview or Rendered.",
                [is_material_or_render_shading_enabled]
            ),
        ]
    ),
    Task(
        "Destroy traffiq vehicle",
        "How to add dirt, scratches and bumps to the traffiq assets.",
        "MEDIUM",
        [
            Step(
                "Remove Default Cube",
                "Select default cube and press Delete.",
                [lambda: "Cube" not in bpy.data.objects]
            ),
            # TODO: Add steps
        ]
    ),
]


# TODO: Use enum for difficulty not string
def get_available_tasks(difficulty: str) -> typing.List[str]:
    return [task.name for task in TASKS if task.difficulty == difficulty]


def load_task(task_name: str, prefs: preferences.Preferences) -> bool:
    global current_task
    for task in TASKS:
        if task.name != task_name:
            continue

        current_task = task
        task.prepare_blend()
        prefs.task.name = task.name
        prefs.task.description = task.description
        prefs.task.current_step = 0
        prefs.task.steps.clear()
        for step in task.steps:
            prefs_step = prefs.task.steps.add()
            prefs_step.name = step.name
            prefs_step.description = step.description
        return True
    return False


def register():
    for cls in MODULE_CLASSES:
        telemetry.wrap_blender_class(cls)
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(MODULE_CLASSES):
        bpy.utils.unregister_class(cls)
