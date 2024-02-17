# State of the Art

Para realizar la aplicacion necesitaremos 3 componentes:

- Las *apis graficas* para renderizar los objetos vtk
- Las *Librerias graficas* para visualizar la web
- Los *renders* para montar la aplicación

```mermaid
graph LR
A[Apis Graficas] --> B[VTK]
A -- No funciona actualmente con Trame --> C[Pyvista]
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