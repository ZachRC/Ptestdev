import stripe
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_customer(user):
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={'user_id': user.id}
        )
        user.stripe_customer_id = customer.id
        user.save()
    return user.stripe_customer_id

def create_subscription_session(user):
    customer_id = create_stripe_customer(user)
    
    # Create a new price for $5/month
    price = stripe.Price.create(
        unit_amount=settings.SUBSCRIPTION_PRICE_AMOUNT,
        currency='usd',
        recurring={'interval': 'month'},
        product_data={'name': 'Monthly Subscription'}
    )

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': price.id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=settings.SITE_URL + '/subscription/success/',
        cancel_url=settings.SITE_URL + '/subscription/cancel/',
    )
    return session

def handle_subscription_success(session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    subscription = stripe.Subscription.retrieve(session.subscription)
    
    from .models import CustomUser
    user = CustomUser.objects.get(stripe_customer_id=session.customer)
    
    # Set subscription status and end date
    user.subscription_status = 'active'
    user.subscription_end = timezone.now() + timedelta(days=30)
    user.save()
    
    return user 