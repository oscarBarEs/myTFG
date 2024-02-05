from trame.widgets import vuetify2 as vuetify

def header():         
    vuetify.VSpacer()
    vuetify.VFileInput(
        multiple=True,
        show_size=True,
        small_chips=True,
        truncate_length=25,
        v_model=("files", None),
        dense=True,
        hide_details=True,
        style="max-width: 300px;",
        accept=".vtp",
        __properties=["accept"],
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