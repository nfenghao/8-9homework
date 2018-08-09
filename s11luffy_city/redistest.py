import redis

conn = redis.Redis(host='192.168.11.136', port=6379)
conn.set('msg', '嘎嘎嘎')
val = conn.get('msg').decode('utf-8')
print(val)
