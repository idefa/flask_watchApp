# coding=utf-8

from flask import Flask, request, redirect, url_for, jsonify, session
from werkzeug.contrib.cache import SimpleCache
import paramiko
import os
import simplejson as json
import sys


# import simplejson as json
# import simplejson as json


class IpInfo(object):
    @classmethod
    def getinfo(self, ip, port, usr, pwd, command):
        output = ''
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port, usr, pwd)
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read()
            ssh.close()
            # ssh.close()
            # output = '{"pmtsstatus":{"text":["abnormal"],"status":0,"exception":["异常"]},"pmtsroot":{"text":["abnormal"],"status":0,"exception":["hvps1异常","hvps2异常"]},"tlqstatus":{"text":["normal"],"status":1,"exception":[""]},"filesystem":{"text":["abnormal"],"status":0,"exception":["/AAA/BBB","/sss/ss2"]}}'
            return output
        except:
            print("Unexpected error:", sys.exc_info()[0])
        finally:
            return output


# 生成Falsk App对象
app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False
app.secret_key = 'mysecretkey'
cache = SimpleCache()


# 登陆页面
@app.route('/')
def index():
    return app.send_static_file('extra-signin.html')


# /login post,登陆api
@app.route('/login', methods=['POST'])
def login():
    data = cache.get('user.json');
    if data is None:
        filename = os.path.join(app.static_folder, 'user.json')
        with open(filename, 'rb') as blog_file:
            data = json.load(blog_file, encoding='utf-8')
            cache.set('user.json', data, 0)
    loginuser = request.form['user']
    loginpwd = request.form['pass']
    if loginuser == data["user"] and loginpwd == data["pwd"]:
        session['username'] = loginuser
        print(loginuser)
        print(loginpwd)
        return redirect(url_for('manager'))
    return redirect('/?msg=' + '用户名密码错误')


# /main 主页面
@app.route('/main')
def main():
    # 判断是否登陆
    if 'username' not in session:
        return redirect('/')

    return app.send_static_file('index.html')


# /main 管理页面
@app.route('/manager')
def manager():
    # 判断是否登陆
    if 'username' not in session:
        return redirect('/')

    return app.send_static_file('manager.html')


# /syslist  get 系统列表api
@app.route('/syslist')
def syslist():
    # 判断是否登陆
    if 'username' not in session:
        return redirect('/')
    data = cache.get('sys.json');
    if data is None:
        filename = os.path.join(app.static_folder, 'sys.json')
        with open(filename, 'rb') as blog_file:
            data = json.load(blog_file, encoding='utf-8')
            cache.set('sys.json', data, 0)
    return json.dumps(data)

# /syslist  get 系统列表api
@app.route('/newsyslist')
def newsyslist():
    # 判断是否登陆
    if 'username' not in session:
        return redirect('/')
    data = cache.get('newSys.json');
    if data is None:
        filename = os.path.join(app.static_folder, 'newSys.json')
        with open(filename, 'rb') as blog_file:
            data = json.load(blog_file, encoding='utf-8')
            cache.set('newSys.json', data, 0)
    return json.dumps(data)


# /iplist  get IP列表Api ,参数system是查询条件,默认为空,代表不筛选,system有值的时候,根据system筛选iplist
@app.route('/iplist', defaults={'system': ''})
@app.route('/iplist/<system>')
def iplist(system):
    # 判断是否登陆
    if 'username' not in session:
        return redirect('/')
    # print(system)

    data = cache.get('ip.json');
    if data is None:
        filename = os.path.join(app.static_folder, 'ip.json')
        with open(filename, 'rb') as blog_file:
            data = json.load(blog_file, encoding='utf-8')
            cache.set('ip.json', data, 0)
    if len(system) > 0:
        list = [];
        for ipinfo in data:
            if ipinfo["system"] == system:
                list.append(ipinfo)
        # print(system)
        # print(list)
        return json.dumps(list)
    return json.dumps(data)


@app.route('/donormal', defaults={'ip': None, 'type': None})
@app.route('/donormal/<ip>', defaults={'type': None})
@app.route('/donormal/<ip>/<type>')
def donormal(ip=None, type=None):
    if ip is None:
        return json.dumps({'mark': '执行失败', 'text': ['ip不能为空']})
    if type is None:
        return json.dumps({'mark': '执行失败', 'text': ['type不能为空']})
    data = cache.get('ip.json');
    if data is None:
        filename = os.path.join(app.static_folder, 'ip.json')
        with open(filename, 'rb') as blog_file:
            data = json.load(blog_file, encoding='utf-8')
            cache.set('ip.json', data, 0)
    jsondata = cache.get(ip +"+"+type+"_info");
    if jsondata is None:
        for jsonobject in data:
            if jsonobject["ip"] == ip:
                for jsonNormalCommand in jsonobject["normalCommands"]:
                    if jsonNormalCommand["type"] == type:
                        ##执行command
                        ##infoStr = IpInfo.getinfo(jsonobject["ip"], jsonobject["port"], jsonobject["usr"],jsonobject["pwd"],jsonNormalCommand["command"]);
                        infoStr='{"mark": "执行成功", "text": ["'+type+'"]}';
                        if len(infoStr) > 0:
                            jsondata = json.dumps(json.loads(infoStr, encoding='utf-8'))
                            cache.set(ip +"+"+type+"_info", jsondata, 10)
                        break;
                break
    return jsondata

@app.route('/doprocess', defaults={'ip': None,'process':None,'type': None,'callback':None})
@app.route('/doprocess/<ip>', defaults={'process': None,'type': None,'callback':None})
@app.route('/doprocess/<ip>/<process>', defaults={'type': None,'callback':None})
@app.route('/doprocess/<ip>/<process>/<type>',defaults={'callback':None})
@app.route('/doprocess/<ip>/<process>/<type>/<callback>')
def doprocess(ip=None,process=None,type=None,callback=None):
    if ip is None:
        return json.dumps({'mark': '执行失败', 'text': ['ip不能为空']})
    if process is None:
        return json.dumps({'mark': '执行失败', 'text': ['process不能为空']})
    if type is None:
        return json.dumps({'mark': '执行失败', 'text': ['type不能为空']})
    data = cache.get('ip.json');
    if data is None:
        filename = os.path.join(app.static_folder, 'ip.json')
        with open(filename, 'rb') as blog_file:
            data = json.load(blog_file, encoding='utf-8')
            cache.set('ip.json', data, 0)
    jsondata = cache.get(ip + "+" + process+"_"+type + "_info");
    if jsondata is None:
        for jsonobject in data:
            if jsonobject["ip"] == ip:
                for jsonProcess in jsonobject["processCommands"]:
                    if jsonProcess["type"] == process:
                        for processBtn in jsonProcess["button"]:
                            if processBtn["type"]==type:
                                ##执行command
                                if callback is None:
                                  ##infoStr = IpInfo.getinfo(jsonobject["ip"], jsonobject["port"], jsonobject["usr"],jsonobject["pwd"],processBtn["command"]);
                                  infoStr = '{"mark": "执行成功", "text": ["' + type + '"]}';
                                else:
                                  ##infoStr = IpInfo.getinfo(jsonobject["ip"], jsonobject["port"], jsonobject["usr"],jsonobject["pwd"],processBtn["returncommand"]);
                                  infoStr = '{"mark": "执行成功", "text": ["' + type + '"]}';
                                if len(infoStr) > 0:
                                    jsondata = json.dumps(json.loads(infoStr, encoding='utf-8'))
                                    cache.set(ip + "+" + process+"_"+type + "_info", jsondata, 10)
                                break
                        break;
                break
    return jsondata


@app.route('/processlist/<ip>')
def processlist(ip):
    data = cache.get('ip.json');
    if data is None:
        filename = os.path.join(app.static_folder, 'ip.json')
        with open(filename, 'rb') as blog_file:
            data = json.load(blog_file, encoding='utf-8')
            cache.set('ip.json', data, 0)
    jsondata = cache.get(ip + "_info");
    if jsondata is None:
        for jsonobject in data:
            if jsonobject["ip"] == ip:
                jsondata = json.dumps(jsonobject['processCommands'])
                cache.set(ip + "_info", jsondata, 10)
                break
    return jsondata


# /ipinfo  get ip的监控信息,参数是ip地址
@app.route('/ipinfo/<ip>')
def ipinfo(ip):
    # 判断是否登陆
    # if 'username' not in session:
    #    return redirect('/')
    data = cache.get('ip.json');
    if data is None:
        filename = os.path.join(app.static_folder, 'ip.json')
        with open(filename, 'rb') as blog_file:
            data = json.load(blog_file, encoding='utf-8')
            cache.set('ip.json', data, 0)
    jsondata = cache.get(ip + "_info");
    if jsondata is None:
        for jsonobject in data:
            if jsonobject["ip"] == ip:
                infoStr = IpInfo.getinfo(jsonobject["ip"], jsonobject["port"], jsonobject["usr"], jsonobject["pwd"],
                                         jsonobject["command"]);
                if len(infoStr) > 0:
                    # print(infoStr.decode("utf-8") )
                    jsonobject["info"] = json.loads(infoStr, encoding='utf-8')
                    # print(jsonobject)
                jsondata = json.dumps(jsonobject)
                cache.set(ip + "_info", jsondata, 10)
                break
    return jsondata


#  app启动函数
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
