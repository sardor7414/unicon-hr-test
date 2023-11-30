# resources.py
from import_export import resources
from import_export.fields import Field
from .models import Todo

class TodoResource(resources.ModelResource):
    member_id = Field(column_name='member_id', attribute='member__id')  # Member modelining id maydonini olish
    member_full_name = Field(column_name='member_full_name', attribute='member__full_name')  # Member modelining full_name maydonini olish

    class Meta:
        model = Todo
        fields = ('id', 'member_id', 'member_full_name', 'organization', 'task', 'location', 'photo')  # Boshqa maydonlarni ham qo'shing
        import_id_fields = ['id']  # id ni import qilishni ko'rsatish




