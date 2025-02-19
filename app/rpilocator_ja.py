from playwright.sync_api import sync_playwright
from flask import *
import json
import time

json_path = "rpilocator_ja.json"

product_description = {
    # ssci
    "RPI-ZERO": "Raspberry Pi Zero v1.3",
    "RPI-ZERO-W": "Raspberry Pi Zero W",
    "RPI-ZERO-WH": "Raspberry Pi Zero WH",
    "RPI-SC0510": "Raspberry Pi Zero 2 W",
    "RPI-3A+": "Raspberry Pi 3 Model A+ 512MB RAM",
    "ELEMENT14-2842228": "Raspberry Pi 3 Model B+ 1GB RAM",
    "RASPBERRY-PI-4-MODEL-B-1GB": "Raspberry Pi 4 Model B 1GB RAM",
    "RASPBERRY-PI-4-MODEL-B-2GB": "Raspberry Pi 4 Model B 2GB RAM",
    "ELEMENT14-3051891": "Raspberry Pi 4 Model B 4GB RAM",
    "RASPBERRY-PI-4-MODEL-B-8GB": "Raspberry Pi 4 Model B 8GB RAM",
    "RPI-SC1110": "Raspberry Pi 5 2GB RAM",
    "RPI-SC1111": "Raspberry Pi 5 4GB RAM",
    "RPI-SC1112": "Raspberry Pi 5 8GB RAM",
    "RPI-SC1113": "Raspberry Pi 5 16GB RAM",
    "RPI-SC1430": "Raspberry Pi AI HAT+ 13TOPS",
    "RPI-SC1174": "Raspberry Pi AI Camera",
    # ksy
    "RASPIZERO13": "Raspberry Pi Zero v1.3",
    "RASPI0W11": "Raspberry Pi Zero W",
    "RASPIZWHSC0065": "Raspberry Pi Zero WH",
    "SC0510": "Raspberry Pi Zero 2 W",
    "RASPI3A1811853": "Raspberry Pi 3 Model A+ 512MB RAM",
    "RASPI3PSC0073": "Raspberry Pi 3 Model B+ 1GB RAM",
    "SC0192": "Raspberry Pi 4 Model B 1GB RAM",
    "SC0193": "Raspberry Pi 4 Model B 2GB RAM",
    "SC0194": "Raspberry Pi 4 Model B 4GB RAM",
    "SC0195": "Raspberry Pi 4 Model B 8GB RAM",
    "SC1110": "Raspberry Pi 5 2GB RAM",
    "SC1111": "Raspberry Pi 5 4GB RAM",
    "SC1112": "Raspberry Pi 5 8GB RAM",
    "SC1113": "Raspberry Pi 5 16GB RAM",
    "SC1785": "Raspberry Pi AI HAT+ 13TOPS",
    "SC1174": "Raspberry Pi AI Camera",
}

ksy_watch_list = [
    219, # Zero W
    406, # Zero WH
    222, # Zero V1.3
    849, # Zero 2W
    512, # 3A+
    435, # 3B+
    483, # 4B 1GB
    497, # 4B 2GB
    723, # 4B 4GB/Element14
    552, # 4B 8GB/Element14
    1095, # 5 2GB
    1015, # 5 4GB
    1016, # 5 8GB
    1157, # 5 16GB
    1114, # AI HAT+ 13TOPS
    1098, # AI Camera
]
eval_ksy = """() => {
    let price_length = document.getElementById('dt_Price').innerText.length - 1;
    return {
        product_code: document.getElementById('dt_Model').innerText,
        stock: document.getElementById('dt_Stock').innerText,
        price: document.getElementById('dt_Price').innerText.replace('円', '').replace(',', '').replace('価格未定', '0'),
    }
}"""
ssci_watch_list = [
    3200, # Zero W
    3646, # Zero WH
    3190, # Zero V1.3
    7600, # Zero 2W
    4110, # 3A+
    #3850, # 3B+(Suspended)
    5682, # 4B 1GB
    5681, # 4B 2GB
    5680, # 4B 4GB/Element14
    6370, # 4B 8GB
    9810, # 5 2GB
    9249, # 5 4GB
    9250, # 5 8GB
    10055, # 5 8GB
    9998, # AI HAT+ 13TOPS
    9813, # AI Camera
]
eval_ssci = """() => {
    return {
        product_code: document.getElementsByClassName('product-block--item-code')[0].innerText.split(': ')[1],
        stock: document.getElementsByClassName('product-block--stock')[0].innerText.split(': ')[1],
        price: document.getElementsByClassName('product-block--price')[0].innerText.substring(1).trim().replace(',', '').split(' ')[0]
    }
}"""

def load_list():
    with open(json_path) as f:
        raw = f.read()
    return json.loads(raw)

def update_list(vendor, pid, url, info):
    data = load_list()
    backup = []
    for c,i in enumerate(data['data']):
        if i[3] == vendor and i[7] == pid:
            # 既存のやつを消す
            backup = data['data'].pop(c)
            break
    # 具体的な在庫数は求めないため、Yes/Noにする
    last_stock = ""
    stock_count = 0
    if 'stock' in info and info['stock']:
        stock_count = int(info['stock'].replace('+', ''))
    if stock_count:
        stock = "Yes"
        last_stock = time.strftime("%Y-%m-%d")
        price = info['price']
    else:
        stock = "No"
        if len(backup):
            last_stock = backup[5]
            price = backup[6]
        else:
            last_stock = ""
            price = info['price'] if 'price' in info else ""
    data['data'].append([
        info['product_code'],
        product_description[info['product_code']] if info['product_code'] in product_description else info['product_code'],
        url,
        vendor,
        stock,
        last_stock,
        price,
        pid
    ])
    output = json.dumps(data)
    with open(json_path, 'w') as f:
        f.write(output)

def crawl(url, evaluate, wait = 0):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path='/usr/bin/chromium',
            headless=True,
            args=['--no-sandbox', '--no-zygote'],
            handle_sigint  = False,
            handle_sigterm = False,
            handle_sighup  = False
        )
        page = browser.new_page()
        page.goto(url)
        if wait:
            page.wait_for_timeout(wait)
        data = page.evaluate(evaluate)
        page.close()
        browser.close()
    return data

def crawl_ksy(i):
    url = f"https://raspberry-pi.ksyic.com/main/index/pdp.id/{i}/pdp.open/{i}"
    result = crawl(url, eval_ksy, wait = 3000)
    update_list('KSY', i, url, result)
    return result

def crawl_ssci(i):
    url = f"https://www.switch-science.com/products/{i}"
    result = crawl(url, eval_ssci)
    update_list('Switch Science', i, url, result)
    return result

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return jsonify(load_list()), 200

@app.route("/rpilocator_ja.json", methods=["GET"])
def return_json():
    return jsonify(load_list()), 200

@app.route("/crawl/all", methods=["GET"])
def crawl_all():
    result = ""
    for i in ssci_watch_list:
        try:
            crawl_ssci(i)
            time.sleep(10)
        except:
            result += "Error at %s\n"%i
    for i in ksy_watch_list:
        try:
            crawl_ksy(i)
            time.sleep(10)
        except:
            result += "Error at %s\n"%i
    if result:
        print(result)
        return result, 500
    else:
        return "OK", 200

@app.route("/crawl/ksy/<int:product_id>", methods=["GET"])
def ksy(product_id):
    if not product_id in ksy_watch_list:
        return "It doesn't watching.", 400
    result = crawl_ksy(product_id)
    return jsonify(result), 200

@app.route("/crawl/ssci/<int:product_id>", methods=["GET"])
def ssci(product_id):
    if not product_id in ssci_watch_list:
        return "It doesn't watching.", 400
    result = crawl_ssci(product_id)
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=31415, threaded=True)
