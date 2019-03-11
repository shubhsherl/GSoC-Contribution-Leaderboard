
from django.shortcuts import render
from .models import  LastUpdate, Relation
from .views import sortUser




def showGsocUser(request):
    sort = 'd'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    if LastUpdate.objects.filter(pk=1):
        lastUpdated = LastUpdate.objects.get(pk=1).updated
    else:
        lastUpdated = ''
    data = sortUser(Relation.objects, sort, _gsoc = True)

    context = {
        'users': data,
        'updated': lastUpdated,
    }
    return render(request, 'core/gsoclist.html', context)
