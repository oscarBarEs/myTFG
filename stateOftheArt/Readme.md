```mermaid
graph LR
A[Apis Graficas] --> B[VTK]
A -- No funciona actualmente --> C[Pyvista]
B --> D[Interfaz web 2D]
C --> D
D --> E[Vuetify]
D --> F[HTML]
E --> G[Renders]
F --> G
G --> H[Trame]
G --> I[VTKjs]
G --> J[ParaViewWeb]
G --> K[Dash Plotly]
```