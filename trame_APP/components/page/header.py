from trame.widgets import vuetify2 as vuetify

def header():         
    vuetify.VSpacer()
    vuetify.VFileInput(
        show_size=True,
        small_chips=True,
        truncate_length=25,
        v_model=("file_exchange", None),
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