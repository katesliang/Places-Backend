from flask_admin.contrib.sqla import ModelView


class PlacesAdminView(ModelView):
    column_searchable_list = (
        "name",
        "types"
    )
    column_editable_list = (
        "name",
        "lat",
        "lon",
        "types",
    )
    column_filters = ("types",)
    column_sortable_list = (
        "name",
        "types",
    )
    column_default_sort = ("name", True)
