import requests
import json
import urllib.request
import random
from fastapi import FastAPI

import functions
import game_utils


import asyncio
from websockets.asyncio.server import serve

import logging 


'''origins = ["*"]
# https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''


BASE_URL = "https://less.palcka.si"
START_POS = "bb4/bb4/6/6/4ww/4ww"
# START_POS = "ww4/w0w3/6/6/4bb/bb4"

START_COLOR = "w"
START_MOVE_POWER = 3

player_color = "w"

global games
games = {}

async def start_game(websocket,msg):
    #? create new game
    """
    {
        "type": "create,
        // "ident":uuid 
    }
    """
    #! white_key = game_utils.new_uuid()
    #! black_key = game_utils.new_uuid()

    white_key = "woite"
    black_key = "bluck"

    b10_board = game_utils.new_b10_board()
    game_id = game_utils.new_game_id()

    games.update(
        {
            game_id: {
                "game": [b10_board, START_POS, START_COLOR, START_MOVE_POWER],
                "white_key": white_key,
                "black_key": black_key,
            }
        }
    )

    print(games)

    """
    for i, v in functions.get_wall_moves(b10_board):
        print(game_utils.from_arry_notation(i), v)
    print("a")

    for i, v in functions.cost_of_moves(START_POS, b10_board, player_color):
        print(game_utils.from_arry_notation(i), v)
    """
    
    await websocket.send(json.dumps(
    {
        "error":False,
        "game_id": game_id,
        "game_end": False,
        "game":[b10_board,START_POS,START_COLOR,START_MOVE_POWER],
         
        "you": "w",
        "ident": white_key,
    }))
    
    
      

async def join_game(websocket,msg):

    game_id = str(game_id)
    if not game_id in games.keys():
        return {"s": False, "game_end": False, "code": "game_id is not found"}

    game_obj = games[game_id]["game"]
    black_key = games[game_id]["black_key"]

    await websocket.send(json.dumps(
        {
        "error":False,
        "game_id": game_id,
        "game_end": False,  # todo this shuld be fiixed
        "game": game_obj,
    
        "your": "b",
        "ident": black_key,
    }    ))


async def handler(websocket):
    async for message in websocket:
        logging.log("Recived:",message)
        
        try:
            msg_obj = json.loads(message)
        except AttributeError: # not a valid json
            logging.error("Recived not a json obj",message)
            return 0
        
        if msg_obj.get("type", None) is None:
            websocket.send(json.dumps({"error":True,"message":"Type of message not specified."}))
            logging.error()
            return
        
        if msg_obj["type"] == "create":
            await start_game(websocket,msg_obj)
        
        elif msg_obj["type"] == "join":
            await join_game(websocket,msg_obj)
            
            
"""            
    


@app.get("/game")
async def game(game_id=None):

    game_id = str(game_id)
    if not game_id in games.keys():
        return {"s": False, "game_end": False, "code": "game_id is not found"}

    game_obj = games[game_id]["game"]
    b10_board, lbp, player_color, move_power = game_obj

    return {
        "s": True,
        "game_id": game_id,
        "game_end": False,
        "board": b10_board,
        "lbp": lbp,
        "move_power": move_power,
        "player_color": player_color,
    }


@app.get("/make_move")
async def make_move(move=None, game_id=None, ident=None):
    if ident is None:
        return {
            "s": False,
            "game_end": False,
            "code": "Identification not suplied",
        }

    if game_id is None:
        return {"s": False, "game_end": False, "code": "game_id is not present"}

    game_id = str(game_id)
    if not game_id in games.keys():
        return {"s": False, "game_end": False, "code": "game_id is not found"}

    if move is None:
        return {"s": False, "game_end": False, "code": "move is not present"}

    succes, move_ary = game_utils.from_coord_notation(move)

    if not succes:
        return {
            "s": False,
            "game_end": False,
            "code": move_ary,
        }

    print("gameeesss", games)

    game_obj = games[game_id]["game"]

    print("req game obj:", game_obj)
    # games.update({game_id:[b10_board,START_POS,START_COLOR,START_MOVE_POWER]})

    b10_board, lbp, player_color, move_power = game_obj

    if player_color == "w":
        corr_key = games[game_id]["white_key"]
    else:
        corr_key = games[game_id]["black_key"]

    if not (ident == corr_key):
        return {
            "s": False,
            "game_end": False,
            "code": "It is not your turn",
        }

    color_legal_cost = functions.cost_of_moves(lbp, b10_board, player_color)
    print(lbp, b10_board, player_color)
    cost = functions.exatct(color_legal_cost, move_ary)
    print(cost)

    print(games)

    if cost == 0:
        return {"s": False, "game_end": False, "code": "Invalid move"}

    games[game_id]["game"] = [b10_board, lbp, player_color, move_power]

    if cost > move_power:
        return {
            "s": False,
            "game_end": False,
            "code": "Move costs more than you hava avalibble",
        }

    lbp = functions.push_move(lbp, move_ary)
    move_power = move_power - cost
    if move_power == 0:
        player_color = game_utils.swap_players(player_color)
        move_power = 3

    print("played", game_utils.from_arry_notation(move_ary), cost, move_power)
    checkForWin, color = game_utils.is_win(lbp)
    games[game_id]["game"] = [b10_board, lbp, player_color, move_power]

    if checkForWin:
        games[game_id]["game"] = [b10_board, lbp, player_color, move_power]
        if color == 1:
            return {
                "s": True,
                "game_end": True,
                "win": 1,
                "lbp": lbp,
                "board": b10_board,
            }
        elif color == -1:
            return {
                "s": True,
                "game_end": True,
                "win": -1,
                "lbp": lbp,
                "board": b10_board,
            }
        else:
            raise ValueError("Not 1 nor -1 ??")

    if move_power == 0:
        player_color = game_utils.swap_players(player_color)
        move_power = 3

    print("for nxt")
    for i, v in functions.cost_of_moves(lbp, b10_board, player_color):
        print(game_utils.from_arry_notation(i), v)

    print(games)

    return {
        "s": True,
        "game_end": False,
        "b10_board": b10_board,
        "lbp": lbp,
        "move_power": move_power,
        "to_move": player_color,
    }
"""
async def main():
    async with serve(handler, "localhost", 8001) as server:
        print(1)
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

