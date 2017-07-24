import lxml as lxml
import re
import requests as requests
from lxml.cssselect import CSSSelector
from lxml import html


def main():
    plate_number = ''
    plate_state = 'IL'
    plate_type = 'PAS'
    last_name = ''
    ticket_amount_selector = CSSSelector('#printFriendlyPage tbody tr')
    total_amount_due = 0

    url = construct_url(plate_number, plate_state, plate_type, last_name)
    response = requests.get(url)
    check_for_good_response(response)
    response.encoding = 'UTF-8'

    tree = lxml.html.fromstring(response.text)
    all_tickets = ticket_amount_selector(tree)

    if len(all_tickets) > 0:
        print("You have %d tickets" % len(all_tickets))
        for count, ticket in enumerate(all_tickets):
            amount_due_locator = CSSSelector("#spanConfirmAmount%d" % count)
            amount = amount_due_locator(ticket)
            clean_amount = construct_clean_amount(amount)
            if clean_amount > 0:
                print("You have an outstanding ticket worth: %s" % clean_amount)
                total_amount_due += clean_amount
            else:
                print('This ticket is not a problem')
    else:
        print('You have no open tickets. Congratulations!')
        exit(0)


def construct_clean_amount(amount):
    clean_amount = re.sub(r"[^\d|\.]", "", amount[0].text)
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