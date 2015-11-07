#!/usr/bin/python

# License: Public Domain
# Hackable PCM demodulator/decoder.
# Author: Tomasz bla Fortuna

import sys
import numpy
from gnuradio import gr
from top_block import top_block
from IPython import embed

class Decoder(gr.sync_block):
    """
    PWM/OOK signal decoder. Bits are decoded using LOW level length
    """

    # Input values over HIGH_LEVEL are considered... high.
    HIGHLEVEL = 0.05

    # Number of samples to consider PWM bit to be `high'
    HIGH_SAMPLES = 100
    # Minimal number of samples to filter out trash
    MIN_SAMPLES = 10
    # min_samples < low_state_count < high_samples < high_state_count

    # Internal state (FSM)
    SILENCE, PACKET = range(2)

    # Silent samples to consider end of packet
    PACKET_GAP = 500

    def __init__(self):
        super(Decoder, self).__init__(name="decoder",
                                      in_sig=[numpy.float32],
                                      out_sig=[])

        self.packet = []
        self.silence_counter = 0
        self.status = self.SILENCE


    def work(self, input_items, output_items):
        "Detect long pauses in signal gather data when it's changing"
        in0 = input_items[0]

        # [real values] -> [True, False, False, True, ...]
        quantized = (in0 > self.HIGHLEVEL)

        if self.status == self.SILENCE and not quantized.any():
            # Silence, silence, silence. We're done.
            return len(in0)

        # We are gathering data for packet, there might be more data
        # or enough silence to start packet analysis.
        for state in quantized:
            if self.status == self.PACKET or state:
                self.packet.append(state)

                if state:
                    self.silence_counter = 0
                    self.status = self.PACKET
                else:
                    self.silence_counter += 1

                    if self.silence_counter > self.PACKET_GAP:
                        self.handle_packet()
                        self.status = self.SILENCE

        return len(in0)

    def handle_packet(self):
        "Extract bits from packet"
        print "PACKET samples={}".format(len(self.packet))

        # Gathered bits
        bits = []

        HIGH, LOW = True, False
        # Current assumed state
        cur_state = True
        # Bit counter
        cur_cnt = 0

        first_high = self.packet.index(True)
        for i in range(first_high, len(self.packet)):
            state = self.packet[i]

            # In general - count length of low-states
            if not state:
                if cur_state is LOW:
                    cur_cnt += 1
                else:
                    cur_state = LOW
                    cur_cnt = 0
            else:
                # New state is High
                if cur_state is LOW:
                    # Handle end of bit
                    #print "BIT LEN:", cur_cnt
                    if cur_cnt < self.MIN_SAMPLES:
                        pass
                    elif cur_cnt > self.HIGH_SAMPLES:
                        bits.append(1)
                    else:
                        bits.append(0)

                    cur_state = HIGH
                    cur_cnt = 0
                else:
                    # Is high, was high, doesn't matter
                    pass

        # Clear data for next packet
        del self.packet
        self.packet = []
        print "DECODED TO", "".join(str(b) for b in bits)


class FinalBlock(top_block):
    "Create a block with our analyzer connected"
    def __init__(self):
        super(FinalBlock, self).__init__()

        self.decoder = Decoder()

        self.connect((self.last_block, 0),
                     (self.decoder, 0))


def main():
    "Generic gnuradio start code"
    from gnuradio import gr
    from PyQt4 import Qt
    from distutils.version import StrictVersion
    from gnuradio.eng_option import eng_option
    from optparse import OptionParser
    import sys
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui','style','raster'))
    qapp = Qt.QApplication(sys.argv)
    tb = FinalBlock()
    tb.start()
    tb.show()
    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None #to clean up Qt widgets


if __name__ == "__main__":
    main()
