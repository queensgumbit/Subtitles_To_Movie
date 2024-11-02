import whisper
import pysrt
from moviepy.editor import VideoFileClip

class MovieSubtitle:
    def __init__(self, movie_file, subtitle_file):
        self.movie_file = movie_file
        self.subtitle_file = subtitle_file
        self.first_word = None
        self.first_word_time = None
        self.first_subtitle_time = None

    def extract_audio_and_transcribe(self):
        video = VideoFileClip(self.movie_file)
        audio = video.audio
        audio_file = "movie_audio.wav"
        audio.write_audiofile(audio_file)
        
        model = whisper.load_model("base")
        result = model.transcribe(audio_file)
        
        # first spoken word and its timestamp
        self.first_word = result['text'].split()[0] #"text" indicated that the audio is turned into text, then "split()" - splitting the text to each word,[0]-first word
        self.first_word_time = result['segments'][0]['start'] #"segments" indicated that the audio is turned into segments of each text and its end and start time.[0]-first segment,['start']-the start time of the first text.

    def get_first_subtitle_time(self):
        # timestamp of the first subtitle line.
        subtitles = pysrt.open(self.subtitle_file) #pysrt is a libarary that can read .srt(subtitles) files.
        first_subtitle = subtitles[0]
        self.first_subtitle_time = first_subtitle.start.to_seconds() #'start' - pysrt is able to access the time of the subtitles +'to_seconds' converts the time to seconds(more convenient to work with one time unit) 

    def compare_times(self):
        #Compare the first word and first subtitle times.
        first_word_time_seconds = self.first_word_time #audio first word
        first_subtitle_time = self.first_subtitle_time #subtitles first word
        is_time_match = abs(first_word_time_seconds - first_subtitle_time) <= 0.1 #if its more that 0.1 return false, if its less or equall-return true
        time_difference = abs(first_word_time_seconds - first_subtitle_time) #time differns in positive value
        return is_time_match, time_difference

    def adjust_subtitles(self):
        #Adjust subtitle timings
        is_time_match, _ = self.compare_times() #_, ->>second value of the tuple is not needed or will be ignored.checking if the value is true or false no need to create global arguments 
        if not is_time_match:
            subtitles = pysrt.open(self.subtitle_file)
            adjustment = self.first_word_time - self.first_subtitle_time
            for subtitle in subtitles:
                subtitle.shift(seconds=adjustment)
            subtitles.save(r" C:\Users\alexd\Desktop\Yasmin\MovieSubtitlesProject\adjust_movie_commentary.srt")

    def analyze(self):
        self.extract_audio_and_transcribe()
        self.get_first_subtitle_time()
        is_time_match, time_difference = self.compare_times() #return the values to the is_time_match and time_differnce after calling teh function
        self.adjust_subtitles()

        print(f"First word: '{self.first_word}' at {self.first_word_time:.2f} seconds") #.2f - > displayed with 2 decimal places
        print(f"First subtitle at {self.first_subtitle_time:.2f} seconds")
        print(f"Time match: {is_time_match}, Difference: {time_difference:.2f} seconds")


if __name__ == "__main__":
    movie_path = r"C:\Users\alexd\Desktop\Yasmin\MovieSubtitlesProject\Dead Poets Society\Dead.Poets.Society.1989.720p.BluRay.x264.YIFY.mp4"
    subtitle_path = r" C:\Users\alexd\Desktop\Yasmin\MovieSubtitlesProject\movie_commentary.srt"
    analyzer = MovieSubtitle(movie_path, subtitle_path)
    analyzer.analyze()
