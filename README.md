What 
====
Stuff created during free experiment or for SDR "Analysis to
synthesis" presentation on 2015.11.05.

Currently, the most interesting part is as-simple-as-can-be Gnuradio
OOK/PCM decoder - served as a presentation example using as few as
possible blocks, yet able to decode flawlessly transmitted bits.
Code is commented and should be `fine'.

Another tool serves to convert .wav files demodulated using (e.g.)
GQRX to be converted into basic data files and then retransmitted on
Raspberry PI using another tool written in C. Should be able to
replicate any OOK signal without getting into details of its
modulation. Those tools were experimental and are crap.

RC Car 
====== 
There's also code included for an USB joystick control over an
old-school 27MHz RC car. It's signal is simple PCM with constant 4 longer pulses 
and a variable number of shorter pulses which sent one of 8 commands:
- forward, left-forward, right-forward,
- backward, left-backward, right-backward,
- left, right


<a href="http://www.youtube.com/watch?feature=player_embedded&v=yueosDPGutY
" target="_blank"><img src="http://img.youtube.com/vi/yueosDPGutY/0.jpg" 
alt="Youtube video of RC car with gqrx showing signal" width="532" height="400" border="10" /></a>


License
=======
PCM decoder is licensed as public domain. Rpi signal replicator code
is based on PIHAT which is based on PIFM and PIFM licensing (GNU GPL
as mentioned on project page) applies.

