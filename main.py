from flask import Flask, make_response, request
import os
from crud import Crud
from routes_helper import RoutesHelper


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

@app.route('/api/google/login', methods=['POST'])
def login_google():
    req = request.json

    name = req.get('name')
    email = req.get('email')
    password = req.get('pw')

    if not (name and email and password):
        return make_response({'error':'Está em falta name ou email ou uid no body do request.'})

    users_table = Crud('user')
    users = users_table.getElements_and_operator(['email', 'pw'], [email, password])

    if(users):
        for user in users:
            if(user['email'] == email and user['pw'] == password):
                message = {"message": "Log in com sucesso.", 'user_id': user['id']}
                return make_response(message), 200
    
    user_table = Crud('user')
    cols, values = RoutesHelper.insert_element('user', req.items())
    user_holder = user_table.getElements_and_operator(cols, values)
    user_row = user_holder[0]
    user_id = user_row['id']
    return make_response({
                'message': 'Utilizador criado com sucesso.',
                'user_id': user_id
    }),201


@app.route('/api/user/<int:id_user>', methods=['GET'])
def get_user(id_user):

    user_handler = Crud('user')
    user = user_handler.get_element_by_pk(id_user, 'id')

    if user:
        return make_response(user)
    
    return make_response({'error':'Este utilizador não existe.'})

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

@app.route('/api/videos/view/<id_video>', methods=['POST'])
def increment_view(id_video):
    video_handler = Crud('video')
    
    video_details = video_handler.get_element_by_pk(id_video,'id')
    if video_details:
        video_handler.update_element(id_video,['views'], [video_details['views'] + 1],  'id')
        new_video_details = video_handler.get_element_by_pk(id_video,'id')
        return make_response(new_video_details)
    
    return make_response({'error':'Este video não existe.'})


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

    for row in comments_video:
        user = user_handler.get_element_by_pk(row['id_user'], 'id')
        row.update({'name':user['name']})

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
    
    video_handler = Crud('video')
    video_in_db = video_handler.get_element_by_pk(id_video, 'id')

    user_list_handler = Crud('user_list')
    user_list_in_db = user_list_handler.get_element_by_pk(id_user_list, 'id')

    if not video_in_db:
        return make_response({'error': 'Este video não existe.'})
    
    if not user_list_in_db:
        return make_response({'error': 'Esta playlist não existe.'})

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

@app.route('/api/playlists/<int:id_user>', methods=['GET'])
def get_playlist(id_user):

    playlist_handler = Crud('user_list')
    playlists = playlist_handler.get_elements_by_string_field('id_user', id_user)
    
    if playlists:
        return make_response(playlists)
    
    return make_response({'message': 'Este utilizador não tem playlists.'})


@app.route('/api/playlists/videos/<int:id_playlist>', methods=['GET'])
def get_videos_from_playlist(id_playlist):

    playlist_handler = Crud('video_list')
    videos = playlist_handler.get_elements_by_string_field('id_user_list', id_playlist)
    
    if videos:
        return make_response(videos)
    
    return make_response({'message': 'Esta playlist não existe ou está vazia.'})
    
@app.route('/api/videos/top/<int:n_top>', methods=['GET'])
def get_top_vieos(n_top):
    handler = Crud('video')
    result = handler.get_top(n_top, 'views')
    
    if result:
        return make_response(result)
    
    return make_response({'error':'Ups alguma coisa correu mal.'})

@app.route('/api/videos/youtube/<id_platform>', methods=['GET'])
def get_video_id_from_id_platform(id_platform):
    handler = Crud('video')
    y_video = handler.get_element_by_pk('id_platform', id_platform)

    if y_video:
        return make_response(y_video)
    
    handler.insert(['id_platform', 'platform', 'views'], [id_platform, 'youtube', 0])
    y_video = handler.get_element_by_pk('id_platform', id_platform)
    
    if y_video:
        return make_response(y_video)
    
    return make_response({'error':'Ups algo correu mal.'})


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
