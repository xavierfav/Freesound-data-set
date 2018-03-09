import freesound, sys, os

import json
from pprint import pprint

client = freesound.FreesoundClient()
client.set_token("eaa4f46407adf86c35c5d5796fd6ea8b05515dca", "token")

# given a sound id which pack we want to omit, retrieve pack_id
# class: Shatter, pack: Stomach
# sound_id_target = 177365

# class: Shatter, pack: Human Chipmunk
sound_id_target = 168135

sound = client.get_sound(sound_id_target)

pack_id = int(sound.pack.split('/')[-2])
print pack_id, sound.pack_name

# retrieve the list of sound ids in the pack
pack = client.get_pack(pack_id)
pack_sounds = pack.get_sounds(fields="id,name,username", page_size=150)

list_ids_pack_sounds = [sound.id for sound in pack_sounds]
list_ids_pack_sounds.sort()
print 'all the %d sounds in the pack: %s, of user %s' % (len(list_ids_pack_sounds), pack.name, pack.username)
# print list_ids_pack_sounds

# confirm
for idx, sound in enumerate(pack_sounds):
    print (idx+1), sound.id, sound.name

a=9