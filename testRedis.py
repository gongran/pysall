import redis

r=redis.StrictRedis(host='192.168.154.128', port=6379, db=0,password='123456',decode_responses=True)
r.set('foo','bar1')
a =r.get('foo')
print(a)
r.hmset("names",{'jim':'001','lilei':'002','mike':'003'})
names=r.hgetall("names")
print(names)
print(names['jim'])