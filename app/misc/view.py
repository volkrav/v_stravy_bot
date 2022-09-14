from app.services.utils import ViewOrder, create_product_list


async def list_products(data: dict) -> ViewOrder:
    product_list = await create_product_list(data.keys())
    amount_payable = 0
    answer = ''
    for index, product in enumerate(product_list, 1):
        amount_payable += data[product.uid] * product.price
        answer += (f'# {index} \n'
                   f'<u><b>{data[product.uid]} шт. * {product.title}</b></u>\n'
                   f'Ціна: {product.price} грн.\n'
                   f'Всього: {data[product.uid] * product.price} грн.\n\n'
                   )
    answer += f'Сумма: {amount_payable} грн.\n\n'
    return ViewOrder(text=answer, amount=amount_payable)
# KeyError
