from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def pager(request, content, page_size=25, adjacent_pages=3):
    '''
        Adds pagination context variables for use in displaying first, adjacent and
        last page links in addition to those created by the object_list generic
        view.

        context - context to be displayed on the page
        content - content to be paginated

        based on the following article:
        www.tummy.com/articles/django-pagination/
    '''

    context = {}
    
    paginator = Paginator(content, page_size)

    page = request.GET.get('page')

    try:
        current_page = paginator.page(page)
    except PageNotAnInteger:
        #If page is not an integer, deliver first page.
        current_page = paginator.page(1)
    except EmptyPage:
        #If page is out of range, deliver lastpage of results.
        current_page = paginator.page(paginator.num_pages)


    startPage = max(current_page.number - adjacent_pages, 1)
    
    if startPage <= 4: 
        startPage = 1

    endPage = current_page.number + adjacent_pages + 1
    
    if endPage >= paginator.num_pages - 1: 
        endPage = paginator.num_pages + 1
    
    page_numbers = [n for n in range(startPage, endPage) \
            if n > 0 and n <= paginator.num_pages]
    

    # context of the paginator to be displayed on the webpage
    context['paginator'] = paginator
    context['has_next'] = current_page.has_next()
    context['has_previous'] = current_page.has_previous()
    context['page_numbers'] = page_numbers 
    context['show_first'] = 1 not in page_numbers
    context['show_last'] = paginator.num_pages not in page_numbers
    context['current_page'] = current_page
    context['pages_range'] = range(1, paginator.num_pages + 1)

    try:
        context['next_page_number'] = current_page.next_page_number()
    except EmptyPage:
        pass

    try:    
        context['previous_page_number'] = current_page.previous_page_number()
    except EmptyPage:
        pass
    
    return context
