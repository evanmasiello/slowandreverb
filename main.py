#!/usr/bin/env python
# =================================
# Sound viewer
# ------------
# [May 2020] - Mina PECHEUX
#
# Based on the work by Yu-Jie Lin
# (Public Domain)
# Github: https://gist.github.com/manugarri/1c0fcfe9619b775bb82de0790ccb88da

import wave
import click
import os

from compute import plt, compute, WIDTH, HEIGHT, \
 SAMPLE_SIZE, CHANNELS, RATE, FPS

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('filename', type=str)
@click.option('-m', '--method', help='Method to use for the video processing', required=True,
              type=click.Choice(['bars', 'spectrum', 'wave', 'rain'], case_sensitive=False))
@click.option('-c', '--color', help='An hex color or "hue_rotate" to auto-update the color throughout the film',
              type=str, default='hue_rotate', show_default=True)
@click.option('--output/--no-output', help='Whether to save the result in a file or display it directly',
              default=True, show_default=True)
def main(filename, method, color, output):
  dpi = plt.rcParams['figure.dpi']
  plt.rcParams['savefig.dpi'] = 300
  plt.rcParams['figure.figsize'] = (1.0 * WIDTH / dpi, 1.0 * HEIGHT / dpi)

  wf = wave.open(filename + '.wav', 'rb')

  # print(wf.getnchannels())
  # print(CHANNELS)
  # print(wf.getsampwidth())
  # print(SAMPLE_SIZE)
  # print(wf.getframerate())
  # print(RATE)

  assert wf.getnchannels() == CHANNELS
  assert wf.getsampwidth() == SAMPLE_SIZE
  #assert wf.getframerate() == RATE

  fig = plt.figure(facecolor='black', edgecolor='black')

  ani = compute(method, color, fig, wf)
  if ani is None:
    wf.close()
    return

  if output:
    ani.save(filename + '.mp4', fps=FPS, savefig_kwargs={'facecolor':'black'})
  else:
    plt.show()

  wf.close()
  os.system('sh add_audio_to_video.sh -a slowreverb -v slowreverb')

if __name__ == '__main__':
  main()
