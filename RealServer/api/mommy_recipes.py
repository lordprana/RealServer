from model_mommy.recipe import related, Recipe, seq
from model_mommy import mommy
from api.models import User

user = Recipe(User, fb_user_id = seq('110000369505832'))