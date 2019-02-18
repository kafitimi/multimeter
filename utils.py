# USAGE: generate_users 50 -c
import sys
import os
import django
import http.client
import json

if __name__ == '__main__':
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
	django.setup()

from multimeter.models import Account


def generate_users(count, args):
	conn = http.client.HTTPConnection('names.drycodes.com')
	print('Retrieving names...', end=' ')
	conn.request('GET', '/%d?separator=space&nameOptions=boy_names' % count)
	response = conn.getresponse()
	code = response.code
	response_json = response.read()
	conn.close()
	print('OK (%d)' % code if code == 200 else 'ERROR (%d)' % code)
	if code == 200:
		if '-c' in args:
			print('Deleting previously generated user(s)...', end=' ')
			deleted_count = Account.objects.filter(email__endswith='generated.com').delete()[0]
			print('OK (%d)' % deleted_count)
		print('Generating users...', end=' ')
		generated = []
		for first_name, last_name in [name.split() for name in json.loads(response_json)]:
			username = '%s.%s' % (first_name.lower(), last_name.lower())
			email = '%s@generated.com' % username
			account = Account(username=username, first_name=first_name, last_name=last_name, email=email)
			account.set_password(username)
			generated.append(account)
		Account.objects.bulk_create(generated)
		print('OK (%d)' % count)
	else:
		print('ERROR')
	print('DONE')


def main(argv):
	if len(argv) < 1:
		sys.exit(1)
	if argv[0] == 'generate_users':
		if argv[1].isdigit():
			generate_users(int(argv[1]), argv[2:])
		else:
			print('Invalid argument: "%s"' % argv[1])
			print('Usage: %s <count>' % argv[0])
			sys.exit(1)
	else:
		print('unrecognized command')


if __name__ == '__main__':
	main(sys.argv[1:])
