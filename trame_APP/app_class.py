
import tempfile
from enum import Enum

import vtk
import pyvista as pv
from pyvista import examples
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.app.file_upload import ClientFile
from trame.ui.router import RouterViewLayout
from trame.widgets import router


from trame.ui.vuetify2 import SinglePageWithDrawerLayout
from trame.widgets import vuetify2 as vuetify, vega, vtk as vtkTrame
from trame.widgets.vtk import VtkLocalView, VtkRemoteView

from trame.decorators import TrameApp, change, life_cycle

from components.tableOfSimulation import table_of_simulation, selection_change_tos, chart_onset_pacing, full_chart
from components.utils.txtToJson import fetch_data
#from components.page.header import header

pv.OFF_SCREEN = True

@TrameApp()
class App_Hearth_Helper:


    def __init__(self,name=None,  table_size=10):

        self.server = get_server(name, client_type="vue2")  
        self.isPage=True
        self.pl

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
    @property
    def view(self):
        if not hasattr(self, "_view"):
            self._view = plotter_ui(self.pl)
        return self._view
    def update_Page(self):
        self.isPage = not self.isPage
        self.update_heart_icon()
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
                # self.ctrl.letsChangeome()
                cell_center = self.mesh.cell_centers().points[0]
                self.update_scalar_dropdown()
            else:
                self.pl.add_mesh(ds, name=file.name)

            self.pl.reset_camera()
            # self._update_UI()
        else:
            self.pl.clear_actors()
            self.pl.reset_camera()  
    @change("data_file_exchange")
    def handle_data(self,data_file_exchange, **kwargs):
        file = ClientFile(data_file_exchange)
        if file.content:
            self._data = fetch_data(file.name)
            self.update_data_table()
            # self.ctrl.letsChangeome()


    def update_data_table(self):
        with self.server.ui.data_table as data_table:
            data_table.clear()
            if  (hasattr(self, "_data")):
                with vuetify.VContainer(classes="justify-left ma-6"):
                    """fig = vega.Figure(classes="ma-2", style="width: 100%;")
                    self.ctrl.fig_update = fig.update"""
                    vuetify.VDataTable(**table_of_simulation(self.data))
        
            else:
                    vuetify.VCardText(children=["Add a data file to start"])

    @change("log_scale")
    def set_log_scale(self,log_scale=False, **kwargs):
        if  hasattr(self, "_actor"):
            self.actor.mapper.lookup_table.log_scale = log_scale
            self.ctrl.view_update()
            # self.ui = self._update_UI()

    @change("scalars")
    def set_scalars(self, **kwargs):
        if  hasattr(self, "_mesh"):
            scalars=self.mesh.active_scalars_name
            self.actor.mapper.array_name = scalars
            self.actor.mapper.scalar_range = self.mesh.get_data_range(scalars)
            self.ctrl.view_update()
    
    def _build_ui(self):
       return self._update_UI()
    
    def header(self,layout):         
        vuetify.VSpacer()
        #FILE
        with vuetify.VBtn(icon=True,click=self.update_Page,to="/heart"):
            # vuetify.VIcon("mdi-heart-settings",click=self.update_heart_icon)
            self.server.ui.heart_icon(layout)
            self.update_heart_icon()

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
        #FILE
        # vuetify.VCheckbox(
        # v_model=("page_chart_visibility", self._page_heart),
        # on_icon="mdi-file-chart",
        # off_icon="mdi-file-chart-outline",
        # classes="mx-1",
        # hide_details=True,
        # dense=True,
        # value=self._page_data
        # )  
        with vuetify.VBtn(icon=True,to="/data"):
            vuetify.VIcon("mdi-file-chart")
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
        with vuetify.VBtn(icon=True,to="/"):
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

    def update_heart_icon(self):
        with self.server.ui.heart_icon as heart_icon:
            heart_icon.clear()
            if  self.isPage:
                vuetify.VIcon("mdi-heart-settings")
            else:
                vuetify.VIcon("mdi-heart-settings-outline")


    def update_scalar_dropdown(self):
        
        with self.server.ui.list_array as array_list:
            print("array_list")
            self.server.ui.list_array.clear()
            print("update_scalar_dropdown")
            if  hasattr(self, "_mesh"):
                vuetify.VSelect(
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
        with RouterViewLayout(self.server, "/"):
            with vuetify.VCard() as card:
                card.classes="fill-width"
                vuetify.VCardTitle("Main Page")
                vuetify.VCardText(children=["Add the file heart to see it, and the file data to see the results. I interact with the data to see the results"])
        with RouterViewLayout(self.server, "/heart") as layout:
            layout.root.classes="fill-height"
            with vuetify.VCard():
                vuetify.VCardTitle("This is Visualizer")            
            if not hasattr(self, "_actor"):
                vuetify.VCardText(children=["Add a heart file to start"])             
            with vtkTrame.VtkLocalView(self.pl.ren_win)as local:
                    def view_update(**kwargs):
                        local.update(**kwargs)                
            self.ctrl.view_update = view_update


        with RouterViewLayout(self.server, "/data") as dataView:
            with vuetify.VCard():
                vuetify.VCardTitle("This is Data")
                self.server.ui.data_table(dataView)


        with SinglePageWithDrawerLayout(self.server) as layout:
            with layout.toolbar:
                self.header(layout)
            with layout.content:
                router.RouterView()
                # Use PyVista UI template for Plotters
                
            with layout.drawer as drawer:
                drawer.width = "40%"
                vuetify.VDivider(classes="mb-2")
                with vuetify.VCard() as cardDrawer:
                    with vuetify.VContainer() as containerArray:
                        self.server.ui.list_array(layout)
                    self.draw_table()
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

def main():
    app = App_Hearth_Helper()
    app.server.start(port=8000)

if __name__ == "__main__":
    # server.start()
    main()