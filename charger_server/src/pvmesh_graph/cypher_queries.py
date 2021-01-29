merge_mesh4th = '''
MERGE (:Mesh4th { name:$name, longitude:$longitude, latitude:$latitude, meshcode:$meshcode })
'''
merge_charger_node = '''
MATCH (m:Mesh4th { meshcode:$meshcode })-[r:LENGTH]->(to_node) \
MERGE (c:Charger { \
        meshcode:$meshcode, name:'Charger_'+toString(m.meshcode), \
        time:$time, latitude:m.latitude, longitude:m.longitude, \
        ppv:$ppv, ppv_030:$ppv_030, ppv_060:$ppv_060, ppv_090:$ppv_090, \
        ppv_120:$ppv_120, ppv_150:$ppv_150, ppv_180:$ppv_180, \
        pd:$pd, pd_030:$pd_030, pd_060:$pd_060, pd_090:$pd_090, \
        pd_120:$pd_120, pd_150:$pd_150, pd_180:$pd_180 \
        }) \
MERGE (c)-[:LENGTH { length:r.length }]->(to_node) \
MERGE (c)<-[:LENGTH { length:r.length }]-(to_node) 
'''
node_relating = '''
MATCH (main_node:#Lable { meshcode:$main_meshcode }) \
MATCH (to_node) \
WHERE to_node.meshcode = $to_meshcode \
MERGE (main_node)-[:LENGTH { length:$length }]->(to_node) \
MERGE (main_node)<-[:LENGTH { length:$length }]-(to_node)
'''

get_charger_props = '''
MATCH (c: Charger) \
RETURN c.meshcode AS meshcode, \
        c.time AS time, \
        c.pd AS pd, \
        c.ppv as ppv \
ORDER BY time DESC
'''

collect_meshcode = 'MATCH (c:Charger) RETURN collect(DISTINCT c.meshcode)'

# get_charger_props = '''
# MATCH (c: Mesh4th) RETURN c.name AS name, c.dd as dd
# '''

# node_relating = '''
# MATCH (main_node:#Lable { meshcode:$main_meshcode }) \
# MATCH (to_node:#Lable { meshcode:$to_meshcode }) \
# MERGE (main_node)-[:LENGTH { length:$length }]->(to_node) \
# MERGE (main_node)<-[:LENGTH { length:$length }]-(to_node)
# '''
sample = '''
MATCH (c:Charger)
RETURN {meshcode:c.meshcode, data: [c {.time, .ppv, .pd}]} AS Data
ORDER BY c.time DESC
'''
charger_mesh = '''
MATCH (c:Charger)
RETURN COUNT(DISTINCT c.meshcode) AS len_mesh, collect(DISTINCT c.meshcode) as mesh_list
'''
