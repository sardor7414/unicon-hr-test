from django.db import models

# Create your models here.

class DefaultAbstract(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Region(DefaultAbstract):
    name = models.CharField(max_length=155, verbose_name="Viloyat nomi:", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Областы"


class District(DefaultAbstract):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Viloyatni tanlang: ")
    name = models.CharField(max_length=150, verbose_name="Tuman nomini kiriting: ", unique=True)
    user = models.ForeignKey("user.User", on_delete=models.SET_NULL, verbose_name="Adminstratorni tanlang: ", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Районы"


class Task(DefaultAbstract):
    name = models.CharField(max_length=255, verbose_name="Vazifani kiriting: ")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Задания"


class Member(DefaultAbstract):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Viloyatni tanlang")
    district = models.ForeignKey(District, on_delete=models.CASCADE, verbose_name="Tumanni tanlang")
    full_name = models.CharField(max_length=255, verbose_name="Xodimning FIO")
    phone = models.CharField(max_length=13, unique=True)
    user = models.ForeignKey("user.User", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Adminstratorni tanlang: ")
    telegram_id = models.BigIntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name_plural = "Сотрудники"


class Todo(DefaultAbstract):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="Xodimni tanlang: ")
    organization = models.CharField(max_length=255, verbose_name="Tashkilotni kiriting: ")
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Vazifani tanlang: ")
    location = models.JSONField(verbose_name="Joylashuv", blank=True, null=True)
    photo = models.ImageField(upload_to='todos/', verbose_name="Rasm")
    

    def __str__(self):
        return f"{self.member}->{self.task}"

    class Meta:
        verbose_name_plural = "Работа выполнена"

