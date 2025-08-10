import requests
import json
import urllib.request
import random
from fastapi import FastAPI

import functions
import game_utils


import asyncio
from websockets.asyncio.server import serve,broadcast

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

async def generate_update_msg(packaged_game:list) -> dict:
    board, pos, color_to_move, move_power = packaged_game
    return {
        "type":"update",
        "b10_board":board,
        "lbp":pos,
        "to_move":color_to_move,
        "move_power":move_power,
    }



async def execute_move(move,game):
    return True,1

async def error(websocket,message):
    event = {
        "type":"error",
        "message":message
    }
    await websocket.send(json.dumps(event))

async def game_over(packaged_game):
    return False
 

async def replay(connected,packaged_game):
    print("sending starting data to both")
    board, pos, color_to_move, move_power = packaged_game
    event = {
        "type":"update",
        "b10_board":board,
        "lbp":pos,
        "to_move":color_to_move,
        "move_power":move_power,
    }
    
    broadcast(connected,json.dumps(event))

    

async def play(websocket,packaged_game,connected):
    async for message in websocket:
        event = json.loads(message)
        
        if (event["type"] != "play"):
            print(f"something is wrong, servers wanted to recive play package, but it got {event}")
        
        print(">",event)
        
        legal,resp = execute_move(packaged_game,event)
        
        if not legal:
            error(websocket,"move not legal")

        event = generate_update_msg(packaged_game)
        
        broadcast(connected,json.dumps(event))
        
        if (game_over(packaged_game)):
        
            event = {
                "type":"win",
                "player":1,}
        
            broadcast(connected,json.dumps(event))
            
        
        


async def start_game(websocket):
    #? create new game

    #! white_key = game_utils.new_uuid()
    #! black_key = game_utils.new_uuid()

    white_key = "woite"
    black_key = "bluck"

    connected = {websocket}

    b10_board = game_utils.new_b10_board()
    game_id = game_utils.new_game_id()
    packaged_game = b10_board, START_POS, START_COLOR, START_MOVE_POWER

    games[game_id] = packaged_game,connected
    
    try:
        event  = {
            "type":"init",
            "join":game_id,
        }
        
        await websocket.send(json.dumps(event))
        
        await play(websocket,packaged_game,1,connected)

    finally:
        print(f"game with id: {game_id} ended")
        del games[game_id]
    
    '''games.update(
        {
            game_id: {
                "game": [b10_board, START_POS, START_COLOR, START_MOVE_POWER],
                "white_key": white_key,
                "black_key": black_key,
            }
        }
    )'''

    print(f"{games=}")

    """
    for i, v in functions.get_wall_moves(b10_board):
        print(game_utils.from_arry_notation(i), v)
    print("a")

    for i, v in functions.cost_of_moves(START_POS, b10_board, player_color):
        print(game_utils.from_arry_notation(i), v)
    """
    
    '''await websocket.send(json.dumps(
    {
        "error":False,
        "game_id": game_id,
        "game_end": False,
        "game":[b10_board,START_POS,START_COLOR,START_MOVE_POWER],
         
        "you": "w",
        "ident": white_key,
    }))'''
    
    
      

async def join_game(websocket,join_key):
    try:
        packaged_game,connected = games[join_key]
    except KeyError:
        await error(websocket,"game not found")
        print("game with id",join_key,"not found")
        return
    
    connected.add(websocket)
    try:
        await replay(connected,packaged_game)
    
        await play(websocket,packaged_game,2,connected)
    
    finally:
        connected.remove(websocket)
        
        
    


async def handler(websocket):
    async for message in websocket:
        print(f"Recived: >{message}")
        
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
            await start_game(websocket)
        
        elif msg_obj["type"] == "join":
            await join_game(websocket,msg_obj["key"])
            
        else:
            print(f"recived {msg_obj['type']}, idk what it is")
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

