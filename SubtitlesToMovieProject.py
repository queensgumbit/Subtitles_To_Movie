import whisper
import pysrt
import os

class MovieSubtitle:
    def __init__(self, movie_file, subtitle_file):
        self.movie_file = movie_file
        self.srt = Srt(subtitle_file) 
        self.first_word = None
        self.first_word_time = None
        self.first_subtitle_time = None

    def extract_audio_and_transcribe(self):
        video_path = self.movie_file
        audio_file = 'audio_of_movie.wav'

        os.system(f'ffmpeg -i "{video_path}" -t 300 -vn -acodec pcm_s16le -ar 44100 -ac 2 "{audio_file}"') #300 [second]-> 5 minutes
        os.system(f'ffmpeg -i "{video_path}" -af silenceremove=1:0:-50dB output.wav') #pre proccesing the uadio
        os.system(f'ffmpeg -i "{video_path}" -filter:a loudnorm output.wav') #pre proccesing the audio
        model = whisper.load_model("base")
        result = model.transcribe(
               audio_file,
               language="en",           
               temperature=0.2,         # lower temperature ->> more consistent transcriptions
               beam_size=5,             # increase beam size ->> explore more transcription options
               task="transcribe",       
               word_timestamps=True     # timestamps for each individual word within the transcription
)
        # first spoken word and its timestamp
        self.first_word = result['text'].split()[0] #"text" indicated that the audio is turned into text, then "split()" - splitting the text to each word,[0]-first word
        self.first_word_time = result['segments'][0]['start'] #"segments" indicated that the audio is turned into segments of each text and its end and start time.[0]-first segment,['start']-the start time of the first text.

    def compare_times(self):
        #Compare the first word and first subtitle times.
        first_word_time_seconds = self.first_word_time #audio first word
        first_subtitle_time = self.srt.first_spoken_line_time() #self.srt calls the Srt function
        if first_subtitle_time is not None:
            time_difference = abs(first_word_time_seconds - first_subtitle_time)
            is_time_match = time_difference <= 0.1
            
            if not is_time_match:
                adjustment = self.first_word_time - first_subtitle_time
                self.srt.shift_subtitles(adjustment)
            return is_time_match, time_difference
        return False,None
    

    def analyze(self):
        self.extract_audio_and_transcribe()
        is_time_match, time_difference = self.compare_times() #return the values to the is_time_match and time_differnce after calling teh function
        
        print(f"First word: '{self.first_word}' at {self.first_word_time:.2f} seconds") #.2f - > displayed with 2 decimal places
        print(f"First subtitle at {self.first_subtitle_time:.2f} seconds")
        print(f"Time match: {is_time_match}, Difference: {time_difference:.2f} seconds")


class Srt:
    def __init__(self,subtitle_file):
        self.subtitle_file = subtitle_file
        self.subtitles = pysrt.open(subtitle_file)
    
    def first_spoken_line_time(self):
        "first [word] line without music symbols!"
        for subtitle in self.subtitles:
            if "♪" not in subtitle.text and "♫" not in subtitle.text:
                return subtitle.start.to_seconds() #returns time in seconds
        return None

    def shift_subtitles(self, adjustment):
        "the actual adjustment of the srt file is the srt class, shifting the subtitles by the specific adjustmnet"
        for subtitle in self.subtitles:
            subtitle.shift(second=adjustment) #we get the adjustment from the moviesub class
        self.subtitles.save(r"C:\Users\alexd\Desktop\Yasmin\MovieSubtitlesProject\adjust_movie_commentary.srt")

        


        
if __name__ == "__main__":
    movie_path = r"C:\Users\alexd\Desktop\Yasmin\MovieSubtitlesProject\Dead Poets Society\Dead.Poets.Society.1989.720p.BluRay.x264.YIFY.mp4"
    subtitle_path = r" C:\Users\alexd\Desktop\Yasmin\MovieSubtitlesProject\movie_commentary.srt"
    analyzer = MovieSubtitle(movie_path, subtitle_path)
    analyzer.analyze()
