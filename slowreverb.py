from __future__ import unicode_literals
import yt_dlp
import ffmpeg
import sys

import streamlit as st
import os

import math

"""
# Slow and Reverb

In this form enter a youtube song link to slow and reverb the audio, a video will also be generated with the slowed and reverbed song.
You can edit the of the video using the slider below, the higher the resolution the longer the video will take to generate.

"""

try:
    dir = './thumbnail/'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

    os.remove("slowreverb.wav")
    os.remove("slowreverb.mp4")
    os.remove("slowreverb_processed.mp4")
    os.remove("slowreverb_processed_done.mp4")
    os.remove("slowreverb_processed_done_processed.mp4")
    os.remove("slow.wav")
    os.remove("test.wav")
except:
    print("no old files")

done = False

if (done == False):
    slider = st.slider("Video Resolution", min_value=0.1, max_value=1.0, value=0.5)

url = st.text_input('Enter a youtube url')

if (url):

    #os.system("youtube-dl --write-thumbnail --skip-download " + url)

    #print("finished")

    from pythumb import Thumbnail
    t = Thumbnail(url)
    t.fetch()
    t.save('thumbnail')

    ydl_opts = {
        'format': 'bestaudio/best',
    #    'outtmpl': 'output.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': 'test',
        'write-thumbnail': 'True',
    }
    def download_from_url(url):
        ydl.download([url])
        stream = ffmpeg.input('output.m4a')
        stream = ffmpeg.output(stream, 'output.wav')


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        args = sys.argv[1:]
        download_from_url(url)


    from pydub import AudioSegment

    sound = AudioSegment.from_file("test.wav", format="wav")

    def speed_change(sound, speed=1.0):
        # Manually override the frame_rate. This tells the computer how many
        # samples to play per second
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * speed)
        })

        # convert the sound with altered frame rate to a standard frame rate
        # so that regular playback programs will work right. They often only
        # know how to play audio at standard frame rate (like 44.1k)
        return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

    slow_sound = speed_change(sound, 0.8).export("slow.wav", format="wav")

    import argparse
    import os
    import sys
    import warnings

    import numpy as np
    import soundfile as sf
    from tqdm import tqdm
    from tqdm.std import TqdmWarning

    from pedalboard import Reverb

    BUFFER_SIZE_SAMPLES = 1024 * 16
    NOISE_FLOOR = 1e-4


    def get_num_frames(f: sf.SoundFile) -> int:
        # On some platforms and formats, f.frames == -1L.
        # Check for this bug and work around it:
        if f.frames > 2 ** 32:
            f.seek(0)
            last_position = f.tell()
            while True:
                # Seek through the file in chunks, returning
                # if the file pointer stops advancing.
                f.seek(1024 * 1024 * 1024, sf.SEEK_CUR)
                new_position = f.tell()
                if new_position == last_position:
                    f.seek(0)
                    return new_position
                else:
                    last_position = new_position
        else:
            return f.frames


    def main():
        warnings.filterwarnings("ignore", category=TqdmWarning)

        parser = argparse.ArgumentParser(description="Add reverb to an audio file.")
        # parser.add_argument("input_file", help="The input file to add reverb to.")
        parser.add_argument(
            "--output-file",
            help=(
                "The name of the output file to write to. If not provided, {input_file}.reverb.wav will"
                " be used."
            ),
            default=None,
        )

        # Instantiate the Reverb object early so we can read its defaults for the argparser --help:
        reverb = Reverb()

        parser.add_argument("--room-size", type=float, default=reverb.room_size)
        parser.add_argument("--damping", type=float, default=reverb.damping)
        parser.add_argument("--wet-level", type=float, default=reverb.wet_level)
        parser.add_argument("--dry-level", type=float, default=reverb.dry_level)
        parser.add_argument("--width", type=float, default=reverb.width)
        parser.add_argument("--freeze-mode", type=float, default=reverb.freeze_mode)

        parser.add_argument(
            "-y",
            "--overwrite",
            action="store_true",
            help="If passed, overwrite the output file if it already exists.",
        )

        parser.add_argument(
            "--cut-reverb-tail",
            action="store_true",
            help=(
                "If passed, remove the reverb tail to the end of the file. "
                "The output file will be identical in length to the input file."
            ),
        )
        args = parser.parse_args()

        args.overwrite = True

        for arg in ('room_size', 'damping', 'wet_level', 'dry_level', 'width', 'freeze_mode'):
            setattr(reverb, arg, getattr(args, arg))

        args.input_file = "slow.wav"

        if not args.output_file:
            args.output_file = "slowreverb.wav"

        sys.stderr.write(f"Opening {args.input_file}...\n")

        with sf.SoundFile(args.input_file) as input_file:
            sys.stderr.write(f"Writing to {args.output_file}...\n")
            if os.path.isfile(args.output_file) and not args.overwrite:
                raise ValueError(
                    f"Output file {args.output_file} already exists! (Pass -y to overwrite.)"
                )
            with sf.SoundFile(
                args.output_file,
                'w',
                samplerate=input_file.samplerate,
                channels=input_file.channels,
            ) as output_file:
                length = get_num_frames(input_file)
                length_seconds = length / input_file.samplerate
                sys.stderr.write(f"Adding reverb to {length_seconds:.2f} seconds of audio...\n")
                with tqdm(
                    total=length_seconds,
                    desc="Adding reverb...",
                    bar_format=(
                        "{percentage:.0f}%|{bar}| {n:.2f}/{total:.2f} seconds processed"
                        " [{elapsed}<{remaining}, {rate:.2f}x]"
                    ),
                    # Avoid a formatting error that occurs if
                    # TQDM tries to print before we've processed a block
                    delay=1000,
                ) as t:
                    for dry_chunk in input_file.blocks(BUFFER_SIZE_SAMPLES, frames=length):
                        # Actually call Pedalboard here:
                        # (reset=False is necessary to allow the reverb tail to
                        # continue from one chunk to the next.)
                        effected_chunk = reverb.process(
                            dry_chunk, sample_rate=input_file.samplerate, reset=False
                        )
                        # print(effected_chunk.shape, np.amax(np.abs(effected_chunk)))
                        output_file.write(effected_chunk)
                        t.update(len(dry_chunk) / input_file.samplerate)
                        t.refresh()
                if not args.cut_reverb_tail:
                    while True:
                        # Pull audio from the effect until there's nothing left:
                        effected_chunk = reverb.process(
                            np.zeros((BUFFER_SIZE_SAMPLES, input_file.channels), np.float32),
                            sample_rate=input_file.samplerate,
                            reset=False,
                        )
                        if np.amax(np.abs(effected_chunk)) < NOISE_FLOOR:
                            break
                        output_file.write(effected_chunk)
        os.remove("slow.wav")
        os.remove("test.wav")
        sys.stderr.write("Done!\n")


    if __name__ == "__main__":
        main()
        done = True

    if (done):

        with open("slowreverb.wav", "rb") as file:
            st.audio(file, format='audio/wav')
            st.download_button(
                label="Download Song",
                data=file,
                file_name="slowreverb.wav",
                mime="audio/wav"
            )

        os.system('python3 main.py slowreverb -m bars')

        import moviepy
        import moviepy.editor as mp

        import os
        fnames = os.listdir("./thumbnail/")

        # print(fnames[1])
        for image in fnames:
            print(image)

        from PIL import Image

        image = Image.open("./thumbnail/"+fnames[0])
        print(f"Original size : {image.size}") # 5464x3640

        if (slider == 1):
            image_resized = image
        else:
            image_resized = image.resize((math.floor(image.width*slider), math.floor(image.height*slider)))
            image_resized.save('./thumbnail/'+fnames[0])

        video = mp.VideoFileClip("slowreverb.mp4")
        logo = (mp.ImageClip("./thumbnail/" + fnames[0]))

        video = video.resize(height=image.height*slider)

        print("duration ")
        print(video.duration)

        #logo = logo.set_duration(video.duration)

        video = video.fx(mp.vfx.mask_color, color=[0, 0, 0], thr=100, s=5)

        final = mp.CompositeVideoClip([logo, video.set_position("center")])

        final = final.set_duration(video.duration)
        final.write_videofile("slowreverb_processed_done.mp4")

        os.system('sh add_audio_to_video.sh -a slowreverb -v slowreverb_processed_done')

        os.remove("./thumbnail/" + fnames[0])

        with open("slowreverb_processed_done_processed.mp4", "rb") as file2:
            st.video(file2, format='video/mp4')
            st.download_button(
                label="Download video",
                data=file2,
                file_name="slowreverb.mp4",
                mime="video/wav"
            )
            
        os.remove("slowreverb.wav")
        os.remove("slowreverb.mp4")
        os.remove("slowreverb_processed.mp4")
        os.remove("slowreverb_processed_done_processed.mp4")
    
