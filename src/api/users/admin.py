from flask_admin.contrib.sqla import ModelView


class UsersAdminView(ModelView):
    column_searchable_list = ("email", "username")
    column_editable_list = ("email", "created_date", "username")
    column_filters = ("email", "username")
    column_sortable_list = ("email", "created_date", "username")
    column_default_sort = ("created_date", True)
