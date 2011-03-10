from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, email_re
from django.utils.translation import ugettext_lazy as _
from kiki.commands import COMMANDS
import re


__all__ = ('EmailDomainValidator', 'EmailNameValidator')


local_part_re, domain_name_re = email_re.pattern.split('@')
local_part_re = re.compile(local_part_re + "$", re.IGNORECASE)
domain_name_re = re.compile("^" + domain_name_re, re.IGNORECASE)
validate_local_part = RegexValidator(local_part_re, _(u'Enter a valid email local part.'), 'invalid')


class DomainNameValidator(RegexValidator):
	def __call__(self, value):
		try:
			super(DomainNameValidator, self).__call__(value)
		except ValidationError, e:
			# Trivial case failed. Try for possible IDN domain-part
			if value:
				try:
					value = value.encode('idna')
				except UnicodeError:
					raise e
				super(DomainNameValidator, self).__call__(value)
			else:
				raise


validate_domain_name = DomainNameValidator(domain_name_re, _(u'Enter a valid domain name.'), 'invalid')


def validate_not_command(value):
	from kiki.models import MailingList
	value = value.rsplit('-', 1)
	if len(value) == 2 and value[1] in COMMANDS:
		raise ValidationError(u"`%s` is a command and cannot be used as part of an email address." % value[1])