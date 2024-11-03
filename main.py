from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import oracledb
import os
import json

app = FastAPI()

# Configuração da conexão com o Oracle no modo Thin

connection = oracledb.connect(
    user=os.getenv("DBUSER"),
    password=os.getenv('DBPASS'),
    dsn=os.getenv('DBDSN')
)

# Modelos de dados
class Game(BaseModel):
    nome: str
    genero: str
    plataforma: str
    status: str

# Rota para consultar todos os usuarios
@app.get("/list-games/")
async def list_games():
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, nome, genero, plataforma, status FROM games"
            )
            rows = cursor.fetchall()
            
            game_list = [
                {
                    'id': row[0], 
                    'nome': row[1], 
                    'genero': row[2], 
                    'plataforma': row[3], 
                    'status': row[4]
                }
                for row in rows
            ]
            
            # Convertendo a lista de dicionários para JSON
            games = json.dumps(game_list, indent=4, ensure_ascii=False)

            return Response(content=games, media_type='application/json')
    except oracledb.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rota para adicionar novo jogo
@app.post("/create-game/")
async def create_game(game: Game):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO games (nome, genero, plataforma, status)
                VALUES (:1, :2, :3, :4)
                """,
                (game.nome, game.genero, game.plataforma, game.status)
            )
        connection.commit()

        return {"message": "Jogo adicionado com sucesso"}
    except oracledb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
# Rota para atualizar jogo
@app.post("/update-game/{game_id}")
async def update_game(game_id: int, game: Game):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE games
                SET nome = :1, genero = :2, plataforma = :3, status = :4
                WHERE id = :5
                """,
                (game.nome, game.genero, game.plataforma, game.status, game_id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
        connection.commit()
        return {"message": "Jogo atualizado com sucesso"}
    except oracledb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
# Rota para deletar jogo
# @app.post("/delete-game/{game_id}")
# async def delete_game(game_id: int):
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 """
#                 DELETE FROM games
#                 WHERE id = :1
#                 """,
#                 (game_id)
#             )
#             if cursor.rowcount == 0:
#                 raise HTTPException(status_code=404, detail="Jogo não encontrado")
#         connection.commit()
#         return {"message": "Jogo deletado com sucesso"}
#     except oracledb.Error as e:
#         connection.rollback()
#         raise HTTPException(status_code=500, detail=str(e))