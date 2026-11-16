from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.assets.media import get_banner_file
from bot.assets.texts import t
from bot.keyboards.address import (
    kb_address_create_confirm,
    kb_address_delete_confirm,
    kb_address_detail,
    kb_address_edit,
    kb_address_edit_addr_confirm,
    kb_address_edit_title_confirm,
    kb_address_list,
)
from bot.keyboards.common import kb_back
from bot.states import AddressCreate, AddressEdit
from clients.api import ApiNotFoundError, api_client
from shared.bot.utils.media_banner import bot_edit_banner, edit_banner

router = Router(name="address")


def _address_list_caption(addresses) -> str:
    return t("address_list_empty") if not addresses else t("address_list_caption", count=len(addresses))


async def _show_address_list(message, addresses) -> None:
    await edit_banner(
        message,
        _address_list_caption(addresses),
        banner=get_banner_file("address-banner"),
        reply_markup=kb_address_list(addresses, page=0),
    )


@router.callback_query(F.data == "addr:list")
async def address_list(call: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    addresses = (await api_client.addresses.list(call.from_user.id)).items
    await _show_address_list(call.message, addresses)
    await call.answer()


@router.callback_query(F.data.regexp(r"^addr_page:\d+$"))
async def address_page(call: CallbackQuery):
    page = int(call.data.split(":")[1]) - 1
    addresses = (await api_client.addresses.list(call.from_user.id)).items
    await call.message.edit_reply_markup(reply_markup=kb_address_list(addresses, page=page))
    await call.answer()


@router.callback_query(F.data.regexp(r"^addr:view:\d+$"))
async def address_view(call: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    address_id = int(call.data.split(":")[2])
    try:
        address = await api_client.addresses.get(user_id=call.from_user.id, address_id=address_id)
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await edit_banner(call.message, t("address_detail", title=address.title, address=address.address), banner=get_banner_file("address-banner"), reply_markup=kb_address_detail(address_id))
    await call.answer()


@router.callback_query(F.data == "addr:add")
async def address_add_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddressCreate.title)
    await state.update_data(addr_bot_msg_id=call.message.message_id)
    await edit_banner(call.message, t("address_create_title"), banner=get_banner_file("address-banner"), reply_markup=kb_back("back_to_addresses", "addr:list"))
    await call.answer()


@router.message(AddressCreate.title)
async def address_add_title(msg: Message, state: FSMContext):
    await msg.delete()
    await state.update_data(addr_title=msg.text.strip()[:256])
    await state.set_state(AddressCreate.address)
    data = await state.get_data()
    await bot_edit_banner(msg.bot, msg.chat.id, data["addr_bot_msg_id"], t("address_create_address"), banner=get_banner_file("address-banner"), reply_markup=kb_back("back_to_addresses", "addr:list"))


@router.message(AddressCreate.address)
async def address_add_address(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    await state.update_data(addr_address=msg.text.strip()[:1000])
    await state.set_state(None)
    await bot_edit_banner(
        msg.bot,
        msg.chat.id,
        data["addr_bot_msg_id"],
        t("address_create_confirm", title=data["addr_title"], address=(await state.get_data())["addr_address"]),
        banner=get_banner_file("address-banner"),
        reply_markup=kb_address_create_confirm(),
    )


@router.callback_query(F.data == "addr:add_yes")
async def address_add_confirm(call: CallbackQuery, state: FSMContext, bot: Bot):
    del bot
    data = await state.get_data()
    await state.clear()
    created = await api_client.addresses.create(
        user_id=call.from_user.id,
        title=data.get("addr_title", ""),
        address=data.get("addr_address", ""),
    )
    addresses = (await api_client.addresses.list(call.from_user.id)).items
    await _show_address_list(call.message, addresses)
    await call.answer(t("address_created"))


@router.callback_query(F.data == "addr:add_cancel")
async def address_add_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    addresses = (await api_client.addresses.list(call.from_user.id)).items
    await _show_address_list(call.message, addresses)
    await call.answer()


@router.callback_query(F.data.regexp(r"^addr:edit:\d+$"))
async def address_edit_menu(call: CallbackQuery):
    address_id = int(call.data.split(":")[2])
    try:
        await api_client.addresses.get(user_id=call.from_user.id, address_id=address_id)
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await call.message.edit_reply_markup(reply_markup=kb_address_edit(address_id))
    await call.answer()


@router.callback_query(F.data.regexp(r"^addr:edit_title:\d+$"))
async def address_edit_title_start(call: CallbackQuery, state: FSMContext):
    address_id = int(call.data.split(":")[2])
    try:
        address = await api_client.addresses.get(user_id=call.from_user.id, address_id=address_id)
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await state.set_state(AddressEdit.title)
    await state.update_data(edit_addr_id=address_id, addr_bot_msg_id=call.message.message_id, edit_old_title=address.title)
    await edit_banner(call.message, t("address_edit_title"), banner=get_banner_file("address-banner"), reply_markup=kb_back("back_to_address", f"addr:view:{address_id}"))
    await call.answer()


@router.message(AddressEdit.title)
async def address_edit_title_process(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    new_title = msg.text.strip()[:256]
    await state.update_data(edit_new_title=new_title)
    await state.set_state(None)
    await bot_edit_banner(
        msg.bot,
        msg.chat.id,
        data["addr_bot_msg_id"],
        t("address_edit_confirm_title", old_title=data["edit_old_title"], new_title=new_title),
        banner=get_banner_file("address-banner"),
        reply_markup=kb_address_edit_title_confirm(data["edit_addr_id"]),
    )


@router.callback_query(F.data.regexp(r"^addr:edit_title_yes:\d+$"))
async def address_edit_title_yes(call: CallbackQuery, state: FSMContext, bot: Bot):
    del bot
    address_id = int(call.data.split(":")[2])
    data = await state.get_data()
    await state.clear()
    try:
        address = await api_client.addresses.update_title(
            user_id=call.from_user.id,
            address_id=address_id,
            title=data.get("edit_new_title", ""),
        )
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await edit_banner(call.message, t("address_detail", title=address.title, address=address.address), banner=get_banner_file("address-banner"), reply_markup=kb_address_detail(address.id))
    await call.answer(t("address_updated"))


@router.callback_query(F.data.regexp(r"^addr:edit_title_cancel:\d+$"))
async def address_edit_title_cancel(call: CallbackQuery, state: FSMContext):
    address_id = int(call.data.split(":")[2])
    await state.clear()
    try:
        address = await api_client.addresses.get(user_id=call.from_user.id, address_id=address_id)
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await edit_banner(call.message, t("address_detail", title=address.title, address=address.address), banner=get_banner_file("address-banner"), reply_markup=kb_address_detail(address.id))
    await call.answer()


@router.callback_query(F.data.regexp(r"^addr:edit_addr:\d+$"))
async def address_edit_addr_start(call: CallbackQuery, state: FSMContext):
    address_id = int(call.data.split(":")[2])
    try:
        address = await api_client.addresses.get(user_id=call.from_user.id, address_id=address_id)
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await state.set_state(AddressEdit.address)
    await state.update_data(edit_addr_id=address_id, addr_bot_msg_id=call.message.message_id, edit_old_address=address.address)
    await edit_banner(call.message, t("address_edit_address"), banner=get_banner_file("address-banner"), reply_markup=kb_back("back_to_address", f"addr:view:{address_id}"))
    await call.answer()


@router.message(AddressEdit.address)
async def address_edit_addr_process(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    new_address = msg.text.strip()[:1000]
    await state.update_data(edit_new_address=new_address)
    await state.set_state(None)
    await bot_edit_banner(
        msg.bot,
        msg.chat.id,
        data["addr_bot_msg_id"],
        t("address_edit_confirm_addr", old_address=data["edit_old_address"], new_address=new_address),
        banner=get_banner_file("address-banner"),
        reply_markup=kb_address_edit_addr_confirm(data["edit_addr_id"]),
    )


@router.callback_query(F.data.regexp(r"^addr:edit_addr_yes:\d+$"))
async def address_edit_addr_yes(call: CallbackQuery, state: FSMContext, bot: Bot):
    del bot
    address_id = int(call.data.split(":")[2])
    data = await state.get_data()
    await state.clear()
    try:
        address = await api_client.addresses.update_address(
            user_id=call.from_user.id,
            address_id=address_id,
            address=data.get("edit_new_address", ""),
        )
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await edit_banner(call.message, t("address_detail", title=address.title, address=address.address), banner=get_banner_file("address-banner"), reply_markup=kb_address_detail(address.id))
    await call.answer(t("address_updated"))


@router.callback_query(F.data.regexp(r"^addr:edit_addr_cancel:\d+$"))
async def address_edit_addr_cancel(call: CallbackQuery, state: FSMContext):
    address_id = int(call.data.split(":")[2])
    await state.clear()
    try:
        address = await api_client.addresses.get(user_id=call.from_user.id, address_id=address_id)
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await edit_banner(call.message, t("address_detail", title=address.title, address=address.address), banner=get_banner_file("address-banner"), reply_markup=kb_address_detail(address.id))
    await call.answer()


@router.callback_query(F.data.regexp(r"^addr:del:\d+$"))
async def address_delete_confirm(call: CallbackQuery):
    address_id = int(call.data.split(":")[2])
    try:
        address = await api_client.addresses.get(user_id=call.from_user.id, address_id=address_id)
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await edit_banner(call.message, t("address_delete_confirm", title=address.title), banner=get_banner_file("address-banner"), reply_markup=kb_address_delete_confirm(address_id))
    await call.answer()


@router.callback_query(F.data.regexp(r"^addr:del_yes:\d+$"))
async def address_delete_yes(call: CallbackQuery, bot: Bot):
    del bot
    address_id = int(call.data.split(":")[2])
    try:
        address = await api_client.addresses.get(user_id=call.from_user.id, address_id=address_id)
    except ApiNotFoundError:
        await call.answer(t("address_not_found"), show_alert=True)
        return
    await api_client.addresses.delete(user_id=call.from_user.id, address_id=address_id)
    addresses = (await api_client.addresses.list(call.from_user.id)).items
    await _show_address_list(call.message, addresses)
    await call.answer(t("address_deleted"))
