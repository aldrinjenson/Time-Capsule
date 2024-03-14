# tests/test_text.py

import unittest
from unittest.mock import patch
from pynput import keyboard
from text.text_capture import TextCapture

class TestTextCapture(unittest.TestCase):
    def setUp(self):
        self.output_dir = "/path/to/test/output"
        self.text_capture = TextCapture(output_dir=self.output_dir)

    def tearDown(self):
        self.text_capture.stop_capture()

    @patch('text.text_capture.TextCapture.save_current_phrase')
    def test_on_key_press(self, mock_save_current_phrase):
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('a'))
        self.assertEqual(self.text_capture.current_phrase, 'a')

    @patch('text.text_capture.TextCapture.save_current_phrase')
    def test_on_key_press_special_keys(self, mock_save_current_phrase):
        self.text_capture.on_key_press(keyboard.Key.enter)
        mock_save_current_phrase.assert_called_with(context_switch=True)

        self.text_capture.on_key_press(keyboard.Key.space)
        self.assertEqual(self.text_capture.current_phrase, ' ')

        self.text_capture.on_key_press(keyboard.Key.backspace)
        self.assertEqual(self.text_capture.current_phrase, '')

    def test_word_completion(self):
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('H'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('e'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('l'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('l'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('o'))
        self.text_capture.on_key_press(keyboard.Key.space)

        self.assertEqual(self.text_capture.current_phrase, 'Hello ')

    @patch('text.text_capture.TextCapture.save_current_phrase')
    def test_continuous_typing(self, mock_save_current_phrase):
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('T'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('h'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('i'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('s'))
        self.text_capture.on_key_press(keyboard.Key.space)
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('i'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('s'))
        self.text_capture.on_key_press(keyboard.Key.space)
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('a'))
        self.text_capture.on_key_press(keyboard.Key.space)
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('t'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('e'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('s'))
        self.text_capture.on_key_press(keyboard.KeyCode.from_char('t'))
        self.text_capture.on_key_press(keyboard.Key.enter)

        self.assertEqual(self.text_capture.current_phrase, '')
        mock_save_current_phrase.assert_called_with(context_switch=True)

    def on_key_press(self, key):
        ...
        try:
            char = key.char
            self.current_phrase += char
            self.last_activity_time = time.time()

            # Check for specific key combinations associated with context switching
            if key in [keyboard.Key.alt_l, keyboard.Key.cmd, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                self.save_current_phrase(context_switch=True)
            elif key == keyboard.Key.enter:
                self.current_phrase += "\n"
                self.save_current_phrase(context_switch=True)

        except AttributeError:
            if key == keyboard.Key.space:
                self.current_phrase += " "
            elif key == keyboard.Key.backspace:
                self.current_phrase = self.current_phrase[:-1]
            elif key == keyboard.Key.tab:
                self.current_phrase += "\t"

if __name__ == "__main__":
    unittest.main()