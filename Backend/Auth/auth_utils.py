from .models import CustomUser

def authenticate_user(email, password):
    try:
        user = CustomUser.objects.get(email=email)
        if user.check_password(password):
            return user
    except CustomUser.DoesNotExist:
        return None

def add_token_transaction(user: CustomUser, input_tokens=0, output_tokens=0):
    # create a record
    TokenTransaction.objects.create(
        user=user,
        input_token=input_tokens,
        output_token=output_tokens
    )
    # update user's total tokens
    user.tokens += input_tokens
    user.tokens -= output_tokens
    user.save()