import os
import re 

import pyvista as pv

from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.router import RouterViewLayout
from trame.widgets import router,trame


from trame.ui.vuetify2 import SinglePageWithDrawerLayout
from trame.widgets import vuetify2 as vuetify,html, vega, vtk as vtkTrame

from trame.decorators import TrameApp, change, life_cycle

from components.tableOfSimulation import table_of_simulation, selection_change_tos, chart_onset_pacing





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
    def __init__(self,ventricle,endo,core,res):
        self.ventricle = ventricle
        self.endo = endo
        self.core = core
        self.res = res


@TrameApp()
class App_Hearth_Helper:


    def __init__(self,name=None,  table_size=10):

        self.server = get_server(name, client_type="vue2")  
        self.isPage=0
        self.pl
        self.currentCase = None
        self.last_node_clicked = None
        self._data = None

        self.chartType =""
        if self.server.hot_reload:
            self.server.controller.on_server_reload.add(self._build_ui)

        self.ui = self._build_ui()
        self.state.trame__title = "MyTFG"
        self.state.update({
             "tooltip": "",
        })
        self.ctrl.view_update()
    
    

    def update_arritmic_info(self,arritmic_info):
        with self.server.ui.arritmic_info as arritmic_info:
            arritmic_info.clear()
            vuetify.VCardText(children=[arritmic_info])

    @property
    def ctrl(self):
        return self.server.controller
    @property
    def state(self):
        return self.server.state

    @property
    def pl(self):
        if not hasattr(self, "_pl"):
            self._pl = pv.Plotter()
        return self._pl

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

            ds = pv.read(ventricle_file)
            mesh=ds
            actor = self.pl.add_mesh(ds,name = ventricle_file,opacity=1)
        
            ventricle = VentricleVTK(mesh,actor)
            return ventricle
        

    def setArritmicView(self):
        self.vtk_mapping={}
        for dat in self.data:
            idReen =int(dat["Id's Reen"])
            idPac =int(dat["id_extraI"])
            cx = self.currentCase.ventricle.mesh.points[idReen]   
            reenName= "Reen"+str(idReen) + "_" + str(dat["idReentrada"])

            
            reenActor = self.pl.add_mesh(pv.Sphere(radius=1.5,center=cx), color="red", name=reenName)
            reenActor.visibility = 0
            self.vtk_mapping[self.get_scene_object_id(reenActor)] = reenName

            
            cy = self.currentCase.ventricle.mesh.points[idPac]
            pacName= "Pac"+str(idPac)+ "_" + str(dat["idReentrada"])
            pacActor = self.pl.add_mesh(pv.Sphere(radius=1.5,center=cy), color="blue", name=pacName)
            pacActor.visibility = 0
            self.vtk_mapping[self.get_scene_object_id(pacActor)] = pacName



    @change("log_scale")
    def set_log_scale(self,log_scale=False, **kwargs):
        self.currentCase.ventricle.actor.mapper.lookup_table.log_scale = log_scale
        self.ctrl.view_update()

    @change("scalars")
    def set_scalars(self,scalars, **kwargs):
        # scalars=self.currentCase.ventricle.mesh.active_scalars_name
        self.currentCase.ventricle.actor.mapper.array_name = scalars
        self.currentCase.ventricle.mesh.set_active_scalars(scalars)   ## Update en la malla !!
        
        self.pl.scalar_bar.SetTitle(scalars)
        self.currentCase.ventricle.actor.mapper.scalar_range = self.currentCase.ventricle.mesh.get_data_range(scalars)
        self.ctrl.view_update()



    @change("opacity")
    def set_opacity(self,opacity, **kwargs):
        self.currentCase.ventricle.actor.GetProperty().SetOpacity(opacity)
        self.ctrl.view_update()
# --------------------------------------------------------------------------------
# DATA CHARTS PIPELINE
# --------------------------------------------------------------------------------

    @change("chartsType")
    def typeOfChart(self,chartsType, **kwargs):
        self.chartType = chartsType
        self.selection_change_tos(self.state.selection)

    @change("selection")
    def selection_change_tos(self,selection=[], **kwargs):
        # Chart
        chart = None
        if self.chartType == "Count Segmentos Reen":
            chart = selection_change_tos(selection)
        elif self.chartType == "Onset/Pacing":
            chart = chart_onset_pacing(selection)
        if chart is not None:
            self.ctrl.fig_update(chart)
        if self.currentCase is not None:
            for x in selection:
                idReen =int(x["Id's Reen"])
                reenName= "Reen"+str(idReen)+ "_" + str(x["idReentrada"])
                self.pl.renderer.actors[reenName].visibility = 1

                idPac =int(x["id_extraI"])
                pacName= "Pac"+str(idPac)+ "_" + str(x["idReentrada"])
                self.pl.renderer.actors[pacName].visibility = 1

            not_selected = [item for item in self.data if item not in selection]
            for x in not_selected:
                idReen =int(x["Id's Reen"])
                reenName= "Reen"+str(idReen)+ "_" + str(x["idReentrada"])
                self.pl.renderer.actors[reenName].visibility = 0

                idPac =int(x["id_extraI"])
                pacName= "Pac"+str(idPac) + "_" + str(x["idReentrada"])
                self.pl.renderer.actors[pacName].visibility = 0

            self.ctrl.view_update()

# --------------------------------------------------------------------------------
# Interactor Pipeline
# --------------------------------------------------------------------------------

    def colour_back(self):
        if self.last_node_clicked is not None:
            if "Pac" in self.last_node_clicked:
                self.pl.renderer.actors[self.last_node_clicked].prop =pv.Property(color='blue')
            else:
                self.pl.renderer.actors[self.last_node_clicked].prop =pv.Property(color='red')
            # self.pl.renderer.actors[self.last_node_clicked].mapper.dataset.scale([1.0, 1.0, 1.0], inplace=True)

    def on_click(self, event):
        self.state.tooltip = ""
        self.state.tooltipStyle = {"display": "none"}        
        if event is None:
            print("Click on: --nothing--")
            if self.last_node_clicked is not None:
                self.colour_back()            
        else:
            nameActor = self.vtk_mapping.get(event.get('remoteId'))
            print("NAME: ",f"Click on: {nameActor}")
            if nameActor is not None:
                id = nameActor.split('_')[1]
                data = next((item for item in self.state.selection if item['idReentrada'] == int(id)), None)

                pacing_value = str(int((float(data['Segmento AHA']))))
                reen_value = str(int(float((data['Segmentos Reen']))))

                # generate the string
                result = f'Reen: {reen_value}       Pac: {pacing_value}'
                pixel_ratio = 2
                self.state.tooltip = result
                self.state.tooltipStyle = {
                    "position": "absolute",
                    "left": f"{(0 / pixel_ratio )+ 10}px",
                    "bottom": f"{(0 / pixel_ratio ) + 10}px",
                    "zIndex": 10,
                    "pointerEvents": "none",
                }                
                
                if "Reen" in nameActor:
                    mode = "Pac"
                    idMode = data['id_extraI']
                else:
                    mode = "Reen"
                    idMode = data['Id\'s Reen']

                nameOther = mode + idMode + '_' + str(data['idReentrada'])
                self.pl.renderer.actors[nameOther].prop =pv.Property(color='green')
                if self.last_node_clicked is not None:
                    self.colour_back()
                self.last_node_clicked = nameOther
                self.ctrl.view_update()

            else:
                self.colour_back()
                self.last_node_clicked = None
                        


# --------------------------------------------------------------------------------
# DYNAMIC LAYOUT
# --------------------------------------------------------------------------------


    def update_data_table(self):
            with self.server.ui.data_table as data_table:
                data_table.clear()
                if self.data is not None:                
                    with vuetify.VContainer(classes="justify-left ma-6"):
                        """fig = vega.Figure(classes="ma-2", style="width: 100%;")
                        self.ctrl.fig_update = fig.update"""
                        vuetify.VDataTable(**table_of_simulation(self.data))
            
                else:
                        vuetify.VCardText(children=["Select a case to start"])

    def update_Page(self, *num, **kwargs):
        self.isPage = num[0]

        self.update_home_icon()
        self.update_heart_icon()
        self.update_chart_icon()

        self.update_drawer_heart()
        self.update_charts_dropdown()


    def update_home_icon(self):
        with self.server.ui.home_icon as home_icon:
            home_icon.clear()
            if  self.isPage == 0:
                vuetify.VIcon("mdi-home-variant")
            else:
                vuetify.VIcon("mdi-home-variant-outline")

    def update_heart_icon(self):
        with self.server.ui.heart_icon as heart_icon:
            heart_icon.clear()
            if  self.isPage == 1:
                vuetify.VIcon("mdi-heart-settings")
                self.ctrl.view_update()
            else:
                vuetify.VIcon("mdi-heart-settings-outline")
    def update_chart_icon(self):
        with self.server.ui.chart_icon as chart_icon:
            chart_icon.clear()
            if  self.isPage == 2:
                vuetify.VIcon("mdi-file-chart")
            else:
                vuetify.VIcon("mdi-file-chart-outline")

    def update_drawer_heart(self):
        with self.server.ui.list_array as array_list:
            array_list.clear()
            if self.currentCase is not None and self.isPage == 1:
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
                                label="Data Arrays",
                                v_model=("scalars", self.currentCase.ventricle.mesh.active_scalars_name),
                                items=("array_mappes", list(self.currentCase.ventricle.mesh.point_data.keys())),
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
                vuetify.VDivider()
                with vuetify.VContainer():
                    with vuetify.VRow() as visibilityMeshes:
                        # 
                        vuetify.VSpacer()
                        vuetify.VCheckbox(
                            label="Endo",
                            v_model=("endoVisibilty", True),
                            hide_details=True,
                            dense=True,
                            outlined=True)
                        vuetify.VCheckbox(
                            label="Core",
                            v_model=("coreVisibilty", True),
                            hide_details=True,
                            dense=True,
                            outlined=True)
                        vuetify.VSpacer()
                vuetify.VSpacer()
                vuetify.VDivider()

    def update_charts_dropdown(self):
        with self.server.ui.charts_type_array as charts_type_array:
            #self.server.ui.list_array.clear()
            charts_type_array.clear()
            if self.data is not None and self.isPage == 2:

                chartsType = ["Count Segmentos Reen", "Onset/Pacing"]
                vuetify.VSelect(
                                label="Chart Type",
                                v_model=("chartsType", chartsType[0]),
                                items=("array_charts", chartsType),
                                hide_details=True,
                                dense=True,
                                outlined=True,
                                classes="pt-1 ml-2",
                                style="max-width: 250px",
                            )
    @change("endoVisibilty")
    def set_endo_visibility(self,endoVisibilty, **kwargs):
        if self.currentCase is not None:
            self.currentCase.endo.actor.visibility = endoVisibilty
            self.ctrl.view_update()
    @change("coreVisibilty")
    def set_core_visibility(self,coreVisibilty, **kwargs):
        if self.currentCase is not None:
            self.currentCase.core.actor.visibility = coreVisibilty
            self.ctrl.view_update()
                

                
        
# --------------------------------------------------------------------------------
# UI LAYOUT
# --------------------------------------------------------------------------------
    
    
       
    
    def header(self,layout):         
        vuetify.VSpacer()
        #FILE
        with vuetify.VBtn(icon=True,click=(self.update_Page,"[0, $event]"),to="/"):
            self.server.ui.home_icon(layout)
            self.update_home_icon()

        with vuetify.VBtn(icon=True,click=(self.update_Page,"[1, $event]"),to="/heart"):
            self.server.ui.heart_icon(layout)
            self.update_heart_icon()

        with vuetify.VBtn(icon=True,click=(self.update_Page,"[2, $event]"),to="/data"):
            self.server.ui.chart_icon(layout)
            self.update_chart_icon()


        vuetify.VSpacer()
        with vuetify.VBtn(icon=True,click=self.resetCase):
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
    
    def actives_change(self,ids, **kwargs):
        self.resetCase()       
        _id = ids[0]
        if  "caso_" in _id:
            self.pl.clear() 
            self._data = None
            rootFolder = next((root for id, root in self.casos if id == _id), None)
            for root, dirs, files in os.walk(rootFolder):
                for file in files:
                    ventricle = None
                    endo = None
                    core = None
                    res = None
                    # Print the names of the files in the root
                    for file in os.listdir(root):
                        if file.endswith(".vtk"):
                            if file.startswith("ventricle"):
                                ventricle = file
                            elif file.startswith("Endo"):  
                                endo = file
                            elif file.startswith("Core"):
                                core = file                      
                            
                        elif file.endswith(".txt"):
                            res = file
                    if ventricle and endo and core and res:

                        ventricle = os.path.join(root,ventricle)

                        ds = pv.read(ventricle)
                        mesh=ds

                        actor = self.pl.add_mesh(ds,name = ventricle,opacity=1,scalars="17_AHA")
                        ven = VentricleVTK(mesh,actor)

                        self.pl.scalar_bar.SetNumberOfLabels(17)

                        endo = os.path.join(root,endo)
                        end= self.getVtkActor(endo)
                        self.pl.remove_scalar_bar("subpartID")


                        core = os.path.join(root,core)
                        cor = self.getVtkActor(core)

                        res = os.path.join(root,res)
    
                        res = self.fetch_data_autoRead(res)
                        self._data = res

                        self.currentCase = dataArritmic(ven,end,cor,res)
                        self.setArritmicView()                         
                        self.update_drawer_heart()
                        self.update_data_table()
                        self.update_charts_dropdown()
                        self.pl.reset_camera()
                        self.ctrl.view_update()                        

    def resetCase(self, **kwargs):
        print("reset")
        self.pl.clear_actors()
        self.ctrl.view_update()
        self._data = None
        self.update_data_table()

        self.currentCase = None
        self.update_drawer_heart()
        self.update_charts_dropdown()
        self.pl.reset_camera()
        self.ctrl.view_update()


    def fetch_data_autoRead(self,json_file):
        data = {}
        with open(json_file, 'r', encoding='utf-8') as file:
            lines = iter(file.readlines())
            for line in lines:
                if line.strip() == "PARÁMETROS DE SIMULACIONES CON REENTRADA:":
                    break
            datos = []
            x=0
            for line in lines:
                
                parts = line.split('->')
                if(parts.__len__() > 2):
                    data = {}
                    data["idReentrada"] = x
                    x+=1                    
                    subparts = parts[2].split(',')
                    for i, subpart in enumerate(subparts):
                        if ':' in subpart:
                            
                            key, value = subpart.split(':')
                            data[key.strip()] = value.strip()
                        else:
                            split_subpart = re.split('(\d.*)', subpart, maxsplit=1)
                            if len(split_subpart) > 1:
                                key = split_subpart[0].strip()
                                value = split_subpart[1].strip()
                                data[key] = value
                    datos.append(data)
        return datos

    def _build_ui(self):
        with RouterViewLayout(self.server, "/"):
            with vuetify.VCard() as card:
                card.classes="fill-width"
                vuetify.VCardTitle("Main Page")
                vuetify.VCardText(children=["Add the file heart to see it, and the file data to see the results. I interact with the data to see the results"])

                def generate_sources(root_dir):
                    sources = []
                    id_counter = 1
                    dir_ids = {root_dir: "0"}  # Keep track of directory ids

                    for root, dirs, files in os.walk(root_dir):
                        depth = root[len(root_dir):].count(os.sep)

                        for dir in dirs:
                            dir_path = os.path.join(root, dir)
                            parent_id = dir_ids[root]  # Get the id of the parent directory
                            dir_ids[dir_path] = str(id_counter)  # Store the id of the current directory
                            if depth > 0:  # If the directory is a subfolder, add 100 to its id
                                id_caso = "caso_" + str(id_counter)
                                case = {"id": id_caso, "parent": parent_id, "visible": 1, "name": dir}
                                self.casos.append((id_caso, dir_path))
                            else:
                                id_doc = "doc_" + str(id_counter)
                                case = {"id": str(id_counter), "parent": parent_id, "visible": 1, "name": dir}
                            
                            sources.append(case)
                            id_counter += 1

                    return sources
                self.casos = []  # Array to store the id and root of each "caso"
       
                root_dir = "./casos"  # Cambia esto a la ruta de tu directorio raíz
                self.sources = generate_sources(root_dir)            
                trame.GitTree(
                    sources=(
                        "pipeline",
                        self.sources,
                    ),
                    actives_change=(self.actives_change, "[$event]")
                )

        # --------------------------------------------------------------------------------
        # HEART LAYOUT
        # --------------------------------------------------------------------------------
                
        with RouterViewLayout(self.server, "/heart") as layout:
            layout.root.classes="fill-height"
            with vuetify.VCard():
                vuetify.VCardTitle("This is Visualizer")            
                vuetify.VCardText(children=["Select a Case <br> Red = Reeentry, Blue = Pacing"]) 
                self.server.ui.arritmic_info(layout)
            with vuetify.VCard(
                style=("tooltipStyle", {"display": "none"}), elevation=2, outlined=True
            ):
                with vuetify.VCardText():
                    html.Pre("{{ tooltip }}")
            with vtkTrame.VtkLocalView(self.pl.ren_win,
                                       picking_modes=("picking_modes", ["click"]),
                            click=(self.on_click, "[$event]")
                )as local:
                    def view_update(**kwargs):
                        local.update(**kwargs)                
            self.ctrl.view_update = view_update
            self.get_scene_object_id = local.get_scene_object_id

        # --------------------------------------------------------------------------------
        # DATA LAYOUT
        # --------------------------------------------------------------------------------
        
        with RouterViewLayout(self.server, "/data") as dataView:
            with vuetify.VCard():
                vuetify.VCardTitle("Data from Multi Sim")
                fig = vega.Figure(classes="ma-2", style="width: 90%;")
                self.ctrl.fig_update = fig.update                
                self.server.ui.data_table(dataView)

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
                vuetify.VDivider(classes="mb-2")
                with vuetify.VCard() as cardDrawer2:
                    self.server.ui.charts_type_array(layout)
                   
        return layout
    




        
# --------------------------------------------------------------------------------
# APP PIPELINE
# --------------------------------------------------------------------------------
    
def main():
    app = App_Hearth_Helper()
    app.server.start(port=8000)

if __name__ == "__main__":
    main()