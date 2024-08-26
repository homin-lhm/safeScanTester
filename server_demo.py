from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/aa', methods=['post'])
def aa():
    data = request.json
    q_id = data['q_id']
    print(data)

    if q_id == 'or or':
        return jsonify({'data': [123, 234, 354]}), 403

    elif q_id == 'b':
        pass

    elif q_id == 'c':
        return jsonify({'data': 'mysql error'}), 403

    else:
        return jsonify({'msg': 'success'}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9676, debug=True)
