import os
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')
RATES = {'leve': {'baja': .05, 'media': .15, 'alta': .30}, 'moderada': {'baja': .15, 'media': .40, 'alta': .65}, 'grave': {'baja': .35, 'media': .70, 'alta': .95}}

@app.get('/')
def home():
    return send_from_directory('.', 'index.html')

@app.get('/api/health')
def health():
    return jsonify(status='ok', service='EcoNiño Perú', backend='Python Flask')

@app.post('/api/simulate')
def simulate():
    data = request.get_json(silent=True) or {}
    scenario = data.get('scenario', 'moderada')
    products = data.get('products', [])
    if scenario not in RATES or not isinstance(products, list) or len(products) > 1000:
        return jsonify(error='Escenario o inventario inválido'), 400
    total = loss = 0.0
    details = []
    for p in products:
        try:
            name = str(p['name'])[:100]
            qty = int(p['qty'])
            cost = float(p['cost'])
            risk = p['risk']
            if not name or qty < 1 or qty > 1000000 or not 0 < cost < 100000000 or risk not in RATES[scenario]:
                raise ValueError()
            value = round(qty * cost, 2)
            item_loss = round(value * RATES[scenario][risk], 2)
        except (ValueError, KeyError, TypeError, OverflowError):
            return jsonify(error='Producto inválido'), 400
        total += value
        loss += item_loss
        details.append({'name': name, 'value': value, 'loss': item_loss})
    return jsonify(total=round(total,2), loss=round(loss,2), remaining=round(total-loss,2), product_count=len(products), scenario=scenario, details=details, educational_estimate=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
