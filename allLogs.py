import os
import re
import datetime

import paramiko


def get_ssh(ip, user, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, 22, user, pw)
    return ssh


def get_rdwp_log(log_type, date, ip, user, pw, serverno):
    ssh = get_ssh(ip, user, pw)
    ml = ""
    yestoday = datetime.datetime.strptime(date, "%Y%m%d")
    yestoday = yestoday - datetime.timedelta(days=1)
    yestoday = yestoday.strftime("%Y%m%d")
    lines = []
    if ("rdwp" == log_type):
        if (serverno == 2):
            stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rdwp2;ls rdwp" + yestoday + "*.log")
            haslines = stdout.readlines()
            if (haslines == []):
                stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rdwp2;unzip rdwp" + yestoday + ".zip")
                haslines = stdout.readlines()
            ml = "cd /data/home/rdw/logs/rdwp2;ls *" + yestoday + "*.log -rt"
            stdin, stdout, stderr = ssh.exec_command(ml)
            lines = stdout.readlines()
            lines.sort(key=lambda d: int(d[13:d.find(".log")]), reverse=True)
            ml = "cd /data/home/rdw/logs/rdwp2;ls *" + date + "*.log -rt"
            stdin, stdout, stderr = ssh.exec_command(ml)
            lines2 = stdout.readlines()
            lines2.sort(key=lambda d: int(d[13:d.find(".log")]), reverse=True)
            lines.extend(lines2)
        else:
            stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rdwp;ls rdwp" + yestoday + "*.log")
            haslines = stdout.readlines()
            if (haslines == []):
                stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rdwp;unzip rdwp" + yestoday + ".zip")
                haslines = stdout.readlines()
                print(haslines)
            ml = "cd /data/home/rdw/logs/rdwp;ls *" + yestoday + "*.log -rt"
            stdin, stdout, stderr = ssh.exec_command(ml)
            lines = stdout.readlines()
            lines.sort(key=lambda d: int(d[13:d.find(".log")]), reverse=True)
            ml = "cd /data/home/rdw/logs/rdwp;ls *" + date + "*.log -rt"
            stdin, stdout, stderr = ssh.exec_command(ml)
            lines2 = stdout.readlines()
            lines2.sort(key=lambda d: int(d[13:d.find(".log")]), reverse=False)
            lines.extend(lines2)
    elif ("rtetl" == log_type):
        ml = "cd /data/home/rdw/logs/rtetl;ls *" + date + "*.log -rt"

    ssh.close()
    if ("rdwp" == log_type):
        lines.append("rdwp.log")
    elif ("rtetl" == log_type):
        lines.append("rtetl.log")
    print(lines)
    return lines


''' 
下载日志文件并根据日期提取到新的文件
'''


def down_load_rdwp(log_date, tj_date):
    lines = get_rdwp_log("rdwp", log_date, "10.145.6.236", "rdw", "rdw", 1)
    lines23701 = get_rdwp_log("rdwp", log_date, "10.145.6.237", "rdw", "rdw", 1)
    lines23702 = get_rdwp_log("rdwp", log_date, "10.145.6.237", "rdw", "rdw", 2)
    t = paramiko.Transport(("10.145.6.236", 22))
    t.connect(username="rdw", password="rdw")
    sftp = paramiko.SFTPClient.from_transport(t)
    try:
        os.remove("logs/rd.log")
    except IOError as e:
        print(e)
    for line in lines:
        path_str = "/data/home/rdw/logs/" + "rdwp" + "/" + line
        sftp.get(path_str.strip('\n'), ("logs/" + line).strip("\n"))
    t = paramiko.Transport(("10.145.6.237", 22))
    t.connect(username="rdw", password="rdw")
    sftp = paramiko.SFTPClient.from_transport(t)
    for line in lines23701:
        path_str = "/data/home/rdw/logs/" + "rdwp" + "/" + line
        sftp.get(path_str.strip('\n'), ("logs/23701" + line).strip("\n"))
    for line in lines23702:
        path_str = "/data/home/rdw/logs/" + "rdwp2" + "/" + line
        sftp.get(path_str.strip('\n'), ("logs/23702" + line).strip("\n"))
    sftp.close()

    lines23701 = list(map(lambda x: "23701" + x, lines23701))
    lines23702 = list(map(lambda x: "23702" + x, lines23702))
    lines.extend(lines23701)
    lines.extend(lines23702)
    ofile = open('logs/rd.log', 'w', encoding="utf-8")
    for fr in lines:
        fr = ("logs/" + fr).strip("\n")
        print(fr)
        for txt in open(fr, 'r', encoding='utf-8'):
            if (txt.find(tj_date) == 0):
                if (txt.find("batchInsert") < 0 and txt.find("batchUpdate") < 0):
                    ofile.write(txt)

    ofile.close()




# down_load_logs("rdwp","20170823")

def monitor_rdwp_log():
    down_load_rdwp("20170904", "2017-09-04")
    file_object = open('logs\\rd.log', 'r', encoding='utf-8')
    all_the_text = file_object.readlines()
    count = 0
    dict_all = {}
    list_local = locals()
    start_time = ""
    end_time = ""
    for line in all_the_text:
        if (line.find("功能代码是") > -1):
            funcode = ""
            dict_now = {}
            searchObj = re.search(r"功能代码是：(.*)", line)
            funcode = searchObj.group(1)
            dict_now["code"] = funcode

            searchObj = re.search(r"uuid:(.{36})", line)
            uuid = searchObj.group(1)
            dict_now["uuid"] = uuid

            searchObj = re.search(r"\d{4}(\-|\/|\.)\d{1,2}\1\d{1,2} \d{2}:\d{2}:\d{2},\d{3}", line)
            time = searchObj.group()
            if (start_time == ""):
                start_time = time
                print("调用接口开始时间:" + time + " !")
            end_time = time
            dict_now["time"] = time
            if (list_local.get("list_" + funcode) == None):
                list_local["list_" + funcode] = []
            list_local["list_" + funcode].append(dict_now)
            count += 1
            dict_all[funcode] = list_local.get("list_" + funcode)
            # print(line)
    print("共调用接口：" + str(int(count / 2)) + "次！")
    print("调用接口结束时间:" + end_time + " !")
    # print(list_local)
    # print(dict_all.keys())
    for key in dict_all.keys():
        t_list = dict_all[key]
        print("---------------------------")
        # print(key + ":" + str(len(t_list)) + "次！")
        jiexi(key, t_list)


def jiexi(key, list_t):
    alluuid = []
    for ll in list_t:
        uuid = ll["uuid"]
        alluuid.append(uuid)
    # 得到所有执行次数相同的uuid是一个
    alluuid = list(set(alluuid))
    # print("共调用接口：" + str(len(alluuid)) + "次！")
    max_time = 0.0
    min_time = 0.0
    all_time = 0.0
    min_uuid = ""
    nowcount=0
    for ll in alluuid:
        map_time = {}
        list_time = []
        count_uuid = 0
        # 统计每个uuid开始和结束时间
        for map_t in list_t:
            uuid = map_t["uuid"]
            if (ll == uuid):
                count_uuid += 1
                time = map_t["time"]
                list_time.append(time)
                map_time[ll] = list_time
                if (count_uuid > 1):
                    list_t.remove(map_t)
                    # list_t.remove(map_t)
                    break
        count_uuid = 0
        nowcount+=1
        if(nowcount%10000==0):
            print(str(nowcount)+":"+ll)
        # print(map_time[ll])
        list_n = map_time[ll]
        time1 = list_n[0]
        if (len(list_n) < 2):
            time2 = time1
            print("缺少结束或开始时间:" + ll)
        else:
            time2 = list_n[1]
        # print(time1)
        # print(time2)
        date1 = datetime.datetime.strptime(time1, '%Y-%m-%d %H:%M:%S,%f')
        date2 = datetime.datetime.strptime(time2, '%Y-%m-%d %H:%M:%S,%f')
        now_time = (date2 - date1).microseconds / 1000
        if (now_time > max_time):
            max_time = now_time
        if (now_time < min_time or min_time == 0.0):
            min_time = now_time
            min_uuid = ll
        all_time += now_time
        # print(ll+":"+str(now_time))

    count = len(alluuid)
    print(key + ":" + str(count) + "次！")
    print("执行平均时间是：" + str(round((all_time / count), 3)) + "毫秒！")
    print("执行最长时间是：" + str(max_time) + "毫秒！")
    print("执行最短时间是：" + str(min_time) + "毫秒！")


if (__name__ == "__main__"):
    monitor_rdwp_log()
