from trame.app import get_server
from trame.ui.html import DivLayout
from trame.widgets import html, client, vtk as vtk_widgets
import pyvista as pv

pv.OFF_SCREEN = True


class PickingExample:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")
        self.pl = pv.Plotter(off_screen=True)
        # VTK
        cone_actor = self.pl.add_mesh(pv.Cone( height=0.5,radius=0.2), name="Cone",color="yellow")
        sphere_actor = self.pl.add_mesh(pv.Sphere(radius=0.25), name="Sphere",color="red")

        # UI
        self.ui = self._build_ui()

        self.vtk_mapping = {
            self.get_scene_object_id(cone_actor): "Cone",
            self.get_scene_object_id(sphere_actor): "Sphere",
        }

    def on_click(self, event):
        if event is None:
            print("Click on: --nothing--")
        else:
            print(f"Click on: {self.vtk_mapping.get(event.get('remoteId'))}")

    def on_select(self, event):
        print(
            "Selected:",
            [self.vtk_mapping.get(actor_id) for actor_id in event.get("remoteIds")],
        )

    def on_hover(self, event):
        if event:
            print(f"Hover on: {self.vtk_mapping.get(event.get('remoteId'))}")

    def _build_ui(self):
        with DivLayout(self.server) as layout:
            client.Style("html, body { padding: 0; margin: 0; }")
            layout.root.style = "width: 100vw; height: 100vh;"

            with html.Select(
                v_model="picking_modes",
                multiple=True,
                style="position: absolute; z-index: 10; top: 10px; right: 10px;",
            ):
                for name in ["hover", "select", "click"]:
                    html.Option(name, value=name)

            html.Div(
                "{{ picking_modes }}",
                style="position: absolute; z-index: 10; top: 10px; left: 10px; color: white;",
            )

            with vtk_widgets.VtkLocalView(
                self.pl.ren_win,
                picking_modes=("picking_modes", []),
                select=(self.on_select, "[$event]"),
                hover=(self.on_hover, "[$event]"),
                click=(self.on_click, "[$event]"),
            ) as view:
                self.get_scene_object_id = view.get_scene_object_id


def main():
    app = PickingExample()
    app.server.start()


if __name__ == "__main__":
    main()
