from django.db import models
from products.models import Product
from django.contrib.auth.models import User



class Outlet(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




class DailyCosting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # NEW

    date = models.DateField()

    outlet = models.ForeignKey(Outlet,on_delete=models.CASCADE)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    opening_stock = models.IntegerField(default=0)

    requisition = models.IntegerField(default=0)

    complimentary = models.IntegerField(default=0)

    complimentary_bfast = models.IntegerField(
        default=0, 
        verbose_name="Complimentary Breakfast"
    )

    closing_stock = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    
    

    def total_stock(self):
        return self.opening_stock + self.requisition

    def sales(self):
        return (
            self.total_stock()
            - self.complimentary
            - self.closing_stock
        )

    def cost_of_production(self):
        return self.sales() * self.product.rate

    def revenue(self):
        return self.sales() * self.product.sales_price
    
    def gross_profit(self):
        return self.revenue() - self.cost_of_production()

    def ratio(self):

        revenue = self.revenue()

        if revenue > 0:
            return (
                self.gross_profit()
                / revenue
            ) * 100

        return 0
    


    def __str__(self):
        return f"{self.outlet.name} - {self.product.name}"