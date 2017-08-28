import os

import paramiko


def my_ssh_client(date,ip,user,pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, 22, user, pw)

    t = paramiko.Transport((ip, 22))
    t.connect(username=user, password=pw)
    sftp = paramiko.SFTPClient.from_transport(t)

    stdin, stdout, stderr = ssh.exec_command("cd /data/home/rdw/logs/rtetl;ls *"+date+"*.log -rt")
    lines = []
    lines = stdout.readlines()
    print(lines)
    try:
        os.remove("logs/rt.log")
    except IOError as e:
        print(e)

    for line in lines:
        path_str = "/data/home/rdw/logs/rtetl/" + line
        sftp.get(path_str.strip('\n'), ("logs/" + line).strip("\n"))
    sftp.get("/data/home/rdw/logs/rtetl/rtetl.log", "logs/rtetl.log")
    ssh.close()
    sftp.close()

    ofile = open('logs/rt.log', 'w')
    lines.append("rtetl.log")
    for fr in lines:
        fr = ("logs/" + fr).strip("\n")
        print(fr)
        for txt in open(fr, 'r', encoding='utf-8'):
            ofile.write(txt)

    ofile.close()


def get_rdwp_log(log_type, date,ip,user,pw,serverno):
    ssh = get_ssh(ip,user,pw)
    ml = ""
    if ("rdwp" == log_type):
        if(serverno==2):
            ml = "cd /data/home/rdw/logs/rdwp2;ls *" + date + "*.log -rt"
        else:
            ml = "cd /data/home/rdw/logs/rdwp;ls *" + date + "*.log -rt"
    elif ("rtetl" == log_type):
        ml = "cd /data/home/rdw/logs/rtetl;ls *" + date + "*.log -rt"
    stdin, stdout, stderr = ssh.exec_command(ml)
    lines = []
    lines = stdout.readlines()
    ssh.close()
    if ("rdwp" == log_type):
        lines.append("rdwp.log")
    elif ("rtetl" == log_type):
        lines.append("rtetl.log")
    # print(lines)
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
    for fr in lines:
        fr = ("logs/" + fr).strip("\n")
        print(fr)
        for txt in open(fr, 'r', encoding='utf-8'):
            ofile.write(txt)

    ofile.close()

# down_load_logs("rdwp","20170823")