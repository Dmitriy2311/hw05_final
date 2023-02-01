from django.core.paginator import Paginator


POST_LIMIT = 10


def paginat(request, data_list):
    paginator = Paginator(data_list, POST_LIMIT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return page_obj
