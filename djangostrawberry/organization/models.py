from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=200)
    establish_date = models.DateField(null=True, blank=True)
    ORD_ID = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    name = models.CharField(max_length=200)
    employee_id = models.IntegerField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    joining_date = models.DateField()
    releiving_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} (ID: {self.employee_id})"
