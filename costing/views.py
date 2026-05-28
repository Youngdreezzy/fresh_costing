from django.shortcuts import render, redirect
from products.models import Product
from .models import DailyCosting, Outlet
from django.contrib import messages
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required



@login_required(login_url='login')
def daily_costing(request):

    products = Product.objects.filter(
        is_active=True
    )

    outlets = Outlet.objects.all()

    if request.method == 'POST':

        date = request.POST.get('date')

        outlet_id = request.POST.get('outlet')

        outlet = Outlet.objects.get(id=outlet_id)

        for product in products:

            opening_stock = request.POST.get(
                f'opening_{product.id}'
            ) or 0

            requisition = request.POST.get(
                f'req_{product.id}'
            ) or 0

            complimentary = request.POST.get(
                f'comp_{product.id}'
            ) or 0

            complimentary_bfast = request.POST.get(f'comp_bfast_{product.id}') or 0

            closing_stock = request.POST.get(
                f'closing_{product.id}'
            ) or 0

            DailyCosting.objects.create(
                user=request.user,                                 # ← Important

                date=date,

                outlet=outlet,

                product=product,

                opening_stock=opening_stock,

                requisition=requisition,

                complimentary=complimentary,

                complimentary_bfast=complimentary_bfast,

                closing_stock=closing_stock,
            )

        messages.success(
            request,
            'Costing saved successfully'
            )

        return redirect('daily_costing')

    context = {
        'products': products,
        'outlets': outlets,
    }

    return render(
        request,
        'costing/daily_costing.html',
        context
    )





from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.db.models import Q

@login_required(login_url='login')
def saved_costings(request):
    # Start with all costings
    costings = DailyCosting.objects.select_related('product', 'outlet', 'user')\
        .order_by('-date', '-created_at')
    
    # Get search parameter from URL
    search_product = request.GET.get('product', '')
    
    # Apply filter if search term exists
    if search_product:
        # Since product is a ForeignKey, search on the name field of the related product model
        costings = costings.filter(
            Q(product__name__icontains=search_product)  # This assumes your Product model has a 'name' field
        )
    
    # Pagination: Show 25 entries per page
    paginator = Paginator(costings, 10)
    page = request.GET.get('page', 1)
    
    try:
        costings_page = paginator.page(page)
    except PageNotAnInteger:
        costings_page = paginator.page(1)
    except EmptyPage:
        costings_page = paginator.page(paginator.num_pages)
    
    context = {
        'costings': costings_page,
        'paginator': paginator,
        'search_product': search_product,
    }
    
    return render(request, 'costing/saved_costings.html', context)

from collections import defaultdict


@login_required(login_url='login')
def summary_report(request):

    costings = DailyCosting.objects.select_related('outlet', 'product', 'user').all()
    
    selected_outlet = request.GET.get('outlet')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date and to_date:
        costings = costings.filter(date__range=[from_date, to_date])
    elif from_date:
        costings = costings.filter(date__gte=from_date)
    elif to_date:
        costings = costings.filter(date__lte=to_date)

    if selected_outlet:
        costings = costings.filter(outlet_id=selected_outlet)

    # Group data by (date, outlet)
    grouped_data = defaultdict(lambda: {
        'revenue': 0,
        'cost': 0,
        'profit': 0,
        'opening_stock_qty': 0,
        'closing_stock_qty': 0,
        'opening_stock_value': 0,
        'closing_stock_value': 0,
    })

    total_revenue = 0
    total_cost = 0
    total_profit = 0
    total_opening_value = 0
    total_closing_value = 0

    for costing in costings:
        key = (costing.date, costing.outlet.name)
        rate = costing.product.rate  # Cost per unit

        revenue = costing.revenue()
        cost = costing.cost_of_production()
        profit = costing.gross_profit()

        opening_value = costing.opening_stock * rate
        closing_value = costing.closing_stock * rate

        grouped_data[key]['revenue'] += revenue
        grouped_data[key]['cost'] += cost
        grouped_data[key]['profit'] += profit
        grouped_data[key]['opening_stock_qty'] += costing.opening_stock
        grouped_data[key]['closing_stock_qty'] += costing.closing_stock
        grouped_data[key]['opening_stock_value'] += opening_value
        grouped_data[key]['closing_stock_value'] += closing_value

        total_revenue += revenue
        total_cost += cost
        total_profit += profit
        total_opening_value += opening_value
        total_closing_value += closing_value

    # Prepare report data
    report_data = []
    for key, value in grouped_data.items():
        date, outlet = key
        ratio = 0
        if value['revenue'] > 0:
            ratio = (value['profit'] / value['revenue']) * 100

        report_data.append({
            'date': date,
            'outlet': outlet,
            'opening_stock_qty': value['opening_stock_qty'],
            'closing_stock_qty': value['closing_stock_qty'],
            'opening_stock_value': value['opening_stock_value'],
            'closing_stock_value': value['closing_stock_value'],
            'revenue': value['revenue'],
            'cost': value['cost'],
            'profit': value['profit'],
            'ratio': ratio,
        })

    overall_ratio = 0
    if total_revenue > 0:
        overall_ratio = (total_profit / total_revenue) * 100

    outlets = Outlet.objects.all()

    context = {
        'report_data': report_data,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'overall_ratio': overall_ratio,
        'total_opening_value': total_opening_value,
        'total_closing_value': total_closing_value,
        'outlets': outlets,
    }

    return render(request, 'costing/summary_report.html', context)





def home(request):
    if request.user.is_authenticated:
        return redirect('daily_costing')
    return render(request, 'home.html')