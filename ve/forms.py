# -*- coding: utf-8 -*-
"""
Venezuelan-specific form helpers.
"""

import re

from django.forms import ValidationError
from django.forms.fields import Select, CharField, RegexField, Field,\
     EMPTY_VALUES
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _


class VEZipCodeField(RegexField):
    """
    A field that accepts a 'classic' NNNN Zip Zone Code.

    See http://www.ipostel.gob.ve/nlinea/CodPost_entidad.php
    """

    default_error_messages = {
        'invalid' : _(u"Enter a zip code in the format XXXX"),
        'max_digits' : _(u"This field requires 4 digits."),
    }

    def __init__(self, *args, **kwargs):
        super(VEZipCodeField, self).__init__(
            r'^\d{4}$',
            max_length=4,
            min_length=4,
            *args,
            **kwargs
            )

    def clean(self, value):
        """
        Value can be a string either in the XXXX format.
        """
        value = super(VEZipCodeField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        if not value.isdigit():
            value = value.replace('.', '')
        if not value.isdigit():
            raise ValidationError(self.error_messages['invalid'])
        if len(value) not in (4,):
            raise ValidationError(self.error_messages['max_digits'])

class VEDNIField(CharField):
    """
    A field that validates 'Cédula de Identidad' (DNI) numbers.
    """
    default_error_messages = {
        'invalid': _(u"This field requires only numbers."),
        'max_digits': _(u"This field requires 7 or 8 digits."),
    }

    def __init__(self, *args, **kwargs):
        super(VEDNIField, self).__init__(
            max_length=10,
            min_length=7,
            *args,
            **kwargs
            )

    def clean(self, value):
        """
        Value can be a string either in the [X]X.XXX.XXX or [X]XXXXXXX formats.
        """
        value = super(VEDNIField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        if not value.isdigit():
            value = re.sub("[-\.]", "", value)
        try:
            int(value)
        except ValueError:
            raise ValidationError(self.error_messages['invalid'])
        if len(value) not in (7, 8):
            raise ValidationError(self.error_messages['max_digits'])

        return value


class VERIFField(RegexField):
    """
    A field that validates a Register Tax Information 
    (Registro Único de Información Fiscal - RIF) issued by SENIAT.

    See http://www.seniat.gob.ve/portal/page/portal/MANEJADOR_CONTENIDO_SENIAT/05MENU_HORIZONTAL/5.1ASISTENCIA_CONTRIBUYENTE/5.1.2ORIENTACION_GENERA/5.1.2.2TRAMITES_ADMINISTR/INFORMACION_01_GENERAL.pdf
    """

    VENEZUELAN_CITIZEN = '1'
    FOREIGN_CITIZEN = '2'
    COMMERCIAL = '3'
    PERSONAL_FIRM = '4'
    GOVERMENT = '5'
    rif_first_char = {
        'v':VENEZUELAN_CITIZEN,
        'e':FOREIGN_CITIZEN,
        'j':COMMERCIAL,
        'p':PERSONAL_FIRM,
        'g':GOVERMENT,
        }
    
    default_error_messages = {
        'invalid': _('Enter a valid RIF in the form: A-XXXXXXXX-X o AXXXXXXXXX.'),
        'checksum': _('Invalid RIF.'),
    }

    def __init__(self, *args, **kwargs):
        super(RIFField, self).__init__(r'^([jJ|vV|eE|gG|pP])-?\d{8}-?\d$',max_lenght=12, min_lenght=10,*args, **kwargs)
    
    def clean(self, value):
        """Value can be either a string in A-XXXXXXXX-X or AXXXXXXXXX format"""
        value = super(RIFField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        value, cd = self.__canon(value)
        if self.__calc_cd(value) != cd:
            raise ValidationError(self.error_messages['checksum'])
        return self.__format(value, cd)

    def __canon(self, rif):
        rif = rif.replace('-', '')
        if rif[0].lower() in self.rif_first_char:
            rif = rif.replace(rif[0], self.rif_first_char[rif[0].lower()])
        else:
            raise ValidationError(self.error_messages['invalid'])
        return rif[:-1], rif[-1]

    def __calc_cd(self, rif):
        '''
            There are 10 digits total, the first digit is in 1-5 range and represents the
            registration type (VENEZUELAN_CITIZEN, FOREIGN_CITIZEN, COMMERCIAL, PERSONAL_FIRM
            GOVERMENT). The next eight digits is the identification number and the last digit
            is a check digit
        '''

        multipliers = (4, 3, 2, 7, 6, 5, 4, 3, 2)
        tmp = sum([m * int(rif[idx]) for idx, m in enumerate(multipliers)])
        return str(11 - tmp % 11)

    def __format(self, rif, check_digit=None):
        if check_digit == None:
            check_digit = rif[-1]
            rif = rif[:-1]
        return u'%s%s%s' % (rif[:2], rif[2:], check_digit)

class VEPhoneField(RegexField):
    """
    A field that validates as Venezuelan phone postal code.
    Valid code is XXXX-XXXXXXX where X is digit.
    """
    default_error_messages = {
        #'invalid' : _(u'Phone numbers must be in XXXX-XXXXXXX format.'),
        'max_digits' : _(u"This field requires 12 digits."),
    }

    def __init__(self, *args, **kwargs):
        super(VEPhoneField, self).__init__(
            r'^\d{4}-\d{7}$',
            max_length=12,
            min_length=12,
            *args,
            **kwargs
            )

    def clean(self, value):
        """
        Value can be a string either in the XXXX-XXXXXXX format.
        """
        value = super(VEPhoneField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        #if not value.isdigit():
        #    value = value.replace('.', '')
        #if not value.isdigit():
        #    raise ValidationError(self.error_messages['invalid'])
        if len(value) not in (12, ):
            raise ValidationError(self.error_messages['max_digits'])


class VERegionsSelect(Select):
    """
    A Select widget that uses a list of Venezuelan regions as its choices.
    """
    def __init__(self, attrs=None):
        from ve_regions import REGION_CHOICES
        super(VERegionsSelect, self).__init__(attrs, choices=REGION_CHOICES)

class VERegionChoiceField(Field):
    """
    A choice field with a list of Venezuelan regions as its choices
    """
    widget = Select
    default_error_messages = {
        "invalid" : _(u'Select one of the available valid Venezuelan regions.'),
        }

    def __init__(self,
                 required=True,
                 widget=None,
                 label=None,
                 initial=None,
                 help_text=None
                 ):
        super(VERegionChoiceField, self).__init__(
            required,
            widget,
            label,
            initial,
            help_text
            )
        from ve_regions import REGION_CHOICES
        self.widget.choices = REGION_CHOICES

    def clean(self, value):
        value = super(VERegionChoiceField, self).clean(value)
        if value in EMPTY_VALUES:
            value = u''
        value = smart_unicode(value)
        if value == u'':
            return value
        valid_values = set([smart_unicode(k) for k, v in self.widget.choices])
        if value not in valid_values:
            raise ValidationError(self.error_messages['invalid'])
        return value


class VEStateSelect(Select):
    """
    A Select widget that uses a list of Venezuelan states as its choices.
    """
    def __init__(self, attrs=None):
        from ve_states import STATE_CHOICES
        super(VEStateSelect, self).__init__(attrs, choices=STATE_CHOICES)


class VEStateChoiceField(Field):
    """
    A choice field that uses a list of Venezuelan states as its choices.
    """
    widget = Select
    default_error_messages = {
        'invalid': _(u'Select a valid Venezuelan state. That state is not one of the available states.'),
    }

    def __init__(self, required=True, widget=None, label=None,
                 initial=None, help_text=None):
        super(VEStateChoiceField, self).__init__(required, widget, label,
                                                 initial, help_text)
        from ve_states import STATE_CHOICES
        self.widget.choices = STATE_CHOICES

    def clean(self, value):
        value = super(VEStateChoiceField, self).clean(value)
        if value in EMPTY_VALUES:
            value = u''
        value = smart_unicode(value)
        if value == u'':
            return value
        valid_values = set([smart_unicode(k) for k, v in self.widget.choices])
        if value not in valid_values:
            raise ValidationError(self.error_messages['invalid'])
        return value


class VESMunicipalitySelect(Select):
    """
    A Select widget that uses a list of Venezuelan municipalities as its choices.
    """
    pass

class VEMunicipalityChoiceField(Field):
    """
    A choice field that uses a list of Venezuelan municipalities as its choices.
    """
    pass

class VEParishesSelect(Select):
    """
    A Select widget that uses a list of Venezuelan parishes as its choices.
    """
    pass

class VEParishesChoiceField(Field):
    """
    A choice field that uses a list of Venezuelan parishes as its choices.
    """
    pass
