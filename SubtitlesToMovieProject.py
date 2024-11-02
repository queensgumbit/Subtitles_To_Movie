import whisper
import pysrt
from moviepy.editor import VideoFileClip

class MovieSubtitle:
    def _init_(self, movie_file, subtitle_file):
        self.movie_file = movie_file
        self.subtitle_file = subtitle_file
        self.first_word = None
        self.first_word_time = None
        self.first_subtitle_time = None

    def extract_audio_and_transcribe(self):
        #Extract audio from the movie file and transcribe it.
        video = VideoFileClip(self.movie_file)
        audio = video.audio
        audio_file = "movie_audio.wav"
        audio.write_audiofile(audio_file)
        
        model = whisper.load_model("base")
        result = model.transcribe(audio_file)
        
        # first spoken word and its timestamp
        self.first_word = result['text'].split()[0]
        self.first_word_time = result['segments'][0]['start']

    def get_first_subtitle_time(self):
        # timestamp of the first subtitle line.
        subtitles = pysrt.open(self.subtitle_file)
        first_subtitle = subtitles[0]
        self.first_subtitle_time = first_subtitle.start.to_seconds()

    def compare_times(self):
        #Compare the first word and first subtitle times.
        first_word_time_seconds = self.first_word_time
        first_subtitle_time = self.first_subtitle_time
        is_time_match = abs(first_word_time_seconds - first_subtitle_time) < 0.1
        time_difference = abs(first_word_time_seconds - first_subtitle_time)
        return is_time_match, time_difference

    def adjust_subtitles(self):
        #Adjust subtitle timings
        is_time_match, _ = self.compare_times()
        if not is_time_match:
            subtitles = pysrt.open(self.subtitle_file)
            adjustment = self.first_word_time - self.first_subtitle_time
            for subtitle in subtitles:
                subtitle.shift(seconds=adjustment)
            subtitles.save('/path/to/adjusted_subtitles.srt')

    def analyze(self):
        #Run the analysis process.
        self.extract_audio_and_transcribe()
        self.get_first_subtitle_time()
        is_time_match, time_difference = self.compare_times()
        self.adjust_subtitles()

        print(f"First word: '{self.first_word}' at {self.first_word_time:.2f} seconds")
        print(f"First subtitle at {self.first_subtitle_time:.2f} seconds")
        print(f"Time match: {is_time_match}, Difference: {time_difference:.2f} seconds")

# Example usage:
if _name_ == "_main_":
    movie_path = "/path/to/your/movie.mp4"
    subtitle_path = "/path/to/your/subtitles.srt"
    analyzer = MovieSubtitleAnalyzer(movie_path, subtitle_path)
    analyzer.analyze()