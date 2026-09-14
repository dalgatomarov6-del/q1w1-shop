"""FSM states."""
from aiogram.fsm.state import State, StatesGroup


class ServiceOrder(StatesGroup):
    custom_amount = State()
    game_id = State()
    promo = State()


class ProductOrder(StatesGroup):
    game_id = State()
    promo = State()


class PromoMenu(StatesGroup):
    enter_code = State()


class AdminProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()
    category = State()
    stock = State()
    select_edit = State()
    edit_field = State()
    edit_value = State()
    select_delete = State()


class AdminTeamMember(StatesGroup):
    name = State()
    role = State()
    game_id = State()
    description = State()
    photo = State()
    edit_value = State()


class AdminPromo(StatesGroup):
    code = State()
    discount_type = State()
    discount_value = State()
    max_uses = State()
    expires = State()
    select_edit = State()
    edit_field = State()
    edit_value = State()
    select_delete = State()


class AdminSettings(StatesGroup):
    edit_value = State()


class AdminBroadcast(StatesGroup):
    message = State()


class AdminSetStatus(StatesGroup):
    pass


class SupportTicket(StatesGroup):
    """User writes the ticket description."""
    message = State()
    reply = State()


class AdminTicketReply(StatesGroup):
    """Admin writes a reply that is delivered to the user through the bot."""
    message = State()


class AdminPrices(StatesGroup):
    edit_price = State()
    add_amount = State()
    add_price = State()
