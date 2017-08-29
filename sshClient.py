import os
import re
import datetime
import paramiko


def my_ssh_client(date,ip,user,pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, 22, user, pw)

    t = paramiko.Transport((ip, 22))
    t.connect(username=user, password=pw)
    sftp = paramiko.SFTPClient.from_transport(t)
    yestoday=datetime.datetime.strptime(date,"%Y%m%d")
    yestoday=yestoday-datetime.timedelta(days=1)
    yestoday = yestoday.strftime("%Y%m%d")
    stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rtetl;ls *" + yestoday + "*.log -rt")
    haslines = stdout.readlines()
    if (haslines == []):
        stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rtetl;unzip rtetl" + yestoday + ".zip")
        haslines = stdout.readlines()
    lines = []
    stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rtetl;ls *" + yestoday + "*.log -rt")
    lines = stdout.readlines()
    lines.sort(key=lambda d: int(d[14:d.find(".log")]))
    stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rtetl;ls *"+date+"*.log -rt")
    lines2=stdout.readlines()
    lines2.sort(key=lambda d: int(d[14:d.find(".log")]))
    lines.extend(lines2)
    print(lines)
    try:
        os.remove("logs/rt.log")
    except IOError as e:
        print(e)
    yestoday = datetime.datetime.strptime(yestoday, "%Y%m%d")
    yestoday = yestoday.strftime("%Y-%m-%d")
    for line in lines:
        path_str = "/data/home/rdw/logs/rtetl/" + line
        sftp.get(path_str.strip('\n'), ("logs/" + line).strip("\n"))
    sftp.get("/data/home/rdw/logs/rtetl/rtetl.log", "logs/rtetl.log")
    ssh.close()
    sftp.close()

    ofile = open('logs/rt.log', 'w',encoding='utf-8')
    lines.append("rtetl.log")
    for fr in lines:
        fr = ("logs/" + fr).strip("\n")
        print(fr)
        for txt in open(fr, 'r', encoding='utf-8'):
            # print(txt)
            # searchObj = re.search(r"\d{4}(\-|\/|\.)\d{1,2}\1\d{1,2} \d{2}:\d{2}:\d{2},\d{3}", txt)
            # print(searchObj.group())
            # print(yestoday+"txt"+txt)
            if(txt.find(yestoday)==0):
                ofile.write(txt)

    ofile.close()


def get_rdwp_log(log_type, date,ip,user,pw,serverno):
    ssh = get_ssh(ip,user,pw)
    ml = ""
    yestoday = datetime.datetime.strptime(date, "%Y%m%d")
    yestoday = yestoday - datetime.timedelta(days=1)
    yestoday = yestoday.strftime("%Y%m%d")
    lines = []
    if ("rdwp" == log_type):
        if(serverno==2):
            stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rdwp2;ls rdwp"+yestoday+"*.log")
            haslines=stdout.readlines()
            if(haslines==[]):
                stdin, stdout, stderr = ssh.exec_command( "cd /data/home/rdw/logs/rdwp2;unzip rdwp"+yestoday+".zip")
                haslines = stdout.readlines()
            ml = "cd /data/home/rdw/logs/rdwp2;ls *" + yestoday + "*.log -rt"
            stdin, stdout, stderr = ssh.exec_command(ml)
            lines = stdout.readlines()
            lines.sort(key=lambda d: int(d[13:d.find(".log")]),reverse=True)
            ml = "cd /data/home/rdw/logs/rdwp2;ls *" + date + "*.log -rt"
            stdin, stdout, stderr = ssh.exec_command(ml)
            lines2 = stdout.readlines()
            lines2.sort(key=lambda d: int(d[13:d.find(".log")],reverse=False))
            lines.extend(lines2)
        else:
            stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rdwp;ls rdwp" + yestoday + "*.log")
            haslines = stdout.readlines()
            if (haslines == []):
                stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rdwp;unzip rdwp" + yestoday + ".zip")
                haslines=stdout.readlines()
                print(haslines)
            ml = "cd /data/home/rdw/logs/rdwp;ls *" + yestoday + "*.log -rt"
            stdin, stdout, stderr = ssh.exec_command(ml)
            lines = stdout.readlines()
            lines.sort(key=lambda d: int(d[13:d.find(".log")]),reverse=True)
            ml = "cd /data/home/rdw/logs/rdwp;ls *" + date + "*.log -rt"
            stdin, stdout, stderr = ssh.exec_command(ml)
            lines2 = stdout.readlines()
            lines2.sort(key=lambda d: int(d[13:d.find(".log")]),reverse=False)
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


def get_ssh(ip,user,pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, 22, user, pw)
    return ssh

''' 
下载日志文件
'''
def down_load_logs(log_type, date,ip,user,pw,pathstr,serverno):
    lines = get_rdwp_log(log_type, date,ip,user,pw,serverno)
    t = paramiko.Transport((ip, 22))
    t.connect(username=user, password=pw)
    sftp = paramiko.SFTPClient.from_transport(t)
    try:
        os.remove("logs/rd.log")
    except IOError as e:
        print(e)
    for line in lines:
        if(serverno==2):
            path_str = pathstr + log_type + "2/" + line
        else:
            path_str = pathstr+ log_type + "/" + line
        sftp.get(path_str.strip('\n'), ("logs/" + line).strip("\n"))
    # sftp.get("/data/home/rdw/logs/rtetl/rtetl.log", "logs/rtetl.log")
    sftp.close()
    now_log=""
    if("rdwp"==log_type):
        now_log="rd.log"
    elif("rtetl"==log_type):
        now_log = "rt.log"
    ofile = open('logs/'+now_log, 'w',encoding="utf-8")
    yestoday = datetime.datetime.strptime(date, "%Y%m%d")
    yestoday = yestoday - datetime.timedelta(days=1)
    yestoday = yestoday.strftime("%Y%m%d")
    yestoday = datetime.datetime.strptime(yestoday, "%Y%m%d")
    yestoday = yestoday.strftime("%Y-%m-%d")
    for fr in lines:
        fr = ("logs/" + fr).strip("\n")
        print(fr)
        for txt in open(fr, 'r', encoding='utf-8'):
            if (txt.find(yestoday) == 0):
                if(txt.find("batchInsert")<0 and txt.find("batchUpdate")<0):
                    ofile.write(txt)

    ofile.close()

# down_load_logs("rdwp","20170823")