from option_pricing.models import Future
from django.db.models import Max
from django.core.paginator import Paginator

def future_bar(request):
    max_date = Future.objects.all().aggregate(Max('date'))
    queryset = Future.objects.all().filter(date=max_date['date__max']).filter(futuresymbol__expmonthdate__gte=max_date['date__max']).order_by('-open_interest')[:18]

    paginator = Paginator(queryset, 6)
    page_number = request.GET.get('page', 1)
    page_obj_fut = paginator.get_page(page_number)

    return {
        'page_obj_fut': page_obj_fut
    }