from gmusicapi import Mobileclient, Musicmanager
from secret import username, password
mm = Musicmanager()
mm.login()

mobile_client = Mobileclient()
mobile_client.login(username, password, Mobileclient.FROM_MAC_ADDRESS)

language_playlist_id = '55434cdf-49ed-47d7-a598-50e846b04489'

def clear_playlist():
    contents = mobile_client.get_all_user_playlist_contents()
    for content in contents:
        if content['id'] == language_playlist_id:
            for track in content['tracks']:
                mobile_client.remove_entries_from_playlist(track['id'])

def upload_to_playlist(file):
    response = mm.upload([file])
    song_id = response[0][file]
    mobile_client.add_songs_to_playlist(language_playlist_id, [song_id])
