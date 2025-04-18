from dotenv import load_dotenv
load_dotenv()


#Step1a: Setup Text to Speech–TTS–model with gTTS
import os
from gtts import gTTS

def text_to_speech_with_gtts_old(input_text, output_filepath):
    language="en"

    audioobj= gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)


input_text="Hi this is Gen Ai with Vinay!"
# text_to_speech_with_gtts_old(input_text=input_text, output_filepath="gtts_testing.mp3")

#Step1b: Setup Text to Speech–TTS–model with ElevenLabs
from elevenlabs import save as save_audio 
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY=os.environ.get("ELEVENLABS_API_KEY")

def text_to_speech_with_elevenlabs_old(input_text, output_filepath):
    client=ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio=client.generate(
        text= input_text,
        voice= "Aria",
        output_format= "mp3_22050_32",
        model= "eleven_turbo_v2"
    )
    save_audio(audio, output_filepath)

# text_to_speech_with_elevenlabs_old(input_text, output_filepath="elevenlabs_testing.mp3") 


#Step2: Use Model for Text output to Voice --> for automatic playback

import subprocess
import platform
from gtts import gTTS
from pydub import AudioSegment
import os

def text_to_speech_with_gtts(input_text, output_filepath_mp3="gtts_output.mp3"):
    language = "en"
    
    # Step 1: Save MP3 from gTTS
    audioobj = gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath_mp3)

    # Step 2: Convert MP3 to WAV
    output_filepath_wav = output_filepath_mp3.replace(".mp3", ".wav")
    sound = AudioSegment.from_mp3(output_filepath_mp3)
    sound.export(output_filepath_wav, format="wav")

    # Step 3: OS-based playback
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath_wav])
        elif os_name == "Windows":  # Windows
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath_wav}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath_wav])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")
    
    return output_filepath_wav

def text_to_speech_with_elevenlabs(input_text, output_filepath_mp3="elevenlabs_output.mp3"):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.generate(
        text=input_text,
        voice="Aria",
        output_format="mp3_22050_32",
        model="eleven_turbo_v2"
    )
    save_audio(audio, output_filepath_mp3)

    # Convert to WAV
    output_filepath_wav = output_filepath_mp3.replace(".mp3", ".wav")
    sound = AudioSegment.from_mp3(output_filepath_mp3)
    sound.export(output_filepath_wav, format="wav")

    # Play audio based on OS
    os_name = platform.system()
    try:
        if os_name == "Darwin":
            subprocess.run(['afplay', output_filepath_wav])
        elif os_name == "Windows":
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath_wav}").PlaySync();'])
        elif os_name == "Linux":
            subprocess.run(['aplay', output_filepath_wav])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")
    
    return output_filepath_wav