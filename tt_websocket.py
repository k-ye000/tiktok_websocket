import json
import time
import requests
import websocket
import random


request_id = 0
target_url = 'https://www.toutiao.com/c/user/token/MS4wLjABAAAAZ-7_bvIhGk-tKa7Z4B3GUSA0d-6Rc3qMsEsMEPPUQig'

def get_websocket_connection():
    r = requests.get(url='http://127.0.0.1:9222/json') #这是开启chrome headless的机器地址
    print(r)
    if r.status_code != 200:
        raise ValueError("can not get the api ,please check if docker is ready")
 
    conn_api = r.json()[0].get('webSocketDebuggerUrl')
    print(conn_api)
    return websocket.create_connection(conn_api)
 
def run_command(conn, method, **kwargs):
    global request_id
    request_id += 1
    command = {'method': method,
               'id': request_id,
               'params': kwargs}
    conn.send(json.dumps(command))
    msg = json.loads(conn.recv())
    if msg.get('id') == request_id:
        return msg
 
def get_element():
    count=0
    conn = get_websocket_connection()
    msg = run_command(conn, 'Page.navigate', url=target_url)
    time.sleep(3)
    get_text = """$x = function (xpath, context) { //定义xpath方法
        var nodes = [];
        try {
            var doc = (context && context.ownerDocument) || window.document;
            var results = doc.evaluate(xpath, context || doc, null, XPathResult.ANY_TYPE, null);
            var node;
            while (node = results.iterateNext()) {
                nodes.push(node);
            }
        } catch (e) {
             throw e;
        }
        return nodes;
    };
    var p=$x('//*[@id="root"]/div/div[3]/div[1]/div/div[2]/div/div//div[1]/a[1]/@href');
    var href_array=[];
    for(var i=0;i<p.length;i++){href_array[i]=p[i]['value']};JSON.stringify(href_array);
    """
    page_down="window.scrollTo(0,document.body.scrollHeight)"
    
    page_height=0
    while True:
        time.sleep(random.random()+1.5)
        msg = run_command(conn, 'Runtime.evaluate', expression=get_text)
        end_page_height=run_command(conn, 'Runtime.evaluate', expression=page_down)

        href_list=json.loads(msg['result']['result']['value'])
        for url in href_list:
            if 'http' in url:
                print(url)
        count+=12
        print("共抓取%s条"%count)
        
        if page_height==end_page_height:
            break
        page_height=end_page_height

if __name__ == '__main__':
    get_element()