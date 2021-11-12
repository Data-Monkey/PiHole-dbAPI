from fastapi import FastAPI, Body, Response, status
from fastapi.params import Path
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3
from sqlite3 import Error

import uvicorn

from os import environ

API_PORT = 8000

DATABASE = r"/etc/pihole/gravity.db"

# ===========================================
# == Define API Models
# ===========================================


class Group(BaseModel):
    name: str 
    description : Optional[str] = None
    enabled: int = Field(..., title="0:Disable, 1:Enable", ge=0, le=10)


# ===========================================
# == Helper Functions
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
    
def select_group(group_name: str):
    """select a GROUP record from the DB and retun a Group() dict"""

    query = "select name, enabled from 'group' where name = '"+group_name+"'"
    result = select_db(DATABASE, query)

    return result[0] 


# ======================================================
# API Endpoints 
# ======================================================

app = FastAPI()

# -------------------- /groups -----------------
@app.get("/groups", 
        status_code=status.HTTP_200_OK)
def get_groups():
    """return a list of dictionaries of all groups"""

    query = "select id, name, enabled from 'group'"
    return  select_db(DATABASE, query)


# -------------------- /group/group_name -----------------
@app.get("/group/{group_name}", 
         response_model=Group,
         status_code=status.HTTP_200_OK)
def get_group_by_name(group_name: str):
    """returns a json string of the group {group_name}"""
    return select_group(group_name)

@app.put("/group/{group_name}", 
        response_model=Group,
        status_code=status.HTTP_200_OK)
def set_group_enabled_by_payload (
        group_name: str ,
        enabled: int = Body(..., title="0:disable, 1:enable", ge=0, le=1)
        ):
    """
    enable or disable the group {group_name}
    on success returns updated group details

    valid values for payload : <br>
    0 : disabled
    1 : enabled 
    """       

    query = "update 'group' set 'enabled'="+str(enabled)+" where name='"+group_name+"'"
    result = update_db(DATABASE, query)
    if result == 0:
        # success! read the group back and return it
        return select_group(group_name)
    else: 
        #response.status_code = status.HTTP_400_BAD_REQUEST
        return "error: group_name not found, no update made"


# @app.put("/group/{group_name}/{enabled}", status_code=status.HTTP_200_OK)
# def set_group_enabled(*,
#         group_name: str = Path(..., title="the name of the group to set"), 
#         enabled: int = Path(..., title="0:disable, 1:enable", ge=0, le=1),
#         response: Response):
#     """
#     enable od disable the group <group_name>
#     returns updated group details

#     valid values for enabled:
#     0 = disabled
#     1 = enabled 
#     """

#     query = "update 'group' set 'enabled'="+str(enabled)+" where name='"+group_name+"'"
#     result = update_db(database, query)
#     if result == 0:
#         query = "select id, name, enabled from 'group' where name = '"+group_name+"'"
#         return select_db(database, query)
#     else: 
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return "error: group_name not found, no update made"


if __name__ == '__main__':
    uvicorn.run(app, port=API_PORT, host="0.0.0.0")