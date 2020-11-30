from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.urls import reverse
from .constants import *
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
    for row in csv.reader(io_str, delimiter=",", quotechar="|"):
        if "+" in row[STATUS]:
            row[STATUS] = True
        else:
            row[STATUS] = False

        try:
            row[USED] = int(row[USED])
        except ValueError:
            row[USED] = 0

        row[DATE] = reformat_date(row[DATE])
        row[PRICE] = format_price(row[PRICE])

        contractor = create_contractor(row[PROJECT])
        source, _ = Sources.objects.get_or_create(name=row[SOURCE])
        _, created = Main.objects.update_or_create(
            date=row[DATE],
            project=contractor,
            price=row[PRICE],
            numbers=row[NUMBERS],
            used=row[USED],
            source=source,
            formation=row[FORMATION],
            responsible=row[RESPONSIBLE],
            link=row[LINK],
            status=row[STATUS],
            comments=row[COMMENTS],
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


class DrfTableView(TemplateView):
    template_name = 'drf_Table.html'


class UpdateTableRow(UpdateView):
    model = Main
    fields = ['date', 'price', 'project', 'price', 'numbers',
              'used', 'source', 'formation', 'link',
              'responsible', 'comments']

    template_name = 'tablerow.html'

    def get_success_url(self):
        url = reverse('new', kwargs={'id': self.object.related_model.id})
        return url + f"?t={self.object.related_model.id}"
