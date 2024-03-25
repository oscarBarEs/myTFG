import os
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
from trame.widgets import vuetify2 as vuetify, vega, vtk as vtkTrame,plotly
from trame.widgets.vtk import VtkLocalView, VtkRemoteView

from trame.decorators import TrameApp, change, life_cycle

from components.tableOfSimulation import table_of_simulation, selection_change_tos, chart_onset_pacing, full_chart
from components.utils.txtToJson import fetch_data
#from components.page.header import header

pv.OFF_SCREEN = True

class VentricleVTK:
    def __init__(self,mesh,actor):
        self.mesh = mesh
        self.actor = actor

class Arritmia:
    def __init__(self,reen,pacing):
        self.reen = reen
        self.pacing = pacing

class dataArritmic:
    def __init_(self,ventricle,endo,core,res,pname):
        self.ventricle = ventricle
        self.endo = endo
        self.core = core
        self.res = res
        self.pname = pname



@TrameApp()
class App_Hearth_Helper:


    def __init__(self,name=None,  table_size=10):

        self.server = get_server(name, client_type="vue2")  
        self.isPage=0
        self.arritmias = []
        self.pl
        self.casos = self.casesReader()
        self.chartType =""
        self.ui = self._build_ui()
        self.ctrl.view_update()
    
    

    def casesReader(self):
        casos = []
        rootFolder = os.path.join(os.path.dirname(__file__), 'casos')
        for root, dirs, files in os.walk(rootFolder):
            for file in files:
                ventricle = None
                endo = None
                core = None
                res = None
                if file.endswith(".vtk"):
                    if file.startswith("ventricle"):
                        ventricle = file
                        print(file)
                    elif file.startswith("Endo"):  
                        endo = file
                        print(file)
                    elif file.startswith("Core"):
                        core = file                      
                        print(file)
                    
                elif file.endswith(".txt"):
                    res = file
                    print(file)
                if ventricle and endo and core and res:
                    pname = os.path.basename(root)

                    ventricle = os.path.join(root,ventricle)
                    ven = self.getVtkActor(ventricle)

                    endo = os.path.join(root,endo)
                    end= self.getVtkActor(endo)

                    core = os.path.join(root,core)
                    cor = self.getVtkActor(core)

                    res = os.path.join(root,res)
   
                    ventricle = pv.read(ventricle)
                    endo = pv.read(endo)
                    core = pv.read(core)
                    res = fetch_data(res)

                    casos.append(dataArritmic(ven,end,cor,res,pname))
                
        return casos
    

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
    

# --------------------------------------------------------------------------------
# HEART PIPELINE
# --------------------------------------------------------------------------------
    def getVtkActor(self,ventricle_file):
        file = ClientFile(ventricle_file)
        if file.content:
            bytes = file.content
            with tempfile.NamedTemporaryFile(suffix=file.name) as path:
                with open(path.name, 'wb') as f:
                    f.write(bytes)
                ds = pv.read(path.name)
                mesh=ds
                actor = self.pl.add_mesh(ds, name=file.name)
            
                ventricle = VentricleVTK(mesh,actor)
                return ventricle
        

    @change("heart_file_exchange")
    def handle(self,heart_file_exchange, **kwargs):
        file = ClientFile(heart_file_exchange)
        if file.content:
            bytes = file.content
            with tempfile.NamedTemporaryFile(suffix=file.name) as path:
                with open(path.name, 'wb') as f:
                    f.write(bytes)
                ds = pv.read(path.name)
            
            if(type(ds).__name__ == "UnstructuredGrid"):
                self._mesh=ds
                self._actor = self.pl.add_mesh(ds, name=file.name,opacity=0)
                cell_center = self.mesh.cell_centers().points[0]
                self.update_scalar_dropdown()
                if hasattr(self, "_data"):
                    self.setArritmicView()

            else:
                self.pl.add_mesh(ds, name=file.name)

            self.pl.reset_camera()
            self.ctrl.view_update()
            # self._update_UI()
    def setArritmicView(self):

        for dat in self.data:
            print(dat)
            idReen =int(dat["Id's Reen"])
            idPac =int(dat["id_extraI"])
            cx = self.mesh.points[idReen]   
            # cxNormal =  arrows[idReen]
            reenName= "Reen"+str(idReen)
            # if self.pl.has_actor(reenName):
            #     return
            self.pl.add_mesh(pv.Sphere(radius=1.5,center=cx), color="red", name=reenName,opacity=0)
            cy = self.mesh.points[idPac]
            pacName= "Pac"+str(idPac)
            self.pl.add_mesh(pv.Sphere(radius=1.5,center=cy), color="blue", name=pacName,opacity=0)


    @change("log_scale")
    def set_log_scale(self,log_scale=False, **kwargs):
        self.actor.mapper.lookup_table.log_scale = log_scale
        self.ctrl.view_update()

    @change("scalars")
    def set_scalars(self,scalars, **kwargs):
        # scalars=self.mesh.active_scalars_name
        self.actor.mapper.array_name = scalars
        self.actor.mapper.scalar_range = self.mesh.get_data_range(scalars)
        self.ctrl.view_update()

    @change("opacity")
    def set_opacity(self,opacity, **kwargs):
        self.actor.GetProperty().SetOpacity(opacity)
        self.ctrl.view_update()
# --------------------------------------------------------------------------------
# DATA CHARTS PIPELINE
# --------------------------------------------------------------------------------

    @change("data_file_exchange")
    def handle_data(self, data_file_exchange, **kwargs):
        file = ClientFile(data_file_exchange)
        if file.content:
            try:
                self._data = fetch_data(file.name)
                self.update_data_table()
                self.update_charts_dropdown()
                if hasattr(self, "_mesh"):
                    self.setArritmicView()
            except UnicodeDecodeError:
                print(f"Error: File {file.name} is not in a valid format or encoding.")
                # Handle the error appropriately here
    @change("chartsType")
    def typeOfChart(self,chartsType, **kwargs):
        self.chartType = chartsType
    @change("selection")
    def selection_change_tos(self,selection=[], **kwargs):
        # Chart


        if self.chartType == "Count Segmentos Reen":
            chart = selection_change_tos(selection)
        else:
            chart = chart_onset_pacing(selection)

        self.ctrl.fig_update(chart)
        if hasattr(self, "_mesh"):
            newMesh = self.mesh.extract_surface()
            arrows = newMesh.point_normals
            print("Num Normales")
            print(len(arrows))
            print("Num Puntos")
            print(len(self.mesh.points))
            print("Arritmias")
            print(self.arritmias)
            for x in selection:
                idReen =int(x["Id's Reen"])
                reenName= "Reen"+str(idReen)
                self.pl.renderer.actors[reenName].GetProperty().SetOpacity(1)

                idPac =int(x["id_extraI"])
                pacName= "Pac"+str(idPac)
                self.pl.renderer.actors[pacName].GetProperty().SetOpacity(1)

            not_selected = [item for item in self.data if item not in selection]
            for x in not_selected:
                idReen =int(x["Id's Reen"])
                reenName= "Reen"+str(idReen)
                self.pl.renderer.actors[reenName].GetProperty().SetOpacity(0)

                idPac =int(x["id_extraI"])
                pacName= "Pac"+str(idPac)
                self.pl.renderer.actors[pacName].GetProperty().SetOpacity(0)

            self.ctrl.view_update()

# --------------------------------------------------------------------------------
# FULL INPUT FILE
# --------------------------------------------------------------------------------


    @change("rootFolder")
    def handlePAtients(self,rootFolder, **kwargs):
        print(rootFolder) 

# --------------------------------------------------------------------------------
# DYNAMIC LAYOUT
# --------------------------------------------------------------------------------


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

    def update_Page(self, *num, **kwargs):
        print(num[0])
        self.isPage = num[0]
        self.update_heart_icon()
        self.update_chart_icon()
        print("Actores")
        # print(self.pl.meshes)

    def update_heart_icon(self):
        with self.server.ui.heart_icon as heart_icon:
            heart_icon.clear()
            if  self.isPage == 1:
                vuetify.VIcon("mdi-heart-settings")
            else:
                vuetify.VIcon("mdi-heart-settings-outline")
    def update_chart_icon(self):
        with self.server.ui.chart_icon as chart_icon:
            chart_icon.clear()
            if  self.isPage == 2:
                vuetify.VIcon("mdi-file-chart")
            else:
                vuetify.VIcon("mdi-file-chart-outline")

    def update_scalar_dropdown(self):
        with self.server.ui.list_array as array_list:
            vuetify.VCardTitle(
                "Heart Visualization Options", 
                classes="grey lighten-1 py-1 grey--text text--darken-3",
                style="user-select: none; cursor: pointer",
                hide_details=True,
                dense=True,
            )
            array_list.clear()
            vuetify.VCheckbox(
                label="Log Scale",
                v_model=("log_scale", False),
                hide_details=True,
                dense=True,
                outlined=True,
            )
            vuetify.VSelect(
                            label="Mapper",
                            v_model=("scalars", self.mesh.active_scalars_name),
                            items=("array_mappes", list(self.mesh.point_data.keys())),
                            hide_details=True,
                            dense=True,
                            outlined=True,
                            classes="pt-1 ml-2",
                            style="max-width: 250px",
                        )
            vuetify.VSlider(
                label="Opacity",
                v_model=("opacity", 0.3),
                min=0.0,
                max=1.0,
                step=0.1)
            
    def update_charts_dropdown(self):
        with self.server.ui.charts_type_array as charts_type_array:
            #self.server.ui.list_array.clear()
            charts_type_array.clear()
            chartsType = ["Count Segmentos Reen", "Onset/Pacing"]
            vuetify.VSelect(
                            label="Scalars",
                            v_model=("chartsType", chartsType[0]),
                            items=("array_charts", chartsType),
                            hide_details=True,
                            dense=True,
                            outlined=True,
                            classes="pt-1 ml-2",
                            style="max-width: 250px",
                        )
        
        
# --------------------------------------------------------------------------------
# UI LAYOUT
# --------------------------------------------------------------------------------
    
    def _build_ui(self):
       return self._update_UI()
    
    def header(self,layout):         
        vuetify.VSpacer()
        #FILE
        with vuetify.VBtn(icon=True,click=(self.update_Page,"[1, $event]"),to="/heart"):
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
        with vuetify.VBtn(icon=True,click=(self.update_Page,"[2, $event]"),to="/data"):
            self.server.ui.chart_icon(layout)
            self.update_chart_icon()

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
        with vuetify.VBtn(icon=True,click=(self.update_Page,"[0, $event]"),to="/"):
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
         

    def _update_UI(self):
        with RouterViewLayout(self.server, "/"):
            with vuetify.VCard() as card:
                card.classes="fill-width"
                vuetify.VCardTitle("Main Page")
                vuetify.VCardText(children=["Add the file heart to see it, and the file data to see the results. I interact with the data to see the results"])
                vuetify.VFileInput(
                    show_size=True,
                    small_chips=True,
                    truncate_length=25,
                    v_model=("rootFolder", None),
                    dense=True,
                    hide_details=True,
                    style="max-width: 300px;",
                )
        # --------------------------------------------------------------------------------
        # HEART LAYOUT
        # --------------------------------------------------------------------------------
                
        with RouterViewLayout(self.server, "/heart") as layout:
            layout.root.classes="fill-height"
            with vuetify.VCard():
                vuetify.VCardTitle("This is Visualizer")            
            if not hasattr(self, "_actor"):
                vuetify.VCardText(children=["Add a heart file to start <br> Red = Reeentry, Blue = Pacing"])             
            with vtkTrame.VtkLocalView(self.pl.ren_win)as local:
                    def view_update(**kwargs):
                        local.update(**kwargs)                
            self.ctrl.view_update = view_update

        # --------------------------------------------------------------------------------
        # DATA LAYOUT
        # --------------------------------------------------------------------------------
        
        with RouterViewLayout(self.server, "/data") as dataView:
            with vuetify.VCard():
                vuetify.VCardTitle("This is Data")
                self.server.ui.data_table(dataView)
                fig = vega.Figure(classes="ma-2", style="width: 100%;")
                self.ctrl.fig_update = fig.update
        # --------------------------------------------------------------------------------
        # VIEW LAYOUT
        # --------------------------------------------------------------------------------
        

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
                    self.server.ui.list_array(layout)
                with vuetify.VCard() as cardDrawer:
                    self.server.ui.charts_type_array(layout)
                   
        return layout
    




        
# --------------------------------------------------------------------------------
# APP PIPELINE
# --------------------------------------------------------------------------------
    
def main():
    app = App_Hearth_Helper()
    app.server.start(port=8000)

if __name__ == "__main__":
    # server.start()
    main()