from MIDI_conversion import *

def test_melody_to_MIDI():
    melody = [[76,74,76,74],[74],[72],[74],[76,76],[76,76,76],[76],[-1]]
    melody_to_MIDI(melody)
    midi_to_wav('./unit_tests/test_results/melody_to_midi_test.mid','./unit_tests/test_results/melody_to_midi_test.wav')

if __name__ == "__main__":
    test_melody_to_MIDI()
