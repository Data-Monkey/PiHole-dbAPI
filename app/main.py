from fastapi import FastAPI, Response, status
from fastapi.params import Path

import sqlite3
from sqlite3 import Error

import uvicorn

from os import environ


database = r"/etc/pihole/gravity.db"


# ===========================================



def select_db(path_to_db, select_query):
      """Returns data from an SQL query as a list of dicts."""
      try:
          con = sqlite3.connect(path_to_db)
          con.row_factory = sqlite3.Row
          things = con.execute(select_query).fetchall()
          unpacked = [{k: item[k] for k in item.keys()} for item in things]
          return unpacked
      except Exception as e:
          print(f"Failed to execute. Query: {select_query}\n with error:\n{e}")
          return []
      finally:
          con.close()


def update_db(path_to_db, update_query):
    print(update_query)
    ret = 9
    try:
        con = sqlite3.connect(path_to_db)
        cur = con.cursor()
        res=cur.execute(update_query)
        con.commit()
    except Exception as e:
        print(f"Failed to execute. Query: {update_query}\n with error:\n{e}")
        return []
    finally:
        con.close()    
    
    if res.rowcount > 0 :
        return  0
    else:
        return 1 # no records updated        
    

# ======================================================
# API Endpoints 
# ======================================================

app = FastAPI()

@app.get("/groups", status_code=status.HTTP_200_OK)
def get_groups():
    """return a list of dictionaries of all groups"""

    query = "select id, name, enabled from 'group'"
    return  select_db(database, query)



@app.get("/group/{group_name}", status_code=status.HTTP_200_OK)
def get_group_by_name(group_name: str):
    """return a dictionaries of the group <group_name>"""
    query = "select id, name, enabled from 'group' where name = '"+group_name+"'"
    return select_db(database, query)


@app.put("/group/{group_name}/{enabled}", status_code=status.HTTP_200_OK)
def set_group_enabled(*,
        group_name: str = Path(..., title="the name of the group to set"), 
        enabled: int = Path(..., title="0:disable, 1:enable", ge=0, le=1),
        response: Response):
    """
    enable od disable the group <group_name>
    returns updated group details

    valid values for enabled:
    0 = disabled
    1 = enabled 
    """

    query = "update 'group' set 'enabled'="+str(enabled)+" where name='"+group_name+"'"
    result = update_db(database, query)
    if result == 0:
        query = "select id, name, enabled from 'group' where name = '"+group_name+"'"
        return select_db(database, query)
    else: 
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "error: group_name not found, no update made"


if __name__ == '__main__':
    uvicorn.run(app, port=8000, host="0.0.0.0")