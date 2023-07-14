def url_name(request):
    return {'url_name': request.resolver_match.url_name}