import re
import time
from datetime import datetime

from sshClient import my_ssh_client

'''
统计rtetl日志
'''


def monitor_rtetl_log(date, ip, user, pw):
    # print(sys.getdefaultencoding())
    my_ssh_client(date, ip, user, pw)
    file_object = open('logs\\rt.log', 'r', encoding='utf-8')
    all_the_text = file_object.readlines()

    tables = ["DI_ANNTY_SURVIVAL_POLICY_T", "DI_ANNU_WORKD_T", "DI_APPL_T", "DI_BANKACCT_LEN_T", "DI_BANK_LIST_T",
              "DI_BENF_T", "DI_CHARGE_T", "DI_CLIENT_ACCT_T", "DI_CLIENT_T", "DI_CODE_DESC_T", "DI_COMPANY_T",
              "DI_DIVD_T",
              "DI_EXPIRE_POLICY_T", "DI_GRP_CLIENT_ACCT_T", "DI_GRP_CLIENT_T", "DI_GRP_POLICY_DTL_T",
              "DI_GRP_POLICY_LIST_T", "DI_GUIDE_TIME_T", "DI_HOSPITAL_LIST_T", "DI_IMAGE_T", "DI_INSURED_T",
              "DI_INSURE_T",
              "DI_NOTE_CODE_CONF_T", "DI_NOTE_REPLY_CONFMN_T", "DI_OCCUP_T", "DI_ORG_AGENCY_T", "DI_ORG_BOS_T",
              "DI_ORG_BROKER_T", "DI_ORG_DMTM_T", "DI_ORG_WS_T", "DI_PAY_BANK_T", "DI_PAY_NET_T", "DI_PAY_T",
              "DI_POLICY_T",
              "DI_PRODUCT_T", "DI_RELAY_T", "FA_AGENCY_ASSESS_T", "FA_AGENCY_PERSIS_T", "FA_AGENT_COMMISSION_T",
              "FA_CLAIM_CASE_T", "FA_CLAIM_T", "FA_GRP_INSC_CLM_T", "FA_NOTICE_T", "FA_PERSIS_CONVT_COEF_T",
              "FA_POLICY_DTL_OWE_T", "FA_RENEW_LIST_T", "FA_UNLNK_UNIV_ACCT_BAL_T", "FA_UNLNK_UNIV_PRICE_T",
              "GRP_CUST_CONF_INFO_T"]
    for table in tables:
        print("---------------------------------------------------")
        index = 0
        index_table = 0
        # 所有消耗时间
        list_time = []
        time_all = 0
        time_max = 0
        time_min = 0
        count_update = 0
        count_del = 0
        for line in all_the_text:

            # print(line.index(table,0))
            if (line.find(table) > -1):
                if (index_table == 0):
                    index_table += 1
                    # print("第一条语句是" + line)
                    # 匹配时间
                    searchObj = re.search(r"\d{4}(\-|\/|\.)\d{1,2}\1\d{1,2} \d{2}:\d{2}:\d{2},\d{3}", line)
                    print("开始执行时间是：" + searchObj.group())
                # print(line)

                if (line.find("共更新了") > -1):
                    searchObj = re.search(r".+(\d+)条", line)
                    num = int(searchObj.group(1))
                    count_update += num
                    # if (num > 0):
                    #     print(searchObj.group())
                    #     print(num)

                if (line.find("共删除了") > -1):
                    searchObj = re.search(r".+(\d+)条", line)
                    num = int(searchObj.group(1))
                    count_del += num
                    # if (num > 0):
                    #     print(searchObj.group())
                    #     print(num)

                if (line.find("共花费了") > -1):
                    index += 1
                    # 匹配花费时间
                    searchObj = re.search(r"(\d+\.\d+)秒", line)
                    # print(line)
                    now_time = searchObj.group(1)
                    time_all = round(time_all + float(now_time), 3)

                    # 统计最大时间
                    if (float(now_time) > time_max):
                        time_max = float(now_time)

                    # 统计最小时间
                    if (float(now_time) < time_max):
                        time_min = float(now_time)
                    # print(searchObj.group(1))
                    # print(time_all)
                    list_time.append(searchObj.group(1))

        print(table + "共执行了" + str(index) + "次！")
        if (index > 0):
            print("平均耗时：" + str(round(time_all / index, 3)) + "秒！")
            print("最大耗时：" + str(time_max) + "秒！")
            print("最小耗时：" + str(time_min) + "秒！")
            print("更新总数：" + str(count_update) + "条！")
            print("删除总数：" + str(count_del) + "条！")


def monitor_rdwp_log(date, ip, user, pw, pathstr, serverno):
    # down_load_logs("rdwp", date,ip,user,pw,pathstr,serverno)
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
            print(ll + ":开始:" + list_n[0] + " 结束：" + list_n[1]+"共花费："+str(now_time)+"秒！")
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
    date02=datetime.strptime(date02, '%Y-%m-%d %H:%M:%S')
    date01 = datetime.strptime(date01, '%Y-%m-%d %H:%M:%S')
    sjc=(date02-date01).total_seconds()
    print("共花费："+str(sjc)+"秒！")
