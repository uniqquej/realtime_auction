from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse

from .models import Auction

def index(request):
    if request.method == "POST":
        name = request.POST.get("name", None)
        if name:
            auction = Auction.objects.create(name=name, auction_users=request.user)
            HttpResponseRedirect(reverse("auction", args=[auction.pk]))
    return render(request, 'index.html')

def room(request, pk):
    auction: Auction = get_object_or_404(Auction, pk=pk)
    return render(request, 'room.html', {
        "auction":auction,
    })