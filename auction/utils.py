from datetime import datetime
import os

import boto3


AWS_SES_REGION = 'us-west-2'


def now():
    return datetime.utcnow()


def format_datetime(t):
    return t.strftime('%Y-%m-%d %H:%M:%S')


def human_readable(delta):
    dt = delta.total_seconds()

    if abs(dt) < 60:
        return round(dt), 'seconds'
    elif abs(dt) < 3600:
        return round(dt / 60), 'minutes'
    elif abs(dt) < 86400:
        return round(dt / 3600), 'hours'
    else:
        return round(dt / 86400), 'days'


def is_hangul(ch):
    """Copied from https://github.com/suminb/hanja/blob/master/hanja/hangul.py
    """
    if ch is None:
        return False
    else:
        return ord(ch) >= 0xac00 and ord(ch) <= 0xd7a3


# NOTE: as of June 13, 2017, SES is only supported in the following
# regions:
# - eu-west-1 (Ireland)
# - us-east-1 (Virginia)
# - us-west-2 (Oregon)
def send_email(to_addresses, subject, body, dry_run=False):
    """Sends an email message via AWS SES.

    :param to_addresses: A list of recipient addresses
    """

    if dry_run:
        return None

    client = boto3.client('ses', region_name=AWS_SES_REGION)
    return client.send_email(**{
        'Source': os.environ['AUCTION_EMAIL_MASTER'],
        'Destination': {
            'ToAddresses': to_addresses,
        },
        'Message': {
            'Subject': {
                'Data': subject,
                'Charset': 'utf-8'
            },
            'Body': {
                'Html': {
                    'Data': body,
                    'Charset': 'utf-8'
                }
            }
        }
    })
