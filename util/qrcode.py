from __future__ import print_function, absolute_import, unicode_literals

from base64 import urlsafe_b64encode, urlsafe_b64decode
from mimetypes import types_map
from io import BytesIO

from flask import Blueprint, current_app, send_file, url_for, jsonify
from qrcode import QRCode
from itsdangerous import Signer

__all__ = ['make_qrcode_image']

bp = Blueprint('qrcode', __name__, url_prefix='/_qrcode')


@bp.route('/<url>/<signature>')
def qrcode_image(url, signature):
    """The endpoint for generated QRCode image."""
    try:
        url = urlsafe_b64decode(url.encode('ascii'))
    except (ValueError, UnicodeEncodeError):
        return jsonify(r=False, error='invalid_data'), 404

    signer = get_qrcode_signer()
    if not signer.verify_signature(url, signature):
        return jsonify(r=False, error='invalid_signature'), 404

    image = make_qrcode_image(url, border=0)
    response = make_image_response(image, kind='png')
    return response


def get_qrcode_signer(app=None):
    """Creates a signer by the secret key of current app."""
    app = app or current_app
    if 'qrcode.signer' not in app.extensions:
        app.extensions['qrcode.signer'] = Signer(app.secret_key)
    return app.extensions['qrcode.signer']


def make_qrcode_image(data, **kwargs):
    """Creates a QRCode image from given data."""
    qrcode = QRCode(**kwargs)
    qrcode.add_data(data)
    return qrcode.make_image()


def make_image_response(image, kind):
    """Creates a cacheable response from given image."""
    mimetype = types_map['.' + kind.lower()]
    io = BytesIO()
    image.save(io, kind.upper())
    io.seek(0)
    return send_file(io, mimetype=mimetype, conditional=True)


def make_qrcode_url(url):
    """Creates a signed URL which pointed to a QRCode image."""
    signer = get_qrcode_signer()
    signature = signer.get_signature(url)
    url = urlsafe_b64encode(url.strip().encode('utf-8'))
    return url_for('jqrcode.qrcode_image', url=url, signature=signature)
