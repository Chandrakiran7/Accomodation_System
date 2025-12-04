from accommodations.models import Accommodation
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime
from decimal import Decimal
from .models import Booking


# ✅ CREATE BOOKING
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    template_name = 'bookings/createbooking.html'
    fields = ['check_in_date', 'check_out_date', 'num_guests', 'special_requests']

    def dispatch(self, request, *args, **kwargs):
        self.accommodation = get_object_or_404(
            Accommodation, pk=self.kwargs['accommodation_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['check_in_date'] = self.request.GET.get('check_in')
        initial['check_out_date'] = self.request.GET.get('check_out')
        initial['num_guests'] = self.request.GET.get('guests')
        return initial

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.guest = self.request.user
        booking.accommodation = self.accommodation

        nights = (booking.check_out_date - booking.check_in_date).days
        accommodation_cost = nights * self.accommodation.price_per_night

        booking.accommodation_cost = accommodation_cost
        booking.total_cost = accommodation_cost
        booking.status = 'pending'
        booking.save()

        messages.success(self.request, "✅ Booking created successfully!")
        return redirect("bookings:my_bookings")


# ✅ BOOKING DETAIL
class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "bookings/detail.html"
    context_object_name = "booking"


# ✅ GUEST BOOKINGS LIST
class MyBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/my_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.filter(
            guest=self.request.user
        ).order_by("-created_at")


# ✅ HOST BOOKINGS
@login_required
def host_bookings(request):
    if request.user.role != "host":
        messages.error(request, "Access denied.")
        return redirect("accounts:profile")

    bookings = Booking.objects.filter(
        accommodation__host=request.user
    ).select_related("guest", "accommodation").order_by("-created_at")

    return render(request, "bookings/my_bookings.html", {"bookings": bookings})


# ✅ EDIT BOOKING (GUEST ONLY) ✅ FIXED DATE BUG
@login_required
def edit_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.user != booking.guest:
        messages.error(request, "You are not allowed to edit this booking.")
        return redirect("bookings:my_bookings")

    if booking.status != "pending":
        messages.error(request, "Only pending bookings can be edited.")
        return redirect("bookings:my_bookings")

    if request.method == "POST":
        booking.check_in_date = datetime.strptime(
            request.POST.get("check_in_date"), "%Y-%m-%d"
        ).date()

        booking.check_out_date = datetime.strptime(
            request.POST.get("check_out_date"), "%Y-%m-%d"
        ).date()

        booking.num_guests = request.POST.get("num_guests")
        booking.special_requests = request.POST.get("special_requests")
        booking.save()

        messages.success(request, "✅ Booking updated successfully.")
        return redirect("bookings:my_bookings")

    return render(request, "bookings/edit_booking.html", {"booking": booking})


# ✅ DELETE BOOKING (GUEST ONLY)
@login_required
def delete_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.user != booking.guest:
        messages.error(request, "You are not allowed to delete this booking.")
        return redirect("bookings:my_bookings")

    booking.delete()
    messages.success(request, "✅ Booking deleted successfully.")
    return redirect("bookings:my_bookings")


# ✅ HOST CONFIRM BOOKING
@login_required
@require_http_methods(["POST"])
def confirm_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.user != booking.accommodation.host:
        messages.error(request, "Only the host can confirm this booking.")
        return redirect("bookings:my_bookings")

    booking.status = "confirmed"
    booking.save()

    messages.success(request, "✅ Booking confirmed successfully.")
    return redirect("bookings:my_bookings")


# ✅ HOST REJECT BOOKING
@login_required
@require_http_methods(["POST"])
def reject_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.user != booking.accommodation.host:
        messages.error(request, "Only the host can reject this booking.")
        return redirect("bookings:my_bookings")

    booking.status = "cancelled"
    booking.save()

    messages.success(request, "✅ Booking rejected successfully.")
    return redirect("bookings:my_bookings")


# ✅ AJAX AVAILABILITY CHECK
@login_required
@require_http_methods(["POST"])
def check_availability(request):
    accommodation_id = request.POST.get("accommodation_id")
    check_in = request.POST.get("check_in_date")
    check_out = request.POST.get("check_out_date")

    try:
        accommodation = Accommodation.objects.get(
            pk=accommodation_id, status="active", is_available=True
        )

        check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

        overlapping = Booking.objects.filter(
            accommodation=accommodation,
            status__in=["confirmed", "checked_in"],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
        )

        if overlapping.exists():
            return JsonResponse({"available": False})

        nights = (check_out_date - check_in_date).days
        accommodation_cost = nights * accommodation.price_per_night
        total_cost = accommodation_cost

        return JsonResponse({
            "available": True,
            "total_cost": float(total_cost)
        })

    except:
        return JsonResponse({"available": False})
