"""callcenters URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from callcenter.views import upload_table, bases_view,  \
    delete_base_file, get_json_database, drfTableView, update_table_row

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload-csv/', upload_table, name="upload"),
    path('', bases_view, name="bases"),
    path('tablesjs/<int:id>', get_json_database, name="js"),
    path('table/delete/<int:id>', delete_base_file, name="delete_db"),
    path('table/<int:id>', drfTableView.as_view(), name="new"),
    path('table/row/<slug:pk>', update_table_row.as_view(), name="update_row"),
]
