from flask_cors import CORS
from flask import *
from flask import request
import re
import threading
import datetime

app = Flask(__name__)
CORS(app)


@app.route("/parse")
def parse():
    content = request.args.get('parseTxt')

    pattern = r'((.)(曜日)(\n|(, ))(.*?)(月 )([0-9]*)((, )([0-9]*))?|(\n課題 )(.*?)( は、完了とマークされていません。\n)(.*?)( / )([\s\S]*?)(\n期限：)([0-9]*)(:)([0-9]*))'
    result = []
    monthArray = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]

    result.append(re.findall(pattern, content))
    hwarray = []
    date = ''
    for data in result[0]:
        if data[17] == '':
            date = {'month': monthArray.index(data[5]), 'day': int(data[7])}
        else:
            print(data)
            hwarray.append({})
            hwarray[-1]['className'] = data[14]
            hwarray[-1]['homeworkName'] = data[12]
            print(date['month'],type(date['month']))
            hwarray[-1]['dueM'] = str(date['month']).zfill(2)
            hwarray[-1]['dueD'] = str(date['day']).zfill(2)
            hwarray[-1]['dueh'] = str(data[18]).zfill(2)
            hwarray[-1]['duem'] = str(data[20]).zfill(2)

    """ pattern = [r'(「)(.*?)(」)', r'(.*?)(\n+\n 課題)', r'(\d+\d)(\/)(\d+\d)( )(\d+\d)+(:)(\d+\d)']
    result = []

    result.append(re.findall(pattern[0], content))
    result.append(re.findall(pattern[1], content))
    result.append(re.findall(pattern[2], content))

    for pt in pattern:
        result.append(re.findall(pt, content))

    hwarray = []

    if result:
        for i, item in enumerate(result[0]):
            hwarray.append({})
            hwarray[i]['homeworkName'] = item[1]

    if result:
        for i, item in enumerate(result[1]):
            if item[0].startswith('　(〆'):
                for k in reversed(range(i)):
                    if not result[1][k][0].startswith('　(〆'):
                        hwarray[i]['className'] = result[1][k][0]
                        break
            else:
                hwarray[i]['className'] = item[0]

    if result:
        for i, item in enumerate(result[2]):
            hwarray[i]['dueM'] = item[0]
            hwarray[i]['dueD'] = item[2]
            hwarray[i]['dueh'] = item[4]
            hwarray[i]['duem'] = item[6]

    print(hwarray) """
    return jsonify({'parsedHomeworks': hwarray})


@app.route("/addnew")
def addnew():
    returnedHW = json.loads(request.args.get('hws'))
    for item in returnedHW["hwl"]:
        item.update({"status": False})

    def isDup(hwName, className):
        if('hwl' in df):
            for item in df['hwl']:
                if item['homeworkName'] == hwName and item['className'] == className:
                    print(hwName + ' is a duplicate.')
                    returnedHW['hwl'] = list(filter(lambda i: not (i['className'] ==
                                                                   className and i['homeworkName']) == hwName, returnedHW['hwl']))
                    break
    with open('./data/savedhw.json', mode='r') as f:
        df = json.load(f)
        for item in returnedHW['hwl']:
            thread = threading.Thread(target=isDup, args=(item['homeworkName'], item['className'],))
            thread.start()
        if 'hwl' in df:
            df['hwl'] += returnedHW['hwl']
        else:
            df = returnedHW
    with open('./data/savedhw.json', mode='w') as f:
        json.dump(df, f, ensure_ascii=False, indent=4)
        return jsonify({'result': 'success'})


@app.route("/hwlist")
def hwlist():
    with open('./data/savedhw.json', mode='r') as f:
        k = json.load(f)
        print(type(k['hwl'][1]['dueM']))
        print(k['hwl'][1]['dueM'])
        thisMonth = datetime.datetime.today().month
        if thisMonth == 12:
            k['hwl'] = sorted(k['hwl'], key=lambda x: ((x['dueM'] if x['dueM']!='12' else '00' )  +
                                                   x['dueD']  + x['dueh']  + x['duem']))
        else:
            k['hwl'] = sorted(k['hwl'], key=lambda x: ((x['dueM'])  +
                                                   x['dueD']  + x['dueh']  + x['duem']))
        
        k['hwl'] = list(filter(lambda x: (x['status'] == False), k['hwl']))
        return jsonify(k)


@app.route("/hwDoneList")
def hwdonelist():
    with open('./data/savedhw.json', mode='r') as f:
        k = json.load(f)
        k['hwl'] = sorted(k['hwl'], key=lambda x: (x['dueM'] +
                                                   x['dueD'] + x['dueh'] + x['duem']))
        k['hwl'] = list(filter(lambda x: (x['status'] == True), k['hwl']))
        return jsonify(k)


@app.route("/markAsDone")
def markAsDone():
    nameOfTask = request.args.get('nameOfTask')
    with open('./data/savedhw.json', mode='r') as f:
        df = json.load(f)
        for item in df['hwl']:
            if item['homeworkName'] == nameOfTask:
                item['status'] = True
        print(df)
    with open('./data/savedhw.json', mode='w') as f:
        print("df:" + str(df))
        json.dump(df, f, ensure_ascii=False, indent=4)
        return jsonify({'result': 'success'})


@app.route("/markAsUndone")
def markAsUndone():
    nameOfTask = request.args.get('nameOfTask')
    with open('./data/savedhw.json', mode='r') as f:
        df = json.load(f)
        for item in df['hwl']:
            if item['homeworkName'] == nameOfTask:
                item['status'] = False
        print(df)
    with open('./data/savedhw.json', mode='w') as f:
        print("df:" + str(df))
        json.dump(df, f, ensure_ascii=False, indent=4)
        return jsonify({'result': 'success'})


@app.route("/delete")
def deleteTask():
    nameOfTask = request.args.get('nameOfTask')
    with open('./data/savedhw.json', mode='r') as f:
        df = json.load(f)
        df['hwl'] = [i for i in df['hwl'] if not (i['homeworkName'] == nameOfTask)]
        print(df)
    with open('./data/savedhw.json', mode='w') as f:
        print("df:" + str(df))
        json.dump(df, f, ensure_ascii=False, indent=4)
        return jsonify({'result': 'success'})


if __name__ == "__main__":
    app.run(port=3000, host='0.0.0.0', debug=False)
