from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.http import QueryDict
from django.urls import reverse
from rest_framework.decorators import api_view
from .models import Main, Table, Contractor, Sources
from .serializers import MainSerializer
from django.contrib import messages
from django.views.generic import TemplateView
from rest_framework import status
from django.views.generic.edit import UpdateView
from rest_framework.response import Response
import csv
import io
import re


def reformat_date(date):
    pattern = "\d\d.\d\d.\d\d\d\d"
    if re.match(pattern, date):
        mo = date[3:5]
        day = date[0:2]
        year = date[6:]
        date = year + '-' + mo + '-' + day
        return date


def create_contractor(name):
    if name:
        contractor, _ = Contractor.objects.get_or_create(name=name)
        return contractor
    else:
        return None


def format_price(price):
    price = re.sub("[^0-9]", "", price)
    return price


def upload_table(request):
    if request.method == 'GET':
        return render(request, template_name="upload.html")

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        HttpResponseBadRequest()

    dataset = csv_file.read().decode('UTF-8')
    io_str = io.StringIO(dataset)
    next(io_str)  # skip header

    table_id = request.POST.get('table_id')

    if table_id:
        base = Table.objects.get(pk=table_id)
    else:
        base, _ = Table.objects.get_or_create(name=csv_file.name, file=csv_file)
    for column in csv.reader(io_str, delimiter=",", quotechar="|"):
        if "+" in column[9]:
            column[9] = True
        else:
            column[9] = False

        try:
            column[4] = int(column[4])
        except ValueError:
            column[4] = 0

        column[0] = reformat_date(column[0])
        column[2] = format_price(column[2])

        contractor = create_contractor(column[1])
        source, _ = Sources.objects.get_or_create(name=column[5])
        _, created = Main.objects.update_or_create(
            date=column[0],
            project=contractor,
            price=column[2],
            numbers=column[3],
            used=column[4],
            source=source,
            formation=column[6],
            responsible=column[7],
            link=column[8],
            status=column[9],
            comments=column[10],
            related_model=base
        )

    messages.success(request, f"База была успешно загружена!")
    return render(request, "upload.html")


def bases_view(request):
    bases = Table.objects.all()
    context = {
        'bases': bases
    }
    return render(request, "bases.html", context)


def delete_base_file(request, id):
    db = Table.objects.get(pk=id)
    if db:
        db.delete()
        messages.success(request, f"База удалена!")
    return redirect(reverse('bases'))


def show_database(request, id):
    db = Table.objects.get(pk=id)
    content = Main.objects.filter(related_model=db)
    context = {
        'table': db,
        'data': content,
    }
    return render(request, "table.html", context)


@api_view(('GET',))
def get_json_database(request, id):
    try:
        db = Table.objects.get(pk=id)
    except Table.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    content = Main.objects.filter(related_model=db)
    serializer = MainSerializer(content, many=True)

    return JsonResponse(serializer.data, safe=False)


class drfTableView(TemplateView):
    template_name = 'drf_Table.html'


class update_table_row(UpdateView):
    model = Main
    fields = ['date', 'price', 'project', 'price', 'numbers',
              'used', 'source', 'formation', 'link', 'status',
              'comments']
    template_name = 'tablerow.html'

    def get_success_url(self):
        return reverse('bases')
