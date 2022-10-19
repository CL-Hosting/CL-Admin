from __future__ import annotations

from cloudlink.server import server as Server
from cloudlink.server.suit import SuitDB  # type: ignore
from sanic import Blueprint, Request
from sanic.response import json, HTTPResponse, empty

from .auth import protected

admin = Blueprint(url_prefix="admin/api/", version=1)


class Admin_API:
    def __init__(self, cloudlink: Server):
        self.cl = cloudlink
        self.db: SuitDB = cloudlink.db  # type: ignore
        admin.ctx.db = self.db

    @admin.get("actions/")
    @protected
    async def last_actions(self, req: Request) -> HTTPResponse:  # type: ignore
        actions: list = self.db.actions.find_many({}).limit(10)
        return json(actions)

    @admin.get("db/<collection>")
    @protected
    async def get_collection(self, req: Request, collection: str) -> HTTPResponse:
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
            if "one" in req.args:
                if not "query" in req.args:
                    # bad request
                    return json(
                        {"type": "KeyError", "error": "no query given", "status": 400},
                        status=400,
                    )
                return json(getattr(self.db, collection).find_one(req.args["query"]))

            if "query" in req.args:
                return json(getattr(self.db, collection).find_many(req.args["query"]))

            return json(getattr(self.db, collection).find_many({}))

        except KeyError as e:
            return json({"type": "KeyError", "error": e, "status": 400}, status=400)

        except Exception as e:
            return json(
                {"type": str(e.__class__.__name__), "error": str(e), "status": 500},
                status=500,
            )

    @admin.post("db/<collection>")
    @protected
    async def post_collection(self, req: Request, collection: str) -> HTTPResponse:
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
            if "one" in req.args:
                if not "data" in req.json:
                    # bad request
                    return json(
                        {"type": "KeyError", "error": "no data given", "status": 400},
                        status=400,
                    )
                getattr(self.db, collection).insert_one(req.json["data"])
                return empty(status=200)

            if not "data" in req.json:
                # bad request
                return json(
                    {"type": "KeyError", "error": "no data given", "status": 400},
                    status=400,
                )

            getattr(self.db, collection).insert_many(req.json["data"])
            return empty(status=200)

        except KeyError as e:
            return json({"type": "KeyError", "error": e, "status": 400}, status=400)
        except Exception as e:
            return json(
                {"type": str(e.__class__.__name__), "error": str(e), "status": 500},
                status=500,
            )

    @admin.put("/db/<collection>")
    @protected
    async def put_collection(self, req: Request, collection: str) -> HTTPResponse:
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
    
    """ ""

        try:
            if not "data" in req.json:
                # bad request
                return json(
                    {"type": "KeyError", "error": "no data given", "status": 400},
                    status=400,
                )

            if "one" in req.args:
                if not "query" in req.args:
                    # bad request
                    return json(
                        {"type": "KeyError", "error": "no query given", "status": 400},
                        status=400,
                    )

                getattr(self.db, collection).update_one(
                    req.args["query"], req.json["data"]
                )
                return empty(status=200)

            if not "query" in req.args:
                getattr(self.db, collection).update_many({}, req.json["data"])
                return empty(status=200)

            getattr(self.db, collection).update_many(
                req.args["query"], req.json["data"]
            )
            return empty(status=200)

        except KeyError as e:
            return json({"type": "KeyError", "error": e, "status": 400}, status=400)
        except Exception as e:
            return json(
                {"type": str(e.__class__.__name__), "error": str(e), "status": 500},
                status=500,
            )

    @admin.delete("/db/<collection>")
    @protected(3)
    async def db_delete(self, req: Request, collection: str) -> HTTPResponse:
        """deletes an item from the database

    :auth:
      level: 3 (admin)

    :param collection:
      the name of the collection to delete the item from

    :query optinal one:
      :param query:
        the query to filter the collection
      sets only the first element for a query
    
    :query optinal query:
        the query to filter the collection

    :return JSON:
      :error:
      - json:
        - error
        - type
        - status
    
    """ ""
        try:
            if "one" in req.args:
                if not "query" in req.args:
                    # bad request
                    return json(
                        {"type": "KeyError", "error": "no query given", "status": 400},
                        status=400,
                    )
                getattr(self.db, collection).delete_one(req.args["query"])
                return empty(status=200)

            if not "query" in req.args:
                getattr(self.db, collection).drop()
                return empty(status=200)

            getattr(self.db, collection).delete_many(req.args["query"])
            return empty(status=200)

        except KeyError as e:
            return json({"type": "KeyError", "error": e, "status": 400}, status=400)
        except Exception as e:
            return json(
                {"type": str(e.__class__.__name__), "error": str(e), "status": 500},
                status=500,
            )
