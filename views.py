from django.http import HttpResponseServerError
from django.shortcuts import render
from XLib import utils
from django.http import JsonResponse
from XLib.utils import NCMSpider


def index(request):
    return render(request, 'index.html', {})


def comment(request):
    id = request.GET.get('song_id', None)
    if not id:
        return HttpResponseServerError('错误：未获取到有效参数，请返回重试。')
    song_info = NCMSpider.get_song_info(id)
    comments = NCMSpider.get_comments(id, 0)
    if song_info.get('status') == 0 or comments.get('status') == 0:
        return HttpResponseServerError('错误：\n'+song_info.get('err', '')+'\n' + comments.get('err', ''))
    return render(request=request, template_name='comment.html', context={
        'song_info_data': song_info,
        'comment_data': comments,
        'song_id': id
    })


def api_comments_data(request):
    id = request.GET.get('song_id', '')
    offset = request.GET.get('offset', '')
    if id == '' or offset == '':
        return JsonResponse({})
    comments = utils.NCMSpider.get_comments(id, offset)
    if comments.get('status') == 0:
        return HttpResponseServerError('错误：\n' + comments.get('err', ''))
    return JsonResponse(data={'comments_data': comments})


def api_search(request):
    name = request.GET.get('name', '')
    if name == '':
       return JsonResponse({})
    search_result = NCMSpider.search_song(name)
    if search_result.get('status') == 0:
        return JsonResponse('错误：\n' + search_result.get('err', ''))
    return JsonResponse(data={'songs': search_result.get('songs', [])})
