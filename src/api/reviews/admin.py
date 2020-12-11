from flask_admin.contrib.sqla import ModelView


class ReviewsAdminView(ModelView):
    column_searchable_list = ("place_id", "user_id")
    column_editable_list = ("rating", "text")
    column_filters = ("place_id",)
    column_sortable_list = ("place_id", "user_id")
    column_default_sort = ("place_id", True)
