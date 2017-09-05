import re
import time
from datetime import datetime

from sshClient import down_load_logs


def monitor_rdwp_log(date, ip, user, pw, pathstr, serverno):
    down_load_logs("rdwp", date, ip, user, pw, pathstr, serverno)
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
    print("调用接口结束时间:" + end_time + " !")
    print("共调用接口：" + str(int(count / 2)) + "次！")
    # print(list_local)
    # print(dict_all.keys())
    for key in dict_all.keys():
        t_list = dict_all[key]
        print("---------------------------")
        # print(key + ":" + str(len(t_list)) + "次！")
        jiexi(key, t_list)


'''
统计接口日志
'''


def jiexi(key, list_t):
    alluuid = []
    for ll in list_t:
        uuid = ll["uuid"]
        alluuid.append(uuid)
    # 得到所有执行次数相同的uuid是一个
    aset = set(alluuid)
    alluuid2 = list(aset)
    alluuid2.sort(key=alluuid.index)
    alluuid = alluuid2
    # print("共调用接口：" + str(len(alluuid)) + "次！")
    max_time = 0.0
    max_uuid = ""
    min_time = 0.0
    min_uuid = ""
    all_time = 0.0
    count_cs = 0
    for ll in alluuid:
        map_time = {}
        list_time = []
        count_uuid = 0
        # 统计每个uuid开始和结束时间
        count_mz = 0
        # list_t_t=list.copy(list_t)
        i = 0
        while i < len(list_t):
            map_t = list_t[i]
            uuid = map_t["uuid"]
            count_mz += 1
            if (ll == uuid):
                # print(str(count_mz) + "次 命中！--" + ll)
                count_mz = 0
                count_uuid += 1
                time = map_t["time"]
                list_time.append(time)
                map_time[ll] = list_time
                list_t.remove(map_t)
                if (count_uuid > 1):
                    break
            else:
                i += 1
        count_uuid = 0
        count_cs += 1
        # if (count_cs % 10000 == 0):
        #     print(str(count_cs) + ":" + ll)
        # print(map_time[ll])
        try:
            list_n = map_time[ll]
        except IOError as e:
            print(map_time)
            print(e)
        time1 = list_n[0]
        if (len(list_n) < 2):
            time2 = time1
            print("缺少结束或开始时间:" + ll)
        else:
            time2 = list_n[1]
        # print(time1)
        # print(time2)
        date1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S,%f')
        date2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S,%f')
        now_time = (date2 - date1).total_seconds()
        if (now_time > 1):
            print(ll + ":开始:" + list_n[0] + " 结束：" + list_n[1] + "共花费：" + str(now_time) + "秒！")
        if (now_time > max_time):
            max_time = now_time
            max_uuid = ll
        if (now_time < min_time or min_time == 0.0):
            min_time = now_time
            min_uuid = ll
        all_time += now_time
        # print(ll+":"+str(now_time))

    count = len(alluuid)
    print(key + ":" + str(count) + "次！")
    print("执行平均时间是：" + str(round((all_time / count), 3)) + "秒！")
    print("执行最长时间是：" + str(max_time) + "秒！uuid：" + max_uuid)
    print("执行最短时间是：" + str(min_time) + "秒！uuid：" + min_uuid)


if (__name__ == "__main__"):
    # shutil.rmtree("logs",True)
    # os.makedirs("logs")
    # 默认日期为当天
    date = time.strftime("%Y%m%d", time.localtime())
    date01 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    date = "20170905"
    print("统计开始时间:" + date01)
    # monitor_rdwp_log(date, "10.145.6.237", "rdw", "rdw",pathstr="/data/home/rdw/logs/",serverno=1)
    monitor_rdwp_log(date, "10.145.6.237", "rdw", "rdw", pathstr="/data/home/rdw/logs/", serverno=1)
    # monitor_rdwp_log(date, "10.145.6.237", "rdw", "rdw", pathstr="/data/home/rdw/logs/", serverno=2)
    date02 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    print("统计结束时间:" + date02)
    date02 = datetime.strptime(date02, '%Y-%m-%d %H:%M:%S')
    date01 = datetime.strptime(date01, '%Y-%m-%d %H:%M:%S')
    sjc = (date02 - date01).total_seconds()
    print("共花费：" + str(sjc) + "秒！")
