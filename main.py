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

avalible_games = {}

async def generate_update_msg(packaged_game:list) -> dict:
    print(f"recived: {packaged_game=}",)
    board, pos, color_to_move, move_power = packaged_game
    return {
        "type":"update",
        "b10_board":board,
        "lbp":pos,
        "to_move":color_to_move,
        "move_power":move_power,
    }

async def execute_move(packaged_game:list,event:dict,user:str)-> bool | list:
    move = event["move"]
  
    succes, move_ary = game_utils.from_algebric(move)

    if not succes:
        return succes,"Wrong algebric move notation"

    b10_board, lbp, player_color, move_power = packaged_game
    
    print("!"*10)
    print(functions.boardify(lbp)[move_ary[1]][move_ary[0]])
    print(user)
    if not (functions.boardify(lbp)[move_ary[1]][move_ary[0]] == user):
        return False, "No permission for moving this piece"
    
    color_legal_cost = functions.cost_of_moves(lbp, b10_board, player_color)
    print(lbp, b10_board, player_color)
    cost = functions.extract(color_legal_cost, move_ary)
    print(cost)

    print(games)

    if cost == -1:
        return False,"Invalid move"
    
    if cost > move_power:
        return False,"Move unavailable (Move costs more than you have avalible)."

    lbp = functions.push_move(lbp, move_ary)
    move_power = move_power - cost
    if move_power == 0:
        print("swaping users ")
        player_color = game_utils.swap_players(player_color)
        move_power = 3

        
    print("played", game_utils.from_arry_notation(move_ary), cost, move_power)
    
    packaged_game = b10_board,lbp,player_color,move_power
    print(f"move completed good, this is {packaged_game=}",)
    
    return True,packaged_game

async def error(websocket,message):
    event = {
        "type":"error",
        "message":message
    }
    await websocket.send(json.dumps(event))

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

async def play(websocket,join_key,player,connected):
    async for message in websocket:
        print(join_key) 
        game_obj = games[join_key]
        packaged_game = game_obj["game"]
        
        event = json.loads(message)
        
        if (event["type"] != "play"):
            print(f"something is wrong, servers wanted to recive play package, but it got {event}")
            return
        print(">",event)
        
        user = None
        if event["ident"] == packaged_game["white_ident"]:
            user = "w"
        elif event["ident"] == packaged_game["black_ident"]:
            user = "b" 
        print("based on ident the user is",user)
        
        if user is None:
            await error(websocket,"No permission for moving this piece")
            continue
        
        
        legal,pp = await execute_move(packaged_game,event,user)
        
        if not legal:
            await error(websocket,pp)
            continue
        
        packaged_game = pp


        
        event = await generate_update_msg(packaged_game)
        
        broadcast(connected,json.dumps(event))
        
        game_over, winner =  await game_utils.game_over(packaged_game)
        
        if (game_over):
            event = {
                "type":"win",
                "player":winner,
            }
        
            await broadcast(connected,json.dumps(event))
            


async def start_game(websocket):
    #? create new game


    connected = {websocket}

    b10_board = game_utils.new_b10_board()
    game_id = game_utils.new_game_id()
    packaged_game = b10_board, START_POS, START_COLOR, START_MOVE_POWER

    white_ident = game_utils.new_uuid()
    black_ident = game_utils.new_uuid()
    
    games[game_id] = {
        "game":packaged_game,
        "connected":connected,
        "white_ident":white_ident,
        "black_ident":black_ident,
    }
    
    try:
        print(f"Starting game with id {game_id}, and sending to p1")
        event  = {
            "type":"init",
            "key":game_id,
        }
        await websocket.send(json.dumps(event))
        
        event = {
            "type":"ident",
            "ident":white_ident,
        }
        await websocket.send(json.dumps(event))
         
        await play(websocket,games[game_id],1,connected)

    finally:
        print(f"game with id: {game_id} ended")
        del games[game_id]
   

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
        game_object = games[join_key]
    except KeyError:
        await error(websocket,"game not found")
        print("game with id",join_key,"not found")
        return
    
    
    black_ident = game_object["black_ident"] 
    game_object["connected"].add(websocket)
    try:
    
        event = {
            "type":"ident",
            "ident":black_ident,
        }
        await websocket.send(json.dumps(event))
         
        await replay(game_object["connected"],game_object["game"])
    
        await play(websocket,join_key,2,game_object["connected"])
    
    finally:
        game_object["connected"].remove(websocket)
        
        
    


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

