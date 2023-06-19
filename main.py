from flask import Flask, make_response, request
import os
from crud import Crud
from routes_helper import RoutesHelper
import json

app = Flask(__name__)


@app.route('/api/register', methods=['POST'])
def register():
    user_table = Crud('user')
    users = user_table.get_all_elements()
    json = request.json
    user_in_bd = False

    if all(key in json.keys() for key in ['email', 'pw', 'name']):
        for user in users:
            if(user['email'] == json['email']):
                user_in_bd = True
        if(not user_in_bd):
            cols, values = RoutesHelper.insert_element('user', json.items())
            user_holder = user_table.getElements_and_operator(cols, values)
            user_row = user_holder[0]
            user_id = user_row['id']
            return make_response({
                'message': 'Utilizador criado com sucesso.',
                'user_id': user_id
            }),201
        else:
            return make_response({"error": "Já existe uma conta com este email."}), 409
    else:
        message = 'Missing required fields'
        return make_response({'error': message}), 400

@app.route('/api/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('pw')

    users_table = Crud('user')
    users = users_table.getElements_and_operator(['email', 'pw'], [email, password])
    if(users):
        for user in users:
            if(user['email'] == email and user['pw'] == password):
                message = {"message": "Log in com sucesso.", 'user_id': user['id']}
                return make_response(message), 200
    message = {'error': 'Email ou Password invalidos. '}
    return make_response(message), 401

@app.route('/api/videos/<string:id>', methods=['GET'])
def get_video_details(id):
    video_handler = Crud('video')
    video_details = video_handler.get_element_by_pk(id,'id')

    if video_details:
        likes_handler = Crud('likes_video')
        like_count = likes_handler.count('id_video', video_details['id'])  
        dislikes_handler = Crud('dislikes_video')
        dislikes_count = dislikes_handler.count('id_video', video_details['id'])
        video_details.update({'likes': like_count, 'dislikes': dislikes_count})
        return make_response(video_details), 200
    
    return make_response({'error':'Video nao encontrado.'}), 404

@app.route('/api/videos/like', methods=['POST'])
def add_like():

    id_user = request.json.get('id_user')
    id_video = request.json.get('id_video')
    
    likes_handler = Crud('likes_video')
    user_handler = Crud('user')
    video_handler = Crud('video')

    valid_user = user_handler.get_element_by_pk(id_user, 'id')
    valid_video = video_handler.get_element_by_pk(id_video, 'id')

    if not valid_user:
        return make_response({'message': f'O utilizador {id_user} não existe.'}), 400

    if not valid_video:
        return make_response({'message': f'O video {id_video} não existe.'}), 400

    row_likes = likes_handler.get_elements_by_string_field('id_video', id_video)
    
    if id_user in [bd_user_id['id_user'] for bd_user_id in row_likes]:
        return make_response({'message': f'O utilizador {id_user} já deu like neste vídeo.'}), 400
    else:
        likes_handler.insert(['id_user', 'id_video'], [id_user, id_video])
        return make_response({
            'id_user':id_user,
            'id_video':id_video,
            'message': f'O utilizador {id_user} deu like no vídeo de ID {id_video}.'
        }) 


@app.route('/api/videos/dislike', methods=['POST'])
def add_dislike():

    id_user = request.json.get('id_user')
    id_video = request.json.get('id_video')
    
    dislikes_handler = Crud('dislikes_video')
    user_handler = Crud('user')
    video_handler = Crud('video')

    valid_user = user_handler.get_element_by_pk(id_user, 'id')
    valid_video = video_handler.get_element_by_pk(id_video, 'id')

    if not valid_user:
        return make_response({'message': f'O utilizador {id_user} não existe.'}), 400

    if not valid_video:
        return make_response({'message': f'O video {id_video} não existe.'}), 400

    row_likes = dislikes_handler.get_elements_by_string_field('id_video', id_video)
    
    if id_user in [bd_user_id['id_user'] for bd_user_id in row_likes]:
        return make_response({'message': f'O utilizador {id_user} já deu dislike neste vídeo.'}), 400
    else:
        dislikes_handler.insert(['id_user', 'id_video'], [id_user, id_video])
        return make_response({
            'id_user':id_user,
            'id_video':id_video,
            'message': f'O utilizador {id_user} deu dislike no vídeo de ID {id_video}.'
        })    

@app.route('/api/videos/<int:id_video>/comments', methods=['GET'])
def get_comments(id_video):
    
    comments_handler = Crud('comments_video')
    comments_video = comments_handler.get_elements_by_string_field('id_video', id_video)
    user_handler = Crud('user')

    if id_video not in [row['id_video'] for row in comments_video]:
        return make_response({'message': f'O vídeo de ID {id_video} não possui comentários.'}), 404

    for x in comments_video:
        user = user_handler.get_element_by_pk(x['id_user'], 'id')
        x.update({'name':user['name']})

    return make_response(comments_video)

@app.route('/api/videos/<int:id_video>/comments', methods=['POST'])
def add_comment(id_video):
    
    id_user = request.json.get('id_user')
    comment_desc = request.json.get('comment')

    user_handler = Crud('user')
    video_handler = Crud('video')

    valid_user = user_handler.get_element_by_pk(id_user, 'id')
    valid_video = video_handler.get_element_by_pk(id_video, 'id')

    if not valid_user:
        return make_response({'message': f'O utilizador {id_user} não existe.'}), 400

    if not valid_video:
        return make_response({'message': f'O video {id_video} não existe.'}), 400
    
    comment_handler = Crud('comments_video')
    comment_handler.insert(['id_user', 'id_video', 'descr'], [id_user, id_video, comment_desc])
    
    return make_response({'message': 'Comentário adicionado com sucesso.'})

@app.route('/api/videos/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comments_handler = Crud('comments_video')
    comment = comments_handler.get_element_by_pk(comment_id, 'id')
    
    if comment:
        comments_handler.delete_element(comment_id, 'id')
        return make_response({'message': f'Comentário de ID {comment_id} foi excluído com sucesso.'}), 200
    
    return make_response({'message': f'O comentário de ID {comment_id} não foi encontrado.'}), 404
      
@app.route('/api/playlists', methods=['POST'])
def create_playlist():
    
    playlist_name = request.json.get('name')
    id_user = request.json.get('id_user')
    
    if playlist_name and id_user:
        user_list_handler = Crud('user_list')
        user_list_handler.insert(['id_user', 'name'],[id_user, playlist_name])
    else:
        return make_response({'message': 'O id do utilizador e o nome da playlist são obrigatórios.'}), 400


    return make_response({'message': 'Playlist criada com sucesso.'}), 201

@app.route('/api/playlists', methods=['DELETE'])
def delete_playlist():
    req = request.json
    list_id = req.get('id')
    if list_id:
        list_handler = Crud('user_list')
        video_handler = Crud('video_list')
        video_handler.delete_element(list_id, 'id_user_list')
        list_handler.delete_element(list_id, 'id')
        return make_response({'message':'Playlist removida com sucesso.'})
    else:
        return make_response({'error':'Id da playlist em falta.'}), 404

@app.route('/api/playlists/videos', methods=['POST'])
def add_video_to_playlist():
    
    req = request.json
    id_user_list = req.get('id_user_list')
    id_video = req.get('id_video')

    if id_video and id_user_list:
        cols = []
        values = []

        for col, value in req.items():
                cols.append(col)
                values.append(value)

        handler = Crud('video_list')
        in_db = handler.getElements_and_operator(cols, values)
        if not in_db:
            handler.insert(cols, values)
            return make_response({'message':'Video inserido à playlist com sucesso.'}), 200
        else:
            return make_response({'error':'Este video já existe na playlist.'}), 409
        
    else:
        return make_response({'error': 'Id da playlist ou id do utilizador em falta.'}), 404

@app.route('/api/playlists/videos', methods=['DELETE'])
def del_video_from_playlist():
    
    req = request.json
    id_user_list = req.get('id_user_list')
    id_video = req.get('id_video')

    if id_video and id_user_list:
        cols = []
        values = []

        for col, value in req.items():
                cols.append(col)
                values.append(value)

        handler = Crud('video_list')
        in_db = handler.getElements_and_operator(cols, values)
        if not in_db:
            return make_response({'message':'Este video não existe na playlist.'}), 200
        else:
            handler.delete_element(id_video, 'id')
            return make_response({'error':'O video foi removido com sucesso.'}), 409
        
    else:
        return make_response({'error': 'Id da playlist ou id do utilizador em falta.'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
