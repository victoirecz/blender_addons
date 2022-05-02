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
import sys
import bpy
import typing


ADDITIONAL_DEPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "python_deps"))
try:
    if os.path.isdir(ADDITIONAL_DEPS_DIR) and ADDITIONAL_DEPS_DIR not in sys.path:
        sys.path.insert(0, ADDITIONAL_DEPS_DIR)

    if "polib" not in locals():
        import polib
        from . import ui
        from . import preferences
        from . import loader
        from . import logic
    else:
        import importlib
        polib = importlib.reload(polib)
        ui = importlib.reload(ui)
        preferences = importlib.reload(preferences)
        loader = importlib.reload(loader)
        logic = importlib.reload(logic)

finally:
    if ADDITIONAL_DEPS_DIR in sys.path:
        sys.path.remove(ADDITIONAL_DEPS_DIR)


bl_info = {
    "name": "quest_system",
    "author": "polygoniq xyz s.r.o.",
    "version": (0, 1, 0),  # bump doc_url as well!
    "blender": (2, 83, 0),
    "location": "currently unknown",
    "description": "",
    "category": "Object",
    "tracker_url": "https://polygoniq.com/discord"
}
telemetry = polib.get_telemetry("quest_system")
telemetry.report_addon(bl_info, __file__)


ADDON_CLASSES: typing.List[typing.Type] = []


def register():
    preferences.register()
    ui.register()
    loader.register()
    logic.register()

    for cls in ADDON_CLASSES:
        telemetry.wrap_blender_class(cls)
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(ADDON_CLASSES):
        bpy.utils.unregister_class(cls)

    logic.unregister()
    loader.unregister()
    ui.unregister()
    preferences.unregister()
