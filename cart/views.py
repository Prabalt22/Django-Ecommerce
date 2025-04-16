from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.
def cart_summary(request):
    # get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, 'cart_summary.html', {'cart_products':cart_products, "quantities":quantities, "totals":totals})

def cart_add(request):
    # get the cart
    cart = Cart(request)
    # test for POST
    if request.POST.get('action') == 'post':
        # get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        
        # lookup product in db
        product = get_object_or_404(Product, id=product_id)
        
        # save to session
        cart.add(product=product, quantity=product_qty)
        
        cart_quantity = cart.__len__()
        
        # return responce
        # responce = JsonResponse({'Product Name: ': product.name})
        messages.success(request, ("Product Added To Cart"))
        responce = JsonResponse({'qty': cart_quantity})
        return responce
    

def cart_delete(request):
    # get the cart
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # get stuff
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        responce = JsonResponse({'product':product_id})
        messages.success(request, ("Item Deleted From Cart"))
        return responce

def cart_update(request):
    # get the cart
    cart = Cart(request)
    # test for POST
    if request.POST.get('action') == 'post':
        # get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        
        cart.update(product=product_id, quantity=product_qty)
        
        responce = JsonResponse({'qty':product_qty})
        messages.success(request, ("Your Cart Been Updated"))
        return responce