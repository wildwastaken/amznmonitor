import requests
from lxml import html, etree

import json
from time import sleep
import argparse
import unicodecsv as csv
import traceback
from dhooks import Webhook, Embed

hook = Webhook('https://discordapp.com/api/webhooks/725009279333171243/29NHF_i9iKRC44CsD3ylPJ-OhYZPWsjhEpvFr3FoGvW7HyRw14HqCcAB0JrBZS08DTDn')


def parse_offer_details(url):
    '''
    Function to parse seller details from amazon offer listing page
    eg:https://www.amazon.com/gp/offer-listing/
    :param url:offer listing url
    :rtype: seller details as json
    '''
    # Add some recent user agent to prevent blocking from amazon
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
        'referer': 'https://www.google.com'
    }

    while True:
        try:
            print("Downloading and processing page :", url)
            response = requests.get(url, headers=headers)
            if response.status_code == 403:
                raise ValueError("Captcha found. Retrying")

            response_text = response.text
            parser = html.fromstring(response_text)
            XPATH_PRODUCT_LISTINGS = "//div[contains(@class, 'a-row a-spacing-mini olpOffer')]"
            # Parsing seller list
            listings = parser.xpath(XPATH_PRODUCT_LISTINGS)
            offer_list = []

            if not listings:
                print("no sellers found")
                return offer_list

            # parsing individual seller
            for listing in listings:
                XPATH_PRODUCT_PRICE = ".//span[contains(@class, 'olpOfferPrice')]//text()"
                XPATH_PRODUCT_PRIME = ".//i/@aria-label"
                XPATH_PRODUCT_SHIPPING = ".//p[contains(@class, 'olpShippingInfo')]//text()"
                XPATH_PRODUCT_CONDITION = ".//span[contains(@class, 'olpCondition')]//text()"
                XPATH_PRODUCT_DELIVERY = ".//div[contains(@class, 'olpDeliveryColumn')]//text()"
                XPATH_PRODUCT_SELLER1 = ".//h3[contains(@class, 'olpSellerName')]//a/text()"
                XPATH_PRODUCT_SELLER2 = ".//h3[contains(@class, 'olpSellerName')]//img//@alt"

                product_price = listing.xpath(XPATH_PRODUCT_PRICE)
                product_price = product_price[0].strip()
                product_prime = listing.xpath(XPATH_PRODUCT_PRIME)
                product_condition = listing.xpath(XPATH_PRODUCT_CONDITION)
                product_shipping = listing.xpath(XPATH_PRODUCT_SHIPPING)
                delivery = listing.xpath(XPATH_PRODUCT_DELIVERY)
                seller1 = listing.xpath(XPATH_PRODUCT_SELLER1)
                seller2 = listing.xpath(XPATH_PRODUCT_SELLER2)

                # cleaning parsed data
                product_prime = product_prime[0].strip() if product_prime else None
                product_condition = ''.join(''.join(product_condition).split()) if product_condition else None
                product_shipping_details = ' '.join(''.join(product_shipping).split()).lstrip("&").rstrip(
                    "Details") if product_shipping else None
                cleaned_delivery = ' '.join(''.join(delivery).split()).replace("Shipping rates and return policy.",
                                                                               "").strip() if delivery else None
                product_seller = ''.join(seller1).strip() if seller1 else ''.join(seller2).strip()

                offer_details = {
                    'price': product_price,
                    'shipping_detais': product_shipping_details,
                    'condition': product_condition,
                    'prime': product_prime,
                    'delivery': cleaned_delivery,
                    'seller': product_seller,
                    'asin': asin,
                    'url': url
                }
                offer_list.append(offer_details)
            return offer_list

        except Exception:
            print("empty page found")
            #break
        except:
            print(traceback.format_exc())
            print("retying :", url)


def start():
    asin = 'B00PCGHAVY'
    condition = 'new'
    shipping = 'prime'

    # for creating url according to the filter applied
    condition_dict = { 'new': '&f_new=true',
                       'used': '&f_used=true',
                       'all': '&condition=all',
                       'like_new': '&f_usedLikeNew=true',
                       'good': '&f_usedGood=true',
                       'verygood': '&f_usedVeryGood=true',
                       'acceptable': '&f_usedAcceptable=true'
                       }
    shipping_dict = { 'prime': '&f_primeEligible=true',
                      'all': '&shipping=all'
                      }

    url = 'https://www.amazon.com/gp/offer-listing/' + asin + '/ref=' + condition_dict.get(
        condition) + shipping_dict.get(shipping)
    data = parse_offer_details(url)

    for dictionary in parse_offer_details(url):
        if dictionary['price'] == '$221.98':
            print('AYYYYY RESTOCK — sending webhook ', asin)
            embed = Embed(
                color=0x5CDBF0,
                timestamp='now'  # sets the timestamp to current time
            )

            image1 = 'https://media.giphy.com/media/khkKH8Dds3tTdLoVYW/giphy.gif'
            image2 = 'https://i.imgur.com/f1LOr4q.png'
            image3 = 'http://www.bowflex.com/on/demandware.static/-/Sites-nautilus-master-catalog/default/dwa1e50944/images/bowflex/selecttech/552/100131/bowflex-selecttech-552-dumbbell-set.png'

            embed.set_title('**Bowflex SelectTech 552 - Two Adjustable Dumbbells**', 'https://www.amazon.com/gp/offer-listing/B001ARYU58/ref=&f_new=true&f_primeEligible=true')
            embed.set_author(name="wild's monitors", icon_url=image1)
            embed.add_field(name='Price', value='$329.00')
            embed.add_field(name='ASIN', value='B001ARYU58')
            embed.set_footer(text='created by wild#9534', icon_url=image1)

            embed.set_thumbnail(image3)
            hook.send(embed=embed)
            #sleep(10)
            parse_offer_details(url)
        else:
            print('rip in the chat')
            #sleep(1)
            parse_offer_details(url)

start()
