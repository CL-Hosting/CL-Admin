from cloudlink.server import Server
from sanic import Blueprint, Request
from sanic.response import json

from .auth import protected

_SANIC = Blueprint(url_prefix="admin/api/", v=1)


class Admin_API:
  def __init__(self, cloudlink:Server):
    self.cl = cloudlink
    self.db = cloudlink.db
    _SANIC.ctx.db = self.db

  @_SANIC.get("actions/")
  @protected
  async def last_actions(self, req):
    actions = self.db.actions.find_many({}).limit(10)
    return json(actions)
    
  
  @_SANIC.get("db/<collection>")
  @protected
  async def get_collection(self, req:Request, collection):
    """gets a collection from the database

    gets the requested collection from the database


    :auth:
      level 3 admin
    
    
    :param collection:
      the name of the collection to get

    :optinal query one:
      :param query:
        the query to filter the collection
      
      only gets the first element for a query

    :optinal query:
      the query to filter the collection

    
    
    :return:
      - list:
        - item:
      - item
        
    :Error:
      - json:
        - error
          - type
          - status
        
    """
    try:
      if 'one' in req.args:
        if not 'query' in req.args:
          #bad request
          return json({"type":"KeyError","error": "no query given", "status":400}, status=400)
        return json(getattr(self.db, collection).find_one(req.args['query']))

      if 'query' in req.args:
        return json(getattr(self.db, collection).find_many(req.args['query']))

      return json(getattr(self.db, collection).find_many({}))

    except KeyError as e:
      return json({"type":"KeyError","error": e, "status":400}, status=400)
    
    except Exception as e:
      return json({"type": str(e.__class__.__name__), "error":str(e), "status":500}, status=500)

  @_SANIC.post("db/<collection>")
  @protected
  async def post_collection(self, req:Request, collection):
    """creates a new item in the database

    adds the data specified to the collection specified

    :auth:
      level: 3 (admin)

    :param collection:
      the name of the collection to add the item to

    :query optinal one:
        :param query:
          the query to filter the collection
        sets only the first element for a query

    :query optinal query:
      the query to filter the collection

    
    :body JSON:
      - data: JSON

    :return:
      - 200
      :error:
        - json:
          - error
          - type
          - status
    """
    try:
      if 'one' in req.args:
        if not 'data' in req.json:
          #bad request
          return json({"type":"KeyError","error": "no data given", "status":400}, status=400)
        getattr(self.db, collection).insert_one(req.json['data'])
        return 200

      if not 'data' in req.json:
        #bad request
        return json({"type":"KeyError","error": "no data given", "status":400}, status=400)
      
      getattr(self.db, collection).insert_many(req.json['data'])
      return 200
      
    except KeyError as e:
      return json({"type":"KeyError","error": e, "status":400}, status=400)
    except Exception as e:
      return json({"type": str(e.__class__.__name__), "error":str(e), "status":500}, status=500)

  @_SANIC.put("/db/<collection>")
  @protected
  async def put_collection(self, req:Request, collection):
    """updates an item in the database
      updates the item specified in the collection specified

    :auth:
        level: 3 (admin)
    
    :param collection:
      the name of the collection to update the item in

    :query optinal one:
      :param query:
        the query to filter the collection
      sets only the first element for a query
    
    :query optinal query:
        the query to filter the collection

    :body JSON:
      - data: JSON
      :error:
      - json:
        - error
        - type
        - status
    
    """""  
    
    try:
      if not 'data' in req.json:
          #bad request
          return json({"type":"KeyError","error": "no data given", "status":400}, status=400)
   
      if 'one' in req.args:
        if not 'query' in req.args:
          #bad request
          return json({"type":"KeyError","error": "no query given", "status":400}, status=400)

        getattr(self.db, collection).update_one(req.args['query'], req.json['data'])
        return 200

      if not 'query' in req.args:
        getattr(self.db, collection).update_many({},req.json['data'])
      
      getattr(self.db, collection).update_many(req.args['query'], req.json['data'])

    except KeyError as e:
      return json({"type":"KeyError","error": e, "status":400}, status=400)
    except Exception as e:
      return json({"type": str(e.__class__.__name__), "error":str(e), "status":500}, status=500)

  