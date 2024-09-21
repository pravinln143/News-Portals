from news.models import Banner


def banners(request):
    return {"banners": Banner.objects.all()}
