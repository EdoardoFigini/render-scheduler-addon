bl_info = {
    "name": "Render Scheduler",
    "author": "Edoardo Figini",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > Render category",
    "description": "Render scheduler",
    "category": "Render",
}


import bpy
from os import path
import sys


def update_collection_visibility(self, context):
    for x in context.scene.render_schedule[
        context.scene.render_schedule_index
    ].collections:
        if self == x:
            set_collection_visibility(context.view_layer.layer_collection, self)
            return


class VisibleCollection(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(name="Collection", type=bpy.types.Collection)
    visible: bpy.props.BoolProperty(
        name="Visible", default=True, update=update_collection_visibility
    )


formats_list = (
    ("PNG", "PNG", ".png"),
    ("JPEG", "JPEG", ".jpg"),
    ("OPEN_EXR", "OpenEXR", ".exr"),
    ("OPEN_EXR_MULTILAYER", "OpenEXR Multilayer", ".exr"),
)
codecs_list = (("ZIP", "ZIP", "ZIP"), ("DWAA", "DWAA", "DWAA"))


class RenderScheduleEntry(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    filepath: bpy.props.StringProperty(
        name="Filepath", subtype="DIR_PATH", description="Path to output folder"
    )
    compositor: bpy.props.BoolProperty(name="Use Compositor", default=True)
    samples: bpy.props.IntProperty(
        name="Samples", description="Sample count to be used in this render"
    )
    format: bpy.props.EnumProperty(name="Format", items=formats_list)
    color_depth: bpy.props.EnumProperty(
        name="Color Depth",
        items=(
            ("8", "8", "(8 bit Depth)"),
            ("16", "16", "(16 bit Depth)"),
            ("32", "32", "(32 bit Depth)"),
        ),
    )
    float_depth: bpy.props.EnumProperty(
        name="Color Depth",
        items=(("16", "Half", "(16 bit Depth)"), ("32", "Full", "(32 bit Depth)")),
    )
    compression_quality: bpy.props.IntProperty(
        name="Compression", default=15, subtype="PERCENTAGE", min=0, max=100
    )
    codec: bpy.props.EnumProperty(name="Codec", items=codecs_list)

    def only_cameras_poll(self, object):
        return object.type == "CAMERA"

    camera: bpy.props.PointerProperty(
        name="Camera",
        type=bpy.types.Object,
        poll=only_cameras_poll,
        description="Camera to be used for this render",
    )

    world: bpy.props.PointerProperty(
        name="World",
        type=bpy.types.World,
        description="World to be used for this render",
    )

    collections: bpy.props.CollectionProperty(type=VisibleCollection)
    collections_idx: bpy.props.IntProperty(name="collections index", default=0)

    active: bpy.props.BoolProperty(name="Active", default=True)
    show_details: bpy.props.BoolProperty(name="Show Details", default=True)


class VIEW3D_UL_collectionlsit(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            if item.collection is None:
                return
            layout.label(
                text=item.collection.name,
                icon=["OUTLINER_COLLECTION", "COLLECTION_" + item.collection.color_tag][
                    item.collection.color_tag != "NONE"
                ],
            )
            layout.prop(
                item,
                "visible",
                text="",
                icon=["RESTRICT_RENDER_ON", "RESTRICT_RENDER_OFF"][item.visible],
                emboss=False,
            )

        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class VIEW3D_UL_schedule(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            box = layout.box()
            col = box.column()

            row = col.split(factor=0.1)
            row.prop(
                item,
                "show_details",
                text="",
                toggle=1,
                icon=["TRIA_RIGHT", "TRIA_DOWN"][item.show_details],
                emboss=False,
            )
            row = row.split(factor=0.9)
            row.prop(item, "name", text="", emboss=False)
            row = row.split()
            row.prop(
                item,
                "active",
                icon_only=True,
                icon=["RESTRICT_RENDER_ON", "RESTRICT_RENDER_OFF"][item.active],
                emboss=False,
            )

            if item.show_details:
                row = box.row()
                row.prop(item, "filepath", text="Filepath")
                row = box.row()
                row.prop(item, "camera", text="Camera")
                row = box.row()
                row.prop(item, "world", text="World")
                row = box.row()
                row.label(
                    text=f"Visible Collections:\t\t{len([x for x in item.collections if x.visible])}"
                )
                row.operator("scene.update_collections", text="", icon="FILE_REFRESH")
                row = box.row()
                row.template_list(
                    "VIEW3D_UL_collectionlsit",
                    "",
                    item,
                    "collections",
                    item,
                    "collections_idx",
                )
                row = box.row()
                row.label(text="Samples")
                row.prop(item, "samples", text="")
                row = box.row()
                row.label(text="Format")
                row.prop(item, "format", text="")
                row = box.row()
                if item.format == "PNG" or item.format == "JPEG":
                    row.label(text="Color Depth")
                    row.prop(item, "color_depth", text="")
                    row = box.row()
                    row.label(text=["Compression", "Quality"][item.format == "JPEG"])
                    row.prop(item, "compression_quality", text="")
                else:
                    row.label(text="Float Depth")
                    row.prop(item, "float_depth", text="")
                    row = box.row()
                    row.label(text="Codec")
                    row.prop(item, "codec", text="")

        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class VIEW3D_PT_render_scheduler(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render"
    bl_label = "Render Scheduler"

    def draw(self, context):
        row = self.layout.row(align=True)
        row.label(text="Scheduled Renders")
        row.operator("render.add_to_schedule", icon="ADD", text="")
        row.operator("render.remove_from_schedule", icon="REMOVE", text="")
        row = self.layout.row()
        row.template_list(
            "VIEW3D_UL_schedule",
            "",
            context.scene,
            "render_schedule",
            context.scene,
            "render_schedule_index",
        )

        row = self.layout.row()
        row.operator("render.render_active", text="Render Active")


class AddToSchedule(bpy.types.Operator):
    bl_idname = "render.add_to_schedule"
    bl_label = "Add to Schedule"

    def execute(self, context):
        new_entry = context.scene.render_schedule.add()
        new_entry.name = f"Render.{context.scene.render_schedule_index:03}"
        new_entry.filepath = "//"
        new_entry.camera = context.scene.camera
        new_entry.active = True
        new_entry.samples = context.scene.cycles.samples
        new_entry.world = context.scene.world

        for c in bpy.data.collections:
            new_coll = new_entry.collections.add()
            new_coll.collection = c
            new_coll.visible = True

        return {"FINISHED"}


class RemoveFromSchedule(bpy.types.Operator):
    bl_idname = "render.remove_from_schedule"
    bl_label = "Remove From Schedule"

    def execute(self, context):
        context.scene.render_schedule.remove(context.scene.render_schedule_index)
        return {"FINISHED"}


class RenderActive(bpy.types.Operator):
    bl_idname = "render.render_active"
    bl_label = "Render Active"

    _timer = None
    shots = None
    stop = False
    rendering = False
    idx = 0

    def pre(self, scene, context=None):
        self.rendering = True

    def post(self, scene, context=None):
        self.rendering = False
        self.idx += 1
        # print('Info: Done')

    def modal(self, context, event):
        if event.type == "TIMER":
            if self.stop:
                return {"CANCELLED"}
            elif self.rendering:
                return {"PASS_THROUGH"}
            elif self.idx >= len(self.shots):
                bpy.app.handlers.render_pre.remove(self.pre)
                bpy.app.handlers.render_complete.remove(self.post)
                bpy.app.handlers.render_cancel.remove(self.cancel)
                print("Info: Finished all")
                return {"FINISHED"}
            else:
                item = self.shots[self.idx]
                if (
                    item.name == ""
                    or item.filepath == ""
                    or item.camera is None
                    or item.world is None
                ):
                    # TODO: custom exception
                    raise Exception("set all params!")

                for c in item.collections:
                    c.collection.hide_render = not c.visible

                #               self.properties.bl_rna.properties['preset_enum'].enum_items
                context.scene.render.image_settings.file_format = item.format

                if item.format == "PNG":
                    bpy.context.scene.render.image_settings.compression = (
                        item.compression_quality
                    )
                elif item.format == "JPEG":
                    bpy.context.scene.render.image_settings.quality = (
                        item.compression_quality
                    )
                else:
                    bpy.context.scene.render.image_settings.exr_codec = item.codec

                filepath = path.join(
                    item.filepath,
                    item.name + [x for x in formats_list if x[0] == item.format][0][2],
                )
                context.scene.camera = item.camera
                context.scene.world = item.world

                context.scene.render.filepath = filepath
                bpy.context.scene.cycles.samples = item.samples

                print(f"Rendering {self.idx}")
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)

        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        self.idx = 0
        self.stop = False
        self.rendering = False

        self.shots = [x for x in bpy.context.scene.render_schedule if x.active]
        print(self.shots)

        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_complete.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancel)

        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        bpy.app.handlers.render_pre.remove(self.pre)
        bpy.app.handlers.render_complete.remove(self.post)
        bpy.app.handlers.render_cancel.remove(self.cancel)
        self.stop = True
        return {"CANCELLED"}


class CollectionsUpdate(bpy.types.Operator):
    bl_idname = "scene.update_collections"
    bl_label = "Update Collections"

    def execute(self, context):
        for i in context.scene.render_schedule:
            for c in bpy.data.collections:
                if c not in [x.collection for x in i.collections]:
                    new_coll = i.collections.add()
                    new_coll.collection = c
                    new_coll.visible = True
            for index in range(len(i.collections)):
                try:
                    if i.collections[index].collection is None:
                        i.collections.remove(index)
                except:
                    pass
        return {"FINISHED"}


class ModalCollectionsCheck(bpy.types.Operator):
    bl_idname = "scene.modal_check_collections"
    bl_label = "Check Collections"

    _timer = None

    def modal(self, context, event):
        if event.type == "TIMER":
            for i in context.scene.render_schedule:
                if len(bpy.data.collections) > len(i.collections):
                    for c in bpy.data.collections:
                        if c not in [x.collection for x in i.collections]:
                            new_coll = i.collections.add()
                            new_coll.collection = c
                            new_coll.visible = True

                for index in range(len(i.collections)):
                    try:
                        if i.collections[index].collection is None:
                            i.collections.remove(index)
                    except:
                        pass

        return {"PASS_THROUGH"}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(1.0, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)


def set_collection_visibility(root, c):
    if len(root.children) == 0:
        return
    if c.collection.name in root.children:
        root.children[c.collection.name].hide_viewport = not c.visible
    else:
        for x in root.children:
            set_collection_visibility(root.children[x.name], c)
    return


def item_selected(self, context):
    i = context.scene.render_schedule[context.scene.render_schedule_index]
    if i.camera is None or i.world is None:
        return

    for c in i.collections:
        set_collection_visibility(context.view_layer.layer_collection, c)

    context.scene.camera = i.camera
    context.scene.world = i.world


def register():
    bpy.utils.register_class(VIEW3D_PT_render_scheduler)
    bpy.utils.register_class(VIEW3D_UL_schedule)
    bpy.utils.register_class(VIEW3D_UL_collectionlsit)
    bpy.utils.register_class(RenderActive)
    bpy.utils.register_class(AddToSchedule)
    bpy.utils.register_class(RemoveFromSchedule)
    bpy.utils.register_class(VisibleCollection)
    bpy.utils.register_class(RenderScheduleEntry)
    bpy.utils.register_class(ModalCollectionsCheck)
    bpy.utils.register_class(CollectionsUpdate)
    bpy.types.Scene.render_schedule = bpy.props.CollectionProperty(
        type=RenderScheduleEntry
    )
    bpy.types.Scene.render_schedule_index = bpy.props.IntProperty(
        name="Index for render_schedule", default=0, update=item_selected
    )


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_render_scheduler)
    bpy.utils.unregister_class(VIEW3D_UL_schedule)
    bpy.utils.unregister_class(VIEW3D_UL_collectionlsit)
    bpy.utils.unregister_class(RenderActive)
    bpy.utils.unregister_class(AddToSchedule)
    bpy.utils.unregister_class(RemoveFromSchedule)
    bpy.utils.unregister_class(VisibleCollection)
    bpy.utils.unregister_class(RenderScheduleEntry)
    bpy.utils.unregister_class(ModalCollectionsCheck)
    bpy.utils.unregister_class(CollectionsUpdate)
    del bpy.types.Scene.render_schedule
    del bpy.types.Scene.render_schedule_index


if __name__ == "__main__":
    register()
    bpy.ops.scene.modal_check_collections()

