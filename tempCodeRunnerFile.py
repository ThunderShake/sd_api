@app.route('/api/playlists/videos/<int:id_playlist>')
def add_video_to_playlist(id_playlist):

    playlist_handler = Crud('video_list')
    videos = playlist_handler.get_elements_by_string_field('id_user_list', id_playlist)
    
    if videos:
        return make_response(videos)
    
    return make_response({'message': 'Esta playlist não tem videos.'})