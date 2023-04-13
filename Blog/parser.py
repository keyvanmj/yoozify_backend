import json
from rest_framework.parsers import BaseParser, DataAndFiles
from django.conf import settings
from django.http.multipartparser import MultiPartParser as DjangoMultiPartParser, MultiPartParserError
import six
from rest_framework.exceptions import ParseError


class MultiPartJSONParser(BaseParser):
    """
    Parser for multipart form data which might contain JSON values
    in some fields as well as file data.
    This is a variation of MultiPartJSONParser, which goes through submitted fields
    and attempts to decode them as JSON where a value exists. It is not to be used as a replacement
    for MultiPartParser, only in cases where MultiPart AND JSON data are expected.
    """
    media_type = 'multipart/form-data'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as a multipart encoded form,
        and returns a DataAndFiles object.
        `.data` will be a `QueryDict` containing all the form parameters, and JSON decoded where available.
        `.files` will be a `QueryDict` containing all the form files.
        """
        parser_context = parser_context or {}
        request = parser_context['request']
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        meta = request.META.copy()
        meta['CONTENT_TYPE'] = media_type
        upload_handlers = request.upload_handlers

        try:
            parser = DjangoMultiPartParser(meta, stream, upload_handlers, encoding)
            data, files = parser.parse()
            for key in data:
                if data[key]:
                    try:
                        data[key] = json.loads(data[key])
                    except ValueError:
                        pass
            return DataAndFiles(data, files)
        except MultiPartParserError as exc:
            raise ParseError('Multipart form parse error - %s' % six.text_type(exc))