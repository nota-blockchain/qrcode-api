from flask import Flask, request, jsonify, render_template, send_file
# from flask_qrcode import QRcode
import /util/qrcode
app = Flask(__name__)
app.register_blueprint(bp)
app.config['SECRET_KEY'] = 'nooooooota'


@app.route("/")
def main():
    return "NOTA API", 200


@app.route("/qrcode", methods=["GET"])
def get_qrcode():
    # please get /qrcode?data=<qrcode_data>
    data = request.args.get("data", "")
    qrcode = make_qrcode_url(data)
    return qrcode


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
