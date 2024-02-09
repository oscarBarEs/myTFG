
import tempfile
from enum import Enum

import vtk
import pyvista as pv
from pyvista import examples
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.app.file_upload import ClientFile

from trame.ui.vuetify2 import SinglePageWithDrawerLayout
from trame.widgets import vuetify2 as vuetify, vega

from trame.decorators import TrameApp, change, life_cycle

from components.tableOfSimulation import table_of_simulation, selection_change_tos, chart_onset_pacing, full_chart
from components.utils.txtToJson import fetch_data
#from components.page.header import header

pv.OFF_SCREEN = True


@TrameApp()
class App_Hearth_Helper:


    def __init__(self,name=None,  table_size=10):
        self.server = get_server(name, client_type="vue2")   
           
        self.pl
        self._page_heart = True
        self._page_data = False
        self._has_heart = False 
        self.ui = self._build_ui()
        
    @property
    def ctrl(self):
        return self.server.controller
    @property
    def state(self):
        return self.server.state

    @property
    def pl(self):
        if not hasattr(self, "_pl"):
            print("pl2")
            self._pl = pv.Plotter()
        return self._pl
    @property
    def mesh(self):
        return self._mesh
    @property
    def actor(self):
        return self._actor
    @property
    def data(self):
        return self._data

    @change("heart_file_exchange")
    def handle(self,heart_file_exchange, **kwargs):
        file = ClientFile(heart_file_exchange)
        if file.content:
            bytes = file.content
            with tempfile.NamedTemporaryFile(suffix=file.name) as path:
                with open(path.name, 'wb') as f:
                    f.write(bytes)
                ds = pv.read(path.name)
            self._mesh=ds
            print(type(self._mesh).__name__)
            if(type(self._mesh).__name__ == "UnstructuredGrid"):
                self._actor = self.pl.add_mesh(ds, name=file.name)
                cell_center = self.mesh.cell_centers().points[0]
                arrow = vtk.vtkConeSource()
                arrow_mesh = self.pl.add_mesh(arrow, color="red")
            else:
                self.pl.add_mesh(ds, name=file.name)

            self.pl.reset_camera()
            self._update_UI()
        else:
            self.pl.clear_actors()
            self.pl.reset_camera()  
    @change("data_file_exchange")
    def handle_data(self,data_file_exchange, **kwargs):
        file = ClientFile(data_file_exchange)
        if file.content:
            self._data = fetch_data(file.name)
            self._update_UI()
    @change("log_scale")
    def set_log_scale(self,log_scale=False, **kwargs):
        if  hasattr(self, "_actor"):
            self.actor.mapper.lookup_table.log_scale = log_scale
            self.ctrl.view_update()
            self.ui = self._update_UI()

    @change("scalars")
    def set_scalars(self, **kwargs):
        if  hasattr(self, "_mesh"):
            scalars=self.mesh.active_scalars_name
            self.actor.mapper.array_name = scalars
            self.actor.mapper.scalar_range = self.mesh.get_data_range(scalars)
            self.ctrl.view_update()

    @change("page_heart_visibility")
    def set_page_heart(self,page_heart_visibility, **kwargs):
        self._page_heart = page_heart_visibility
        self._page_data = not page_heart_visibility
        self.ui = self._update_UI()

    @change("page_chart_visibility")
    def set_page_data(self,page_chart_visibility, **kwargs):
        self._page_data = page_chart_visibility
        self._page_heart = not page_chart_visibility
        self.ui = self._update_UI()

    def _build_ui(self):
       return self._update_UI()
    
    def header(self):         
        vuetify.VSpacer()

        vuetify.VCheckbox(
        v_model=("page_heart_visibility", self._page_data),
        on_icon="mdi-heart-settings",
        off_icon="mdi-heart-settings-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
        value=self._page_heart
        )
        vuetify.VBtn(
            icon="mdi-heart-settings",
            classes="mx-1",
        )
      
        vuetify.VFileInput(
            show_size=True,
            small_chips=True,
            truncate_length=25,
            v_model=("heart_file_exchange", None),
            dense=True,
            hide_details=True,
            style="max-width: 300px;",
        )
        vuetify.VSpacer()

        vuetify.VCheckbox(
        v_model=("page_chart_visibility", self._page_heart),
        on_icon="mdi-file-chart",
        off_icon="mdi-file-chart-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
        value=self._page_data
    )  
        vuetify.VFileInput(
            show_size=True,
            small_chips=True,
            truncate_length=25,
            v_model=("data_file_exchange", None),
            dense=True,
            hide_details=True,
            style="max-width: 300px;",
        )

        vuetify.VSpacer()
        with vuetify.VBtn(icon=True):
            vuetify.VIcon("mdi-restore")

        vuetify.VDivider(vertical=True, classes="mx-2")

        vuetify.VSwitch(
            v_model="$vuetify.theme.dark",
            hide_details=True,
            dense=True,
        )
        vuetify.VProgressLinear(
            indeterminate=True, absolute=True, bottom=True, active=("trame__busy",)
        )
    def scalar_dropdown(self):
        if  hasattr(self, "_mesh"):
            return vuetify.VSelect(
                label="Scalars",
                v_model=("scalars", self.mesh.active_scalars_name),
                items=("array_list", list(self.mesh.point_data.keys())),
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1 ml-2",
                style="max-width: 250px",
            ) 
    def _update_UI(self):
        with SinglePageWithDrawerLayout(self.server) as layout:
            with layout.toolbar:
                self.header()
            with layout.content:
                # Use PyVista UI template for Plotters
                self.main_view()
            with layout.drawer as drawer:
                drawer.width = "40%"
                vuetify.VDivider(classes="mb-2")
                with vuetify.VCard():

                    self.scalar_dropdown()
                    self.draw_table()
                    vuetify.VCardText(children=["This is a heart mesh"])
        return layout
    def draw_table(self):
        if hasattr(self, "_actor"):
            vuetify.VCheckbox(
                    label="Log Scale",
                    v_model=("log_scale", False),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                )
        if  hasattr(self, "_data"):
            with vuetify.VContainer(classes="justify-left ma-6") as container:
                """fig = vega.Figure(classes="ma-2", style="width: 100%;")
                self.ctrl.fig_update = fig.update"""
            return vuetify.VDataTable(**table_of_simulation(self.data))
    def main_view(self):
        if  hasattr(self, "_actor"):
            with vuetify.VContainer(fluid=True, classes="pa-0 fill-height") as container:
                view = plotter_ui(self.pl)
                self.ctrl.view_update = view.update
        else:
            vuetify.VCardText(children=["Add a heart file to start"])
            with vuetify.VContainer(fluid=True, classes="pa-0 fill-height",style="display:none") as container:
                view = plotter_ui(self.pl)
                self.ctrl.view_update = view.update

        return container
@TrameApp()
class App_show_Helper:
    def __init__(self,pl):
        self.pl=pl    
        self.ui = self._build_ui()

    def _build_ui(self):
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height") as container:
            view = plotter_ui(self.pl)
            self.ctrl.view_update = view.update


def main():
    app = App_Hearth_Helper()
    app.server.start(port=8000)

if __name__ == "__main__":
    # server.start()
    main()