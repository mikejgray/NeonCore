from os.path import join, dirname
from mycroft.configuration import Configuration
from mycroft.processing_modules import ModuleLoaderService
from mycroft.util.json_helper import merge_dict
from speech_recognition import AudioData


class AudioParsersService(ModuleLoaderService):

    def __init__(self, bus):
        parsers_dir = join(dirname(__file__), "modules").rstrip("/")
        super(AudioParsersService, self).__init__(bus, parsers_dir)
        self.config = Configuration.get().get("audio_parsers", {})
        self.blacklist = self.config.get("blacklist", [])

    def feed_audio(self, chunk):
        for module in self.modules:
            instance = self.get_module(module)
            instance.on_audio(chunk)

    def feed_hotword(self, chunk):
        for module in self.modules:
            instance = self.get_module(module)
            instance.on_hotword(chunk)

    def feed_speech(self, chunk):
        for module in self.modules:
            instance = self.get_module(module)
            instance.on_speech(chunk)

    def get_context(self, audio_data):
        context = {}
        for module in self.modules:
            instance = self.get_module(module)
            audio_data, data = instance.on_speech_end(audio_data)
            context = merge_dict(context, data)
        return audio_data, context


class AudioParser:
    # audio chunks are AudioData objects,
    # read https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__init__.py#L325

    def __init__(self, name="test_parser", priority=50):
        self.name = name
        self.bus = None
        self.priority = priority
        self.config = Configuration.get().\
            get("audio_parsers", {}).get( self.name, {})

    def bind(self, bus):
        """ attach messagebus """
        self.bus = bus

    def initialize(self):
        """ perform any initialization actions """
        pass

    def on_audio(self, audio_data):
        """ Take any action you want, audio_data is a non-speech chunk """
        assert isinstance(audio_data, AudioData)

    def on_hotword(self, audio_data):
        """ Take any action you want, audio_data is a full wake/hotword
        Common action would be to prepare to received speech chunks
        NOTE: this might be a hotword or a wakeword, listening is not assured
        NOTE: file consumer will not call this, it is NOT safe to assume
        this is always called before on_speech
        """
        assert isinstance(audio_data, AudioData)

    def on_speech(self, audio_data):
        """ Take any action you want, audio_data is a speech chunk (NOT a
        full utterance) during recording

         NOTE: file consumer might send a full utterance

         You can do streaming predictions or save the audio_data"""
        assert isinstance(audio_data, AudioData)

    def on_speech_end(self, audio_data):
        """ return any additional message context to be passed in
        recognize_loop:utterance message, usually a streaming prediction

         Optionally make the prediction here with saved chunks (extra latency
         """
        return audio_data, {}

    def default_shutdown(self):
        """ perform any shutdown actions """
        pass
