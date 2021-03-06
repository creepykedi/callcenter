from django.db import models

# Create your models here.


class Contractor(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Table(models.Model):
    name = models.CharField(max_length=256)
    file = models.FileField()

    def __str__(self):
        return self.name


class Sources(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Main(models.Model):
    date = models.DateField(verbose_name="Дата")
    project = models.ForeignKey(Contractor, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Проект")
    price = models.DecimalField(max_digits=16, decimal_places=2, null=True,
                                blank=True, verbose_name="Цена")
    numbers = models.IntegerField(null=True, blank=True, verbose_name="Количество")
    used = models.IntegerField(default=0, blank=True, verbose_name="Использовано")
    remaining = models.IntegerField(null=True, blank=True, verbose_name="Остаток")
    source = models.ForeignKey(Sources, on_delete=models.CASCADE, null=True,
                               blank=True, verbose_name="Источник")
    formation = models.CharField(max_length=256, null=True, blank=True, verbose_name="Сформировано из")
    responsible = models.CharField(max_length=256, null=True, blank=True, verbose_name="Ответственный")
    link = models.URLField(null=True, blank=True, verbose_name="Ссылка")
    status = models.BooleanField(null=True, blank=True, default=False, verbose_name="Статус")
    comments = models.TextField(null=True, blank=True, verbose_name="Комментариий")
    cost_per_number = models.FloatField(null=True, blank=True, verbose_name="Цена за номер")
    related_model = models.ForeignKey(Table, on_delete=models.CASCADE, null=True, blank=True)

    def calculate_cost(self):
        if self.numbers and self.price:
            self.numbers = int(self.numbers)
            self.price = float(self.price)
            self.cost_per_number = self.price / self.numbers

    def calculate_remaining(self):
        if self.numbers and self.used:
            self.numbers = int(self.numbers)
            self.used = int(self.used)
            self.remaining = self.numbers - self.used
            if self.remaining == 0:
                self.status = True
        if not self.used:
            self.remaining = self.numbers

    def __str__(self):
        return f"{str(self.pk)}, {self.project}, осталось {self.remaining}"

    def save(self, *args, **kwargs):
        self.calculate_cost()
        self.calculate_remaining()
        super(Main, self).save(*args, **kwargs)
