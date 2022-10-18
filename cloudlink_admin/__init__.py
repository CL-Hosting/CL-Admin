from sanic import Request, Websocket
from sanic import Sanic
from sanic_ext import openapi
from sanic.response import json, empty

import time

class admin:
    def __init__(self, cloudlink):
        self.app = Sanic("Cloudlink_Admin")
        self.app.ctx.cloudlink = cloudlink
        

        
        self.app.ctx.db = self.app.ctx.cloudlink.suit.db #support Cl suit
        import bson
        self.bson = bson 

        self.app.add_websocket_route(self.cloudlink, "/") #pass through API
        self.db = self.app.get("/db/<db>/<table>")(self.db_get) #non systatic shuger for @app.get()


    async def cloudlink(self, req:Request, websocket:Websocket):
        self.app.ctx.cloudlink.__handler__(websocket)

    
    def IsAuthed(self, req, min_level=3):
        db = self.app.ctx.db
        usr = db.users.find_one({
            "session":{
                "token": req.token
            }
        })
        if usr is None:
            return False
        
        if time.time - usr['session']['timeout'] < 2400:
            db.users.update_one(
                {
                 "session":{
                     "token":req.token
                 }
                },
                {
                    "$set":{
                        "session":{
                            "token":None,
                            "refresh_token":None,
                            "timeout":0
                        }
                    }
                }
            )    
            return False
        
        if usr.get("level", 0) >= min_level:
            return True
        return False

    @openapi.summary("Gets items from the db")
    @openapi.description("gets all of the items from th db with a specified query")
    async def db_get(self, req:Request, db_name, table_name):
        if not self.IsAuthed(req):
            return 401

        try:
            table_obj = getattr(getattr(self.app.ctx.db, db_name), table_name)
            if 'one' in req.args:
                if not 'query' in req.args:
                    return 400
            
            
                items = table_obj.find_one(req.args.get('query'))
                if items is None:
                    return empty()

                return json(items, dumps=self.bson.dumps) #type: ignore
            
    

            if 'query' in req.args:
                items = table_obj.find_many(req.args.get('query'))
                if items is None:
                    return empty()
                return json(items, dumps=self.bson.dumps) #type: ignore
        
            items = table_name.find_many({})
            if items is None:
                return empty()
            return json(items, dumps=self.bson.dumps) #type: ignore
        except AttributeError:
            return 404

        except:
            return empty()

    async def db_post(self, req:Request, db_name, table_name):
        if not self.IsAuthed(req):
            return 401

        try:
            data = req.json
            db = getattr(getattr(self.app.ctx.db, db_name), table_name)
            db.insert_one(data)
            return 200
        except AttributeError:
            return 404

        except:
            #bad request
            return 400
        
    async def db_put(self, req:Request, db_name, table_name):
        if not self.IsAuthed(req):
            return 401
        
        
        
        try:
            data= req.json
            query = data.get('query')
            edited = data.get('edited')
            
            db = getattr(getattr(self.app.ctx.db, db_name), table_name)
            db.update_one(query, edited)
            return 200
        except AttributeError:
            return 404
        except:
            return 400
