from django.db import models

class CustomAutoField(models.AutoField):
    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return connection.ops.sequence_reset_sql(self.model._meta.db_table, [1000])
        return super().get_db_prep_value(value, connection, prepared)
    
class Customer(models.Model):
    customer_id = CustomAutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    age = models.IntegerField()
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    current_debt = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def approved_limit(self):
        return self.monthly_salary * 36
    
    @approved_limit.setter
    def approved_limit(self, value):
        self._approved_limit = value
        
    # Override save method to update _approved_limit before saving
    def save(self, *args, **kwargs):
        self._approved_limit = self.approved_limit
        super().save(*args, **kwargs)
# Create your models here.
