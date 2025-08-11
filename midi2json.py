import os
import json
from mido import MidiFile

def midi_note_to_freq(note):
    return 440.0 * 2 ** ((note - 69) / 12)

def get_template_for_instrument(instrument_name):
    mapping = {
        'piano': 'synth.json',
        'synth': 'synth.json',
        'lead': 'synth.json',
        'bells': 'blipSelect.json',
        'bass': 'pickupCoin.json',
        'kick': 'explosion.json',
        'snare': 'hitHurt.json',
        'hihat': 'click.json',
        'cymbal': 'mutate.json',
        'clap': 'hitHurt.json',
        'tom': 'hitHurt.json',
    }
    for key in mapping:
        if key in instrument_name.lower():
            return mapping[key]
    return 'synth.json'

def load_template(template_dir, template_file):
    path = os.path.join(template_dir, template_file)
    with open(path, 'r') as f:
        return json.load(f)

def midi_to_json(midi_path, template_dir, output_path):
    midi = MidiFile(midi_path)
    level_nodes = []
    sound_id = 1
    for i, track in enumerate(midi.tracks):
        instrument_name = track.name if track.name else 'synth'
        template_file = get_template_for_instrument(instrument_name)
        template = load_template(template_dir, template_file)
        current_time = 0
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                freq = midi_note_to_freq(msg.note)
                current_time += msg.time
                y_pos = current_time
                sound_parameters = {}
                sound_parameters = {
                        "frequencyBase": freq,
                        "frequencyLimit": freq,
                        "frequencyRamp": -100,
                        "frequencyDeltaRamp": -100,
                        "pitchJumpMod": 0.10000000149011612,
                        "dutyCycleRamp": -1,
                        "flangerFrequency": 0.04607183486223221,
                        "highPassFilterFrequency": 18.271696090698242
                    }
                node = {
                    'levelNodeSound': {
                        'position': {'x': 0, 'y': y_pos, 'z': 0},
                        'parameters': sound_parameters,
                        'name': instrument_name,
                        'volume': -1,
                        'maxRangeFactor': 1,
                        'rotation': {'x': 0, 'y': 0, 'z': 0, 'w': 1},
                        'scale': {'x': 1, 'y': 1, 'z': 1}
                    }
                }
                level_nodes.append(node)
                trigger = {
                    'levelNodeTrigger': {
                        'shape': 1001,
                        'position': {'x': 0, 'y': y_pos, 'z': 0},
                        'scale': {'x': 1, 'y': 1, 'z': 1},
                        'rotation': {'x': 0, 'y': 0, 'z': 0, 'w': 1},
                        'isShared': True,
                        'triggerSources': [{'triggerSourceBasic': {'type': 4}}],
                        'triggerTargets': [{'triggerTargetSound': {'objectID': sound_id, 'mode': 3}}]
                    }
                }
                level_nodes.append(trigger)
                sound_id += 1
    result = {
        'formatVersion': 15,
        'title': 'sound',
        'complexity': 13,
        'maxCheckpointCount': 10,
        'ambienceSettings': {
            'skyZenithColor': {'r': 0.28, 'g': 0.476, 'b': 0.73, 'a': 1},
            'skyHorizonColor': {'r': 0.916, 'g': 0.9574, 'b': 0.9574, 'a': 1},
            'sunAltitude': 45,
            'sunAzimuth': 315,
            'sunSize': 1
        },
        'levelNodes': level_nodes
    }
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=4)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Usage: python midi2json.py <input.mid> <output.json>')
        sys.exit(1)
    midi_to_json(sys.argv[1], 'templates', sys.argv[2])
