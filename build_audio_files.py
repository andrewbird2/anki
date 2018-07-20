#!/usr/bin/env python

import random
import sys

sys.path.append('/usr/share/anki')
from anki import Collection
from pydub import AudioSegment
from google_play import clear_playlist, upload_to_playlist

collection_path = "/mnt/hgfs/C/Users/andrew.bird/AppData/Roaming/Anki2/Andrew/collection.anki2"
media_path = "/mnt/hgfs/C/Users/andrew.bird/AppData/Roaming/Anki2/Andrew/collection.media/"


def build_deck_audio(name, keep_only_two_sided=False, loops=1):
    print('Processing %s' % name)
    col = Collection(collection_path)

    deck_id = col.decks.id(name)

    note_ids = col.db.list("select distinct nid from cards where did = %s" % deck_id)
    random.shuffle(note_ids)

    pause_short = AudioSegment.silent(duration=1000)
    pause_3s = AudioSegment.silent(duration=2700)

    cumulative = AudioSegment.silent(duration=2000)

    failed_cards = 0

    for i, note_id in enumerate(note_ids):
        note = col.getNote(note_id)

        should_add = False
        for card in note.cards():
            if card.queue != -1:
                should_add = True

        if should_add:
            try:
                items = dict(note.items())
                prompt = items['audio_prompt']
                answer = items['audio_answer']
                if '[sound:' in prompt:
                    prompt_clean = prompt[prompt.find("[sound:") + 7:prompt.find("]")]
                    prompt_audio = AudioSegment.from_mp3('%s%s' % (media_path, prompt_clean))
                if '[sound:' in answer:
                    answer_clean = answer[answer.find("[sound:") + 7:answer.find("]")]
                    answer_audio = AudioSegment.from_mp3('%s%s' % (media_path, answer_clean))
                if '[sound:' in prompt and '[sound:' in answer:
                    cumulative += (prompt_audio + pause_short + answer_audio)
                elif answer and not keep_only_two_sided:
                    cumulative += answer_audio
                elif prompt and not keep_only_two_sided:
                    cumulative += prompt_audio
                if answer or prompt:
                    cumulative += pause_3s
            except Exception as e:
                print(e)
                failed_cards += 1

    final = cumulative
    for i in range(loops - 1):
        final += cumulative

    final.export('/home/andrew/anki/tmp/%s.mp3' % name, format="mp3")
    print('Uploading %s to google' % name)
    upload_to_playlist('/home/andrew/anki/tmp/%s.mp3' % name)
    col.close()
    print('Sucessfully compiled audio for %s.  There were %s failures.' % (name, failed_cards))


clear_playlist()
build_deck_audio('Czech', keep_only_two_sided=True, loops=5)
build_deck_audio('Spanish', keep_only_two_sided=True, loops=2)
build_deck_audio('German', keep_only_two_sided=True, loops=1)
