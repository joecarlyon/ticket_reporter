import lxml as lxml
import re
import requests as requests
import argparse
from lxml.cssselect import CSSSelector
from lxml import html


def main():
    args = parse_arguments()

    plate_number = args.plate_number
    plate_state = args.plate_state
    plate_type = args.plate_type
    last_name = args.last_name
    ticket_amount_selector = CSSSelector('#printFriendlyPage tbody tr')

    url = construct_url(plate_number, plate_state, plate_type, last_name)
    response = requests.get(url)
    check_for_good_response(response)
    response.encoding = 'UTF-8'

    tree = lxml.html.fromstring(response.text)
    all_tickets = ticket_amount_selector(tree)

    if len(all_tickets) > 0:
        open_each_ticket(all_tickets)
    else:
        print('You have no open tickets. Congratulations!')
        exit(0)


def open_each_ticket(all_tickets):
    total_amount_due = 0
    print("You have %d tickets" % len(all_tickets))
    print("-" * 75)

    for count, ticket in enumerate(all_tickets):
        ticket_number = ticket[1].text
        ticket_date = ticket[5].text
        amount = ticket[6][0].text
        clean_amount = construct_clean_amount(amount)
        print_ticket_info(ticket_number, ticket_date, clean_amount)
        total_amount_due += clean_amount


def print_ticket_info(ticket_number, ticket_date, clean_amount):
    if clean_amount > 0:
        print("Ticket %s issued on %s has an outstanding amount of:" % (ticket_number, ticket_date, clean_amount))
    else:
        print('Ticket %s issued on %s has been resolved' % (ticket_number, ticket_date))


def parse_arguments():
    parser = argparse.ArgumentParser(description='Get the number of outstanding Chicago tickets')
    parser.add_argument('-N', '--plate-number', type=str, help='License plate number', required=True)
    parser.add_argument('-S', '--plate-state', type=str, help='Registered state', default='IL')
    parser.add_argument('-T', '--plate-type', type=str, help='Plate class type', default='PAS')
    parser.add_argument('-L', '--last-name', type=str, help='Registered owner\'s last name', required=True)
    args = parser.parse_args()
    return args


def construct_clean_amount(amount):
    clean_amount = re.sub(r"[^\d|\.]", "", amount)
    return int(round(float(clean_amount)))


def check_for_good_response(response):
    if response.status_code != 200:
        print('Something went wrong with the request')
        exit(1)


def construct_url(plate_number, plate_state, plate_type, last_name):
    return "https://parkingtickets.cityofchicago.org/CPSWeb/retrieveTicketsByLicensePlate.do?plateNumber=%s" \
           "&plateState=%s&plateType=%s&plateOwnerName=%s" % (plate_number, plate_state, plate_type, last_name)


if __name__ == '__main__':
  main()