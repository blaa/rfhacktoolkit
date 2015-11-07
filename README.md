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


License
=======
PCM decoder is licensed as public domain. Rpi signal replicator code
is based on PIHAT which is based on PIFM and PIFM licensing (GNU GPL
as mentioned on project page) applies.

